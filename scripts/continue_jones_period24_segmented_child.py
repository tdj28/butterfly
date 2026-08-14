#!/usr/bin/env python3
"""Continue one primitive segmented period-24 candidate away from its flip."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import scipy

from butterfly import (
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    flow_monodromy,
    legacy_rossler_section,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from multiple_shooting_core import correct_arclength
from qualify_jones_period12_children import _section_count
from validate_multiple_shooting_switch import half_closure
from switch_jones_period12_segmented_child import normalized_event, qualified_audit_bytes


SCHEMAS = {
    "butterfly.jones-period24-segmented-continuation-manifest.v1",
    "butterfly.jones-period48-segmented-continuation-manifest.v1",
    "butterfly.jones-period96-segmented-continuation-manifest.v1",
    "butterfly.jones-period192-segmented-continuation-manifest.v1",
    "butterfly.jones-period384-segmented-continuation-manifest.v1",
    "butterfly.jones-period768-segmented-continuation-manifest.v1",
    "butterfly.jones-period1536-segmented-continuation-manifest.v1",
}


def variables(row: dict, segment_count: int) -> np.ndarray:
    nodes = np.asarray(row["nodes"], dtype=float)
    if nodes.shape != (segment_count, 3):
        raise ValueError("row node shape does not match segment count")
    return np.r_[nodes.ravel(), float(row["period_time"]), float(row["a"])]


def half_node_rms(value: np.ndarray, segment_count: int) -> float:
    nodes = value[: 3 * segment_count].reshape(segment_count, 3)
    return float(
        np.sqrt(
            np.mean(
                (nodes[: segment_count // 2] - nodes[segment_count // 2 :]) ** 2
            )
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--switch-receipt", type=Path, required=True)
    parser.add_argument("--event-receipt", type=Path, required=True)
    parser.add_argument("--audit-receipt", type=Path)
    parser.add_argument("--identity-receipt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") not in SCHEMAS:
        raise SystemExit("unsupported Jones period-24 continuation manifest")
    switch_bytes = args.switch_receipt.read_bytes()
    event_bytes = args.event_receipt.read_bytes()
    if sha256_bytes(switch_bytes) != manifest["switch_receipt_sha256"]:
        raise SystemExit("switch receipt hash mismatch")
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    switch = json.loads(switch_bytes)
    raw_event = json.loads(event_bytes)
    if not switch.get("passed"):
        raise SystemExit("a passed switch receipt is required")
    try:
        audit_bytes = qualified_audit_bytes(
            raw_event, event_bytes, manifest, args.audit_receipt
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error
    identity_bytes = None
    if "identity_receipt_sha256" in manifest:
        if args.identity_receipt is None:
            raise SystemExit("this continuation requires a bound identity receipt")
        identity_bytes = args.identity_receipt.read_bytes()
        if sha256_bytes(identity_bytes) != manifest["identity_receipt_sha256"]:
            raise SystemExit("identity receipt hash mismatch")
        identity = json.loads(identity_bytes)
        if (
            not identity.get("passed")
            or identity.get("schema") != manifest["identity_schema"]
            or int(identity.get("canonical_source_sign", 0))
            != int(manifest["source_candidate"]["direction"])
        ):
            raise SystemExit("identity receipt does not qualify the source sign")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    event = normalized_event(raw_event, manifest)
    segment_count = int(manifest["segment_count"])
    target = manifest["source_candidate"]
    candidates = [
        row
        for row in switch["accepted_candidates"]
        if float(row["step_length"]) == float(target["step_length"])
        and int(row["direction"]) == int(target["direction"])
    ]
    if len(candidates) != 1:
        raise SystemExit("source candidate is not uniquely selected")
    seed = candidates[0]
    event_variables = np.r_[
        np.tile(np.asarray(event["nodes"], dtype=float), (2, 1)).ravel(),
        2.0 * float(event["period_time"]),
        float(event["corrected_a"]),
    ]
    points = [event_variables, variables(seed, segment_count)]
    fixed_b = float(manifest["fixed_b"])
    fixed_c = float(manifest["fixed_c"])
    solver = SolverConfig(**manifest["solver"])
    phase_reference = points[0][:3].copy()
    phase_parameters = RosslerParameters(
        a=float(event["corrected_a"]), b=fixed_b, c=fixed_c
    )
    phase = rossler_rhs(0.0, phase_reference, phase_parameters)
    phase /= np.linalg.norm(phase)
    rows = [
        {
            "step_index": -1,
            "a": float(seed["a"]),
            "period_time": float(seed["period_time"]),
            "half_node_rms": half_node_rms(points[-1], segment_count),
            "nodes": seed["nodes"],
            "status": seed["status"],
        }
    ]
    statuses = []
    nominal_step = float(manifest["continuation"]["nominal_step"])
    minimum_step = float(manifest["continuation"]["minimum_step"])
    growth = float(manifest["continuation"]["growth_factor"])
    step_length = nominal_step
    started = time.perf_counter()
    for step_index in range(int(manifest["continuation"]["maximum_steps"])):
        tangent = points[-1] - points[-2]
        tangent /= np.linalg.norm(tangent)
        trial_step = step_length
        accepted = False
        while trial_step >= minimum_step:
            predictor = points[-1] + trial_step * tangent
            corrected, status = correct_arclength(
                predictor,
                tangent,
                segment_count=segment_count,
                a=None,
                c=fixed_c,
                phase=phase,
                phase_reference=phase_reference,
                solver=solver,
                tolerance=float(manifest["corrector"]["tolerance"]),
                max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
                continuation_parameter="a",
                fixed_b=fixed_b,
                sparse_jacobian=manifest.get("jacobian_storage") == "sparse_csr",
            )
            status = {
                **status,
                "step_index": step_index,
                "trial_step": trial_step,
            }
            statuses.append(status)
            if status["success"]:
                accepted = True
                break
            trial_step *= 0.5
        if not accepted:
            break
        points.append(corrected)
        row = {
            "step_index": step_index,
            "a": float(corrected[3 * segment_count + 1]),
            "period_time": float(corrected[3 * segment_count]),
            "half_node_rms": half_node_rms(corrected, segment_count),
            "nodes": corrected[: 3 * segment_count]
            .reshape(segment_count, 3)
            .tolist(),
            "status": status,
        }
        rows.append(row)
        print(
            json.dumps(
                {
                    "step_index": step_index,
                    "a": row["a"],
                    "period_time": row["period_time"],
                    "half_node_rms": row["half_node_rms"],
                    "trial_step": trial_step,
                },
                sort_keys=True,
            ),
            flush=True,
        )
        step_length = min(nominal_step, trial_step * growth)
        a_guard = manifest["continuation"]["a_guard"]
        if not float(a_guard[0]) <= row["a"] <= float(a_guard[1]):
            break

    terminal = rows[-1]
    terminal_nodes = np.asarray(terminal["nodes"], dtype=float)
    terminal_parameters = RosslerParameters(
        a=terminal["a"], b=fixed_b, c=fixed_c
    )
    monodromy = flow_monodromy(
        terminal_parameters,
        terminal_nodes[0],
        terminal["period_time"],
        config=solver,
    )
    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    transverse = np.delete(monodromy.multipliers, neutral_index)
    dominant = complex(transverse[int(np.argmax(np.abs(transverse)))])
    terminal_orbit = SimpleNamespace(
        initial_state=terminal_nodes[0], period_time=terminal["period_time"]
    )
    historical_count = _section_count(
        terminal_parameters,
        terminal_orbit,
        legacy_rossler_section(terminal_parameters),
        int(manifest["identity"]["historical_phase_count"]),
        solver,
    )
    barrio_count = _section_count(
        terminal_parameters,
        terminal_orbit,
        barrio_rossler_section(terminal_parameters),
        int(manifest["identity"]["barrio_phase_count"]),
        solver,
    )
    terminal_diagnostics = {
        "closure_error": float(monodromy.closure_error),
        "neutral_multiplier_error": float(
            abs(monodromy.multipliers[neutral_index] - 1.0)
        ),
        "dominant_transverse_multiplier": {
            "real": float(dominant.real),
            "imag": float(dominant.imag),
            "modulus": float(abs(dominant)),
        },
        "half_period_closure": half_closure(
            terminal_nodes[0],
            terminal["period_time"],
            terminal_parameters,
            solver,
        ),
        "historical_phase_count": historical_count[0],
        "historical_integration_success": historical_count[1],
        "barrio_phase_count": barrio_count[0],
        "barrio_integration_success": barrio_count[1],
    }
    a_span = abs(float(terminal["a"]) - float(event["corrected_a"]))
    acceptance = manifest["acceptance"]
    passed = bool(
        len(rows) >= int(acceptance["minimum_points"])
        and a_span >= float(acceptance["minimum_a_span"])
        and max(row["status"]["matching_residual"] for row in rows)
        <= float(acceptance["maximum_matching_residual"])
        and min(row["half_node_rms"] for row in rows)
        >= float(acceptance["minimum_half_node_rms"])
        and terminal_diagnostics["closure_error"]
        <= float(acceptance["maximum_closure_error"])
        and terminal_diagnostics["neutral_multiplier_error"]
        <= float(acceptance["maximum_neutral_error"])
        and terminal_diagnostics["half_period_closure"]
        >= float(acceptance["minimum_half_period_closure"])
        and abs(terminal["period_time"] / float(event["period_time"]) - 2.0)
        <= float(acceptance["maximum_period_ratio_error"])
        and terminal_diagnostics["historical_integration_success"]
        and terminal_diagnostics["barrio_integration_success"]
        and terminal_diagnostics["historical_phase_count"]
        == int(manifest["identity"]["historical_phase_count"])
        and terminal_diagnostics["barrio_phase_count"]
        == int(manifest["identity"]["barrio_phase_count"])
    )
    output = {
        "schema": manifest.get(
            "output_schema",
            "butterfly.jones-period24-segmented-continuation-receipt.v1",
        ),
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "switch_receipt_sha256": sha256_bytes(switch_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "audit_receipt_sha256": (
            sha256_bytes(audit_bytes) if audit_bytes is not None else None
        ),
        "identity_receipt_sha256": (
            sha256_bytes(identity_bytes) if identity_bytes is not None else None
        ),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fixed_b": fixed_b,
        "fixed_c": fixed_c,
        "event_a": float(event["corrected_a"]),
        "parent_period_time": float(event["period_time"]),
        "segment_count": segment_count,
        "rows": rows,
        "statuses": statuses,
        "point_count": len(rows),
        "a_span_from_event": a_span,
        "terminal_diagnostics": terminal_diagnostics,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    printed = {key: value for key, value in output.items() if key != "rows"}
    printed["statuses"] = len(statuses)
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

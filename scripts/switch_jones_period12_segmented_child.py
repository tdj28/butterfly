#!/usr/bin/env python3
"""Switch a qualified segmented Jones flip to doubled-period candidates."""

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
from multiple_shooting_core import base_system, correct_arclength
from qualify_jones_period12_children import _section_count
from switch_augmented_flip_child import phase_fixed_child_tangent
from validate_multiple_shooting_switch import half_closure


SCHEMAS = {
    "butterfly.jones-period12-segmented-child-switch-manifest.v1",
    "butterfly.jones-period24-segmented-child-switch-manifest.v1",
    "butterfly.jones-period48-segmented-child-switch-manifest.v1",
    "butterfly.jones-period96-segmented-child-switch-manifest.v1",
    "butterfly.jones-period192-segmented-child-switch-manifest.v1",
    "butterfly.jones-period384-segmented-child-switch-manifest.v1",
}


def doubled_event_variables(event: dict) -> np.ndarray:
    nodes = np.asarray(event["nodes"], dtype=float)
    return np.r_[
        np.tile(nodes, (2, 1)).ravel(),
        2.0 * float(event["period_time"]),
        float(event["corrected_a"]),
    ]


def qualified_audit_bytes(
    event: dict,
    event_bytes: bytes,
    manifest: dict,
    audit_path: Path | None,
) -> bytes | None:
    """Return a bound passing audit for a failed event, or none for a pass."""
    if event.get("passed"):
        return None
    if audit_path is None:
        raise ValueError("a failed event requires its bound passing audit")
    audit_bytes = audit_path.read_bytes()
    if sha256_bytes(audit_bytes) != manifest.get("audit_receipt_sha256"):
        raise ValueError("audit receipt hash mismatch")
    audit = json.loads(audit_bytes)
    if (
        audit.get("schema") != manifest.get("audit_schema")
        or not audit.get("passed")
        or audit.get("event_receipt_sha256") != sha256_bytes(event_bytes)
        or not all(audit.get("checks", {}).values())
    ):
        raise ValueError("event is not qualified by the bound audit")
    return audit_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") not in SCHEMAS:
        raise SystemExit("unsupported Jones segmented child-switch manifest")
    event_bytes = args.event.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    event = json.loads(event_bytes)
    if event.get("schema") != manifest["event_schema"]:
        raise SystemExit("event schema mismatch")
    try:
        audit_bytes = qualified_audit_bytes(
            event, event_bytes, manifest, args.audit
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    source_segment_count = int(event["segment_count"])
    segment_count = int(manifest["segment_count"])
    if segment_count != 2 * source_segment_count:
        raise SystemExit("target segment count must double the event source")
    fixed_b = float(manifest["fixed_b"])
    fixed_c = float(manifest["fixed_c"])
    if event["fixed_b"] != fixed_b or event["fixed_c"] != fixed_c:
        raise SystemExit("fixed coordinates do not match the event")
    event_a = float(event["corrected_a"])
    event_variables = doubled_event_variables(event)
    solver = SolverConfig(**manifest["solver"])
    parameters = RosslerParameters(a=event_a, b=fixed_b, c=fixed_c)
    phase = rossler_rhs(0.0, event_variables[:3], parameters)
    phase /= np.linalg.norm(phase)
    event_residual, event_jacobian = base_system(
        event_variables,
        segment_count=segment_count,
        a=None,
        c=fixed_c,
        phase=phase,
        phase_reference=event_variables[:3],
        solver=solver,
        continuation_parameter="a",
        fixed_b=fixed_b,
    )
    secondary_tangent, phase_coefficient = phase_fixed_child_tangent(
        event, parameters, phase
    )
    secondary_null_residual = float(
        np.linalg.norm(event_jacobian @ secondary_tangent)
    )
    _, singular_values, _ = np.linalg.svd(event_jacobian, full_matrices=True)
    acceptance = manifest["acceptance"]
    attempts = []
    started = time.perf_counter()
    for step_length in manifest["step_lengths"]:
        for direction in (-1, 1):
            tangent = int(direction) * secondary_tangent
            predictor = event_variables + float(step_length) * tangent
            corrected, status = correct_arclength(
                predictor,
                tangent,
                segment_count=segment_count,
                a=None,
                c=fixed_c,
                phase=phase,
                phase_reference=event_variables[:3],
                solver=solver,
                tolerance=float(manifest["corrector"]["tolerance"]),
                max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
                continuation_parameter="a",
                fixed_b=fixed_b,
            )
            row = {
                "step_length": float(step_length),
                "direction": int(direction),
                "status": status,
                "accepted": False,
            }
            if status["success"]:
                nodes = corrected[: 3 * segment_count].reshape(segment_count, 3)
                duration = float(corrected[3 * segment_count])
                corrected_a = float(corrected[3 * segment_count + 1])
                current_parameters = RosslerParameters(
                    a=corrected_a, b=fixed_b, c=fixed_c
                )
                orbit = SimpleNamespace(initial_state=nodes[0], period_time=duration)
                monodromy = flow_monodromy(
                    current_parameters, nodes[0], duration, config=solver
                )
                neutral_index = int(
                    np.argmin(np.abs(monodromy.multipliers - 1.0))
                )
                transverse = np.delete(monodromy.multipliers, neutral_index)
                dominant = complex(
                    transverse[int(np.argmax(np.abs(transverse)))]
                )
                historical_count = _section_count(
                    current_parameters,
                    orbit,
                    legacy_rossler_section(current_parameters),
                    int(manifest["identity"]["historical_phase_count"]),
                    solver,
                )
                barrio_count = _section_count(
                    current_parameters,
                    orbit,
                    barrio_rossler_section(current_parameters),
                    int(manifest["identity"]["barrio_phase_count"]),
                    solver,
                )
                row.update(
                    {
                        "a": corrected_a,
                        "parameter_displacement": corrected_a - event_a,
                        "period_time": duration,
                        "period_ratio_to_parent": duration
                        / float(event["period_time"]),
                        "matching_closure_error": float(monodromy.closure_error),
                        "neutral_multiplier_error": float(
                            abs(monodromy.multipliers[neutral_index] - 1.0)
                        ),
                        "dominant_transverse_multiplier": {
                            "real": float(dominant.real),
                            "imag": float(dominant.imag),
                            "modulus": float(abs(dominant)),
                        },
                        "half_period_closure": half_closure(
                            nodes[0], duration, current_parameters, solver
                        ),
                        "half_node_rms": float(
                            np.sqrt(
                                np.mean(
                                    (
                                        nodes[: segment_count // 2]
                                        - nodes[segment_count // 2 :]
                                    )
                                    ** 2
                                )
                            )
                        ),
                        "historical_phase_count": historical_count[0],
                        "historical_integration_success": historical_count[1],
                        "barrio_phase_count": barrio_count[0],
                        "barrio_integration_success": barrio_count[1],
                        "initial_state": nodes[0].tolist(),
                        "nodes": nodes.tolist(),
                    }
                )
                row["accepted"] = bool(
                    status["matching_residual"]
                    <= float(acceptance["maximum_matching_residual"])
                    and status["phase_residual"]
                    <= float(acceptance["maximum_phase_residual"])
                    and row["matching_closure_error"]
                    <= float(acceptance["maximum_closure_error"])
                    and row["neutral_multiplier_error"]
                    <= float(acceptance["maximum_neutral_error"])
                    and row["half_period_closure"]
                    >= float(acceptance["minimum_half_period_closure"])
                    and row["half_node_rms"]
                    >= float(acceptance["minimum_half_node_rms"])
                    and float(acceptance["minimum_parameter_displacement"])
                    <= abs(row["parameter_displacement"])
                    <= float(acceptance["maximum_parameter_displacement"])
                    and abs(row["period_ratio_to_parent"] - 2.0)
                    <= float(acceptance["maximum_period_ratio_error"])
                    and row["historical_integration_success"]
                    and row["barrio_integration_success"]
                    and row["historical_phase_count"]
                    == int(manifest["identity"]["historical_phase_count"])
                    and row["barrio_phase_count"]
                    == int(manifest["identity"]["barrio_phase_count"])
                )
            attempts.append(row)
            print(
                json.dumps(
                    {
                        "step_length": step_length,
                        "direction": direction,
                        "accepted": row["accepted"],
                        "status": status,
                        "a": row.get("a"),
                        "half_period_closure": row.get("half_period_closure"),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    accepted = [row for row in attempts if row["accepted"]]
    passed = bool(
        np.linalg.norm(event_residual[:-1])
        <= float(acceptance["maximum_event_matching_residual"])
        and secondary_null_residual
        <= float(acceptance["maximum_secondary_null_residual"])
        and len(accepted) >= int(acceptance["minimum_accepted_candidates"])
    )
    output = {
        "schema": manifest.get(
            "output_schema",
            "butterfly.jones-period12-segmented-child-switch-receipt.v1",
        ),
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "audit_receipt_sha256": (
            sha256_bytes(audit_bytes) if audit_bytes is not None else None
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
        "event_a": event_a,
        "parent_period_time": float(event["period_time"]),
        "source_segment_count": source_segment_count,
        "segment_count": segment_count,
        "event_matching_residual": float(np.linalg.norm(event_residual[:-1])),
        "event_smallest_singular_values": singular_values[-2:].tolist(),
        "phase_fix_coefficient": phase_coefficient,
        "secondary_null_residual": secondary_null_residual,
        "attempts": attempts,
        "accepted_candidates": accepted,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    printed = {**output, "attempts": len(attempts)}
    printed["accepted_candidates"] = [
        {key: value for key, value in row.items() if key != "nodes"}
        for row in accepted
    ]
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

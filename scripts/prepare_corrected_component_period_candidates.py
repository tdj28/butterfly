#!/usr/bin/env python3
"""Correct a geometry-only sample of period-component flow orbits on CPU."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from butterfly import (
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    classify_fundamental_period,
    collect_crossings,
    correct_periodic_orbit,
    flow_monodromy,
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.prepare_gpu_component_period_candidates import farthest_component_sample
from scripts.search_jones_floquet_center import signed_dominant_nontrivial


SCHEMA = "butterfly.corrected-component-period-candidates-manifest.v1"


def _complex_row(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag), "modulus": float(abs(value))}


def _evaluate(task: dict) -> dict:
    selection_index = int(task["selection_index"])
    point_index = int(task["point_index"])
    parameters = RosslerParameters(**task["parameters"])
    expected_period = int(task["expected_period"])
    solver = SolverConfig(**task["solver"])
    crossing = task["crossing"]
    acceptance = task["acceptance"]
    try:
        attractor = collect_crossings(
            parameters,
            tuple(map(float, crossing["initial_state"])),
            legacy_rossler_section(parameters),
            transient=float(crossing["transient"]),
            observation_horizon=float(crossing["observation_horizon"]),
            max_crossings=int(crossing["max_crossings"]),
            config=solver,
        )
        recurrence = classify_fundamental_period(
            attractor.states,
            max_period=int(crossing["max_period"]),
            required_repeats=int(crossing["required_repeats"]),
            atol=float(crossing["atol"]),
            rtol=float(crossing["rtol"]),
        )
        if recurrence.fundamental_period != expected_period:
            raise RuntimeError(
                f"expected period {expected_period}, got {recurrence.fundamental_period}"
            )
        if len(attractor.times) < expected_period + 1:
            raise RuntimeError("insufficient section crossings for a shooting seed")
        seed_index = -expected_period - 1
        seed_state = attractor.states[seed_index]
        seed_period = float(attractor.times[-1] - attractor.times[seed_index])
        correction = correct_periodic_orbit(
            parameters,
            seed_state,
            seed_period,
            config=solver,
            max_evaluations=int(task["corrector"]["maximum_evaluations"]),
            tolerance=float(task["corrector"]["tolerance"]),
        )
        monodromy = flow_monodromy(
            parameters,
            correction.initial_state,
            correction.period_time,
            config=solver,
        )
        dominant, neutral, _ = signed_dominant_nontrivial(monodromy.multipliers)
        barrio = collect_crossings(
            parameters,
            correction.initial_state,
            barrio_rossler_section(parameters),
            transient=0.0,
            observation_horizon=correction.period_time * (1.0 + 1e-7),
            max_crossings=expected_period + 4,
            config=solver,
        )
        keep = (barrio.times > correction.period_time * 1e-7) & (
            barrio.times <= correction.period_time * (1.0 + 1e-7)
        )
        section_states = barrio.states[keep]
        checks = {
            "attractor_integration": bool(attractor.integration_success),
            "period": recurrence.fundamental_period == expected_period,
            "correction": bool(correction.success),
            "closure": correction.closure_error
            <= float(acceptance["maximum_flow_closure"]),
            "phase": abs(correction.phase_residual)
            <= float(acceptance["maximum_phase_residual"]),
            "monodromy_integration": bool(monodromy.success),
            "neutral": abs(neutral - 1.0)
            <= float(acceptance["maximum_neutral_multiplier_error"]),
            "dominant_real": abs(dominant.imag)
            <= float(acceptance["maximum_dominant_imaginary_part"]),
            "stable": abs(dominant) < 1.0,
            "barrio_integration": bool(barrio.integration_success),
            "barrio_crossing_count": len(section_states) == expected_period,
        }
        return {
            "id": f"component-sample-{selection_index:03d}",
            "selection_order": selection_index,
            "point_index": point_index,
            "grid_index": task["grid_index"],
            "parameters": task["parameters"],
            "attractor": {
                "fundamental_period": recurrence.fundamental_period,
                "recurrence_error": recurrence.recurrence_error,
                "recurrence_tolerance": recurrence.recurrence_tolerance,
                "crossing_count": len(attractor.times),
            },
            "correction": {
                "initial_state": correction.initial_state.tolist(),
                "period_time": correction.period_time,
                "closure_error": correction.closure_error,
                "phase_residual": correction.phase_residual,
                "correction_norm": correction.correction_norm,
                "evaluations": correction.evaluations,
                "optimizer_success": correction.optimizer_success,
            },
            "section": {
                "kind": "barrio_positive_x",
                "crossing_count": len(section_states),
            },
            "section_states": section_states.tolist(),
            "dominant_nontrivial_multiplier": _complex_row(dominant),
            "neutral_multiplier": _complex_row(neutral),
            "checks": checks,
            "passed": all(checks.values()),
        }
    except Exception as error:
        return {
            "id": f"component-sample-{selection_index:03d}",
            "selection_order": selection_index,
            "point_index": point_index,
            "grid_index": task["grid_index"],
            "parameters": task["parameters"],
            "error": f"{type(error).__name__}: {error}",
            "passed": False,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported corrected component-candidate manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("corrected component candidates require clean source")
    for evidence in manifest.get("evidence", ()):
        raw = Path(evidence["path"]).read_bytes()
        if sha256_bytes(raw) != evidence["sha256"]:
            raise SystemExit(f"evidence hash mismatch: {evidence['path']}")
    documents = {}
    document_bytes = {}
    for name, declared in manifest["inputs"].items():
        raw = Path(declared["path"]).read_bytes()
        if sha256_bytes(raw) != declared["sha256"]:
            raise SystemExit(f"input hash mismatch: {name}")
        document_bytes[name] = raw
        documents[name] = json.loads(raw)
    frame = documents["frame"]
    frame_receipt = documents["frame_receipt"]
    component = documents["component"]
    if frame_receipt.get("result_sha256") != sha256_bytes(document_bytes["frame"]):
        raise SystemExit("frame receipt does not bind the frame")
    if component.get("frame_sha256") != sha256_bytes(document_bytes["frame"]):
        raise SystemExit("component does not bind the frame")
    shape = tuple(map(int, frame["shape"]))
    rows_by_index = {int(row["point_index"]): row for row in frame["rows"]}
    parameters_by_index = {
        index: (float(row["a"]), float(row["c"]))
        for index, row in rows_by_index.items()
    }
    anchor_index = tuple(map(int, component["anchor_index"]))
    anchor_point_index = anchor_index[0] * shape[1] + anchor_index[1]
    selection = manifest["selection"]
    selected_indices, fill_radius = farthest_component_sample(
        component["point_indices"],
        parameters_by_index,
        sample_count=int(selection["sample_count"]),
        anchor_point_index=anchor_point_index,
    )
    tasks = []
    for selection_index, point_index in enumerate(selected_indices):
        row = rows_by_index[point_index]
        tasks.append(
            {
                "selection_index": selection_index,
                "point_index": point_index,
                "grid_index": list(divmod(point_index, shape[1])),
                "parameters": {
                    "a": float(row["a"]),
                    "b": float(row["b"]),
                    "c": float(row["c"]),
                },
                "expected_period": int(selection["target_period"]),
                "solver": manifest["solver"],
                "crossing": manifest["crossing"],
                "corrector": manifest["corrector"],
                "acceptance": manifest["acceptance"],
            }
        )
    started = time.perf_counter()
    workers = min(int(manifest["parallel"]["maximum_workers"]), os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        candidates = []
        for candidate in executor.map(_evaluate, tasks):
            candidates.append(candidate)
            print(
                json.dumps(
                    {
                        "id": candidate["id"],
                        "passed": candidate["passed"],
                        "error": candidate.get("error"),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    passed_count = sum(row["passed"] for row in candidates)
    receipt = {
        "schema": "butterfly.corrected-component-period-candidates.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "input_sha256": {
            name: sha256_bytes(raw) for name, raw in document_bytes.items()
        },
        "selection": {
            "method": "normalized deterministic farthest-point sampling anchored at the source landmark",
            "target_period": int(selection["target_period"]),
            "component_point_count": len(component["point_indices"]),
            "sample_count": len(selected_indices),
            "point_indices": selected_indices,
            "normalized_fill_radius": fill_radius,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "maximum_workers": workers,
        },
        "passed_candidate_count": passed_count,
        "candidates": candidates,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed_count
        >= int(manifest["acceptance"]["minimum_passed_candidates"]),
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(receipt)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256_bytes(output_bytes),
                "passed": receipt["passed"],
                "passed_candidate_count": passed_count,
                "elapsed_seconds": receipt["elapsed_seconds"],
            },
            sort_keys=True,
        )
    )
    return 0 if receipt["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

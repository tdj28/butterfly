#!/usr/bin/env python3
"""Correct a dense local mesh of one flow-orbit family from a frozen seed."""

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
    collect_crossings,
    correct_periodic_orbit,
    flow_monodromy,
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.search_jones_floquet_center import signed_dominant_nontrivial


SCHEMA = "butterfly.local-barrio-orbit-mesh-manifest.v1"


def local_grid(specification: dict) -> tuple[np.ndarray, np.ndarray]:
    """Return validated, inclusive local ``a`` and ``c`` coordinate arrays."""

    a_values = np.linspace(
        float(specification["a_range"][0]),
        float(specification["a_range"][1]),
        int(specification["a_count"]),
    )
    c_values = np.linspace(
        float(specification["c_range"][0]),
        float(specification["c_range"][1]),
        int(specification["c_count"]),
    )
    if len(a_values) < 3 or len(c_values) < 3:
        raise ValueError("local mesh requires at least three points per axis")
    if not np.all(np.diff(a_values) > 0.0) or not np.all(np.diff(c_values) > 0.0):
        raise ValueError("local mesh axes must be strictly increasing")
    center = specification["required_center"]
    if not np.any(np.isclose(a_values, float(center["a"]), rtol=0.0, atol=1e-14)):
        raise ValueError("required center is absent from the a grid")
    if not np.any(np.isclose(c_values, float(center["c"]), rtol=0.0, atol=1e-13)):
        raise ValueError("required center is absent from the c grid")
    return a_values, c_values


def _complex_row(value: complex) -> dict[str, float]:
    return {
        "real": float(value.real),
        "imag": float(value.imag),
        "modulus": float(abs(value)),
    }


def _one_period_section_states(
    parameters: RosslerParameters,
    correction,
    section,
    expected_count: int,
    solver: SolverConfig,
) -> tuple[np.ndarray, bool]:
    crossings = collect_crossings(
        parameters,
        correction.initial_state,
        section,
        transient=0.0,
        observation_horizon=correction.period_time * (1.0 + 1e-7),
        max_crossings=expected_count + 6,
        config=solver,
    )
    keep = (crossings.times > correction.period_time * 1e-7) & (
        crossings.times <= correction.period_time * (1.0 + 1e-7)
    )
    return crossings.states[keep], bool(crossings.integration_success)


def _evaluate(task: dict) -> dict:
    parameters = RosslerParameters(**task["parameters"])
    solver = SolverConfig(**task["solver"])
    acceptance = task["acceptance"]
    try:
        correction = correct_periodic_orbit(
            parameters,
            task["seed_initial_state"],
            float(task["seed_period_time"]),
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
        legacy_states, legacy_success = _one_period_section_states(
            parameters,
            correction,
            legacy_rossler_section(parameters),
            int(task["historical_phase_count"]),
            solver,
        )
        barrio_states, barrio_success = _one_period_section_states(
            parameters,
            correction,
            barrio_rossler_section(parameters),
            int(task["barrio_phase_count"]),
            solver,
        )
        period_difference = abs(
            correction.period_time - float(task["seed_period_time"])
        )
        checks = {
            "correction": bool(correction.success),
            "closure": correction.closure_error
            <= float(acceptance["maximum_flow_closure"]),
            "phase": abs(correction.phase_residual)
            <= float(acceptance["maximum_phase_residual"]),
            "correction_norm": correction.correction_norm
            <= float(acceptance["maximum_correction_norm"]),
            "period_identity": period_difference
            <= float(acceptance["maximum_period_time_difference"]),
            "monodromy_integration": bool(monodromy.success),
            "neutral": abs(neutral - 1.0)
            <= float(acceptance["maximum_neutral_multiplier_error"]),
            "dominant_real": abs(dominant.imag)
            <= float(acceptance["maximum_dominant_imaginary_part"]),
            "stable": abs(dominant) < 1.0,
            "historical_integration": legacy_success,
            "historical_phase_count": len(legacy_states)
            == int(task["historical_phase_count"]),
            "barrio_integration": barrio_success,
            "barrio_phase_count": len(barrio_states)
            == int(task["barrio_phase_count"]),
        }
        return {
            "id": task["id"],
            "grid_index": task["grid_index"],
            "parameters": task["parameters"],
            "correction": {
                "initial_state": correction.initial_state.tolist(),
                "period_time": correction.period_time,
                "closure_error": correction.closure_error,
                "phase_residual": correction.phase_residual,
                "correction_norm": correction.correction_norm,
                "period_time_difference": period_difference,
                "evaluations": correction.evaluations,
                "optimizer_success": correction.optimizer_success,
            },
            "historical_section": {
                "kind": "legacy_negative",
                "crossing_count": len(legacy_states),
            },
            "section": {
                "kind": "barrio_positive_x",
                "crossing_count": len(barrio_states),
            },
            "section_states": barrio_states.tolist(),
            "dominant_nontrivial_multiplier": _complex_row(dominant),
            "neutral_multiplier": _complex_row(neutral),
            "checks": checks,
            "passed": all(checks.values()),
        }
    except Exception as error:
        return {
            "id": task["id"],
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
        raise SystemExit("unsupported local Barrio orbit-mesh manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("local orbit mesh requires clean source")
    for evidence in manifest.get("evidence", ()):
        raw = Path(evidence["path"]).read_bytes()
        if sha256_bytes(raw) != evidence["sha256"]:
            raise SystemExit(f"evidence hash mismatch: {evidence['path']}")
    candidate_declaration = manifest["seed_candidate_input"]
    candidate_bytes = Path(candidate_declaration["path"]).read_bytes()
    if sha256_bytes(candidate_bytes) != candidate_declaration["sha256"]:
        raise SystemExit("seed candidate input hash mismatch")
    candidate_document = json.loads(candidate_bytes)
    seed_rows = [
        row
        for row in candidate_document["candidates"]
        if row["id"] == manifest["seed"]["candidate_id"] and row["passed"]
    ]
    if len(seed_rows) != 1:
        raise SystemExit("expected exactly one passed seed candidate")
    seed = seed_rows[0]
    if seed["parameters"] != manifest["seed"]["parameters"]:
        raise SystemExit("seed parameter mismatch")
    a_values, c_values = local_grid(manifest["grid"])
    tasks = []
    for a_index, a_value in enumerate(a_values):
        for c_index, c_value in enumerate(c_values):
            tasks.append(
                {
                    "id": f"local-a{a_index:03d}-c{c_index:03d}",
                    "grid_index": [a_index, c_index],
                    "parameters": {
                        "a": float(a_value),
                        "b": float(manifest["grid"]["b"]),
                        "c": float(c_value),
                    },
                    "seed_initial_state": seed["correction"]["initial_state"],
                    "seed_period_time": seed["correction"]["period_time"],
                    "historical_phase_count": manifest["seed"][
                        "historical_phase_count"
                    ],
                    "barrio_phase_count": manifest["seed"]["barrio_phase_count"],
                    "solver": manifest["solver"],
                    "corrector": manifest["corrector"],
                    "acceptance": manifest["acceptance"],
                }
            )
    started = time.perf_counter()
    workers = min(int(manifest["parallel"]["maximum_workers"]), os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        candidates = []
        for candidate in executor.map(_evaluate, tasks, chunksize=4):
            candidates.append(candidate)
            if len(candidates) % 100 == 0 or len(candidates) == len(tasks):
                print(
                    json.dumps(
                        {
                            "completed": len(candidates),
                            "passed": sum(row["passed"] for row in candidates),
                            "total": len(tasks),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
    passed_count = sum(row["passed"] for row in candidates)
    center = manifest["grid"]["required_center"]
    center_rows = [
        row
        for row in candidates
        if np.isclose(row["parameters"]["a"], center["a"], rtol=0.0, atol=1e-14)
        and np.isclose(row["parameters"]["c"], center["c"], rtol=0.0, atol=1e-13)
    ]
    center_passed = len(center_rows) == 1 and bool(center_rows[0]["passed"])
    passed = bool(
        center_passed
        and passed_count >= int(manifest["acceptance"]["minimum_passed_candidates"])
    )
    output = {
        "schema": "butterfly.local-barrio-orbit-mesh.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "seed_candidate_input_sha256": sha256_bytes(candidate_bytes),
        "source": source,
        "grid": {
            "a_values": a_values.tolist(),
            "c_values": c_values.tolist(),
            "b": float(manifest["grid"]["b"]),
            "shape": [len(a_values), len(c_values)],
            "required_center": center,
        },
        "seed": manifest["seed"],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "maximum_workers": workers,
        },
        "candidate_count": len(candidates),
        "passed_candidate_count": passed_count,
        "center_passed": center_passed,
        "candidates": candidates,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256_bytes(output_bytes),
                "candidate_count": len(candidates),
                "passed_candidate_count": passed_count,
                "center_passed": center_passed,
                "passed": passed,
                "elapsed_seconds": output["elapsed_seconds"],
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Prepare corrected period-6 candidates from every frozen Floquet zero edge."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    PoincareSection,
    RosslerParameters,
    SolverConfig,
    collect_crossings,
    correct_periodic_orbit,
    flow_monodromy,
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.search_jones_floquet_center import signed_dominant_nontrivial


SCHEMA = "butterfly.jones-zero-edge-candidates-manifest.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def zero_edges(values) -> list[tuple[str, int, int, int, int]]:
    """Return every adjacent finite sign-changing edge in deterministic order."""

    grid = np.asarray(values, dtype=float)
    edges: list[tuple[str, int, int, int, int]] = []
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1] - 1):
            if np.isfinite(grid[i, j]) and np.isfinite(grid[i, j + 1]) and grid[i, j] * grid[i, j + 1] < 0.0:
                edges.append(("c", i, j, i, j + 1))
    for i in range(grid.shape[0] - 1):
        for j in range(grid.shape[1]):
            if np.isfinite(grid[i, j]) and np.isfinite(grid[i + 1, j]) and grid[i, j] * grid[i + 1, j] < 0.0:
                edges.append(("a", i, j, i + 1, j))
    return edges


def interpolate_zero(left_parameters, right_parameters, left_value: float, right_value: float) -> tuple[dict, float]:
    if left_value * right_value >= 0.0:
        raise ValueError("zero interpolation requires opposite signs")
    fraction = abs(left_value) / (abs(left_value) + abs(right_value))
    return (
        {
            name: float(left_parameters[name] + fraction * (right_parameters[name] - left_parameters[name]))
            for name in ("a", "b", "c")
        },
        float(fraction),
    )


def _section(parameters: RosslerParameters) -> PoincareSection:
    base = legacy_rossler_section(parameters)
    return PoincareSection(
        normal=base.normal,
        offset=base.offset,
        direction=-1,
        gate_axis=base.gate_axis,
        gate_upper=base.gate_upper,
        name="legacy-small-equilibrium-half-plane:negative",
    )


def _orbit_states(parameters, state, period, solver, expected_period):
    crossings = collect_crossings(
        parameters,
        state,
        _section(parameters),
        transient=0.0,
        observation_horizon=period * (1.0 + 1e-7),
        max_crossings=expected_period + 4,
        config=solver,
    )
    keep = (crossings.times > period * 1e-7) & (crossings.times <= period * (1.0 + 1e-7))
    return crossings.states[keep], bool(crossings.integration_success)


def _phase_error(left, right, scales) -> float:
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    scales = np.asarray(scales, dtype=float)
    if left.shape != right.shape:
        return float("inf")
    return min(
        float(np.max(np.linalg.norm((left - np.roll(right, shift, axis=0))[:, (0, 2)] / scales, axis=1)))
        for shift in range(len(left))
    )


def _row_map(receipt, a_values, c_values):
    rows = {}
    for row in receipt["coarse_grid"]["rows"]:
        parameters = row["parameters"]
        i = int(np.argmin(np.abs(a_values - float(parameters["a"]))))
        j = int(np.argmin(np.abs(c_values - float(parameters["c"]))))
        if abs(a_values[i] - parameters["a"]) > 1e-12 or abs(c_values[j] - parameters["c"]) > 1e-12:
            raise ValueError("receipt row is off its declared grid")
        rows[(i, j)] = row
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported zero-edge candidate manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    input_path = Path(manifest["input"]["path"])
    if sha256_file(input_path) != manifest["input"]["sha256"]:
        raise SystemExit("EXP-188 receipt hash mismatch")
    receipt = json.loads(input_path.read_bytes())
    a_values = np.asarray(receipt["coarse_grid"]["a_values"], dtype=float)
    c_values = np.asarray(receipt["coarse_grid"]["c_values"], dtype=float)
    multiplier_grid = np.asarray(
        [[np.nan if value is None else value for value in row] for row in receipt["coarse_grid"]["multiplier_grid"]],
        dtype=float,
    )
    edges = zero_edges(multiplier_grid)
    if len(edges) != int(manifest["selection"]["expected_zero_edge_count"]):
        raise SystemExit(f"expected {manifest['selection']['expected_zero_edge_count']} zero edges, found {len(edges)}")
    row_map = _row_map(receipt, a_values, c_values)
    solver = SolverConfig(**manifest["solver"])
    expected_period = int(manifest["selection"]["expected_period"])
    acceptance = manifest["acceptance"]
    started = time.perf_counter()
    candidates = []
    for candidate_index, (orientation, i0, j0, i1, j1) in enumerate(edges):
        left = row_map[(i0, j0)]
        right = row_map[(i1, j1)]
        left_multiplier = float(multiplier_grid[i0, j0])
        right_multiplier = float(multiplier_grid[i1, j1])
        parameters_dict, fraction = interpolate_zero(
            left["parameters"], right["parameters"], left_multiplier, right_multiplier
        )
        seed_row = left if abs(left_multiplier) <= abs(right_multiplier) else right
        parameters = RosslerParameters(**parameters_dict)
        seed_state = np.asarray(seed_row["correction"]["initial_state"], dtype=float)
        seed_period = float(seed_row["correction"]["period_time"])
        try:
            seed_parameters = RosslerParameters(**seed_row["parameters"])
            seed_states, seed_success = _orbit_states(
                seed_parameters, seed_state, seed_period, solver, expected_period
            )
            correction = correct_periodic_orbit(
                parameters,
                seed_state,
                seed_period,
                config=solver,
                max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
                tolerance=float(manifest["corrector"]["tolerance"]),
            )
            orbit_states, crossing_success = _orbit_states(
                parameters, correction.initial_state, correction.period_time, solver, expected_period
            )
            monodromy = flow_monodromy(
                parameters, correction.initial_state, correction.period_time, config=solver
            )
            dominant, neutral, _ = signed_dominant_nontrivial(monodromy.multipliers)
            identity_error = _phase_error(
                orbit_states, seed_states, manifest["selection"]["coordinate_scales"]
            )
            checks = {
                "endpoint_stable": abs(left_multiplier) < 1.0 and abs(right_multiplier) < 1.0,
                "seed_crossings": seed_success and len(seed_states) == expected_period,
                "correction": correction.success,
                "crossings": crossing_success and len(orbit_states) == expected_period,
                "closure": correction.closure_error <= float(acceptance["maximum_flow_closure"]),
                "phase": correction.phase_residual <= float(acceptance["maximum_phase_residual"]),
                "neutral": abs(neutral - 1.0) <= float(acceptance["maximum_neutral_multiplier_error"]),
                "dominant_real": abs(dominant.imag) <= float(acceptance["maximum_dominant_imaginary_part"]),
                "candidate_stable": abs(dominant) < 1.0,
                "zero_interpolation": abs(dominant.real) <= float(acceptance["maximum_interpolated_multiplier_magnitude"]),
                "identity": identity_error <= float(acceptance["maximum_endpoint_scaled_orbit_error"]),
            }
            candidate = {
                "id": f"zero-edge-{candidate_index:03d}",
                "edge": {
                    "orientation": orientation,
                    "left_index": [i0, j0],
                    "right_index": [i1, j1],
                    "left_multiplier": left_multiplier,
                    "right_multiplier": right_multiplier,
                    "interpolation_fraction": fraction,
                },
                "parameters": parameters_dict,
                "correction": {
                    "initial_state": correction.initial_state.tolist(),
                    "period_time": correction.period_time,
                    "closure_error": correction.closure_error,
                    "phase_residual": correction.phase_residual,
                    "evaluations": correction.evaluations,
                },
                "section_states": orbit_states.tolist(),
                "dominant_nontrivial_multiplier": {
                    "real": float(dominant.real),
                    "imag": float(dominant.imag),
                    "modulus": float(abs(dominant)),
                },
                "neutral_multiplier_error": float(abs(neutral - 1.0)),
                "endpoint_scaled_orbit_error": identity_error,
                "checks": checks,
                "passed": all(checks.values()),
            }
        except Exception as error:
            candidate = {
                "id": f"zero-edge-{candidate_index:03d}",
                "edge": {
                    "orientation": orientation,
                    "left_index": [i0, j0],
                    "right_index": [i1, j1],
                    "left_multiplier": left_multiplier,
                    "right_multiplier": right_multiplier,
                    "interpolation_fraction": fraction,
                },
                "parameters": parameters_dict,
                "error": f"{type(error).__name__}: {error}",
                "passed": False,
            }
        candidates.append(candidate)
        print(json.dumps({"id": candidate["id"], "passed": candidate["passed"]}, sort_keys=True), flush=True)

    passed_candidates = [row for row in candidates if row["passed"]]
    passed = len(passed_candidates) >= int(acceptance["minimum_passed_candidates"])
    output = {
        "schema": "butterfly.jones-zero-edge-candidates.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "input_receipt_sha256": manifest["input"]["sha256"],
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "zero_edge_count": len(edges),
        "passed_candidate_count": len(passed_candidates),
        "candidates": candidates,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(output))
    print(json.dumps({"output": str(args.output), "passed": passed, "passed_candidates": len(passed_candidates)}, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

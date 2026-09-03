#!/usr/bin/env python3
"""Refine the historical-section grazing nominated by EXP-212."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from butterfly import RosslerParameters, SolverConfig, rossler_equilibria, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.continue_jones_period6_flip_curve import _solve_event


SCHEMA = "butterfly.jones-period6-flip-section-grazing-manifest.v1"


def nearest_y_extremum(parameters, state, period_time, solver):
    equilibrium = rossler_equilibria(parameters)[0]

    def y_extremum(_time, point):
        return point[0] + parameters.a * point[1]

    y_extremum.direction = 0
    y_extremum.terminal = False
    integration = solve_ivp(
        lambda time_value, point: rossler_rhs(time_value, point, parameters),
        (0.0, period_time * (1.0 + 1e-8)),
        state,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
        events=y_extremum,
    )
    if not integration.success:
        raise RuntimeError(f"grazing integration failed: {integration.message}")
    times = np.asarray(integration.t_events[0], dtype=float)
    states = np.asarray(integration.y_events[0], dtype=float)
    keep = times > period_time * 1e-7
    times = times[keep]
    states = states[keep]
    clearances = states[:, 1] - equilibrium[1]
    index = int(np.argmin(np.abs(clearances)))
    point = states[index]
    rhs = rossler_rhs(times[index], point, parameters)
    return {
        "extremum_count": int(len(times)),
        "extremum_time": float(times[index]),
        "extremum_state": point.tolist(),
        "signed_y_clearance": float(clearances[index]),
        "gate_margin": float(equilibrium[0] - point[0]),
        "section_value": float(point[1] - equilibrium[1]),
        "tangency_residual": float(rhs[1]),
        "second_derivative_y": float(rhs[0] + parameters.a * rhs[1]),
    }


def evaluate(c_value, seed, manifest, solver):
    event = _solve_event(float(c_value), seed, manifest, solver)
    parameters = RosslerParameters(
        a=float(event["a"]), b=float(manifest["fixed_b"]), c=float(c_value)
    )
    return {
        **event,
        **nearest_y_extremum(
            parameters,
            np.asarray(event["initial_state"], dtype=float),
            float(event["period_time"]),
            solver,
        ),
    }


def _scientific_event_passes(row):
    return all(
        value
        for name, value in row["checks"].items()
        if name != "historical_section"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported flip-section-grazing manifest")
    source_bytes = args.source_receipt.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    source_receipt = json.loads(source_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("section-grazing refinement requires clean source")
    accepted = source_receipt["directions"]["down"]["rows"]
    seed = accepted[-1]
    solver = SolverConfig(**manifest["solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    left_c, right_c = map(float, manifest["c_bracket"])
    started = time.perf_counter()
    left = evaluate(left_c, seed, manifest, solver)
    right = evaluate(right_c, seed, manifest, solver)
    if left["signed_y_clearance"] * right["signed_y_clearance"] > 0.0:
        raise RuntimeError("historical section grazing is not bracketed")
    evaluations = []
    for _ in range(int(manifest["refinement"]["maximum_iterations"])):
        if right_c - left_c <= float(manifest["refinement"]["c_tolerance"]):
            break
        c_value = 0.5 * (left_c + right_c)
        current = evaluate(
            c_value,
            left if abs(c_value - left_c) < abs(right_c - c_value) else right,
            manifest,
            solver,
        )
        evaluations.append(current)
        if left["signed_y_clearance"] * current["signed_y_clearance"] <= 0.0:
            right_c, right = c_value, current
        else:
            left_c, left = c_value, current
    candidates = [left, right, *evaluations]
    best = min(candidates, key=lambda row: abs(row["signed_y_clearance"]))
    c_estimate = 0.5 * (left_c + right_c)
    independent = evaluate(c_estimate, best, manifest, independent_solver)
    acceptance = manifest["acceptance"]
    bracket_width = right_c - left_c
    passed = bool(
        bracket_width <= float(acceptance["maximum_c_bracket_width"])
        and _scientific_event_passes(left)
        and _scientific_event_passes(right)
        and left["historical_phase_count"]
        == int(acceptance["lower_c_historical_phase_count"])
        and right["historical_phase_count"]
        == int(acceptance["upper_c_historical_phase_count"])
        and left["barrio_phase_count"] == int(acceptance["barrio_phase_count"])
        and right["barrio_phase_count"] == int(acceptance["barrio_phase_count"])
        and abs(best["signed_y_clearance"])
        <= float(acceptance["maximum_y_clearance"])
        and abs(best["gate_margin"]) <= float(acceptance["maximum_gate_margin"])
        and abs(best["tangency_residual"])
        <= float(acceptance["maximum_tangency_residual"])
        and abs(best["second_derivative_y"])
        >= float(acceptance["minimum_second_derivative_magnitude"])
        and _scientific_event_passes(independent)
        and abs(independent["signed_y_clearance"])
        <= float(acceptance["maximum_independent_y_clearance"])
        and abs(float(independent["a"]) - float(best["a"]))
        <= float(acceptance["maximum_solver_a_difference"])
        and abs(float(independent["period_time"]) - float(best["period_time"]))
        / float(best["period_time"])
        <= float(acceptance["maximum_solver_period_relative_difference"])
    )
    output = {
        "schema": "butterfly.jones-period6-flip-section-grazing-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": sha256_bytes(source_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "c_bracket": [left_c, right_c],
        "c_estimate": c_estimate,
        "bracket_width": bracket_width,
        "left_endpoint": left,
        "right_endpoint": right,
        "best_evaluation": best,
        "independent_radau": independent,
        "evaluations": evaluations,
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
                "passed": passed,
                "c_estimate": c_estimate,
                "bracket_width": bracket_width,
                "best_y_clearance": best["signed_y_clearance"],
                "best_gate_margin": best["gate_margin"],
                "phase_counts": [
                    left["historical_phase_count"],
                    right["historical_phase_count"],
                    left["barrio_phase_count"],
                    right["barrio_phase_count"],
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Refine a periodic orbit's grazing of the legacy Rössler section boundary."""
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
from qualify_separated_normal_form import (
    correct_fixed_b,
    interpolate_branch,
    nontrivial_modulus,
)


def grazing_data(parameters, state, period_time, solver):
    equilibrium = rossler_equilibria(parameters)[0]

    def y_extremum(_time, point):
        return point[0] + parameters.a * point[1]

    y_extremum.direction = 0
    y_extremum.terminal = False
    result = solve_ivp(
        lambda t, x: rossler_rhs(t, x, parameters),
        (0.0, period_time * (1.0 + 1e-8)),
        state,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
        events=y_extremum,
    )
    times = np.asarray(result.t_events[0])
    states = np.asarray(result.y_events[0])
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
        "integration_success": bool(result.success),
    }


def evaluate(b, rows, a, c, solver, corrector):
    state, period_time = interpolate_branch(rows, b)
    orbit, multipliers = correct_fixed_b(
        a=a,
        b=b,
        c=c,
        initial_state=state,
        period_time=period_time,
        solver=solver,
        tolerance=corrector["tolerance"],
        max_evaluations=corrector["max_evaluations"],
    )
    parameters = RosslerParameters(a=a, b=b, c=c)
    return {
        "b": b,
        "initial_state": orbit.initial_state.tolist(),
        "period_time": orbit.period_time,
        "closure_error": orbit.closure_error,
        "multiplier_modulus": nontrivial_modulus(multipliers),
        **grazing_data(parameters, orbit.initial_state, orbit.period_time, solver),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--branches", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    branch_bytes = args.branches.read_bytes()
    if sha256_bytes(branch_bytes) != manifest["branch_receipt_sha256"]:
        raise SystemExit("branch receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["dirty"]:
        raise SystemExit("clean source required")
    branches = json.loads(branch_bytes)
    rows = next(
        branch["rows"]
        for branch in branches["branches"]
        if branch["direction"] == manifest["branch_direction"]
    )
    a = manifest["fixed_a"]
    c = manifest["fixed_c"]
    solver = SolverConfig(**manifest["solver"])
    left_b, right_b = manifest["b_bracket"]
    started = time.perf_counter()
    left = evaluate(left_b, rows, a, c, solver, manifest["corrector"])
    right = evaluate(right_b, rows, a, c, solver, manifest["corrector"])
    if left["signed_y_clearance"] * right["signed_y_clearance"] > 0.0:
        raise RuntimeError("section grazing is not bracketed")
    evaluations = []
    for _ in range(manifest["refinement"]["maximum_iterations"]):
        if right_b - left_b <= manifest["refinement"]["b_tolerance"]:
            break
        b = (left_b + right_b) / 2.0
        current = evaluate(b, rows, a, c, solver, manifest["corrector"])
        evaluations.append(current)
        if left["signed_y_clearance"] * current["signed_y_clearance"] <= 0.0:
            right_b, right = b, current
        else:
            left_b, left = b, current
    best = min(
        [left, right, *evaluations], key=lambda row: abs(row["signed_y_clearance"])
    )
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.legacy-section-grazing-refinement.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "branch_receipt_sha256": sha256_bytes(branch_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "b_bracket": [left_b, right_b],
        "b_estimate": (left_b + right_b) / 2.0,
        "bracket_width": right_b - left_b,
        "left_endpoint": left,
        "right_endpoint": right,
        "best_evaluation": best,
        "evaluations": evaluations,
        "elapsed_seconds": time.perf_counter() - started,
    }
    output["passed"] = (
        output["bracket_width"] <= acceptance["max_b_bracket_width"]
        and abs(best["signed_y_clearance"]) <= acceptance["max_y_clearance"]
        and abs(best["gate_margin"]) <= acceptance["max_gate_margin"]
        and abs(best["tangency_residual"]) <= acceptance["max_tangency_residual"]
        and best["second_derivative_y"] < 0.0
        and best["closure_error"] <= acceptance["max_closure_error"]
        and best["multiplier_modulus"] < 1.0
    )
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {key: value for key, value in output.items() if key != "evaluations"},
            sort_keys=True,
        )
    )
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

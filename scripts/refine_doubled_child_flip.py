#!/usr/bin/env python3
"""Refine a doubled-child Floquet -1 event with half-period identity."""
from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from qualify_separated_normal_form import correct_fixed_b, interpolate_branch


def evaluate(b, rows, a, c, solver, corrector):
    state, period_time = interpolate_branch(rows, b)
    orbit, monodromy = correct_fixed_b(
        a=a,
        b=b,
        c=c,
        initial_state=state,
        period_time=period_time,
        solver=solver,
        tolerance=corrector["tolerance"],
        max_evaluations=corrector["max_evaluations"],
    )
    neutral = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    multiplier = complex(max(np.delete(monodromy.multipliers, neutral), key=abs))
    parameters = RosslerParameters(a=a, b=b, c=c)
    half = solve_ivp(
        lambda t, x: rossler_rhs(t, x, parameters),
        (0.0, 0.5 * orbit.period_time),
        orbit.initial_state,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
    )
    return {
        "b": b,
        "initial_state": orbit.initial_state.tolist(),
        "period_time": orbit.period_time,
        "closure_error": orbit.closure_error,
        "half_period_closure": float(
            np.linalg.norm(half.y[:, -1] - orbit.initial_state)
        ),
        "multiplier": {"real": multiplier.real, "imag": multiplier.imag},
        "multiplier_residual": multiplier.real + 1.0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--branch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    branch_bytes = args.branch.read_bytes()
    if sha256_bytes(branch_bytes) != manifest["branch_receipt_sha256"]:
        raise SystemExit("branch receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["dirty"]:
        raise SystemExit("clean source required")
    receipt = json.loads(branch_bytes)
    rows = next(
        branch["rows"]
        for branch in receipt["branches"]
        if branch["direction"] == manifest["branch_direction"]
    )
    a = float(rows[0]["a"])
    c = float(rows[0]["c"])
    solver = SolverConfig(**manifest["solver"])
    left_b, right_b = manifest["b_bracket"]
    started = time.perf_counter()
    left = evaluate(left_b, rows, a, c, solver, manifest["corrector"])
    right = evaluate(right_b, rows, a, c, solver, manifest["corrector"])
    if left["multiplier_residual"] * right["multiplier_residual"] > 0.0:
        raise RuntimeError("child flip is not bracketed")
    evaluations = []
    for _ in range(manifest["refinement"]["maximum_iterations"]):
        if right_b - left_b <= manifest["refinement"]["b_tolerance"]:
            break
        b = 0.5 * (left_b + right_b)
        current = evaluate(b, rows, a, c, solver, manifest["corrector"])
        evaluations.append(current)
        if left["multiplier_residual"] * current["multiplier_residual"] <= 0.0:
            right_b, right = b, current
        else:
            left_b, left = b, current
    best = min(
        [left, right, *evaluations],
        key=lambda row: abs(row["multiplier_residual"]),
    )
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.doubled-child-flip-refinement.v1",
        "experiment_id": manifest["experiment_id"],
        "parent_period_label": manifest["parent_period_label"],
        "child_period_label": manifest["child_period_label"],
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
        "b_estimate": 0.5 * (left_b + right_b),
        "bracket_width": right_b - left_b,
        "left_endpoint": left,
        "right_endpoint": right,
        "best_evaluation": best,
        "evaluations": evaluations,
        "elapsed_seconds": time.perf_counter() - started,
    }
    output["passed"] = (
        output["bracket_width"] <= acceptance["max_b_bracket_width"]
        and abs(best["multiplier_residual"])
        <= acceptance["max_multiplier_residual"]
        and abs(best["multiplier"]["imag"])
        <= acceptance["max_multiplier_imaginary_part"]
        and best["closure_error"] <= acceptance["max_closure_error"]
        and best["half_period_closure"]
        >= acceptance["minimum_half_period_closure"]
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

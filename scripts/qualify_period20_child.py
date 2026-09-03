#!/usr/bin/env python3
"""Qualify period-20 arm identity and stability exchange at fixed b."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from compare_periodic_orbit_identity import dense_orbit, phase_aligned_rms
from qualify_separated_normal_form import (
    correct_fixed_b,
    interpolate_branch,
    nontrivial_modulus,
)


def half_period_closure(orbit, parameters, solver):
    result = solve_ivp(
        lambda t, x: rossler_rhs(t, x, parameters),
        (0.0, 0.5 * orbit.period_time),
        orbit.initial_state,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
    )
    return float(np.linalg.norm(result.y[:, -1] - orbit.initial_state))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--children", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    child_bytes = args.children.read_bytes()
    parent_bytes = args.parent.read_bytes()
    if sha256_bytes(child_bytes) != manifest["child_branch_receipt_sha256"]:
        raise SystemExit("child branch hash mismatch")
    if sha256_bytes(parent_bytes) != manifest["parent_branch_receipt_sha256"]:
        raise SystemExit("parent branch hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["dirty"]:
        raise SystemExit("clean source required")
    child_receipt = json.loads(child_bytes)
    parent_receipt = json.loads(parent_bytes)
    parent_rows = next(
        branch["rows"]
        for branch in parent_receipt["branches"]
        if branch["direction"] == manifest["parent_branch_direction"]
    )
    target_b = manifest["target_b"]
    a = float(parent_rows[0]["a"])
    c = float(parent_rows[0]["c"])
    parameters = RosslerParameters(a=a, b=target_b, c=c)
    solver = SolverConfig(**manifest["solver"])
    corrector = manifest["corrector"]
    parent_state, parent_period = interpolate_branch(parent_rows, target_b)
    parent = correct_fixed_b(
        a=a,
        b=target_b,
        c=c,
        initial_state=parent_state,
        period_time=parent_period,
        solver=solver,
        tolerance=corrector["tolerance"],
        max_evaluations=corrector["max_evaluations"],
    )
    children = []
    for branch in child_receipt["branches"]:
        state, period = interpolate_branch(branch["rows"], target_b)
        children.append(
            correct_fixed_b(
                a=a,
                b=target_b,
                c=c,
                initial_state=state,
                period_time=period,
                solver=solver,
                tolerance=corrector["tolerance"],
                max_evaluations=corrector["max_evaluations"],
            )
        )
    dense = [dense_orbit(child[0], parameters, solver) for child in children]
    identity = phase_aligned_rms(
        (children[0][0], dense[0]),
        (children[1][0], dense[1]),
        phase_samples=manifest["comparison"]["phase_samples"],
        coarse_shifts=manifest["comparison"]["coarse_shifts"],
        shift_tolerance=manifest["comparison"]["shift_tolerance"],
    )
    parent_modulus = nontrivial_modulus(parent[1])
    child_moduli = [nontrivial_modulus(child[1]) for child in children]
    half_closures = [
        half_period_closure(child[0], parameters, solver) for child in children
    ]
    period_ratios = [
        child[0].period_time / parent[0].period_time for child in children
    ]
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.period20-child-qualification.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "child_branch_receipt_sha256": sha256_bytes(child_bytes),
        "parent_branch_receipt_sha256": sha256_bytes(parent_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "parameters": {"a": a, "b": target_b, "c": c},
        "parent": {
            "period_time": parent[0].period_time,
            "closure_error": parent[0].closure_error,
            "multiplier_modulus": parent_modulus,
        },
        "children": [
            {
                "period_time": child[0].period_time,
                "closure_error": child[0].closure_error,
                "multiplier_modulus": modulus,
                "half_period_closure": half_closure,
                "parent_period_ratio": period_ratio,
            }
            for child, modulus, half_closure, period_ratio in zip(
                children, child_moduli, half_closures, period_ratios
            )
        ],
        "child_arm_identity": identity,
    }
    output["passed"] = (
        identity["rms"] <= acceptance["max_child_arm_rms"]
        and parent[0].closure_error <= acceptance["max_closure_error"]
        and all(
            child[0].closure_error <= acceptance["max_closure_error"]
            for child in children
        )
        and parent_modulus > 1.0
        and all(modulus < 1.0 for modulus in child_moduli)
        and all(
            closure >= acceptance["minimum_half_period_closure"]
            for closure in half_closures
        )
        and all(
            abs(ratio - 2.0) <= acceptance["max_period_ratio_error"]
            for ratio in period_ratios
        )
    )
    atomic_write(args.output, canonical_json(output))
    print(json.dumps(output, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

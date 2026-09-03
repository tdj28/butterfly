#!/usr/bin/env python3
"""Qualify a one-arm doubled child and recover it from perturbed attraction."""
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
    parser.add_argument("--child", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    child_bytes = args.child.read_bytes()
    parent_bytes = args.parent.read_bytes()
    if sha256_bytes(child_bytes) != manifest["child_branch_receipt_sha256"]:
        raise SystemExit("child receipt hash mismatch")
    if sha256_bytes(parent_bytes) != manifest["parent_branch_receipt_sha256"]:
        raise SystemExit("parent receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["dirty"]:
        raise SystemExit("clean source required")
    child_receipt = json.loads(child_bytes)
    parent_receipt = json.loads(parent_bytes)
    child_rows = next(
        branch["rows"]
        for branch in child_receipt["branches"]
        if branch["direction"] == manifest["child_branch_direction"]
    )
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
    parent_seed = interpolate_branch(parent_rows, target_b)
    child_seed = interpolate_branch(child_rows, target_b)
    parent = correct_fixed_b(
        a=a,
        b=target_b,
        c=c,
        initial_state=parent_seed[0],
        period_time=parent_seed[1],
        solver=solver,
        tolerance=corrector["tolerance"],
        max_evaluations=corrector["max_evaluations"],
    )
    child = correct_fixed_b(
        a=a,
        b=target_b,
        c=c,
        initial_state=child_seed[0],
        period_time=child_seed[1],
        solver=solver,
        tolerance=corrector["tolerance"],
        max_evaluations=corrector["max_evaluations"],
    )
    perturbation = np.asarray(manifest["attraction"]["perturbation"], dtype=float)
    attraction = solve_ivp(
        lambda t, x: rossler_rhs(t, x, parameters),
        (0.0, manifest["attraction"]["transient_periods"] * child[0].period_time),
        child[0].initial_state + perturbation,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=manifest["attraction"]["max_step"],
    )
    recovered = correct_fixed_b(
        a=a,
        b=target_b,
        c=c,
        initial_state=attraction.y[:, -1],
        period_time=child[0].period_time,
        solver=solver,
        tolerance=corrector["tolerance"],
        max_evaluations=corrector["max_evaluations"],
    )
    child_dense = dense_orbit(child[0], parameters, solver)
    recovered_dense = dense_orbit(recovered[0], parameters, solver)
    identity = phase_aligned_rms(
        (child[0], child_dense),
        (recovered[0], recovered_dense),
        phase_samples=manifest["comparison"]["phase_samples"],
        coarse_shifts=manifest["comparison"]["coarse_shifts"],
        shift_tolerance=manifest["comparison"]["shift_tolerance"],
    )
    parent_modulus = nontrivial_modulus(parent[1])
    child_modulus = nontrivial_modulus(child[1])
    recovered_modulus = nontrivial_modulus(recovered[1])
    half_closure = half_period_closure(child[0], parameters, solver)
    period_ratio = child[0].period_time / parent[0].period_time
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.single-doubled-child-qualification.v1",
        "experiment_id": manifest["experiment_id"],
        "parent_period_label": manifest["parent_period_label"],
        "child_period_label": manifest["child_period_label"],
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
        "child": {
            "period_time": child[0].period_time,
            "closure_error": child[0].closure_error,
            "half_period_closure": half_closure,
            "multiplier_modulus": child_modulus,
            "parent_period_ratio": period_ratio,
        },
        "recovered": {
            "closure_error": recovered[0].closure_error,
            "multiplier_modulus": recovered_modulus,
            "identity": identity,
            "integration_success": bool(attraction.success),
        },
    }
    output["passed"] = (
        parent[0].closure_error <= acceptance["max_closure_error"]
        and child[0].closure_error <= acceptance["max_closure_error"]
        and recovered[0].closure_error <= acceptance["max_closure_error"]
        and parent_modulus > 1.0
        and child_modulus < 1.0
        and recovered_modulus < 1.0
        and half_closure >= acceptance["minimum_half_period_closure"]
        and abs(period_ratio - 2.0) <= acceptance["max_period_ratio_error"]
        and identity["rms"] <= acceptance["max_recovered_identity_rms"]
        and attraction.success
    )
    atomic_write(args.output, canonical_json(output))
    print(json.dumps(output, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

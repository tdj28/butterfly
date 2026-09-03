#!/usr/bin/env python3
"""Independently qualify the primitive stable period-4 child after EXP-162."""

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
from compare_periodic_orbit_identity import dense_orbit, phase_aligned_rms
from qualify_period2_c_child import (
    _correct,
    _half_period_closure,
    _interpolate_c,
    _summary,
    _winding,
)


def run_child_qualification(
    *,
    manifest_schema: str,
    output_schema: str,
    labels: list[str],
    expected_parent_winding: float,
    expected_child_winding: float,
    scientific_scope: str,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--child", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != manifest_schema:
        raise SystemExit("unsupported c-child qualification manifest")
    child_bytes = args.child.read_bytes()
    parent_bytes = args.parent.read_bytes()
    if sha256_bytes(child_bytes) != manifest["child_receipt_sha256"]:
        raise SystemExit("child receipt hash mismatch")
    if sha256_bytes(parent_bytes) != manifest["parent_receipt_sha256"]:
        raise SystemExit("parent receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    child_receipt = json.loads(child_bytes)
    parent_receipt = json.loads(parent_bytes)
    target_c = float(manifest["target_c"])
    parameters = RosslerParameters(
        a=float(manifest["fixed_a"]),
        b=float(manifest["fixed_b"]),
        c=target_c,
    )
    reference_solver = SolverConfig(**manifest["reference_solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    corrector = manifest["corrector"]
    parent_seed = _interpolate_c(parent_receipt["rows"], target_c)
    child_seeds = [
        _interpolate_c(branch["rows"], target_c)
        for branch in child_receipt["branches"]
    ]
    started = time.perf_counter()
    reference = [_correct(parameters, parent_seed, reference_solver, corrector)]
    reference.extend(
        _correct(parameters, seed, reference_solver, corrector) for seed in child_seeds
    )
    independent = [
        _correct(
            parameters,
            (item[0].initial_state, item[0].period_time),
            independent_solver,
            corrector,
        )
        for item in reference
    ]
    reference_dense = [
        dense_orbit(item[0], parameters, reference_solver) for item in reference
    ]
    independent_dense = [
        dense_orbit(item[0], parameters, independent_solver) for item in independent
    ]
    comparison = manifest["comparison"]

    def identity(left, right, left_dense, right_dense):
        return phase_aligned_rms(
            (left, left_dense),
            (right, right_dense),
            phase_samples=int(comparison["phase_samples"]),
            coarse_shifts=int(comparison["coarse_shifts"]),
            shift_tolerance=float(comparison["shift_tolerance"]),
        )

    arm_identity = identity(
        reference[1][0],
        reference[2][0],
        reference_dense[1],
        reference_dense[2],
    )
    solver_identities = [
        identity(
            reference[index][0],
            independent[index][0],
            reference_dense[index],
            independent_dense[index],
        )
        for index in range(3)
    ]
    half_closures = [
        _half_period_closure(parameters, item[0], independent_solver)
        for item in independent[1:]
    ]
    windings = [
        _winding(
            parameters,
            item[0],
            independent_solver,
            int(manifest["orbit_sample_count"]),
        )
        for item in independent
    ]
    period_ratios = [
        item[0].period_time / independent[0][0].period_time
        for item in independent[1:]
    ]

    attraction = manifest["attraction"]
    perturbation = np.asarray(attraction["perturbation"], dtype=float)
    child = independent[1][0]
    recovery_integration = solve_ivp(
        lambda current_time, state: rossler_rhs(current_time, state, parameters),
        (0.0, float(attraction["transient_periods"]) * child.period_time),
        child.initial_state + perturbation,
        method=independent_solver.method,
        rtol=independent_solver.rtol,
        atol=independent_solver.atol,
        max_step=float(attraction["max_step"]),
    )
    if not recovery_integration.success:
        raise RuntimeError(f"attraction integration failed: {recovery_integration.message}")
    recovered = _correct(
        parameters,
        (recovery_integration.y[:, -1], child.period_time),
        independent_solver,
        corrector,
    )
    recovered_dense = dense_orbit(recovered[0], parameters, independent_solver)
    recovered_identity = identity(
        independent[1][0],
        recovered[0],
        independent_dense[1],
        recovered_dense,
    )
    reference_summaries = [_summary(*item) for item in reference]
    independent_summaries = [_summary(*item) for item in independent]
    recovered_summary = _summary(*recovered)
    modulus_differences = [
        abs(
            reference_summaries[index]["dominant_nontrivial_multiplier"]["modulus"]
            - independent_summaries[index]["dominant_nontrivial_multiplier"][
                "modulus"
            ]
        )
        for index in range(3)
    ]
    acceptance = manifest["acceptance"]
    passed = bool(
        max(
            row["closure_error"]
            for row in reference_summaries + independent_summaries + [recovered_summary]
        )
        <= float(acceptance["maximum_closure_error"])
        and arm_identity["rms"] <= float(acceptance["maximum_arm_identity_rms"])
        and max(item["rms"] for item in solver_identities)
        <= float(acceptance["maximum_solver_identity_rms"])
        and max(modulus_differences)
        <= float(acceptance["maximum_solver_modulus_difference"])
        and not independent_summaries[0]["stable"]
        and all(row["stable"] for row in independent_summaries[1:])
        and all(
            value >= float(acceptance["minimum_half_period_closure"])
            for value in half_closures
        )
        and all(
            abs(value - 2.0) <= float(acceptance["maximum_period_ratio_error"])
            for value in period_ratios
        )
        and abs(windings[0] - expected_parent_winding)
        <= float(acceptance["maximum_winding_error"])
        and all(
            abs(value - expected_child_winding)
            <= float(acceptance["maximum_winding_error"])
            for value in windings[1:]
        )
        and recovered_summary["stable"]
        and recovered_identity["rms"]
        <= float(acceptance["maximum_recovered_identity_rms"])
    )
    output = {
        "schema": output_schema,
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "child_receipt_sha256": sha256_bytes(child_bytes),
        "parent_receipt_sha256": sha256_bytes(parent_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "parameters": {"a": parameters.a, "b": parameters.b, "c": parameters.c},
        "reference_dop853": reference_summaries,
        "independent_radau": independent_summaries,
        "labels": labels,
        "child_arm_identity": arm_identity,
        "solver_identities": solver_identities,
        "solver_modulus_differences": modulus_differences,
        "half_period_closures": half_closures,
        "parent_period_ratios": period_ratios,
        "winding_numbers": windings,
        "recovered": {
            **recovered_summary,
            "identity": recovered_identity,
            "integration_success": bool(recovery_integration.success),
        },
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "scientific_scope": scientific_scope,
    }
    atomic_write(args.output, canonical_json(output))
    print(json.dumps(output, sort_keys=True))
    return 0 if passed else 1


def main() -> int:
    return run_child_qualification(
        manifest_schema="butterfly.period4-c-child-qualification-manifest.v1",
        output_schema="butterfly.period4-c-child-qualification-receipt.v1",
        labels=["period2-parent", "period4-minus", "period4-plus"],
        expected_parent_winding=2.0,
        expected_child_winding=4.0,
        scientific_scope=(
            "primitive stable period-4 child and local stability exchange after the "
            "second fixed-path flip; not the later cascade or homoclinic endpoint"
        ),
    )


if __name__ == "__main__":
    raise SystemExit(main())

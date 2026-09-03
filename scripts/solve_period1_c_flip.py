#!/usr/bin/env python3
"""Solve the first fixed-(a,b) period-1 flip with an exact c-Jacobian."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import least_squares

from audit_segmented_floquet_precision import block_and_product_floquet
from butterfly import (
    RosslerParameters,
    SolverConfig,
    augmented_flip_system,
    flow_monodromy,
    integrate_trajectory,
    rossler_equilibria,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from solve_analytic_augmented_flip import flip_spectrum_metrics
from solve_augmented_segmented_flip import initial_tangent_nodes


def _seed_row(receipt, bracket):
    if receipt.get("schema") != "butterfly.hopf-period1-to-hub-receipt.v1":
        raise ValueError("source is not a Hopf-to-hub period-1 receipt")
    midpoint = 0.5 * (float(bracket[0]) + float(bracket[1]))
    candidates = [
        row
        for row in receipt["rows"]
        if float(bracket[0]) <= row["parameters"]["c"] <= float(bracket[1])
    ]
    if not candidates:
        raise ValueError("source receipt has no row inside the flip bracket")
    return min(candidates, key=lambda row: abs(row["parameters"]["c"] - midpoint))


def _orbit_nodes(parameters, state, period, segment_count, solver):
    times = np.arange(segment_count, dtype=float) * period / segment_count
    trajectory = integrate_trajectory(
        parameters,
        state,
        (0.0, period),
        config=solver,
        t_eval=times,
    )
    if not trajectory.success or trajectory.y.shape != (3, segment_count):
        raise RuntimeError("failed to sample multiple-shooting nodes")
    return trajectory.y.T.copy()


def _winding(parameters, state, period, solver, sample_count):
    trajectory = integrate_trajectory(
        parameters,
        state,
        (0.0, period),
        config=solver,
        t_eval=np.linspace(0.0, period, sample_count),
    )
    equilibrium = rossler_equilibria(parameters)[0]
    centered = trajectory.y.T - equilibrium
    angles = np.unwrap(np.arctan2(centered[:, 1], centered[:, 0]))
    return float((angles[-1] - angles[0]) / (2.0 * np.pi))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.period1-c-flip-manifest.v1":
        raise SystemExit("unsupported period-1 c-flip manifest")
    source_bytes = args.source_receipt.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    receipt = json.loads(source_bytes)
    bracket = list(map(float, manifest["c_bracket"]))
    seed_row = _seed_row(receipt, bracket)
    a = float(manifest["fixed_a"])
    b = float(manifest["fixed_b"])
    seed_c = float(seed_row["parameters"]["c"])
    seed_parameters = RosslerParameters(a=a, b=b, c=seed_c)
    solver = SolverConfig(**manifest["reference_solver"])
    segment_count = int(manifest["segment_count"])
    seed_state = np.asarray(seed_row["initial_state"], dtype=float)
    seed_period = float(seed_row["period_time"])
    nodes = _orbit_nodes(
        seed_parameters, seed_state, seed_period, segment_count, solver
    )
    tangent_nodes, seed_multiplier = initial_tangent_nodes(
        nodes, seed_period, seed_parameters, solver
    )
    phase_reference = nodes[0].copy()
    phase = rossler_rhs(0.0, phase_reference, seed_parameters)
    phase /= np.linalg.norm(phase)
    initial = np.r_[nodes.ravel(), seed_period, seed_c, tangent_nodes.ravel()]
    state_count = 3 * segment_count
    cached_variables = None
    cached_residual = None
    cached_jacobian = None
    integrated_pairs = 0

    def evaluate(value):
        nonlocal cached_variables, cached_residual, cached_jacobian, integrated_pairs
        if cached_variables is not None and np.array_equal(value, cached_variables):
            return cached_residual, cached_jacobian
        residual, jacobian = augmented_flip_system(
            value,
            segment_count=segment_count,
            a=a,
            c=None,
            phase=phase,
            phase_reference=phase_reference,
            solver=solver,
            continuation_parameter="c",
            fixed_b=b,
        )
        integrated_pairs += 1
        print(
            json.dumps(
                {
                    "evaluation": integrated_pairs,
                    "c": float(value[state_count + 1]),
                    "residual_norm": float(np.linalg.norm(residual)),
                },
                sort_keys=True,
            ),
            flush=True,
        )
        cached_variables = value.copy()
        cached_residual = residual
        cached_jacobian = jacobian
        return residual, jacobian

    initial_residual, _ = evaluate(initial)
    lower = np.full(len(initial), -np.inf)
    upper = np.full(len(initial), np.inf)
    lower[state_count] = 1e-12
    lower[state_count + 1] = bracket[0]
    upper[state_count + 1] = bracket[1]
    started = time.perf_counter()
    solution = least_squares(
        lambda value: evaluate(value)[0],
        initial,
        jac=lambda value: evaluate(value)[1],
        bounds=(lower, upper),
        method="trf",
        tr_solver="exact",
        x_scale="jac",
        xtol=float(manifest["corrector"]["tolerance"]),
        ftol=float(manifest["corrector"]["tolerance"]),
        gtol=float(manifest["corrector"]["tolerance"]),
        max_nfev=int(manifest["corrector"]["maximum_evaluations"]),
    )
    elapsed = time.perf_counter() - started
    residual, _ = evaluate(solution.x)
    corrected_nodes = solution.x[:state_count].reshape(segment_count, 3)
    corrected_period = float(solution.x[state_count])
    corrected_c = float(solution.x[state_count + 1])
    corrected_tangents = solution.x[state_count + 2 :].reshape(segment_count, 3)
    corrected_parameters = RosslerParameters(a=a, b=b, c=corrected_c)
    floquet = block_and_product_floquet(
        corrected_nodes,
        corrected_period,
        corrected_parameters,
        solver,
        manifest["cyclic_shifts"],
    )
    spectrum = flip_spectrum_metrics(floquet)
    independent_solver = SolverConfig(**manifest["independent_solver"])
    independent = flow_monodromy(
        corrected_parameters,
        corrected_nodes[0],
        corrected_period,
        config=independent_solver,
    )
    neutral_index = int(np.argmin(np.abs(independent.multipliers - 1.0)))
    flip_indices = [index for index in range(3) if index != neutral_index]
    independent_flip = min(
        (independent.multipliers[index] for index in flip_indices),
        key=lambda value: abs(value + 1.0),
    )
    winding = _winding(
        corrected_parameters,
        corrected_nodes[0],
        corrected_period,
        independent_solver,
        int(manifest["orbit_sample_count"]),
    )
    orbit_residual = float(np.linalg.norm(residual[:state_count]))
    phase_residual = float(abs(residual[state_count]))
    tangent_residual = float(np.linalg.norm(residual[state_count + 1 : -1]))
    normalization_residual = float(abs(residual[-1]))
    acceptance = manifest["acceptance"]
    passed = bool(
        solution.success
        and bracket[0] <= corrected_c <= bracket[1]
        and orbit_residual <= acceptance["maximum_orbit_residual"]
        and phase_residual <= acceptance["maximum_phase_residual"]
        and tangent_residual <= acceptance["maximum_tangent_residual"]
        and normalization_residual <= acceptance["maximum_normalization_residual"]
        and abs(spectrum["direct_flip_residual"])
        <= acceptance["maximum_reference_flip_residual"]
        and spectrum["maximum_direct_imaginary"]
        <= acceptance["maximum_multiplier_imaginary"]
        and spectrum["block_product_difference"]
        <= acceptance["maximum_block_product_difference"]
        and spectrum["cyclic_product_spread"]
        <= acceptance["maximum_cyclic_product_spread"]
        and independent.closure_error <= acceptance["maximum_independent_closure"]
        and abs(independent.multipliers[neutral_index] - 1.0)
        <= acceptance["maximum_independent_neutral_error"]
        and abs(independent_flip + 1.0)
        <= acceptance["maximum_independent_flip_residual"]
        and abs(independent_flip.imag) <= acceptance["maximum_multiplier_imaginary"]
        and abs(winding - 1.0) <= acceptance["maximum_winding_error"]
    )
    output = {
        "schema": "butterfly.period1-c-flip-receipt.v1",
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
        "fixed_a": a,
        "fixed_b": b,
        "c_bracket": bracket,
        "seed_c": seed_c,
        "seed_multiplier": {
            "real": float(seed_multiplier.real),
            "imag": float(seed_multiplier.imag),
        },
        "corrected_c": corrected_c,
        "period_time": corrected_period,
        "nodes": corrected_nodes.tolist(),
        "tangent_nodes": corrected_tangents.tolist(),
        "initial_residual_norm": float(np.linalg.norm(initial_residual)),
        "residuals": {
            "orbit_matching": orbit_residual,
            "phase": phase_residual,
            "tangent_transport": tangent_residual,
            "normalization": normalization_residual,
        },
        "reference_floquet": floquet,
        "flip_spectrum": spectrum,
        "independent_radau": {
            "closure_error": independent.closure_error,
            "neutral_multiplier_error": float(
                abs(independent.multipliers[neutral_index] - 1.0)
            ),
            "flip_multiplier": {
                "real": float(independent_flip.real),
                "imag": float(independent_flip.imag),
            },
            "winding_number": winding,
        },
        "solver": {
            "success": bool(solution.success),
            "message": solution.message,
            "evaluations": int(solution.nfev),
            "jacobian_evaluations": int(solution.njev) if solution.njev is not None else None,
            "integrated_residual_jacobian_pairs": integrated_pairs,
            "elapsed_seconds": elapsed,
        },
        "passed": passed,
        "scientific_scope": (
            "coupled first period-1 flip on the fixed-(a,b) Hopf-to-hub path; "
            "not a switched period-2 child, higher cascade, symbolic ordering, "
            "or homoclinic connection"
        ),
    }
    atomic_write(args.output, canonical_json(output))
    printed = {
        key: value for key, value in output.items() if key not in {"nodes", "tangent_nodes"}
    }
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

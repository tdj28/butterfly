#!/usr/bin/env python3
"""Solve a segmented Rössler flip event with an exact augmented Jacobian."""
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
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from solve_augmented_segmented_flip import initial_tangent_nodes


def flip_spectrum_metrics(floquet):
    """Select the flip multiplier explicitly, independent of neutral labels."""

    block_clusters = floquet["block"]["clusters"]
    block_flip = min(
        (cluster["floquet_multiplier"] for cluster in block_clusters),
        key=lambda value: abs(complex(value["real"], value["imag"]) + 1.0),
    )
    direct_flips = []
    for row in floquet["direct_products"]:
        selected = min(
            row["eigenvalues"],
            key=lambda value: abs(complex(value["real"], value["imag"]) + 1.0),
        )
        direct_flips.append(
            {
                "cyclic_shift": row["cyclic_shift"],
                "real": float(selected["real"]),
                "imag": float(selected["imag"]),
            }
        )
    direct_reals = [row["real"] for row in direct_flips]
    direct_imaginaries = [abs(row["imag"]) for row in direct_flips]
    direct_median = float(np.median(direct_reals))
    return {
        "block_flip_multiplier": block_flip,
        "direct_flip_multipliers": direct_flips,
        "direct_flip_median": direct_median,
        "direct_flip_residual": direct_median + 1.0,
        "maximum_direct_imaginary": max(direct_imaginaries),
        "block_product_difference": abs(float(block_flip["real"]) - direct_median),
        "cyclic_product_spread": max(direct_reals) - min(direct_reals),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--baseline-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.analytic-augmented-flip-manifest.v1":
        raise SystemExit("unsupported analytic augmented flip manifest")
    source_bytes = args.source_receipt.read_bytes()
    baseline_bytes = args.baseline_receipt.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    if sha256_bytes(baseline_bytes) != manifest["baseline_receipt_sha256"]:
        raise SystemExit("baseline receipt hash mismatch")
    baseline = json.loads(baseline_bytes)
    if baseline.get("experiment_id") != manifest["baseline_experiment_id"]:
        raise SystemExit("baseline experiment mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    source_receipt = json.loads(source_bytes)
    if source_receipt.get("schema") != manifest["source_schema"]:
        raise SystemExit("bound source schema mismatch")
    seed = source_receipt["best_evaluation"]
    nodes = np.asarray(seed["nodes"], dtype=float)
    segment_count = len(nodes)
    if segment_count != manifest["segment_count"]:
        raise SystemExit("source segment count mismatch")
    duration = float(seed["period_time"])
    seed_b = float(seed["b"]) + float(manifest["seed_b_offset"])
    lower_b, upper_b = map(float, manifest["b_bounds"])
    if not lower_b < seed_b < upper_b:
        raise SystemExit("offset seed lies outside frozen bounds")
    a = float(manifest["fixed_a"])
    c = float(manifest["fixed_c"])
    solver = SolverConfig(**manifest["solver"])
    seed_parameters = RosslerParameters(a=a, b=seed_b, c=c)
    tangent_nodes, seed_multiplier = initial_tangent_nodes(
        nodes, duration, seed_parameters, solver
    )
    phase_reference = nodes[0].copy()
    phase = rossler_rhs(0.0, phase_reference, seed_parameters)
    phase /= np.linalg.norm(phase)
    initial = np.r_[nodes.ravel(), duration, seed_b, tangent_nodes.ravel()]
    cached_variables = None
    cached_residual = None
    cached_jacobian = None
    evaluations = 0

    def evaluate(value):
        nonlocal cached_variables, cached_residual, cached_jacobian, evaluations
        if cached_variables is not None and np.array_equal(value, cached_variables):
            return cached_residual, cached_jacobian
        residual, jacobian = augmented_flip_system(
            value,
            segment_count=segment_count,
            a=a,
            c=c,
            phase=phase,
            phase_reference=phase_reference,
            solver=solver,
        )
        evaluations += 1
        print(
            json.dumps(
                {
                    "evaluation": evaluations,
                    "residual_norm": float(np.linalg.norm(residual)),
                    "b": float(value[3 * segment_count + 1]),
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
    state_count = 3 * segment_count
    lower = np.full(len(initial), -np.inf)
    upper = np.full(len(initial), np.inf)
    lower[state_count] = 1e-12
    lower[state_count + 1] = lower_b
    upper[state_count + 1] = upper_b
    started = time.perf_counter()
    solution = least_squares(
        lambda value: evaluate(value)[0],
        initial,
        jac=lambda value: evaluate(value)[1],
        bounds=(lower, upper),
        method="trf",
        tr_solver="exact",
        x_scale="jac",
        xtol=manifest["corrector"]["tolerance"],
        ftol=manifest["corrector"]["tolerance"],
        gtol=manifest["corrector"]["tolerance"],
        max_nfev=manifest["corrector"]["max_evaluations"],
        verbose=manifest["corrector"]["verbose"],
    )
    elapsed = time.perf_counter() - started
    residual, _ = evaluate(solution.x)
    corrected_nodes = solution.x[:state_count].reshape(segment_count, 3)
    corrected_duration = float(solution.x[state_count])
    corrected_b = float(solution.x[state_count + 1])
    corrected_tangents = solution.x[state_count + 2 :].reshape(segment_count, 3)
    corrected_parameters = RosslerParameters(a=a, b=corrected_b, c=c)
    floquet = block_and_product_floquet(
        corrected_nodes,
        corrected_duration,
        corrected_parameters,
        solver,
        manifest["cyclic_shifts"],
    )
    spectrum = flip_spectrum_metrics(floquet)
    reference_error = corrected_b - float(manifest["reference_b"])
    orbit = residual[:state_count]
    phase_residual = float(residual[state_count])
    tangent = residual[state_count + 1 : -1]
    normalization = float(residual[-1])
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.analytic-augmented-flip.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "parent_period_label": manifest["parent_period_label"],
        "child_period_label": manifest["child_period_label"],
        "segment_count": segment_count,
        "seed_b": seed_b,
        "seed_multiplier": {
            "real": float(seed_multiplier.real),
            "imag": float(seed_multiplier.imag),
        },
        "b_bounds": [lower_b, upper_b],
        "reference_b": manifest["reference_b"],
        "reference_error": reference_error,
        "corrected_b": corrected_b,
        "period_time": corrected_duration,
        "nodes": corrected_nodes.tolist(),
        "tangent_nodes": corrected_tangents.tolist(),
        "initial_residual_norm": float(np.linalg.norm(initial_residual)),
        "residuals": {
            "orbit_matching": float(np.linalg.norm(orbit)),
            "phase": abs(phase_residual),
            "tangent_transport": float(np.linalg.norm(tangent)),
            "normalization": abs(normalization),
        },
        "independent_floquet": floquet,
        "flip_spectrum": spectrum,
        "solver": {
            "success": bool(solution.success),
            "message": solution.message,
            "evaluations": int(solution.nfev),
            "jacobian_evaluations": int(solution.njev) if solution.njev is not None else None,
            "integrated_residual_jacobian_pairs": evaluations,
            "cost": float(solution.cost),
            "optimality": float(solution.optimality),
            "elapsed_seconds": elapsed,
        },
    }
    output["passed"] = bool(
        solution.success
        and lower_b <= corrected_b <= upper_b
        and abs(reference_error) <= acceptance["max_reference_error"]
        and output["residuals"]["orbit_matching"] <= acceptance["max_orbit_residual"]
        and output["residuals"]["phase"] <= acceptance["max_phase_residual"]
        and output["residuals"]["tangent_transport"]
        <= acceptance["max_tangent_residual"]
        and output["residuals"]["normalization"]
        <= acceptance["max_normalization_residual"]
        and abs(spectrum["direct_flip_residual"])
        <= acceptance["max_independent_multiplier_residual"]
        and spectrum["maximum_direct_imaginary"]
        <= acceptance["max_independent_multiplier_imaginary"]
        and spectrum["block_product_difference"]
        <= acceptance["max_block_product_difference"]
        and spectrum["cyclic_product_spread"]
        <= acceptance["max_cyclic_product_spread"]
    )
    atomic_write(args.output, canonical_json(output))
    printed = {
        key: value for key, value in output.items() if key not in {"nodes", "tangent_nodes"}
    }
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

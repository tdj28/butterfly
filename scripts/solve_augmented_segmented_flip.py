#!/usr/bin/env python3
"""Solve a segmented periodic orbit and anti-periodic tangent field together."""
from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix

from audit_segmented_floquet_precision import block_and_product_floquet
from butterfly import RosslerParameters, SolverConfig, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from multiple_shooting_core import integrate_segment


def augmented_sparsity(segment_count: int):
    state_count = 3 * segment_count
    variable_count = 6 * segment_count + 2
    pattern = lil_matrix((variable_count, variable_count), dtype=bool)
    time_column = state_count
    parameter_column = state_count + 1
    tangent_offset = state_count + 2
    for index in range(segment_count):
        next_index = (index + 1) % segment_count
        orbit_rows = slice(3 * index, 3 * index + 3)
        current_state = slice(3 * index, 3 * index + 3)
        next_state = slice(3 * next_index, 3 * next_index + 3)
        pattern[orbit_rows, current_state] = True
        pattern[orbit_rows, next_state] = True
        pattern[orbit_rows, time_column] = True
        pattern[orbit_rows, parameter_column] = True

        tangent_rows = slice(state_count + 1 + 3 * index, state_count + 4 + 3 * index)
        current_tangent = slice(
            tangent_offset + 3 * index, tangent_offset + 3 * index + 3
        )
        next_tangent = slice(
            tangent_offset + 3 * next_index, tangent_offset + 3 * next_index + 3
        )
        pattern[tangent_rows, current_state] = True
        pattern[tangent_rows, current_tangent] = True
        pattern[tangent_rows, next_tangent] = True
        pattern[tangent_rows, time_column] = True
        pattern[tangent_rows, parameter_column] = True
    pattern[state_count, :3] = True
    pattern[-1, tangent_offset : tangent_offset + 3] = True
    return pattern.tocsr()


def segment_data(nodes, duration, parameters, solver):
    segment_duration = duration / len(nodes)
    return [
        integrate_segment(node, segment_duration, parameters, solver)[:2]
        for node in nodes
    ]


def initial_tangent_nodes(nodes, duration, parameters, solver):
    data = segment_data(nodes, duration, parameters, solver)
    monodromy = np.eye(3)
    for _, transition in data:
        monodromy = transition @ monodromy
    values, vectors = np.linalg.eig(monodromy)
    index = int(np.argmin(np.abs(values + 1.0)))
    vector = vectors[:, index]
    if np.linalg.norm(vector.imag) > 1e-8:
        raise RuntimeError("nearest -1 eigenvector is not real")
    current = vector.real
    current /= np.linalg.norm(current)
    tangent_nodes = [current]
    for _, transition in data[:-1]:
        tangent_nodes.append(transition @ tangent_nodes[-1])
    return np.asarray(tangent_nodes), complex(values[index])


def residual_components(
    variables,
    *,
    segment_count,
    a,
    c,
    phase,
    phase_reference,
    solver,
):
    state_count = 3 * segment_count
    nodes = variables[:state_count].reshape(segment_count, 3)
    duration = float(variables[state_count])
    b = float(variables[state_count + 1])
    tangents = variables[state_count + 2 :].reshape(segment_count, 3)
    parameters = RosslerParameters(a=a, b=b, c=c)
    data = segment_data(nodes, duration, parameters, solver)
    orbit_rows = []
    tangent_rows = []
    for index, (endpoint, transition) in enumerate(data):
        next_index = (index + 1) % segment_count
        orbit_rows.append(endpoint - nodes[next_index])
        if index + 1 < segment_count:
            tangent_rows.append(transition @ tangents[index] - tangents[next_index])
        else:
            tangent_rows.append(transition @ tangents[index] + tangents[0])
    orbit = np.concatenate(orbit_rows)
    tangent = np.concatenate(tangent_rows)
    phase_residual = float(np.dot(phase, nodes[0] - phase_reference))
    normalization = float(np.dot(tangents[0], tangents[0]) - 1.0)
    return orbit, phase_residual, tangent, normalization


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.augmented-segmented-flip-manifest.v1":
        raise SystemExit("unsupported augmented segmented flip manifest")
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

    def components(value):
        return residual_components(
            value,
            segment_count=segment_count,
            a=a,
            c=c,
            phase=phase,
            phase_reference=phase_reference,
            solver=solver,
        )

    def residual(value):
        orbit, phase_residual, tangent, normalization = components(value)
        return np.r_[orbit, phase_residual, tangent, normalization]

    initial_orbit, initial_phase, initial_tangent, initial_norm = components(initial)
    lower = np.full(len(initial), -np.inf)
    upper = np.full(len(initial), np.inf)
    state_count = 3 * segment_count
    lower[state_count] = 1e-12
    lower[state_count + 1] = lower_b
    upper[state_count + 1] = upper_b
    started = time.perf_counter()
    solution = least_squares(
        residual,
        initial,
        jac_sparsity=augmented_sparsity(segment_count),
        bounds=(lower, upper),
        method="trf",
        tr_solver="lsmr",
        x_scale="jac",
        xtol=manifest["corrector"]["tolerance"],
        ftol=manifest["corrector"]["tolerance"],
        gtol=manifest["corrector"]["tolerance"],
        max_nfev=manifest["corrector"]["max_evaluations"],
        verbose=manifest["corrector"]["verbose"],
    )
    elapsed = time.perf_counter() - started
    orbit, phase_residual, tangent, normalization = components(solution.x)
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
    block_value = floquet["block"]["dominant_nontrivial_multiplier"]
    product_values = [
        row["dominant_nontrivial_multiplier"]["real"]
        for row in floquet["direct_products"]
    ]
    block_product_difference = abs(block_value["real"] - float(np.median(product_values)))
    cyclic_product_spread = max(product_values) - min(product_values)
    reference_error = corrected_b - float(manifest["reference_b"])
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.augmented-segmented-flip.v1",
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
        "initial_residuals": {
            "orbit_matching": float(np.linalg.norm(initial_orbit)),
            "phase": abs(initial_phase),
            "tangent_transport": float(np.linalg.norm(initial_tangent)),
            "normalization": abs(initial_norm),
        },
        "residuals": {
            "orbit_matching": float(np.linalg.norm(orbit)),
            "phase": abs(phase_residual),
            "tangent_transport": float(np.linalg.norm(tangent)),
            "normalization": abs(normalization),
        },
        "independent_floquet": floquet,
        "independent_multiplier_residual": block_value["real"] + 1.0,
        "block_product_difference": block_product_difference,
        "cyclic_product_spread": cyclic_product_spread,
        "solver": {
            "success": bool(solution.success),
            "message": solution.message,
            "evaluations": int(solution.nfev),
            "jacobian_evaluations": int(solution.njev) if solution.njev is not None else None,
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
        and abs(output["independent_multiplier_residual"])
        <= acceptance["max_independent_multiplier_residual"]
        and block_product_difference <= acceptance["max_block_product_difference"]
        and cyclic_product_spread <= acceptance["max_cyclic_product_spread"]
    )
    atomic_write(args.output, canonical_json(output))
    printed = {key: value for key, value in output.items() if key not in {"nodes", "tangent_nodes"}}
    print(json.dumps(printed, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

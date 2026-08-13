#!/usr/bin/env python3
"""Solve the Jones returning-arm period-12 flip by augmented multiple shooting."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import scipy
from scipy.optimize import least_squares

from audit_segmented_floquet_precision import block_and_product_floquet
from butterfly import (
    RosslerParameters,
    SolverConfig,
    augmented_flip_system,
    barrio_rossler_section,
    flow_monodromy,
    legacy_rossler_section,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from qualify_jones_period12_children import (
    _closure_at_fraction,
    _section_count,
    proper_subperiod_fractions,
)
from solve_analytic_augmented_flip import flip_spectrum_metrics
from solve_augmented_segmented_flip import initial_tangent_nodes
from solve_period1_c_flip import _orbit_nodes


SCHEMA = "butterfly.jones-period12-augmented-flip-manifest.v1"


def source_child(receipt: dict, solver_name: str) -> dict:
    """Extract the exact period-12 event seed from a passed EXP-232 receipt."""

    if not receipt.get("passed"):
        raise ValueError("a passed period-12 flip receipt is required")
    root = receipt["root_results"][solver_name]["root_full"]
    return {
        "a": float(root["a"]),
        "b": float(root["b"]),
        "c": float(root["c"]),
        "initial_state": list(root["child"]["initial_state"]),
        "period_time": float(root["child"]["period_time"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Jones period-12 augmented-flip manifest")
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

    seed = source_child(json.loads(source_bytes), manifest["source_solver"])
    fixed_b = float(manifest["fixed_b"])
    fixed_c = float(manifest["fixed_c"])
    if seed["b"] != fixed_b or seed["c"] != fixed_c:
        raise SystemExit("manifest fixed coordinates do not match source seed")
    a_bounds = list(map(float, manifest["a_bounds"]))
    solver = SolverConfig(**manifest["reference_solver"])
    segment_count = int(manifest["segment_count"])
    seed_parameters = RosslerParameters(a=seed["a"], b=fixed_b, c=fixed_c)
    nodes = _orbit_nodes(
        seed_parameters,
        np.asarray(seed["initial_state"], dtype=float),
        seed["period_time"],
        segment_count,
        solver,
    )
    tangent_nodes, seed_multiplier = initial_tangent_nodes(
        nodes, seed["period_time"], seed_parameters, solver
    )
    phase_reference = nodes[0].copy()
    phase = rossler_rhs(0.0, phase_reference, seed_parameters)
    phase /= np.linalg.norm(phase)
    initial = np.r_[
        nodes.ravel(), seed["period_time"], seed["a"], tangent_nodes.ravel()
    ]
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
            a=None,
            c=fixed_c,
            phase=phase,
            phase_reference=phase_reference,
            solver=solver,
            continuation_parameter="a",
            fixed_b=fixed_b,
        )
        integrated_pairs += 1
        print(
            json.dumps(
                {
                    "evaluation": integrated_pairs,
                    "a": float(value[state_count + 1]),
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
    lower[state_count + 1] = a_bounds[0]
    upper[state_count + 1] = a_bounds[1]
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
    corrected_a = float(solution.x[state_count + 1])
    corrected_tangents = solution.x[state_count + 2 :].reshape(segment_count, 3)
    parameters = RosslerParameters(a=corrected_a, b=fixed_b, c=fixed_c)
    floquet = block_and_product_floquet(
        corrected_nodes,
        corrected_period,
        parameters,
        solver,
        manifest["cyclic_shifts"],
    )
    spectrum = flip_spectrum_metrics(floquet)
    independent_solver = SolverConfig(**manifest["independent_solver"])
    independent = flow_monodromy(
        parameters, corrected_nodes[0], corrected_period, config=independent_solver
    )
    neutral_index = int(np.argmin(np.abs(independent.multipliers - 1.0)))
    transverse = np.delete(independent.multipliers, neutral_index)
    independent_flip = complex(transverse[int(np.argmin(np.abs(transverse + 1.0)))])
    orbit = SimpleNamespace(
        initial_state=corrected_nodes[0], period_time=corrected_period
    )
    historical_count = _section_count(
        parameters,
        orbit,
        legacy_rossler_section(parameters),
        int(manifest["identity"]["historical_phase_count"]),
        independent_solver,
    )
    barrio_count = _section_count(
        parameters,
        orbit,
        barrio_rossler_section(parameters),
        int(manifest["identity"]["barrio_phase_count"]),
        independent_solver,
    )
    subperiod_closures = [
        {
            "fraction": fraction,
            "closure": _closure_at_fraction(
                parameters, orbit, fraction, independent_solver
            ),
        }
        for fraction in proper_subperiod_fractions(
            int(manifest["identity"]["historical_phase_count"])
        )
    ]
    minimum_subperiod_closure = min(row["closure"] for row in subperiod_closures)
    orbit_residual = float(np.linalg.norm(residual[:state_count]))
    phase_residual = float(abs(residual[state_count]))
    tangent_residual = float(np.linalg.norm(residual[state_count + 1 : -1]))
    normalization_residual = float(abs(residual[-1]))
    acceptance = manifest["acceptance"]
    independent_closure = float(independent.closure_error)
    independent_neutral_error = float(
        abs(independent.multipliers[neutral_index] - 1.0)
    )
    checks = {
        "solver": bool(solution.success),
        "a_bounds": a_bounds[0] <= corrected_a <= a_bounds[1],
        "reference_a": abs(corrected_a - seed["a"])
        <= float(acceptance["maximum_reference_a_error"]),
        "orbit": orbit_residual <= float(acceptance["maximum_orbit_residual"]),
        "phase": phase_residual <= float(acceptance["maximum_phase_residual"]),
        "tangent": tangent_residual
        <= float(acceptance["maximum_tangent_residual"]),
        "normalization": normalization_residual
        <= float(acceptance["maximum_normalization_residual"]),
        "reference_flip": abs(float(spectrum["direct_flip_residual"]))
        <= float(acceptance["maximum_reference_flip_residual"]),
        "independent_closure": independent_closure
        <= float(acceptance["maximum_independent_closure"]),
        "independent_neutral": independent_neutral_error
        <= float(acceptance["maximum_independent_neutral_error"]),
        "independent_flip": abs(independent_flip + 1.0)
        <= float(acceptance["maximum_independent_flip_residual"]),
        "real_flip": abs(independent_flip.imag)
        <= float(acceptance["maximum_multiplier_imaginary"]),
        "primitive": minimum_subperiod_closure
        >= float(acceptance["minimum_proper_subperiod_closure"]),
        "section_identity": bool(
            historical_count[1]
            and barrio_count[1]
            and historical_count[0]
            == int(manifest["identity"]["historical_phase_count"])
            and barrio_count[0]
            == int(manifest["identity"]["barrio_phase_count"])
        ),
    }
    output = {
        "schema": "butterfly.jones-period12-augmented-flip-receipt.v1",
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
        "fixed_b": fixed_b,
        "fixed_c": fixed_c,
        "a_bounds": a_bounds,
        "seed": seed,
        "seed_multiplier": {
            "real": float(seed_multiplier.real),
            "imag": float(seed_multiplier.imag),
        },
        "segment_count": segment_count,
        "corrected_a": corrected_a,
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
            "closure_error": independent_closure,
            "neutral_multiplier_error": independent_neutral_error,
            "flip_multiplier": {
                "real": float(independent_flip.real),
                "imag": float(independent_flip.imag),
            },
        },
        "section_identity": {
            "historical_phase_count": historical_count[0],
            "historical_integration_success": historical_count[1],
            "barrio_phase_count": barrio_count[0],
            "barrio_integration_success": barrio_count[1],
        },
        "proper_subperiod_closures": subperiod_closures,
        "minimum_proper_subperiod_closure": float(minimum_subperiod_closure),
        "solver": {
            "success": bool(solution.success),
            "message": solution.message,
            "evaluations": int(solution.nfev),
            "jacobian_evaluations": (
                int(solution.njev) if solution.njev is not None else None
            ),
            "integrated_residual_jacobian_pairs": integrated_pairs,
            "elapsed_seconds": elapsed,
        },
        "checks": checks,
        "passed": all(checks.values()),
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    printed = {
        key: value
        for key, value in output.items()
        if key not in {"nodes", "tangent_nodes", "reference_floquet"}
    }
    print(json.dumps(printed, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

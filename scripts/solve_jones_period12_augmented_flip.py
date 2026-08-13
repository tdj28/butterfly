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


SCHEMAS = {
    "butterfly.jones-period12-augmented-flip-manifest.v1",
    "butterfly.jones-period24-augmented-flip-manifest.v1",
    "butterfly.jones-period48-augmented-flip-manifest.v1",
    "butterfly.jones-period48-augmented-flip-manifest.v2",
    "butterfly.jones-period96-augmented-flip-manifest.v1",
    "butterfly.jones-period192-augmented-flip-manifest.v1",
    "butterfly.jones-period384-augmented-flip-manifest.v1",
    "butterfly.jones-period768-augmented-flip-manifest.v1",
}


def source_child(receipt: dict, solver_name: str, manifest: dict | None = None) -> dict:
    """Extract an event seed from EXP-232 or an exact segmented continuation."""

    if not receipt.get("passed"):
        raise ValueError("a passed source receipt is required")
    if receipt.get("schema") in {
        "butterfly.jones-period24-segmented-continuation-receipt.v1",
        "butterfly.jones-period48-segmented-continuation-receipt.v1",
        "butterfly.jones-period96-segmented-continuation-receipt.v1",
        "butterfly.jones-period192-segmented-continuation-receipt.v1",
        "butterfly.jones-period384-segmented-continuation-receipt.v1",
        "butterfly.jones-period768-segmented-continuation-receipt.v1",
    }:
        if manifest is None or "source_row_index" not in manifest:
            raise ValueError("segmented source requires a frozen source row index")
        row = receipt["rows"][int(manifest["source_row_index"])]
        return {
            "a": float(row["a"]),
            "b": float(receipt["fixed_b"]),
            "c": float(receipt["fixed_c"]),
            "initial_state": list(row["nodes"][0]),
            "period_time": float(row["period_time"]),
            "nodes": row["nodes"],
        }
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
    parser.add_argument("--bracket-receipt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") not in SCHEMAS:
        raise SystemExit("unsupported Jones augmented-flip manifest")
    source_bytes = args.source_receipt.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_receipt_sha256"]:
        raise SystemExit("source receipt hash mismatch")
    bracket_bytes = None
    bracket = None
    if "bracket_receipt_sha256" in manifest:
        if args.bracket_receipt is None:
            raise SystemExit("this manifest requires a bracket receipt")
        bracket_bytes = args.bracket_receipt.read_bytes()
        if sha256_bytes(bracket_bytes) != manifest["bracket_receipt_sha256"]:
            raise SystemExit("bracket receipt hash mismatch")
        bracket = json.loads(bracket_bytes)
        if not bracket.get("passed") or len(bracket["flip_brackets"]) != 1:
            raise SystemExit("a passed unique flip bracket is required")
        frozen_bracket = list(map(float, bracket["flip_brackets"][0]["a_bracket"]))
        if frozen_bracket != list(map(float, manifest["a_bounds"])):
            raise SystemExit("manifest a bounds do not match the bracket receipt")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    source_receipt = json.loads(source_bytes)
    if manifest.get("seed_method") == "secant_interpolation":
        if bracket is None:
            raise SystemExit("secant interpolation requires a bracket receipt")
        event_bracket = bracket["flip_brackets"][0]
        left = source_receipt["rows"][int(event_bracket["left_index"])]
        right = source_receipt["rows"][int(event_bracket["right_index"])]
        left_residual = float(event_bracket["left_multiplier"]["real"]) + 1.0
        right_residual = float(event_bracket["right_multiplier"]["real"]) + 1.0
        seed_a = (
            float(left["a"]) * right_residual
            - float(right["a"]) * left_residual
        ) / (right_residual - left_residual)
        fraction = (seed_a - float(left["a"])) / (
            float(right["a"]) - float(left["a"])
        )
        nodes = (1.0 - fraction) * np.asarray(left["nodes"], dtype=float)
        nodes += fraction * np.asarray(right["nodes"], dtype=float)
        seed = {
            "a": float(seed_a),
            "b": float(source_receipt["fixed_b"]),
            "c": float(source_receipt["fixed_c"]),
            "initial_state": nodes[0].tolist(),
            "period_time": float(
                (1.0 - fraction) * float(left["period_time"])
                + fraction * float(right["period_time"])
            ),
            "nodes": nodes.tolist(),
            "seed_method": "secant_interpolation",
            "secant_fraction": float(fraction),
            "source_row_indices": [
                int(event_bracket["left_index"]),
                int(event_bracket["right_index"]),
            ],
        }
    elif manifest.get("seed_method") == "failed_event_refinement":
        if source_receipt.get("passed"):
            raise SystemExit("failed-event refinement requires a failed source")
        expected_checks = {
            key: key != manifest["isolated_failed_check"]
            for key in source_receipt["checks"]
        }
        if source_receipt["checks"] != expected_checks:
            raise SystemExit("source failure is not isolated as declared")
        seed = {
            "a": float(source_receipt["corrected_a"]),
            "b": float(source_receipt["fixed_b"]),
            "c": float(source_receipt["fixed_c"]),
            "initial_state": list(source_receipt["nodes"][0]),
            "period_time": float(source_receipt["period_time"]),
            "nodes": source_receipt["nodes"],
            "tangent_nodes": source_receipt["tangent_nodes"],
            "seed_method": "failed_event_refinement",
        }
    else:
        seed = source_child(
            source_receipt, manifest["source_solver"], manifest
        )
    fixed_b = float(manifest["fixed_b"])
    fixed_c = float(manifest["fixed_c"])
    if seed["b"] != fixed_b or seed["c"] != fixed_c:
        raise SystemExit("manifest fixed coordinates do not match source seed")
    a_bounds = list(map(float, manifest["a_bounds"]))
    solver = SolverConfig(**manifest["reference_solver"])
    segment_count = int(manifest["segment_count"])
    seed_parameters = RosslerParameters(a=seed["a"], b=fixed_b, c=fixed_c)
    if "nodes" in seed and len(seed["nodes"]) == segment_count:
        nodes = np.asarray(seed["nodes"], dtype=float)
    else:
        nodes = _orbit_nodes(
            seed_parameters,
            np.asarray(seed["initial_state"], dtype=float),
            seed["period_time"],
            segment_count,
            solver,
        )
    if "tangent_nodes" in seed:
        tangent_nodes = np.asarray(seed["tangent_nodes"], dtype=float)
        seed_multiplier = complex(
            source_receipt["flip_spectrum"]["direct_flip_median"], 0.0
        )
    else:
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
    independent_segmented = None
    if manifest.get("independent_representation") == "segmented_augmented":
        independent_residual, _ = augmented_flip_system(
            solution.x,
            segment_count=segment_count,
            a=None,
            c=fixed_c,
            phase=phase,
            phase_reference=phase_reference,
            solver=independent_solver,
            continuation_parameter="a",
            fixed_b=fixed_b,
        )
        independent_floquet = block_and_product_floquet(
            corrected_nodes,
            corrected_period,
            parameters,
            independent_solver,
            manifest["cyclic_shifts"],
        )
        independent_spectrum = flip_spectrum_metrics(independent_floquet)
        independent_components = {
            "orbit_matching": float(
                np.linalg.norm(independent_residual[:state_count])
            ),
            "phase": float(abs(independent_residual[state_count])),
            "tangent_transport": float(
                np.linalg.norm(independent_residual[state_count + 1 : -1])
            ),
            "normalization": float(abs(independent_residual[-1])),
        }
        independent_flip = complex(
            float(independent_spectrum["direct_flip_median"]), 0.0
        )
        independent_segmented = {
            "representation": "segmented_augmented",
            "residuals": independent_components,
            "floquet": independent_floquet,
            "flip_spectrum": independent_spectrum,
        }
    else:
        independent = flow_monodromy(
            parameters,
            corrected_nodes[0],
            corrected_period,
            config=independent_solver,
        )
        neutral_index = int(np.argmin(np.abs(independent.multipliers - 1.0)))
        transverse = np.delete(independent.multipliers, neutral_index)
        independent_flip = complex(
            transverse[int(np.argmin(np.abs(transverse + 1.0)))]
        )
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
    accepted_solver_status = bool(solution.success)
    if (
        not accepted_solver_status
        and manifest.get("allow_max_evaluations_if_residual_qualified")
        and "maximum number of function evaluations" in solution.message
    ):
        accepted_solver_status = bool(
            orbit_residual <= float(acceptance["maximum_orbit_residual"])
            and phase_residual <= float(acceptance["maximum_phase_residual"])
            and tangent_residual <= float(acceptance["maximum_tangent_residual"])
            and normalization_residual
            <= float(acceptance["maximum_normalization_residual"])
            and abs(float(spectrum["direct_flip_residual"]))
            <= float(acceptance["maximum_reference_flip_residual"])
        )
    checks = {
        "solver": accepted_solver_status,
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
    if independent_segmented is not None:
        independent_components = independent_segmented["residuals"]
        independent_spectrum = independent_segmented["flip_spectrum"]
        checks.update(
            {
                "independent_orbit": independent_components["orbit_matching"]
                <= float(acceptance["maximum_independent_orbit_residual"]),
                "independent_phase": independent_components["phase"]
                <= float(acceptance["maximum_independent_phase_residual"]),
                "independent_tangent": independent_components[
                    "tangent_transport"
                ]
                <= float(acceptance["maximum_independent_tangent_residual"]),
                "independent_normalization": independent_components[
                    "normalization"
                ]
                <= float(
                    acceptance["maximum_independent_normalization_residual"]
                ),
                "independent_flip": abs(
                    float(independent_spectrum["direct_flip_residual"])
                )
                <= float(acceptance["maximum_independent_flip_residual"]),
                "real_flip": independent_spectrum["maximum_direct_imaginary"]
                <= float(acceptance["maximum_multiplier_imaginary"]),
                "independent_cyclic": independent_spectrum[
                    "cyclic_product_spread"
                ]
                <= float(acceptance["maximum_independent_cyclic_spread"]),
            }
        )
    else:
        independent_closure = float(independent.closure_error)
        independent_neutral_error = float(
            abs(independent.multipliers[neutral_index] - 1.0)
        )
        checks.update(
            {
                "independent_closure": independent_closure
                <= float(acceptance["maximum_independent_closure"]),
                "independent_neutral": independent_neutral_error
                <= float(acceptance["maximum_independent_neutral_error"]),
                "independent_flip": abs(independent_flip + 1.0)
                <= float(acceptance["maximum_independent_flip_residual"]),
                "real_flip": abs(independent_flip.imag)
                <= float(acceptance["maximum_multiplier_imaginary"]),
            }
        )
    output = {
        "schema": manifest.get(
            "output_schema", "butterfly.jones-period12-augmented-flip-receipt.v1"
        ),
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": sha256_bytes(source_bytes),
        "bracket_receipt_sha256": (
            sha256_bytes(bracket_bytes) if bracket_bytes is not None else None
        ),
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
        "independent_radau": (
            independent_segmented
            if independent_segmented is not None
            else {
                "representation": "single_shot",
                "closure_error": independent_closure,
                "neutral_multiplier_error": independent_neutral_error,
                "flip_multiplier": {
                    "real": float(independent_flip.real),
                    "imag": float(independent_flip.imag),
                },
            }
        ),
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
            "status_accepted": accepted_solver_status,
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

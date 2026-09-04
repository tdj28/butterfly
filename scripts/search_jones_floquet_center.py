#!/usr/bin/env python3
"""Replay the retired EXP-187/188 signed-Floquet center heuristic.

This diagnostic does not locate full-flow superstability curves: the exact
finite-time monodromy is invertible. Sign changes of a selected eigenvalue's
real part are not eigenvalue zeros. Retained for historical reproducibility;
see docs/findings/FND-060-floquet-zero-surface-does-not-uniquely-locate-center.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    PoincareSection,
    RosslerParameters,
    SolverConfig,
    collect_crossings,
    correct_periodic_orbit,
    flow_monodromy,
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-floquet-center-search-manifest.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _section(parameters: RosslerParameters) -> PoincareSection:
    base = legacy_rossler_section(parameters)
    return PoincareSection(
        normal=base.normal,
        offset=base.offset,
        direction=-1,
        gate_axis=base.gate_axis,
        gate_upper=base.gate_upper,
        name="legacy-small-equilibrium-half-plane:negative",
    )


def _complex_row(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag), "modulus": float(abs(value))}


def signed_dominant_nontrivial(multipliers) -> tuple[complex, complex, int]:
    """Return the largest-modulus transverse multiplier and neutral multiplier."""

    values = np.asarray(multipliers, dtype=np.complex128)
    if values.shape != (3,):
        raise ValueError("a three-dimensional flow must supply three multipliers")
    neutral_index = int(np.argmin(np.abs(values - 1.0)))
    transverse = np.delete(values, neutral_index)
    dominant = complex(transverse[int(np.argmax(np.abs(transverse)))])
    return dominant, complex(values[neutral_index]), neutral_index


def ring_sign_alternations(values, *, zero_tolerance: float = 0.0) -> int:
    """Count cyclic sign changes; a transverse zero-crossing has four."""

    signs = []
    for value in values:
        if value > zero_tolerance:
            signs.append(1)
        elif value < -zero_tolerance:
            signs.append(-1)
        else:
            signs.append(0)
    if not signs or any(sign == 0 for sign in signs):
        return 0
    return sum(left != right for left, right in zip(signs, signs[1:] + signs[:1]))


def quadratic_saddle_candidates(
    a_values,
    c_values,
    multiplier_grid,
    *,
    maximum_stationary_cell_offset: float,
    minimum_ring_sign_alternations: int,
    zero_tolerance: float,
) -> list[dict]:
    """Fit normalized 3x3 quadratics and return interior saddle-zero candidates."""

    a_values = np.asarray(a_values, dtype=float)
    c_values = np.asarray(c_values, dtype=float)
    values = np.asarray(multiplier_grid, dtype=float)
    if values.shape != (len(a_values), len(c_values)):
        raise ValueError("multiplier grid shape does not match axes")
    if len(a_values) < 3 or len(c_values) < 3:
        return []
    candidates = []
    ring_offsets = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1))
    for i in range(1, len(a_values) - 1):
        for j in range(1, len(c_values) - 1):
            patch = values[i - 1 : i + 2, j - 1 : j + 2]
            if not np.all(np.isfinite(patch)):
                continue
            da = float((a_values[i + 1] - a_values[i - 1]) / 2.0)
            dc = float((c_values[j + 1] - c_values[j - 1]) / 2.0)
            if da <= 0.0 or dc <= 0.0:
                continue
            design = []
            observed = []
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    u = float((a_values[i + di] - a_values[i]) / da)
                    v = float((c_values[j + dj] - c_values[j]) / dc)
                    design.append((1.0, u, v, u * u, u * v, v * v))
                    observed.append(float(values[i + di, j + dj]))
            matrix = np.asarray(design, dtype=float)
            observed_array = np.asarray(observed, dtype=float)
            coefficients, *_ = np.linalg.lstsq(matrix, observed_array, rcond=None)
            hessian = np.asarray(
                [[2.0 * coefficients[3], coefficients[4]], [coefficients[4], 2.0 * coefficients[5]]],
                dtype=float,
            )
            eigenvalues = np.linalg.eigvalsh(hessian)
            if eigenvalues[0] >= 0.0 or eigenvalues[1] <= 0.0:
                continue
            try:
                stationary = np.linalg.solve(hessian, -coefficients[1:3])
            except np.linalg.LinAlgError:
                continue
            if np.max(np.abs(stationary)) > maximum_stationary_cell_offset:
                continue
            u, v = map(float, stationary)
            stationary_value = float(
                coefficients[0]
                + coefficients[1] * u
                + coefficients[2] * v
                + coefficients[3] * u * u
                + coefficients[4] * u * v
                + coefficients[5] * v * v
            )
            fitted = matrix @ coefficients
            fit_rms = float(np.sqrt(np.mean((fitted - observed_array) ** 2)))
            ring = [float(values[i + di, j + dj]) for di, dj in ring_offsets]
            alternations = ring_sign_alternations(ring, zero_tolerance=zero_tolerance)
            if alternations < minimum_ring_sign_alternations:
                continue
            candidate_a = float(a_values[i] + u * da)
            candidate_c = float(c_values[j] + v * dc)
            candidates.append(
                {
                    "center_index": [i, j],
                    "parameters": {"a": candidate_a, "c": candidate_c},
                    "normalized_stationary_offset": [u, v],
                    "stationary_multiplier": stationary_value,
                    "fit_rms": fit_rms,
                    "hessian_eigenvalues": eigenvalues.tolist(),
                    "ring_sign_alternations": alternations,
                    "ring_values": ring,
                    "score": abs(stationary_value) + fit_rms,
                }
            )
    return sorted(candidates, key=lambda row: (row["score"], row["parameters"]["a"], row["parameters"]["c"]))


def _phase_aligned_error(left, right, scales) -> dict:
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    scales = np.asarray(scales, dtype=float)
    if left.shape != right.shape or left.ndim != 2 or left.shape[1] != 3:
        return {"resolved": False, "shift": None, "maximum_scaled_error": None}
    errors = []
    for shift in range(len(left)):
        delta = (left - np.roll(right, shift, axis=0))[:, (0, 2)] / scales
        errors.append(float(np.max(np.linalg.norm(delta, axis=1))))
    best = int(np.argmin(errors))
    return {"resolved": True, "shift": best, "maximum_scaled_error": errors[best]}


def _orbit_crossings(parameters, correction, solver, expected_period):
    section = _section(parameters)
    crossings = collect_crossings(
        parameters,
        correction.initial_state,
        section,
        transient=0.0,
        observation_horizon=correction.period_time * (1.0 + 1e-7),
        max_crossings=expected_period + 4,
        config=solver,
    )
    keep = (crossings.times > correction.period_time * 1e-7) & (
        crossings.times <= correction.period_time * (1.0 + 1e-7)
    )
    return crossings.states[keep], bool(crossings.integration_success)


def _evaluate_orbit(
    a: float,
    c: float,
    *,
    b: float,
    seed_state,
    seed_period: float,
    solver: SolverConfig,
    manifest: dict,
    predecessor_states=None,
) -> tuple[dict, dict | None]:
    acceptance = manifest["acceptance"]
    expected_period = int(manifest["seed"]["expected_period"])
    parameters = RosslerParameters(a=float(a), b=float(b), c=float(c))
    try:
        correction = correct_periodic_orbit(
            parameters,
            seed_state,
            seed_period,
            config=solver,
            max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
            tolerance=float(manifest["corrector"]["tolerance"]),
        )
        section_states, crossing_success = _orbit_crossings(
            parameters, correction, solver, expected_period
        )
        monodromy = flow_monodromy(
            parameters,
            correction.initial_state,
            correction.period_time,
            config=solver,
        )
        dominant, neutral, _ = signed_dominant_nontrivial(monodromy.multipliers)
        if predecessor_states is None:
            predecessor_error = {"resolved": True, "shift": 0, "maximum_scaled_error": 0.0}
        else:
            predecessor_error = _phase_aligned_error(
                section_states,
                predecessor_states,
                manifest["continuation"]["coordinate_scales"],
            )
        checks = {
            "correction": bool(correction.success),
            "flow_integration": bool(monodromy.success and crossing_success),
            "closure": bool(correction.closure_error <= float(acceptance["maximum_flow_closure"])),
            "phase": bool(correction.phase_residual <= float(acceptance["maximum_phase_residual"])),
            "section_identity": len(section_states) == expected_period,
            "neutral_multiplier": abs(neutral - 1.0) <= float(acceptance["maximum_neutral_multiplier_error"]),
            "dominant_real": abs(dominant.imag) <= float(acceptance["maximum_dominant_imaginary_part"]),
            "neighbor_identity": bool(
                predecessor_error["resolved"]
                and predecessor_error["maximum_scaled_error"] is not None
                and predecessor_error["maximum_scaled_error"]
                <= float(acceptance["maximum_neighbor_scaled_orbit_error"])
            ),
        }
        valid = all(checks.values())
        row = {
            "parameters": {"a": float(a), "b": float(b), "c": float(c)},
            "correction": {
                "initial_state": correction.initial_state.tolist(),
                "period_time": correction.period_time,
                "closure_error": correction.closure_error,
                "phase_residual": correction.phase_residual,
                "correction_norm": correction.correction_norm,
                "evaluations": correction.evaluations,
                "optimizer_success": correction.optimizer_success,
            },
            "section_crossing_count": len(section_states),
            "multipliers": [_complex_row(value) for value in monodromy.multipliers],
            "dominant_nontrivial_multiplier": _complex_row(dominant),
            "neutral_multiplier": _complex_row(neutral),
            "predicted_determinant": monodromy.predicted_determinant,
            "computed_determinant": monodromy.computed_determinant,
            "predecessor_orbit_error": predecessor_error,
            "checks": checks,
            "valid": valid,
        }
        internal = {
            "state": correction.initial_state,
            "period": correction.period_time,
            "section_states": section_states,
        }
        return row, internal
    except Exception as error:  # preserve a failed continuation cell in the receipt
        return {
            "parameters": {"a": float(a), "b": float(b), "c": float(c)},
            "error": f"{type(error).__name__}: {error}",
            "valid": False,
        }, None


def _axis(center: float, step: float, count: int) -> np.ndarray:
    if count < 3 or count % 2 == 0 or step <= 0.0:
        raise ValueError("grid count must be odd and at least three with positive step")
    half = count // 2
    return center + np.arange(-half, half + 1, dtype=float) * step


def _coarse_grid(manifest, solver):
    seed = manifest["seed"]
    grid = manifest["coarse_grid"]
    b = float(seed["parameters"]["b"])
    a_values = _axis(float(seed["parameters"]["a"]), float(grid["a_step"]), int(grid["a_count"]))
    c_values = _axis(float(seed["parameters"]["c"]), float(grid["c_step"]), int(grid["c_count"]))
    center_i = len(a_values) // 2
    center_j = len(c_values) // 2
    rows: dict[tuple[int, int], dict] = {}
    internals: dict[tuple[int, int], dict] = {}

    center_row, center_internal = _evaluate_orbit(
        a_values[center_i],
        c_values[center_j],
        b=b,
        seed_state=seed["initial_state"],
        seed_period=float(seed["period_time"]),
        solver=solver,
        manifest=manifest,
    )
    rows[(center_i, center_j)] = center_row
    if center_internal is None or not center_row["valid"]:
        return a_values, c_values, rows, internals
    internals[(center_i, center_j)] = center_internal

    for direction in (-1, 1):
        predecessor = center_internal
        for i in range(center_i + direction, -1 if direction < 0 else len(a_values), direction):
            row, internal = _evaluate_orbit(
                a_values[i],
                c_values[center_j],
                b=b,
                seed_state=predecessor["state"],
                seed_period=predecessor["period"],
                solver=solver,
                manifest=manifest,
                predecessor_states=predecessor["section_states"],
            )
            rows[(i, center_j)] = row
            if internal is None or not row["valid"]:
                break
            internals[(i, center_j)] = internal
            predecessor = internal

    for i in range(len(a_values)):
        spine = internals.get((i, center_j))
        if spine is None:
            continue
        for direction in (-1, 1):
            predecessor = spine
            for j in range(center_j + direction, -1 if direction < 0 else len(c_values), direction):
                row, internal = _evaluate_orbit(
                    a_values[i],
                    c_values[j],
                    b=b,
                    seed_state=predecessor["state"],
                    seed_period=predecessor["period"],
                    solver=solver,
                    manifest=manifest,
                    predecessor_states=predecessor["section_states"],
                )
                rows[(i, j)] = row
                if internal is None or not row["valid"]:
                    break
                internals[(i, j)] = internal
                predecessor = internal
        print(json.dumps({"a_index": i, "valid_cells": len(internals)}, sort_keys=True), flush=True)
    return a_values, c_values, rows, internals


def _multiplier_grid(a_values, c_values, rows) -> np.ndarray:
    values = np.full((len(a_values), len(c_values)), np.nan, dtype=float)
    for (i, j), row in rows.items():
        if row.get("valid"):
            values[i, j] = float(row["dominant_nontrivial_multiplier"]["real"])
    return values


def _serializable_grid(values) -> list[list[float | None]]:
    return [
        [float(value) if np.isfinite(value) else None for value in row]
        for row in np.asarray(values, dtype=float)
    ]


def _closest_internal(a: float, c: float, rows, internals):
    candidates = []
    for index, internal in internals.items():
        row = rows[index]
        parameters = row["parameters"]
        candidates.append(((parameters["a"] - a) ** 2 + (parameters["c"] - c) ** 2, internal))
    if not candidates:
        raise RuntimeError("no valid orbit is available for refinement")
    return min(candidates, key=lambda item: item[0])[1]


def _refine_candidate(candidate, factor, manifest, solver, reference_internal):
    grid = manifest["coarse_grid"]
    b = float(manifest["seed"]["parameters"]["b"])
    a_step = float(grid["a_step"]) * float(factor)
    c_step = float(grid["c_step"]) * float(factor)
    center_a = float(candidate["parameters"]["a"])
    center_c = float(candidate["parameters"]["c"])
    a_values = center_a + np.arange(-2, 3, dtype=float) * a_step
    c_values = center_c + np.arange(-2, 3, dtype=float) * c_step
    center_row, center_internal = _evaluate_orbit(
        center_a,
        center_c,
        b=b,
        seed_state=reference_internal["state"],
        seed_period=reference_internal["period"],
        solver=solver,
        manifest=manifest,
        predecessor_states=reference_internal["section_states"],
    )
    if center_internal is None or not center_row["valid"]:
        return {"factor": factor, "center": center_row, "rows": [], "candidates": []}, None, None
    rows = {}
    internals = {}
    for i, a in enumerate(a_values):
        for j, c in enumerate(c_values):
            if i == 2 and j == 2:
                row, internal = center_row, center_internal
            else:
                row, internal = _evaluate_orbit(
                    a,
                    c,
                    b=b,
                    seed_state=center_internal["state"],
                    seed_period=center_internal["period"],
                    solver=solver,
                    manifest=manifest,
                    predecessor_states=center_internal["section_states"],
                )
            rows[(i, j)] = row
            if internal is not None and row["valid"]:
                internals[(i, j)] = internal
    values = _multiplier_grid(a_values, c_values, rows)
    fit = manifest["saddle_fit"]
    candidates = quadratic_saddle_candidates(
        a_values,
        c_values,
        values,
        maximum_stationary_cell_offset=float(fit["maximum_stationary_cell_offset"]),
        minimum_ring_sign_alternations=int(fit["minimum_ring_sign_alternations"]),
        zero_tolerance=float(fit["ring_zero_tolerance"]),
    )
    output = {
        "factor": float(factor),
        "a_values": a_values.tolist(),
        "c_values": c_values.tolist(),
        "rows": [rows[index] for index in sorted(rows)],
        "multiplier_grid": _serializable_grid(values),
        "candidates": candidates,
    }
    if not candidates:
        return output, None, None
    selected = candidates[0]
    selected_internal = _closest_internal(
        selected["parameters"]["a"], selected["parameters"]["c"], rows, internals
    )
    return output, selected, selected_internal


def _validation(final_candidate, final_factor, manifest, dop_solver, radau_solver, seed_internal):
    b = float(manifest["seed"]["parameters"]["b"])
    base = manifest["coarse_grid"]
    a_step = float(base["a_step"]) * float(final_factor)
    c_step = float(base["c_step"]) * float(final_factor)
    center_a = float(final_candidate["parameters"]["a"])
    center_c = float(final_candidate["parameters"]["c"])
    offsets = ((0, 0), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1))
    rows = []
    solver_internals = {}
    for solver_name, solver in (("dop853", dop_solver), ("radau", radau_solver)):
        center_row, center_internal = _evaluate_orbit(
            center_a,
            center_c,
            b=b,
            seed_state=seed_internal["state"],
            seed_period=seed_internal["period"],
            solver=solver,
            manifest=manifest,
            predecessor_states=seed_internal["section_states"],
        )
        rows.append({"solver": solver_name, "offset": [0, 0], **center_row})
        if center_internal is None or not center_row["valid"]:
            solver_internals[solver_name] = {}
            continue
        solver_internals[solver_name] = {(0, 0): center_internal}
        for di, dj in offsets[1:]:
            row, internal = _evaluate_orbit(
                center_a + di * a_step,
                center_c + dj * c_step,
                b=b,
                seed_state=center_internal["state"],
                seed_period=center_internal["period"],
                solver=solver,
                manifest=manifest,
                predecessor_states=center_internal["section_states"],
            )
            rows.append({"solver": solver_name, "offset": [di, dj], **row})
            if internal is not None and row["valid"]:
                solver_internals[solver_name][(di, dj)] = internal

    pair_rows = []
    for offset in offsets:
        dop_row = next(row for row in rows if row["solver"] == "dop853" and tuple(row["offset"]) == offset)
        radau_row = next(row for row in rows if row["solver"] == "radau" and tuple(row["offset"]) == offset)
        if dop_row.get("valid") and radau_row.get("valid"):
            orbit_error = _phase_aligned_error(
                solver_internals["dop853"][offset]["section_states"],
                solver_internals["radau"][offset]["section_states"],
                manifest["continuation"]["coordinate_scales"],
            )
            multiplier_difference = abs(
                dop_row["dominant_nontrivial_multiplier"]["real"]
                - radau_row["dominant_nontrivial_multiplier"]["real"]
            )
        else:
            orbit_error = {"resolved": False, "shift": None, "maximum_scaled_error": None}
            multiplier_difference = None
        pair_rows.append(
            {
                "offset": list(offset),
                "orbit_parity": orbit_error,
                "signed_multiplier_difference": multiplier_difference,
            }
        )
    ring_offsets = offsets[1:]
    alternations = {}
    for solver_name in ("dop853", "radau"):
        ring = [
            next(row for row in rows if row["solver"] == solver_name and tuple(row["offset"]) == offset)
            for offset in ring_offsets
        ]
        if all(row.get("valid") for row in ring):
            values = [row["dominant_nontrivial_multiplier"]["real"] for row in ring]
            alternations[solver_name] = {
                "values": values,
                "count": ring_sign_alternations(
                    values, zero_tolerance=float(manifest["saddle_fit"]["ring_zero_tolerance"])
                ),
            }
        else:
            alternations[solver_name] = {"values": [], "count": 0}
    return {
        "center_parameters": {"a": center_a, "b": b, "c": center_c},
        "a_step": a_step,
        "c_step": c_step,
        "rows": rows,
        "solver_pairs": pair_rows,
        "ring_sign_alternations": alternations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Jones Floquet-center manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    for evidence in manifest["evidence"]:
        if sha256_file(Path(evidence["path"])) != evidence["sha256"]:
            raise SystemExit(f"evidence hash mismatch: {evidence['path']}")

    started = time.perf_counter()
    dop_solver = SolverConfig(**manifest["solvers"]["dop853"])
    radau_solver = SolverConfig(**manifest["solvers"]["radau"])
    a_values, c_values, grid_rows, grid_internals = _coarse_grid(manifest, dop_solver)
    multiplier_grid = _multiplier_grid(a_values, c_values, grid_rows)
    fit = manifest["saddle_fit"]
    coarse_candidates = quadratic_saddle_candidates(
        a_values,
        c_values,
        multiplier_grid,
        maximum_stationary_cell_offset=float(fit["maximum_stationary_cell_offset"]),
        minimum_ring_sign_alternations=int(fit["minimum_ring_sign_alternations"]),
        zero_tolerance=float(fit["ring_zero_tolerance"]),
    )
    selected = coarse_candidates[0] if coarse_candidates else None
    selected_internal = None
    if selected is not None:
        selected_internal = _closest_internal(
            selected["parameters"]["a"], selected["parameters"]["c"], grid_rows, grid_internals
        )

    refinement_rows = []
    final_factor = 1.0
    if selected is not None and selected_internal is not None:
        for factor in manifest["refinement_factors"]:
            refinement, next_selected, next_internal = _refine_candidate(
                selected, float(factor), manifest, dop_solver, selected_internal
            )
            refinement_rows.append(refinement)
            if next_selected is None or next_internal is None:
                selected = None
                selected_internal = None
                break
            selected = next_selected
            selected_internal = next_internal
            final_factor = float(factor)

    validation = None
    if selected is not None and selected_internal is not None:
        validation = _validation(
            selected, final_factor, manifest, dop_solver, radau_solver, selected_internal
        )

    acceptance = manifest["acceptance"]
    valid_fraction = len(grid_internals) / (len(a_values) * len(c_values))
    coarse_passed = bool(
        valid_fraction >= float(acceptance["minimum_coarse_valid_fraction"])
        and len(coarse_candidates) >= 1
    )
    refinement_passed = bool(
        selected is not None
        and len(refinement_rows) == len(manifest["refinement_factors"])
        and all(level["candidates"] for level in refinement_rows)
        and abs(selected["stationary_multiplier"])
        <= float(acceptance["maximum_fitted_stationary_multiplier"])
        and selected["fit_rms"] <= float(acceptance["maximum_final_fit_rms"])
    )
    if validation is None:
        validation_passed = False
    else:
        valid_rows = all(row.get("valid") for row in validation["rows"])
        center_rows = [row for row in validation["rows"] if row["offset"] == [0, 0]]
        center_small = bool(
            len(center_rows) == 2
            and all(
                abs(row["dominant_nontrivial_multiplier"]["real"])
                <= float(acceptance["maximum_validated_center_multiplier"])
                for row in center_rows
            )
        )
        pair_parity = all(
            row["orbit_parity"]["resolved"]
            and row["orbit_parity"]["maximum_scaled_error"]
            <= float(acceptance["maximum_solver_orbit_scaled_error"])
            and row["signed_multiplier_difference"] is not None
            and row["signed_multiplier_difference"]
            <= float(acceptance["maximum_solver_multiplier_difference"])
            for row in validation["solver_pairs"]
        )
        sign_topology = all(
            row["count"] >= int(fit["minimum_ring_sign_alternations"])
            for row in validation["ring_sign_alternations"].values()
        )
        validation_passed = bool(valid_rows and center_small and pair_parity and sign_topology)
    passed = bool(coarse_passed and refinement_passed and validation_passed)

    receipt = {
        "schema": "butterfly.jones-floquet-center-search.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "seed": manifest["seed"],
        "coarse_grid": {
            "a_values": a_values.tolist(),
            "c_values": c_values.tolist(),
            "rows": [grid_rows[index] for index in sorted(grid_rows)],
            "multiplier_grid": _serializable_grid(multiplier_grid),
            "valid_fraction": valid_fraction,
            "candidates": coarse_candidates,
        },
        "refinements": refinement_rows,
        "selected_candidate": selected,
        "validation": validation,
        "gates": {
            "coarse_passed": coarse_passed,
            "refinement_passed": refinement_passed,
            "validation_passed": validation_passed,
            "passed": passed,
        },
        "elapsed_seconds": time.perf_counter() - started,
        "claim_scope": manifest["claim_scope"],
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({"passed": passed, "selected_candidate": selected, "gates": receipt["gates"]}, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

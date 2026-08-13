#!/usr/bin/env python3
"""Test fixed-c normal-form opening and attraction of EXP-208 children."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

from butterfly import (
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    collect_crossings,
    correct_periodic_orbit,
    flow_monodromy,
    legacy_rossler_section,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.compare_periodic_orbit_identity import dense_orbit, phase_aligned_rms
from scripts.qualify_jones_period12_children import proper_subperiod_fractions


SCHEMA = "butterfly.jones-period12-normal-form-manifest.v1"


def fit_power_law(offsets, amplitudes):
    offsets = np.asarray(offsets, dtype=float)
    amplitudes = np.asarray(amplitudes, dtype=float)
    if offsets.shape != amplitudes.shape or offsets.size < 3:
        raise ValueError("power-law fit requires at least three paired values")
    if np.any(offsets <= 0.0) or np.any(amplitudes <= 0.0):
        raise ValueError("power-law inputs must be positive")
    x_values = np.log(offsets)
    y_values = np.log(amplitudes)
    slope, intercept = np.polyfit(x_values, y_values, 1)
    predicted = slope * x_values + intercept
    total = float(np.sum((y_values - np.mean(y_values)) ** 2))
    residual = float(np.sum((y_values - predicted) ** 2))
    r_squared = 1.0 - residual / total if total > 0.0 else 1.0
    return {
        "exponent": float(slope),
        "log_intercept": float(intercept),
        "r_squared": float(r_squared),
    }


def flip_multiplier_ratio(parent_multiplier, child_multiplier):
    parent = complex(parent_multiplier)
    child = complex(child_multiplier)
    denominator = -parent.real - 1.0
    if denominator <= 0.0:
        return float("nan")
    return float((1.0 - child.real) / denominator)


def _correct(parameters, state, period_time, solver, corrector):
    orbit = correct_periodic_orbit(
        parameters,
        state,
        period_time,
        config=solver,
        tolerance=float(corrector["tolerance"]),
        max_evaluations=int(corrector["maximum_evaluations"]),
    )
    if not orbit.success:
        raise RuntimeError(f"periodic correction failed: {orbit.message}")
    monodromy = flow_monodromy(
        parameters, orbit.initial_state, orbit.period_time, config=solver
    )
    return orbit, monodromy


def _dominant(monodromy):
    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    transverse = np.delete(monodromy.multipliers, neutral_index)
    return complex(transverse[int(np.argmax(np.abs(transverse)))])


def _summary(orbit, monodromy):
    dominant = _dominant(monodromy)
    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    return {
        "initial_state": orbit.initial_state.tolist(),
        "period_time": float(orbit.period_time),
        "closure_error": float(monodromy.closure_error),
        "phase_residual": float(orbit.phase_residual),
        "dominant_transverse_multiplier": {
            "real": float(dominant.real),
            "imag": float(dominant.imag),
            "modulus": float(abs(dominant)),
        },
        "neutral_multiplier_error": float(
            abs(monodromy.multipliers[neutral_index] - 1.0)
        ),
    }


def _section_count(parameters, orbit, section, expected, solver):
    crossings = collect_crossings(
        parameters,
        orbit.initial_state,
        section,
        transient=0.0,
        observation_horizon=orbit.period_time * (1.0 + 1e-7),
        max_crossings=int(expected) + 8,
        config=solver,
    )
    keep = (crossings.times > orbit.period_time * 1e-7) & (
        crossings.times <= orbit.period_time * (1.0 + 1e-7)
    )
    return {
        "count": int(np.count_nonzero(keep)),
        "integration_success": bool(crossings.integration_success),
    }


def _identity(left, right, left_dense, right_dense, comparison):
    return phase_aligned_rms(
        (left, left_dense),
        (right, right_dense),
        phase_samples=int(comparison["phase_samples"]),
        coarse_shifts=int(comparison["coarse_shifts"]),
        shift_tolerance=float(comparison["shift_tolerance"]),
    )


def _row_diagnostics(parameters, parent, child, solver, manifest):
    parent_dense = dense_orbit(parent[0], parameters, solver)
    child_dense = dense_orbit(child[0], parameters, solver)
    parent_double = SimpleNamespace(
        initial_state=parent[0].initial_state,
        period_time=2.0 * parent[0].period_time,
    )
    parent_double_dense = dense_orbit(parent_double, parameters, solver)
    opening = _identity(
        parent_double,
        child[0],
        parent_double_dense,
        child_dense,
        manifest["comparison"],
    )
    fractions = proper_subperiod_fractions(
        int(manifest["identity"]["historical_child_phase_count"])
    )
    proper_closures = [
        {
            "fraction": fraction,
            "closure": float(
                np.linalg.norm(
                    child_dense(fraction * child[0].period_time)
                    - child[0].initial_state
                )
            ),
        }
        for fraction in fractions
    ]
    section_counts = {
        "parent_historical": _section_count(
            parameters,
            parent[0],
            legacy_rossler_section(parameters),
            manifest["identity"]["historical_parent_phase_count"],
            solver,
        ),
        "parent_barrio": _section_count(
            parameters,
            parent[0],
            barrio_rossler_section(parameters),
            manifest["identity"]["barrio_parent_phase_count"],
            solver,
        ),
        "child_historical": _section_count(
            parameters,
            child[0],
            legacy_rossler_section(parameters),
            manifest["identity"]["historical_child_phase_count"],
            solver,
        ),
        "child_barrio": _section_count(
            parameters,
            child[0],
            barrio_rossler_section(parameters),
            manifest["identity"]["barrio_child_phase_count"],
            solver,
        ),
    }
    parent_summary = _summary(*parent)
    child_summary = _summary(*child)
    ratio = flip_multiplier_ratio(_dominant(parent[1]), _dominant(child[1]))
    return {
        "parent": parent_summary,
        "child": child_summary,
        "opening_identity": opening,
        "period_ratio": float(child[0].period_time / parent[0].period_time),
        "flip_multiplier_ratio": ratio,
        "proper_subperiod_closures": proper_closures,
        "minimum_proper_subperiod_closure": min(
            item["closure"] for item in proper_closures
        ),
        "section_counts": section_counts,
        "dense": {"parent": parent_dense, "child": child_dense},
    }


def _radau_check(parameters, reference, reference_diagnostics, solver, manifest):
    parent = _correct(
        parameters,
        reference[0][0].initial_state,
        reference[0][0].period_time,
        solver,
        manifest["corrector"],
    )
    child = _correct(
        parameters,
        reference[1][0].initial_state,
        reference[1][0].period_time,
        solver,
        manifest["corrector"],
    )
    dense = [dense_orbit(item[0], parameters, solver) for item in (parent, child)]
    identities = [
        _identity(
            reference[index][0],
            item[0],
            reference_diagnostics["dense"]["parent" if index == 0 else "child"],
            dense[index],
            manifest["comparison"],
        )
        for index, item in enumerate((parent, child))
    ]
    reference_summaries = [
        reference_diagnostics["parent"], reference_diagnostics["child"]
    ]
    independent_summaries = [_summary(*parent), _summary(*child)]
    return {
        "parent": independent_summaries[0],
        "child": independent_summaries[1],
        "solver_identities": {"parent": identities[0], "child": identities[1]},
        "multiplier_modulus_differences": {
            name: abs(
                reference_summaries[index]["dominant_transverse_multiplier"][
                    "modulus"
                ]
                - independent_summaries[index]["dominant_transverse_multiplier"][
                    "modulus"
                ]
            )
            for index, name in enumerate(("parent", "child"))
        },
        "period_relative_differences": {
            name: abs(reference[index][0].period_time - item[0].period_time)
            / item[0].period_time
            for index, (name, item) in enumerate(
                zip(("parent", "child"), (parent, child), strict=True)
            )
        },
    }


def _attraction_checks(parameters, child, child_dense, solver, manifest):
    attraction = manifest["attraction"]
    results = []
    phase_grid = np.linspace(0.0, 1.0, int(attraction["orbit_samples"]), endpoint=False)
    orbit_states = child_dense(phase_grid * child.period_time).T
    for perturbation_values in attraction["perturbations"]:
        perturbation = np.asarray(perturbation_values, dtype=float)
        integration = solve_ivp(
            lambda time_value, state: rossler_rhs(time_value, state, parameters),
            (0.0, float(attraction["transient_periods"]) * child.period_time),
            child.initial_state + perturbation,
            method=solver.method,
            rtol=solver.rtol,
            atol=solver.atol,
            max_step=float(attraction["max_step"]),
        )
        if not integration.success:
            raise RuntimeError(f"attraction integration failed: {integration.message}")
        terminal = integration.y[:, -1]
        coarse_distances = np.linalg.norm(orbit_states - terminal, axis=1)
        best_index = int(np.argmin(coarse_distances))
        spacing = 1.0 / len(phase_grid)
        best_phase = float(phase_grid[best_index])
        refined = minimize_scalar(
            lambda phase: float(
                np.linalg.norm(
                    child_dense((phase % 1.0) * child.period_time) - terminal
                )
            ),
            bounds=(best_phase - spacing, best_phase + spacing),
            method="bounded",
            options={"xatol": 1e-13},
        )
        terminal_distance = float(refined.fun)
        recovered = _correct(
            parameters,
            terminal,
            child.period_time,
            solver,
            manifest["corrector"],
        )
        recovered_dense = dense_orbit(recovered[0], parameters, solver)
        recovered_identity = _identity(
            child,
            recovered[0],
            child_dense,
            recovered_dense,
            manifest["comparison"],
        )
        results.append(
            {
                "perturbation": perturbation.tolist(),
                "integration_success": bool(integration.success),
                "terminal_orbit_distance": terminal_distance,
                "terminal_phase": float(refined.x % 1.0),
                "recovered": _summary(*recovered),
                "recovered_identity": recovered_identity,
            }
        )
    return results


def _qualify_target(target, event, manifest, solvers):
    reference_solver, independent_solver, attraction_solver = solvers
    c_value = float(target["c"])
    event_a = float(event["a"])
    target_a = float(target["a"])
    full_offset = target_a - event_a
    if full_offset <= 0.0:
        raise ValueError("child target must lie on the positive-a side of the event")
    parent_seed = (
        np.asarray(target["reference_dop853"]["parent"]["initial_state"], dtype=float),
        float(target["reference_dop853"]["parent"]["period_time"]),
    )
    child_seed = (
        np.asarray(target["reference_dop853"]["child"]["initial_state"], dtype=float),
        float(target["reference_dop853"]["child"]["period_time"]),
    )
    rows = []
    independent_fractions = {float(value) for value in manifest["independent_fractions"]}
    for fraction in sorted(
        (float(value) for value in manifest["offset_fractions"]), reverse=True
    ):
        a_value = event_a + fraction * full_offset
        parameters = RosslerParameters(a=a_value, b=float(manifest["fixed_b"]), c=c_value)
        parent = _correct(
            parameters, parent_seed[0], parent_seed[1], reference_solver, manifest["corrector"]
        )
        child = _correct(
            parameters, child_seed[0], child_seed[1], reference_solver, manifest["corrector"]
        )
        diagnostics = _row_diagnostics(
            parameters, parent, child, reference_solver, manifest
        )
        radau = None
        if fraction in independent_fractions:
            radau = _radau_check(
                parameters, (parent, child), diagnostics, independent_solver, manifest
            )
        rows.append(
            {
                "fraction": fraction,
                "a": a_value,
                "offset_a": a_value - event_a,
                **{key: value for key, value in diagnostics.items() if key != "dense"},
                "independent_radau": radau,
            }
        )
        parent_seed = (parent[0].initial_state, parent[0].period_time)
        child_seed = (child[0].initial_state, child[0].period_time)
    rows.sort(key=lambda row: row["fraction"])
    fit = fit_power_law(
        [row["offset_a"] for row in rows],
        [row["opening_identity"]["rms"] for row in rows],
    )
    full_row = rows[-1]
    full_parameters = RosslerParameters(
        a=full_row["a"], b=float(manifest["fixed_b"]), c=c_value
    )
    full_child = _correct(
        full_parameters,
        full_row["child"]["initial_state"],
        full_row["child"]["period_time"],
        reference_solver,
        manifest["corrector"],
    )
    full_child_dense = dense_orbit(full_child[0], full_parameters, reference_solver)
    attraction = _attraction_checks(
        full_parameters,
        full_child[0],
        full_child_dense,
        attraction_solver,
        manifest,
    )
    acceptance = manifest["acceptance"]
    identity = manifest["identity"]
    expected_counts = {
        "parent_historical": int(identity["historical_parent_phase_count"]),
        "parent_barrio": int(identity["barrio_parent_phase_count"]),
        "child_historical": int(identity["historical_child_phase_count"]),
        "child_barrio": int(identity["barrio_child_phase_count"]),
    }
    radau_rows = [row["independent_radau"] for row in rows if row["independent_radau"]]
    passed = bool(
        len(rows) == int(acceptance["required_branch_points"])
        and float(acceptance["minimum_opening_exponent"])
        <= fit["exponent"]
        <= float(acceptance["maximum_opening_exponent"])
        and fit["r_squared"] >= float(acceptance["minimum_opening_r_squared"])
        and all(
            row["parent"]["closure_error"] <= float(acceptance["maximum_closure_error"])
            and row["child"]["closure_error"] <= float(acceptance["maximum_closure_error"])
            and row["parent"]["dominant_transverse_multiplier"]["real"]
            <= -float(acceptance["minimum_parent_multiplier_modulus"])
            and row["child"]["dominant_transverse_multiplier"]["modulus"]
            <= float(acceptance["maximum_child_multiplier_modulus"])
            and abs(row["period_ratio"] - 2.0)
            <= float(acceptance["maximum_period_ratio_error"])
            and row["minimum_proper_subperiod_closure"]
            >= float(acceptance["minimum_proper_subperiod_closure"])
            and float(acceptance["minimum_multiplier_ratio"])
            <= row["flip_multiplier_ratio"]
            <= float(acceptance["maximum_multiplier_ratio"])
            and all(
                row["section_counts"][name]["count"] == expected
                and row["section_counts"][name]["integration_success"]
                for name, expected in expected_counts.items()
            )
            for row in rows
        )
        and float(acceptance["minimum_median_multiplier_ratio"])
        <= float(np.median([row["flip_multiplier_ratio"] for row in rows]))
        <= float(acceptance["maximum_median_multiplier_ratio"])
        and len(radau_rows) == len(independent_fractions)
        and all(
            max(item["rms"] for item in row["solver_identities"].values())
            <= float(acceptance["maximum_solver_identity_rms"])
            and max(row["multiplier_modulus_differences"].values())
            <= float(acceptance["maximum_solver_modulus_difference"])
            and max(row["period_relative_differences"].values())
            <= float(acceptance["maximum_solver_period_relative_difference"])
            for row in radau_rows
        )
        and all(
            row["terminal_orbit_distance"]
            <= float(acceptance["maximum_attraction_terminal_distance"])
            and row["recovered_identity"]["rms"]
            <= float(acceptance["maximum_recovered_identity_rms"])
            for row in attraction
        )
    )
    return {
        "c": c_value,
        "event_a": event_a,
        "target_a": target_a,
        "full_offset_a": full_offset,
        "rows": rows,
        "opening_power_law": fit,
        "median_flip_multiplier_ratio": float(
            np.median([row["flip_multiplier_ratio"] for row in rows])
        ),
        "attraction": attraction,
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event-receipt", type=Path, required=True)
    parser.add_argument("--child-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported period-12 normal-form manifest")
    event_bytes = args.event_receipt.read_bytes()
    child_bytes = args.child_receipt.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(child_bytes) != manifest["child_receipt_sha256"]:
        raise SystemExit("child receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("period-12 normal-form qualification requires clean source")
    event_receipt = json.loads(event_bytes)
    child_receipt = json.loads(child_bytes)
    if not event_receipt.get("passed") or not child_receipt.get("passed"):
        raise SystemExit("source experiment receipts must have passed")
    event_lookup = {float(row["c"]): row for row in event_receipt["rows"]}
    reference_solver = SolverConfig(**manifest["reference_solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    attraction_solver = SolverConfig(**manifest["attraction_solver"])
    started = time.perf_counter()
    targets = [
        _qualify_target(
            target,
            event_lookup[float(target["c"])],
            manifest,
            (reference_solver, independent_solver, attraction_solver),
        )
        for target in child_receipt["rows"]
    ]
    passed = bool(
        len(targets) == int(manifest["acceptance"]["required_targets"])
        and all(target["passed"] for target in targets)
    )
    output = {
        "schema": "butterfly.jones-period12-normal-form-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "child_receipt_sha256": sha256_bytes(child_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "targets": targets,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256_bytes(output_bytes),
                "passed": passed,
                "targets": [
                    {
                        "c": target["c"],
                        "passed": target["passed"],
                        "exponent": target["opening_power_law"]["exponent"],
                        "r_squared": target["opening_power_law"]["r_squared"],
                        "median_multiplier_ratio": target[
                            "median_flip_multiplier_ratio"
                        ],
                    }
                    for target in targets
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

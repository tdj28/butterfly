#!/usr/bin/env python3
"""Independently qualify three EXP-207 period-12 child nominations."""

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
try:
    from scripts.compare_periodic_orbit_identity import dense_orbit, phase_aligned_rms
except ModuleNotFoundError:  # Direct execution places scripts/ on sys.path.
    from compare_periodic_orbit_identity import dense_orbit, phase_aligned_rms


SCHEMA = "butterfly.jones-period12-child-qualification-manifest.v1"


def proper_subperiod_fractions(section_period: int) -> list[float]:
    """Return fractions for every proper divisor of a section period."""

    if section_period < 2:
        raise ValueError("section period must be at least two")
    divisors = [value for value in range(1, section_period) if section_period % value == 0]
    return [value / section_period for value in divisors]


def select_candidate(events: list[dict], target: dict) -> tuple[dict, dict]:
    """Select one manifest-declared event and row without fallback heuristics."""

    matching_events = [
        event for event in events if float(event["c"]) == float(target["c"])
    ]
    if len(matching_events) != 1:
        raise ValueError("target c does not select exactly one source event")
    event = matching_events[0]
    matching_branches = [
        branch
        for branch in event["branches"]
        if int(branch["direction"]) == int(target["source_direction"])
    ]
    if len(matching_branches) != 1:
        raise ValueError("target direction does not select exactly one source branch")
    matching_rows = [
        row
        for row in matching_branches[0]["rows"]
        if float(row["a"]) == float(target["candidate_a"])
    ]
    if len(matching_rows) != 1:
        raise ValueError("target a does not select exactly one source row")
    return event, matching_rows[0]


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


def _summary(orbit, monodromy):
    neutral_index = int(np.argmin(np.abs(monodromy.multipliers - 1.0)))
    transverse = np.delete(monodromy.multipliers, neutral_index)
    dominant = complex(transverse[int(np.argmax(np.abs(transverse)))])
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
    correction = SimpleNamespace(
        initial_state=orbit.initial_state, period_time=orbit.period_time
    )
    crossings = collect_crossings(
        parameters,
        correction.initial_state,
        section,
        transient=0.0,
        observation_horizon=correction.period_time * (1.0 + 1e-7),
        max_crossings=int(expected) + 8,
        config=solver,
    )
    keep = (crossings.times > correction.period_time * 1e-7) & (
        crossings.times <= correction.period_time * (1.0 + 1e-7)
    )
    return int(np.count_nonzero(keep)), bool(crossings.integration_success)


def _closure_at_fraction(parameters, orbit, fraction, solver):
    integration = solve_ivp(
        lambda time_value, state: rossler_rhs(time_value, state, parameters),
        (0.0, float(fraction) * orbit.period_time),
        orbit.initial_state,
        method=solver.method,
        rtol=solver.rtol,
        atol=solver.atol,
        max_step=solver.max_step,
    )
    if not integration.success:
        raise RuntimeError(f"subperiod integration failed: {integration.message}")
    return float(np.linalg.norm(integration.y[:, -1] - orbit.initial_state))


def _qualify_target(target, event, candidate, manifest, solvers):
    parameters = RosslerParameters(
        a=float(target["candidate_a"]),
        b=float(manifest["fixed_b"]),
        c=float(target["c"]),
    )
    reference_solver, independent_solver = solvers
    corrector = manifest["corrector"]
    parent_event_state = np.asarray(event["event_variables"][:3], dtype=float)
    parent_event_period = 0.5 * float(event["event_variables"][3])
    child_state = np.asarray(candidate["initial_state"], dtype=float)
    child_period = float(candidate["period_time"])

    reference_parent = _correct(
        parameters,
        parent_event_state,
        parent_event_period,
        reference_solver,
        corrector,
    )
    reference_child = _correct(
        parameters, child_state, child_period, reference_solver, corrector
    )
    independent_parent = _correct(
        parameters,
        reference_parent[0].initial_state,
        reference_parent[0].period_time,
        independent_solver,
        corrector,
    )
    independent_child = _correct(
        parameters,
        reference_child[0].initial_state,
        reference_child[0].period_time,
        independent_solver,
        corrector,
    )

    reference = [reference_parent, reference_child]
    independent = [independent_parent, independent_child]
    reference_dense = [
        dense_orbit(item[0], parameters, reference_solver) for item in reference
    ]
    independent_dense = [
        dense_orbit(item[0], parameters, independent_solver) for item in independent
    ]
    comparison = manifest["comparison"]
    solver_identities = [
        phase_aligned_rms(
            (reference[index][0], reference_dense[index]),
            (independent[index][0], independent_dense[index]),
            phase_samples=int(comparison["phase_samples"]),
            coarse_shifts=int(comparison["coarse_shifts"]),
            shift_tolerance=float(comparison["shift_tolerance"]),
        )
        for index in range(2)
    ]
    reference_summaries = [_summary(*item) for item in reference]
    independent_summaries = [_summary(*item) for item in independent]
    modulus_differences = [
        abs(
            reference_summaries[index]["dominant_transverse_multiplier"]["modulus"]
            - independent_summaries[index]["dominant_transverse_multiplier"][
                "modulus"
            ]
        )
        for index in range(2)
    ]
    period_relative_differences = [
        abs(reference[index][0].period_time - independent[index][0].period_time)
        / independent[index][0].period_time
        for index in range(2)
    ]
    fractions = proper_subperiod_fractions(
        int(manifest["identity"]["historical_child_phase_count"])
    )
    subperiod_closures = [
        {
            "fraction": fraction,
            "closure": _closure_at_fraction(
                parameters, independent_child[0], fraction, independent_solver
            ),
        }
        for fraction in fractions
    ]
    section_counts = {
        "parent_historical": _section_count(
            parameters,
            independent_parent[0],
            legacy_rossler_section(parameters),
            manifest["identity"]["historical_parent_phase_count"],
            independent_solver,
        ),
        "parent_barrio": _section_count(
            parameters,
            independent_parent[0],
            barrio_rossler_section(parameters),
            manifest["identity"]["barrio_parent_phase_count"],
            independent_solver,
        ),
        "child_historical": _section_count(
            parameters,
            independent_child[0],
            legacy_rossler_section(parameters),
            manifest["identity"]["historical_child_phase_count"],
            independent_solver,
        ),
        "child_barrio": _section_count(
            parameters,
            independent_child[0],
            barrio_rossler_section(parameters),
            manifest["identity"]["barrio_child_phase_count"],
            independent_solver,
        ),
    }
    period_ratio = independent_child[0].period_time / independent_parent[0].period_time
    acceptance = manifest["acceptance"]
    identity = manifest["identity"]
    expected_counts = {
        "parent_historical": int(identity["historical_parent_phase_count"]),
        "parent_barrio": int(identity["barrio_parent_phase_count"]),
        "child_historical": int(identity["historical_child_phase_count"]),
        "child_barrio": int(identity["barrio_child_phase_count"]),
    }
    all_summaries = reference_summaries + independent_summaries
    min_subperiod = min(row["closure"] for row in subperiod_closures)
    child_closure = independent_summaries[1]["closure_error"]
    passed = bool(
        max(row["closure_error"] for row in all_summaries)
        <= float(acceptance["maximum_closure_error"])
        and max(item["rms"] for item in solver_identities)
        <= float(acceptance["maximum_solver_identity_rms"])
        and max(modulus_differences)
        <= float(acceptance["maximum_solver_modulus_difference"])
        and max(period_relative_differences)
        <= float(acceptance["maximum_solver_period_relative_difference"])
        and independent_summaries[0]["dominant_transverse_multiplier"]["modulus"]
        >= float(acceptance["minimum_parent_multiplier_modulus"])
        and independent_summaries[1]["dominant_transverse_multiplier"]["modulus"]
        <= float(acceptance["maximum_child_multiplier_modulus"])
        and abs(period_ratio - 2.0)
        <= float(acceptance["maximum_period_ratio_error"])
        and min_subperiod >= float(acceptance["minimum_proper_subperiod_closure"])
        and min_subperiod / max(child_closure, np.finfo(float).tiny)
        >= float(acceptance["minimum_subperiod_to_full_closure_ratio"])
        and all(
            section_counts[name][0] == expected
            and section_counts[name][1]
            for name, expected in expected_counts.items()
        )
    )
    return {
        "c": parameters.c,
        "a": parameters.a,
        "source_direction": int(target["source_direction"]),
        "reference_dop853": {
            "parent": reference_summaries[0],
            "child": reference_summaries[1],
        },
        "independent_radau": {
            "parent": independent_summaries[0],
            "child": independent_summaries[1],
        },
        "solver_identities": {
            "parent": solver_identities[0],
            "child": solver_identities[1],
        },
        "solver_modulus_differences": {
            "parent": modulus_differences[0],
            "child": modulus_differences[1],
        },
        "solver_period_relative_differences": {
            "parent": period_relative_differences[0],
            "child": period_relative_differences[1],
        },
        "child_to_parent_period_ratio": float(period_ratio),
        "proper_subperiod_closures": subperiod_closures,
        "minimum_proper_subperiod_closure": float(min_subperiod),
        "minimum_subperiod_to_full_closure_ratio": float(
            min_subperiod / max(child_closure, np.finfo(float).tiny)
        ),
        "section_counts": {
            name: {"count": value[0], "integration_success": value[1]}
            for name, value in section_counts.items()
        },
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event-receipt", type=Path, required=True)
    parser.add_argument("--candidate-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported period-12 qualification manifest")
    event_bytes = args.event_receipt.read_bytes()
    candidate_bytes = args.candidate_receipt.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(candidate_bytes) != manifest["candidate_receipt_sha256"]:
        raise SystemExit("candidate receipt hash mismatch")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("period-12 qualification requires clean source")
    event_receipt = json.loads(event_bytes)
    candidate_receipt = json.loads(candidate_bytes)
    if not event_receipt.get("passed"):
        raise SystemExit("EXP-206 event receipt must have passed")
    reference_solver = SolverConfig(**manifest["reference_solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    selected = [
        (*select_candidate(candidate_receipt["events"], target), target)
        for target in manifest["targets"]
    ]
    started = time.perf_counter()
    rows = [
        _qualify_target(
            target,
            event,
            candidate,
            manifest,
            (reference_solver, independent_solver),
        )
        for event, candidate, target in selected
    ]
    passed = bool(
        len(rows) == int(manifest["acceptance"]["required_targets"])
        and all(row["passed"] for row in rows)
    )
    output = {
        "schema": "butterfly.jones-period12-child-qualification-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "candidate_receipt_sha256": sha256_bytes(candidate_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "rows": rows,
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
                        "c": row["c"],
                        "a": row["a"],
                        "passed": row["passed"],
                        "period_ratio": row["child_to_parent_period_ratio"],
                        "minimum_subperiod_closure": row[
                            "minimum_proper_subperiod_closure"
                        ],
                    }
                    for row in rows
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

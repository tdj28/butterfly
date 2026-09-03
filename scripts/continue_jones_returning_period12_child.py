#!/usr/bin/env python3
"""Continue one qualified period-12 child along the returning flip arm."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    correct_periodic_orbit,
    flow_monodromy,
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.qualify_jones_period12_children import (
    _closure_at_fraction,
    _qualify_target,
    _section_count,
    _summary,
    proper_subperiod_fractions,
)


SCHEMA = "butterfly.jones-returning-period12-child-continuation-manifest.v1"


def select_seed(receipt, selector):
    """Select one prospectively declared qualified candidate without fallback."""

    events = [
        event for event in receipt["events"] if float(event["c"]) == float(selector["c"])
    ]
    if len(events) != 1:
        raise ValueError("seed c does not select exactly one event")
    candidates = [
        candidate
        for candidate in events[0]["candidates"]
        if float(candidate["step_length"]) == float(selector["step_length"])
        and int(candidate["source_direction"]) == int(selector["source_direction"])
        and float(candidate["candidate_a"]) == float(selector["candidate_a"])
    ]
    if len(candidates) != 1 or not candidates[0]["passed"]:
        raise ValueError("seed selector does not identify one passed child")
    return events[0], candidates[0]


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


def _continue_row(event, child_seed, delta_a, manifest, solver):
    parameters = RosslerParameters(
        a=float(event["a"]) + float(delta_a),
        b=float(manifest["fixed_b"]),
        c=float(event["c"]),
    )
    parent = _correct(
        parameters,
        event["initial_state"],
        event["period_time"],
        solver,
        manifest["corrector"],
    )
    child = _correct(
        parameters,
        child_seed["initial_state"],
        child_seed["period_time"],
        solver,
        manifest["corrector"],
    )
    parent_summary = _summary(*parent)
    child_summary = _summary(*child)
    identity = manifest["identity"]
    section_counts = {
        "parent_historical": _section_count(
            parameters,
            parent[0],
            legacy_rossler_section(parameters),
            int(identity["historical_parent_phase_count"]),
            solver,
        ),
        "parent_barrio": _section_count(
            parameters,
            parent[0],
            barrio_rossler_section(parameters),
            int(identity["barrio_parent_phase_count"]),
            solver,
        ),
        "child_historical": _section_count(
            parameters,
            child[0],
            legacy_rossler_section(parameters),
            int(identity["historical_child_phase_count"]),
            solver,
        ),
        "child_barrio": _section_count(
            parameters,
            child[0],
            barrio_rossler_section(parameters),
            int(identity["barrio_child_phase_count"]),
            solver,
        ),
    }
    fractions = proper_subperiod_fractions(int(identity["historical_child_phase_count"]))
    subperiod_closures = [
        {
            "fraction": fraction,
            "closure": _closure_at_fraction(parameters, child[0], fraction, solver),
        }
        for fraction in fractions
    ]
    period_ratio = child[0].period_time / parent[0].period_time
    minimum_subperiod = min(row["closure"] for row in subperiod_closures)
    acceptance = manifest["acceptance"]
    expected_counts = {
        "parent_historical": int(identity["historical_parent_phase_count"]),
        "parent_barrio": int(identity["barrio_parent_phase_count"]),
        "child_historical": int(identity["historical_child_phase_count"]),
        "child_barrio": int(identity["barrio_child_phase_count"]),
    }
    checks = {
        "closure": max(parent_summary["closure_error"], child_summary["closure_error"])
        <= float(acceptance["maximum_closure_error"]),
        "parent_unstable": parent_summary["dominant_transverse_multiplier"]["modulus"]
        >= float(acceptance["minimum_parent_multiplier_modulus"]),
        "child_stable": child_summary["dominant_transverse_multiplier"]["modulus"]
        <= float(acceptance["maximum_child_multiplier_modulus"]),
        "period_ratio": abs(period_ratio - 2.0)
        <= float(acceptance["maximum_period_ratio_error"]),
        "proper_subperiod": minimum_subperiod
        >= float(acceptance["minimum_proper_subperiod_closure"]),
        "section_identity": all(
            section_counts[name][0] == expected
            and section_counts[name][1]
            for name, expected in expected_counts.items()
        ),
    }
    return {
        "a": parameters.a,
        "b": parameters.b,
        "c": parameters.c,
        "event_a": float(event["a"]),
        "delta_a": float(delta_a),
        "parent": parent_summary,
        "child": child_summary,
        "period_ratio": float(period_ratio),
        "proper_subperiod_closures": subperiod_closures,
        "minimum_proper_subperiod_closure": float(minimum_subperiod),
        "section_counts": {
            name: {"count": value[0], "integration_success": value[1]}
            for name, value in section_counts.items()
        },
        "checks": checks,
        "passed": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event-receipt", type=Path, required=True)
    parser.add_argument("--seed-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported returning-child continuation manifest")
    event_bytes = args.event_receipt.read_bytes()
    seed_bytes = args.seed_receipt.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(seed_bytes) != manifest["seed_receipt_sha256"]:
        raise SystemExit("seed receipt hash mismatch")
    events_receipt = json.loads(event_bytes)
    seed_receipt = json.loads(seed_bytes)
    if not events_receipt.get("passed"):
        raise SystemExit("returning event arm must have passed")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("returning-child continuation requires clean source")
    seed_event, seed_candidate = select_seed(seed_receipt, manifest["seed_selector"])
    seed_child = seed_candidate["qualified"]["independent_radau"]["child"]
    delta_a = float(seed_candidate["candidate_a"]) - float(seed_event["event_a"])
    target = manifest["target"]
    selected_events = [
        row
        for row in events_receipt["rows"]
        if float(target["minimum_c"]) <= float(row["c"]) <= float(target["maximum_c"])
    ]
    selected_events.sort(key=lambda row: float(row["c"]))
    if len(selected_events) != int(target["required_event_count"]):
        raise SystemExit("target range does not select the frozen event count")
    solver = SolverConfig(**manifest["solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    rows = []
    failure = None
    current_child = seed_child
    started = time.perf_counter()
    for index, event in enumerate(selected_events):
        try:
            row = _continue_row(event, current_child, delta_a, manifest, solver)
        except Exception as error:
            failure = {
                "index": index,
                "c": float(event["c"]),
                "error": f"{type(error).__name__}: {error}",
            }
            break
        if not row["passed"]:
            failure = {
                "index": index,
                "c": float(event["c"]),
                "error": "continued row failed identity or stability checks",
                "checks": row["checks"],
            }
            break
        rows.append(row)
        current_child = row["child"]
    independent_controls = []
    if rows:
        for index in manifest["independent_control_indices"]:
            if int(index) >= len(rows):
                continue
            event = selected_events[int(index)]
            row = rows[int(index)]
            qualified = _qualify_target(
                {
                    "c": row["c"],
                    "candidate_a": row["a"],
                    "source_direction": -1,
                },
                {
                    "c": row["c"],
                    "event_a": event["a"],
                    "event_variables": [
                        *event["initial_state"],
                        2.0 * float(event["period_time"]),
                        float(event["a"]),
                    ],
                },
                {
                    "initial_state": row["child"]["initial_state"],
                    "period_time": row["child"]["period_time"],
                },
                manifest,
                (solver, independent_solver),
            )
            independent_controls.append({"index": int(index), **qualified})
    adjacent_state = [
        float(
            np.linalg.norm(
                np.asarray(right["child"]["initial_state"])
                - np.asarray(left["child"]["initial_state"])
            )
        )
        for left, right in zip(rows[:-1], rows[1:], strict=True)
    ]
    acceptance = manifest["acceptance"]
    passed = bool(
        len(rows) == int(target["required_event_count"])
        and failure is None
        and max(adjacent_state, default=0.0)
        <= float(acceptance["maximum_adjacent_child_state_distance"])
        and len(independent_controls) == len(manifest["independent_control_indices"])
        and all(control["passed"] for control in independent_controls)
    )
    output = {
        "schema": "butterfly.jones-returning-period12-child-continuation-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "seed_receipt_sha256": sha256_bytes(seed_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "delta_a": delta_a,
        "target_event_count": len(selected_events),
        "rows": rows,
        "failure": failure,
        "maximum_adjacent_child_state_distance": max(adjacent_state, default=0.0),
        "independent_controls": independent_controls,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(json.dumps({
        "output": str(args.output),
        "sha256": sha256_bytes(output_bytes),
        "passed": passed,
        "point_count": len(rows),
        "target_event_count": len(selected_events),
        "c_range": [rows[0]["c"], rows[-1]["c"]] if rows else [None, None],
        "failure": failure,
    }, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

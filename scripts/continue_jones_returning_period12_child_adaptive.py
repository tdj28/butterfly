#!/usr/bin/env python3
"""Adaptively continue the returning-arm period-12 child to the middle slice."""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from butterfly import SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from scripts.bridge_jones_returning_period12_child import interpolate_event
from scripts.continue_jones_returning_period12_child import _continue_row, select_seed
from scripts.qualify_jones_period12_children import _qualify_target


SCHEMA = "butterfly.jones-returning-period12-child-adaptive-manifest.v1"


def step_is_acceptable(row, child_state_distance, maximum_distance):
    """Require both the scientific gates and local branch coherence."""

    return bool(
        row.get("passed")
        and np.isfinite(child_state_distance)
        and float(child_state_distance) <= float(maximum_distance)
    )


def _attempt_summary(
    *,
    attempt_index,
    interval_index,
    depth,
    fraction,
    event,
    row=None,
    child_state_distance=None,
    accepted=False,
    error=None,
):
    """Keep rejected trials auditable without duplicating full orbit payloads."""

    result = {
        "attempt_index": int(attempt_index),
        "interval_index": int(interval_index),
        "depth": int(depth),
        "interval_fraction": float(fraction),
        "a": float(event["a"]),
        "c": float(event["c"]),
        "nonlinear_converged": row is not None,
        "child_state_distance": (
            None if child_state_distance is None else float(child_state_distance)
        ),
        "accepted": bool(accepted),
        "error": error,
    }
    if row is not None:
        result.update(
            {
                "corrected_a": float(row["a"]),
                "checks": row["checks"],
                "period_ratio": float(row["period_ratio"]),
                "parent_multiplier_modulus": float(
                    row["parent"]["dominant_transverse_multiplier"]["modulus"]
                ),
                "child_multiplier_modulus": float(
                    row["child"]["dominant_transverse_multiplier"]["modulus"]
                ),
                "section_counts": row["section_counts"],
            }
        )
    return result


def _annotate_row(row, interval_index, depth, fraction, exact_event_index):
    row["source_interval_index"] = int(interval_index)
    row["bisection_depth"] = int(depth)
    row["interval_fraction"] = float(fraction)
    row["exact_event_index"] = (
        None if exact_event_index is None else int(exact_event_index)
    )
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event-receipt", type=Path, required=True)
    parser.add_argument("--seed-receipt", type=Path, required=True)
    parser.add_argument("--bridge-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported adaptive returning-child manifest")
    input_paths = {
        "event": args.event_receipt,
        "seed": args.seed_receipt,
        "bridge": args.bridge_receipt,
    }
    input_bytes = {name: path.read_bytes() for name, path in input_paths.items()}
    for name, data in input_bytes.items():
        if sha256_bytes(data) != manifest[f"{name}_receipt_sha256"]:
            raise SystemExit(f"{name} receipt hash mismatch")
    event_receipt = json.loads(input_bytes["event"])
    seed_receipt = json.loads(input_bytes["seed"])
    bridge_receipt = json.loads(input_bytes["bridge"])
    if not event_receipt.get("passed") or not bridge_receipt.get("passed"):
        raise SystemExit("adaptive continuation requires passed arm and bridge receipts")

    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("adaptive returning-child continuation requires clean source")

    seed_event, seed_candidate = select_seed(seed_receipt, manifest["seed_selector"])
    seed_child = seed_candidate["qualified"]["independent_radau"]["child"]
    delta_a = float(seed_candidate["candidate_a"]) - float(seed_event["event_a"])
    target = manifest["target"]
    selected_events = [
        row
        for row in event_receipt["rows"]
        if float(target["minimum_c"]) <= float(row["c"]) <= float(target["maximum_c"])
    ]
    selected_events.sort(key=lambda row: float(row["c"]))
    if len(selected_events) != int(target["required_event_count"]):
        raise SystemExit("target range does not select the frozen event count")

    solver = SolverConfig(**manifest["solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    maximum_distance = float(
        manifest["acceptance"]["maximum_adjacent_child_state_distance"]
    )
    maximum_depth = int(manifest["adaptive"]["maximum_bisection_depth"])
    rows = []
    attempts = []
    failure = None
    bridged_intervals = 0
    started = time.perf_counter()

    def attempt(event, child, interval_index, depth, fraction, exact_event_index):
        nonlocal attempts
        try:
            row = _continue_row(event, child, delta_a, manifest, solver)
            distance = float(
                np.linalg.norm(
                    np.asarray(row["child"]["initial_state"], dtype=float)
                    - np.asarray(child["initial_state"], dtype=float)
                )
            )
            accepted = step_is_acceptable(row, distance, maximum_distance)
            attempts.append(
                _attempt_summary(
                    attempt_index=len(attempts),
                    interval_index=interval_index,
                    depth=depth,
                    fraction=fraction,
                    event=event,
                    row=row,
                    child_state_distance=distance,
                    accepted=accepted,
                )
            )
            if not accepted:
                return None
            return _annotate_row(
                row, interval_index, depth, fraction, exact_event_index
            )
        except Exception as error:
            attempts.append(
                _attempt_summary(
                    attempt_index=len(attempts),
                    interval_index=interval_index,
                    depth=depth,
                    fraction=fraction,
                    event=event,
                    error=f"{type(error).__name__}: {error}",
                )
            )
            return None

    def bridge_interval(
        left_event,
        right_event,
        child,
        interval_index,
        left_fraction,
        right_fraction,
        depth,
    ):
        exact_event_index = interval_index + 1 if right_fraction == 1.0 else None
        accepted = attempt(
            right_event,
            child,
            interval_index,
            depth,
            right_fraction,
            exact_event_index,
        )
        if accepted is not None:
            return [accepted], accepted["child"], None
        if depth >= maximum_depth:
            return [], child, {
                "interval_index": int(interval_index),
                "left_fraction": float(left_fraction),
                "right_fraction": float(right_fraction),
                "depth": int(depth),
                "c_range": [float(left_event["c"]), float(right_event["c"])],
                "error": "maximum bisection depth exhausted without an acceptable step",
            }
        middle_fraction = 0.5 * (left_fraction + right_fraction)
        local_fraction = (middle_fraction - left_fraction) / (
            right_fraction - left_fraction
        )
        middle_event = interpolate_event(left_event, right_event, local_fraction)
        left_rows, middle_child, left_failure = bridge_interval(
            left_event,
            middle_event,
            child,
            interval_index,
            left_fraction,
            middle_fraction,
            depth + 1,
        )
        if left_failure is not None:
            return left_rows, middle_child, left_failure
        right_rows, final_child, right_failure = bridge_interval(
            middle_event,
            right_event,
            middle_child,
            interval_index,
            middle_fraction,
            right_fraction,
            depth + 1,
        )
        return left_rows + right_rows, final_child, right_failure

    current_child = seed_child
    start = attempt(selected_events[0], current_child, -1, 0, 0.0, 0)
    if start is None:
        failure = {
            "interval_index": -1,
            "c": float(selected_events[0]["c"]),
            "error": "starting child failed frozen gates or coherence bound",
        }
    else:
        rows.append(start)
        current_child = start["child"]
        for interval_index, (left_event, right_event) in enumerate(
            zip(selected_events[:-1], selected_events[1:], strict=True)
        ):
            interval_rows, current_child, interval_failure = bridge_interval(
                left_event,
                right_event,
                current_child,
                interval_index,
                0.0,
                1.0,
                0,
            )
            rows.extend(interval_rows)
            if interval_failure is not None:
                failure = interval_failure
                break
            bridged_intervals += 1

    exact_rows = {
        int(row["exact_event_index"]): row
        for row in rows
        if row["exact_event_index"] is not None
    }
    independent_controls = []
    for event_index in manifest["independent_control_event_indices"]:
        event_index = int(event_index)
        if event_index not in exact_rows:
            continue
        event = selected_events[event_index]
        row = exact_rows[event_index]
        try:
            qualified = _qualify_target(
                {
                    "c": row["c"],
                    "candidate_a": row["a"],
                    "source_direction": int(
                        manifest["seed_selector"]["source_direction"]
                    ),
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
            independent_controls.append(
                {"event_index": event_index, **qualified}
            )
        except Exception as error:
            independent_controls.append(
                {
                    "event_index": event_index,
                    "c": float(event["c"]),
                    "passed": False,
                    "error": f"{type(error).__name__}: {error}",
                }
            )

    adjacent_state = [
        float(
            np.linalg.norm(
                np.asarray(right["child"]["initial_state"], dtype=float)
                - np.asarray(left["child"]["initial_state"], dtype=float)
            )
        )
        for left, right in zip(rows[:-1], rows[1:], strict=True)
    ]
    exact_event_count = len(exact_rows)
    passed = bool(
        failure is None
        and bridged_intervals == len(selected_events) - 1
        and exact_event_count == len(selected_events)
        and max(adjacent_state, default=0.0) <= maximum_distance
        and len(independent_controls)
        == len(manifest["independent_control_event_indices"])
        and all(control["passed"] for control in independent_controls)
    )
    output = {
        "schema": "butterfly.jones-returning-period12-child-adaptive-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        **{
            f"{name}_receipt_sha256": sha256_bytes(data)
            for name, data in input_bytes.items()
        },
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "delta_a": delta_a,
        "target_event_count": len(selected_events),
        "exact_event_count": exact_event_count,
        "bridged_interval_count": bridged_intervals,
        "accepted_rows": rows,
        "attempts": attempts,
        "failure": failure,
        "maximum_adjacent_child_state_distance": max(adjacent_state, default=0.0),
        "maximum_bisection_depth_used": max(
            (int(row["bisection_depth"]) for row in rows), default=0
        ),
        "independent_controls": independent_controls,
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
                "accepted_point_count": len(rows),
                "attempt_count": len(attempts),
                "exact_event_count": exact_event_count,
                "bridged_interval_count": bridged_intervals,
                "c_range": [rows[0]["c"], rows[-1]["c"]] if rows else [None, None],
                "maximum_bisection_depth_used": output[
                    "maximum_bisection_depth_used"
                ],
                "failure": failure,
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

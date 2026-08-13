#!/usr/bin/env python3
"""Resume the returning child using exact source-arm correction at every step."""

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
from scripts.continue_jones_period6_flip_curve import _solve_event
from scripts.continue_jones_returning_period12_child import _continue_row
from scripts.continue_jones_returning_period12_child_adaptive import (
    _annotate_row,
    step_is_acceptable,
)
from scripts.qualify_jones_period12_children import _qualify_target


SCHEMA = "butterfly.jones-returning-period12-child-exact-arm-manifest.v1"


def event_manifest(manifest):
    """Expose only the fixed-c augmented-event configuration."""

    return {
        "fixed_b": manifest["fixed_b"],
        "a_guard": manifest["event_correction"]["a_guard"],
        "corrector": manifest["event_correction"]["corrector"],
        "acceptance": manifest["event_correction"]["acceptance"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event-receipt", type=Path, required=True)
    parser.add_argument("--adaptive-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported exact-arm returning-child manifest")
    event_bytes = args.event_receipt.read_bytes()
    adaptive_bytes = args.adaptive_receipt.read_bytes()
    if sha256_bytes(event_bytes) != manifest["event_receipt_sha256"]:
        raise SystemExit("event receipt hash mismatch")
    if sha256_bytes(adaptive_bytes) != manifest["adaptive_receipt_sha256"]:
        raise SystemExit("adaptive receipt hash mismatch")
    arm = json.loads(event_bytes)
    adaptive = json.loads(adaptive_bytes)
    if not arm.get("passed"):
        raise SystemExit("exact-arm continuation requires a passed event arm")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("exact-arm returning-child continuation requires clean source")

    target = manifest["target"]
    source_events = [
        row
        for row in arm["rows"]
        if float(target["minimum_c"]) <= float(row["c"]) <= float(target["maximum_c"])
    ]
    source_events.sort(key=lambda row: float(row["c"]))
    if len(source_events) != int(target["source_event_count"]):
        raise SystemExit("source range does not select the frozen event count")
    seed_index = int(target["seed_exact_event_index"])
    terminal_index = int(target["terminal_exact_event_index"])
    if not 0 <= seed_index < terminal_index < len(source_events):
        raise SystemExit("invalid frozen source-event indices")
    seed_rows = [
        row
        for row in adaptive["accepted_rows"]
        if row.get("exact_event_index") == seed_index
    ]
    if len(seed_rows) != 1 or not seed_rows[0].get("passed"):
        raise SystemExit("adaptive receipt does not provide the frozen passed seed")
    seed_row = seed_rows[0]
    delta_a = float(adaptive["delta_a"])
    if abs(delta_a - float(manifest["expected_delta_a"])) > 1e-15:
        raise SystemExit("adaptive offset does not match the frozen value")

    solver = SolverConfig(**manifest["solver"])
    event_solver = SolverConfig(**manifest["event_solver"])
    independent_solver = SolverConfig(**manifest["independent_solver"])
    event_configuration = event_manifest(manifest)
    maximum_distance = float(
        manifest["acceptance"]["maximum_adjacent_child_state_distance"]
    )
    maximum_depth = int(manifest["adaptive"]["maximum_bisection_depth"])
    rows = []
    attempts = []
    exact_event_cache = {}
    failure = None
    bridged_intervals = 0
    started = time.perf_counter()

    def exact_event(seed):
        c_value = float(seed["c"])
        if c_value not in exact_event_cache:
            corrected = _solve_event(
                c_value, seed, event_configuration, event_solver
            )
            if not corrected["passed"]:
                raise RuntimeError("fresh source event failed exact gates")
            corrected["seed_a"] = float(seed["a"])
            corrected["seed_a_error"] = float(seed["a"]) - float(corrected["a"])
            exact_event_cache[c_value] = corrected
        return exact_event_cache[c_value]

    def attempt(seed_event, child, interval_index, depth, fraction, exact_index):
        attempt_index = len(attempts)
        try:
            event = exact_event(seed_event)
            row = _continue_row(event, child, delta_a, manifest, solver)
            distance = float(
                np.linalg.norm(
                    np.asarray(row["child"]["initial_state"], dtype=float)
                    - np.asarray(child["initial_state"], dtype=float)
                )
            )
            accepted = step_is_acceptable(row, distance, maximum_distance)
            attempts.append(
                {
                    "attempt_index": attempt_index,
                    "interval_index": int(interval_index),
                    "depth": int(depth),
                    "interval_fraction": float(fraction),
                    "c": float(event["c"]),
                    "exact_event_a": float(event["a"]),
                    "event_seed_a_error": float(event["seed_a_error"]),
                    "path_a": float(row["a"]),
                    "child_state_distance": distance,
                    "period_ratio": float(row["period_ratio"]),
                    "parent_multiplier_modulus": float(
                        row["parent"]["dominant_transverse_multiplier"]["modulus"]
                    ),
                    "child_multiplier_modulus": float(
                        row["child"]["dominant_transverse_multiplier"]["modulus"]
                    ),
                    "checks": row["checks"],
                    "accepted": accepted,
                    "error": None,
                }
            )
            if not accepted:
                return None
            return _annotate_row(
                row, interval_index, depth, fraction, exact_index
            )
        except Exception as error:
            attempts.append(
                {
                    "attempt_index": attempt_index,
                    "interval_index": int(interval_index),
                    "depth": int(depth),
                    "interval_fraction": float(fraction),
                    "c": float(seed_event["c"]),
                    "accepted": False,
                    "error": f"{type(error).__name__}: {error}",
                }
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
        right_index = interval_index + 1 if right_fraction == 1.0 else None
        accepted = attempt(
            right_event,
            child,
            interval_index,
            depth,
            right_fraction,
            right_index,
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
                "error": "maximum bisection depth exhausted without an acceptable exact-arm step",
            }
        middle_fraction = 0.5 * (left_fraction + right_fraction)
        local_fraction = (middle_fraction - left_fraction) / (
            right_fraction - left_fraction
        )
        interpolated_seed = interpolate_event(
            left_event, right_event, local_fraction
        )
        middle_event = exact_event(interpolated_seed)
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

    current_child = seed_row["child"]
    first_source = source_events[seed_index]
    start = attempt(first_source, current_child, seed_index - 1, 0, 0.0, seed_index)
    if start is None:
        failure = {
            "interval_index": seed_index - 1,
            "c": float(first_source["c"]),
            "error": "starting child failed exact-arm gates or coherence bound",
        }
    else:
        rows.append(start)
        current_child = start["child"]
        for interval_index in range(seed_index, terminal_index):
            left_event = exact_event(source_events[interval_index])
            right_seed = source_events[interval_index + 1]
            interval_rows, current_child, interval_failure = bridge_interval(
                left_event,
                right_seed,
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
        event = exact_event(source_events[event_index])
        row = exact_rows[event_index]
        try:
            qualified = _qualify_target(
                {
                    "c": row["c"],
                    "candidate_a": row["a"],
                    "source_direction": int(manifest["source_direction"]),
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
            independent_controls.append({"event_index": event_index, **qualified})
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
    required_exact_count = terminal_index - seed_index + 1
    passed = bool(
        failure is None
        and bridged_intervals == terminal_index - seed_index
        and len(exact_rows) == required_exact_count
        and max(adjacent_state, default=0.0) <= maximum_distance
        and len(independent_controls)
        == len(manifest["independent_control_event_indices"])
        and all(control["passed"] for control in independent_controls)
    )
    interpolation_errors = [
        abs(float(event["seed_a_error"])) for event in exact_event_cache.values()
    ]
    output = {
        "schema": "butterfly.jones-returning-period12-child-exact-arm-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "adaptive_receipt_sha256": sha256_bytes(adaptive_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "delta_a": delta_a,
        "seed_exact_event_index": seed_index,
        "terminal_exact_event_index": terminal_index,
        "required_exact_event_count": required_exact_count,
        "exact_event_count": len(exact_rows),
        "bridged_interval_count": bridged_intervals,
        "fresh_event_correction_count": len(exact_event_cache),
        "maximum_event_seed_a_error": max(interpolation_errors, default=0.0),
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
                "fresh_event_correction_count": len(exact_event_cache),
                "exact_event_count": len(exact_rows),
                "bridged_interval_count": bridged_intervals,
                "c_range": [rows[0]["c"], rows[-1]["c"]] if rows else [None, None],
                "maximum_event_seed_a_error": output["maximum_event_seed_a_error"],
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

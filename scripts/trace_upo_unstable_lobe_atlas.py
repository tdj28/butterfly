#!/usr/bin/env python3
"""Trace capture-truncated unstable-manifold lobes from validated UPO seeds."""

from __future__ import annotations

import argparse
import json
import platform
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    collect_crossings,
    next_section_return,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _stable_cycle(parameters, manifest, solver):
    config = manifest["stable_cycle"]
    section = barrio_rossler_section(parameters)
    crossings = collect_crossings(
        parameters,
        config["initial_state"],
        section,
        transient=float(config["transient_time"]),
        observation_horizon=float(config["observation_horizon"]),
        max_crossings=int(config["crossing_count"]),
        config=solver,
    )
    period = int(config["section_period"])
    scales = np.asarray(manifest["coordinate_scales"], dtype=float)
    if not crossings.integration_success or len(crossings.states) < 2 * period:
        return None, {
            "integration_success": crossings.integration_success,
            "crossing_count": len(crossings.states),
            "passed": False,
        }
    recurrence = np.linalg.norm(
        (crossings.states[period:] - crossings.states[:-period]) / scales,
        axis=1,
    )
    states = np.asarray(crossings.states[-period:], dtype=float)
    maximum_recurrence = float(np.max(recurrence[-period:]))
    audit = {
        "integration_success": crossings.integration_success,
        "crossing_count": len(crossings.states),
        "section_period": period,
        "states": states.tolist(),
        "maximum_scaled_recurrence": maximum_recurrence,
        "passed": maximum_recurrence
        <= float(manifest["acceptance"]["maximum_stable_cycle_recurrence"]),
    }
    return states, audit


def _trace_task(task):
    parameters = RosslerParameters(**task["parameters"])
    section = barrio_rossler_section(parameters)
    solver = SolverConfig(**task["solver"])
    state = np.asarray(task["base_state"], dtype=float) + float(
        task["amplitude"]
    ) * np.asarray(task["direction"], dtype=float)
    normal = np.asarray(section.normal, dtype=float)
    state -= normal * (section.value(state) / float(np.dot(normal, normal)))
    cycle = np.asarray(task["stable_cycle"], dtype=float)
    scales = np.asarray(task["coordinate_scales"], dtype=float)
    states = []
    flight_times = []
    capture_streak = 0
    capture_start = None
    success = True
    message = "return horizon completed without capture"
    for return_index in range(int(task["return_horizon"])):
        result = next_section_return(
            parameters,
            state,
            section,
            config=solver,
            maximum_flight_time=float(task["maximum_flight_time"]),
        )
        if not result.success:
            success = False
            message = result.message
            break
        state = result.state
        states.append(state.tolist())
        flight_times.append(result.flight_time)
        distance = float(
            np.min(np.linalg.norm((cycle - state) / scales, axis=1))
        )
        if distance <= float(task["capture_radius"]):
            capture_streak += 1
            if capture_streak == 1:
                capture_start = return_index
        else:
            capture_streak = 0
            capture_start = None
        if capture_streak >= int(task["required_capture_crossings"]):
            message = "stable-cycle capture qualified"
            break
    retained_count = len(states)
    captured = capture_streak >= int(task["required_capture_crossings"])
    if captured and capture_start is not None:
        retained_count = capture_start
    return {
        "case_id": task["case_id"],
        "family_id": task["family_id"],
        "sign": int(task["sign"]),
        "phase_index": int(task.get("phase_index", 0)),
        "phase_return_offset": int(task.get("phase_return_offset", 0)),
        "amplitude_index": int(task["amplitude_index"]),
        "amplitude": abs(float(task["amplitude"])),
        "integration_success": success,
        "message": message,
        "captured": captured,
        "capture_start_return": capture_start,
        "computed_returns": len(states),
        "retained_pre_capture_returns": retained_count,
        "total_flight_time": float(sum(flight_times)),
        "states": states,
    }


def _occupancy(states, manifest):
    values = np.asarray(states, dtype=float)
    bins = int(manifest["occupancy"]["bins_per_axis"])
    bounds = np.asarray(manifest["occupancy"]["bounds"], dtype=float)
    axes = np.asarray(manifest["occupancy"]["coordinate_axes"], dtype=int)
    occupied = np.zeros((bins, bins), dtype=bool)
    if values.size == 0:
        return occupied, 0.0
    selected = values[:, axes]
    inside = np.all((selected >= bounds[:, 0]) & (selected <= bounds[:, 1]), axis=1)
    normalized = (selected[inside] - bounds[:, 0]) / (bounds[:, 1] - bounds[:, 0])
    indices = np.minimum((normalized * bins).astype(int), bins - 1)
    if len(indices):
        occupied[indices[:, 0], indices[:, 1]] = True
    return occupied, float(np.mean(inside))


def _dilate(occupied, radius):
    value = np.asarray(occupied, dtype=bool)
    radius = int(radius)
    if radius < 0:
        raise ValueError("dilation radius must be nonnegative")
    padded = np.pad(value, radius)
    result = np.zeros_like(value)
    for row_offset in range(2 * radius + 1):
        for column_offset in range(2 * radius + 1):
            result |= padded[
                row_offset : row_offset + value.shape[0],
                column_offset : column_offset + value.shape[1],
            ]
    return result


def _coverage(target, reference, radius):
    target = np.asarray(target, dtype=bool)
    count = int(np.count_nonzero(target))
    if count == 0:
        return 0.0
    return float(np.count_nonzero(target & _dilate(reference, radius)) / count)


def _dilated_jaccard(left, right, radius):
    left_dilated = _dilate(left, radius)
    right_dilated = _dilate(right, radius)
    union = int(np.count_nonzero(left_dilated | right_dilated))
    if union == 0:
        return 1.0
    return float(np.count_nonzero(left_dilated & right_dilated) / union)


def _group_summaries(traces, manifest):
    coarse = set(int(value) for value in manifest["seed_grid"]["coarse_indices"])
    grouped = {}
    for trace in traces:
        key = (trace["case_id"], trace["family_id"], trace["sign"])
        grouped.setdefault(key, []).append(trace)
    summaries = []
    occupancies = {}
    acceptance = manifest["acceptance"]
    radius = int(manifest["occupancy"]["dilation_radius_cells"])
    for key, rows in sorted(grouped.items()):
        fine_states = []
        coarse_states = []
        capture_returns = []
        for row in rows:
            retained = row["states"][: row["retained_pre_capture_returns"]]
            fine_states.extend(retained)
            if row["amplitude_index"] in coarse:
                coarse_states.extend(retained)
            if row["captured"]:
                capture_returns.append(row["capture_start_return"])
        fine_occupancy, inside_fraction = _occupancy(fine_states, manifest)
        coarse_occupancy, _ = _occupancy(coarse_states, manifest)
        seed_coverage = _coverage(fine_occupancy, coarse_occupancy, radius)
        checks = {
            "trace_integrations": all(row["integration_success"] for row in rows),
            "minimum_pre_capture_support": len(fine_states)
            >= int(acceptance["minimum_pre_capture_points_per_group"]),
            "analysis_domain_coverage": inside_fraction
            >= float(acceptance["minimum_inside_domain_fraction"]),
            "seed_density_coverage": seed_coverage
            >= float(acceptance["minimum_coarse_coverage_of_fine_occupancy"]),
        }
        case_id, family_id, sign = key
        summaries.append(
            {
                "case_id": case_id,
                "family_id": family_id,
                "sign": sign,
                "trajectory_count": len(rows),
                "pre_capture_point_count": len(fine_states),
                "captured_trajectory_count": sum(row["captured"] for row in rows),
                "capture_return_interval": (
                    [int(min(capture_returns)), int(max(capture_returns))]
                    if capture_returns
                    else None
                ),
                "inside_domain_fraction": inside_fraction,
                "occupied_cell_count": int(np.count_nonzero(fine_occupancy)),
                "coarse_coverage_of_fine_occupancy": seed_coverage,
                "checks": checks,
                "passed": all(checks.values()),
            }
        )
        occupancies[key] = fine_occupancy
    return summaries, occupancies


def _endpoint_changes(summaries, occupancies, manifest):
    cases = [case["id"] for case in manifest["cases"]]
    if len(cases) != 2:
        raise ValueError("endpoint comparison requires exactly two cases")
    lookup = {
        (row["case_id"], row["family_id"], row["sign"]): row for row in summaries
    }
    radius = int(manifest["occupancy"]["dilation_radius_cells"])
    comparisons = []
    for family in manifest["families"]:
        for sign in (-1, 1):
            left_key = (cases[0], family["id"], sign)
            right_key = (cases[1], family["id"], sign)
            left = lookup[left_key]
            right = lookup[right_key]
            jaccard = _dilated_jaccard(
                occupancies[left_key], occupancies[right_key], radius
            )
            left_capture = left["captured_trajectory_count"] / left["trajectory_count"]
            right_capture = right["captured_trajectory_count"] / right["trajectory_count"]
            score = (1.0 - jaccard) + 0.25 * abs(right_capture - left_capture)
            comparisons.append(
                {
                    "family_id": family["id"],
                    "sign": sign,
                    "dilated_occupancy_jaccard": jaccard,
                    "left_capture_fraction": left_capture,
                    "right_capture_fraction": right_capture,
                    "discovery_score": score,
                    "eligible": left["passed"] and right["passed"],
                }
            )
    eligible = [row for row in comparisons if row["eligible"]]
    eligible.sort(key=lambda row: (-row["discovery_score"], row["family_id"], row["sign"]))
    selected = eligible[: int(manifest["selection"]["candidate_count"])]
    return comparisons, selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.upo-unstable-lobe-atlas-manifest.v1":
        raise SystemExit("unsupported UPO unstable-lobe atlas manifest")
    source_path = Path(manifest["source_seed_receipt"]["path"])
    source_bytes = source_path.read_bytes()
    if sha256_bytes(source_bytes) != manifest["source_seed_receipt"]["sha256"]:
        raise SystemExit("source manifold-seed receipt hash mismatch")
    seed_receipt = json.loads(source_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    solver = SolverConfig(**manifest["reference_solver"])
    cycles = {}
    cycle_audits = []
    for case in manifest["cases"]:
        parameters = RosslerParameters(**case["parameters"])
        cycle, audit = _stable_cycle(parameters, manifest, solver)
        audit["case_id"] = case["id"]
        cycle_audits.append(audit)
        if cycle is not None:
            cycles[case["id"]] = cycle
    if not all(row["passed"] for row in cycle_audits):
        raise SystemExit("stable-cycle qualification failed")
    seed_lookup = {
        (row["case_id"], row["family_id"]): row
        for row in seed_receipt["instances"]
        if row["passed"]
    }
    tasks = []
    for case in manifest["cases"]:
        for family in manifest["families"]:
            seed = seed_lookup[(case["id"], family["id"])]
            for amplitude_index, epsilon in enumerate(
                manifest["seed_grid"]["amplitudes"]
            ):
                for sign in (-1, 1):
                    tasks.append(
                        {
                            "case_id": case["id"],
                            "family_id": family["id"],
                            "sign": sign,
                            "amplitude_index": amplitude_index,
                            "amplitude": sign * float(epsilon),
                            "parameters": case["parameters"],
                            "base_state": seed["base_section_state"],
                            "direction": seed["section_unstable_direction"],
                            "stable_cycle": cycles[case["id"]].tolist(),
                            "coordinate_scales": manifest["coordinate_scales"],
                            "solver": manifest["reference_solver"],
                            "return_horizon": manifest["return_horizon"],
                            "maximum_flight_time": manifest["maximum_flight_time"],
                            "capture_radius": manifest["capture"]["scaled_radius"],
                            "required_capture_crossings": manifest["capture"][
                                "required_consecutive_crossings"
                            ],
                        }
                    )
    started = time.perf_counter()
    traces = []
    with ProcessPoolExecutor(max_workers=int(manifest["workers"])) as executor:
        futures = [executor.submit(_trace_task, task) for task in tasks]
        for index, future in enumerate(as_completed(futures), start=1):
            trace = future.result()
            traces.append(trace)
            if index % 20 == 0 or index == len(futures):
                print(
                    json.dumps(
                        {
                            "completed_traces": index,
                            "total_traces": len(futures),
                            "integration_failures": sum(
                                not row["integration_success"] for row in traces
                            ),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
    traces.sort(
        key=lambda row: (
            row["case_id"],
            row["family_id"],
            row["sign"],
            row["amplitude_index"],
        )
    )
    summaries, occupancies = _group_summaries(traces, manifest)
    comparisons, selected = _endpoint_changes(summaries, occupancies, manifest)
    receipt = {
        "schema": "butterfly.upo-unstable-lobe-atlas-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_seed_receipt_sha256": sha256_bytes(source_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "stable_cycles": cycle_audits,
        "traces": traces,
        "group_summaries": summaries,
        "endpoint_comparisons": comparisons,
        "selected_refinement_candidates": selected,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": bool(
            traces
            and all(row["integration_success"] for row in traces)
            and all(row["passed"] for row in summaries)
            and len(selected) == int(manifest["selection"]["candidate_count"])
        ),
        "scientific_scope": (
            "capture-truncated lobe discovery atlas, not a qualified connection event"
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(
        json.dumps(
            {
                "experiment_id": receipt["experiment_id"],
                "manifest_sha256": receipt["manifest_sha256"],
                "trace_count": len(traces),
                "group_count": len(summaries),
                "selected_refinement_candidates": selected,
                "elapsed_seconds": receipt["elapsed_seconds"],
                "passed": receipt["passed"],
            },
            sort_keys=True,
        )
    )
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

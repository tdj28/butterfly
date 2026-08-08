#!/usr/bin/env python3
"""Test whether a frozen extra return-map branch captures unusually quickly."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import io
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy
from scipy.stats import chi2

from butterfly import (
    OrbitLabel,
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    classify_fundamental_period,
    collect_crossings,
    scrambled_sobol_section_states,
    sprinkler_survivors,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _kaplan_meier(durations, events, tau):
    durations = np.asarray(durations, dtype=float)
    events = np.asarray(events, dtype=bool)
    if durations.ndim != 1 or events.shape != durations.shape or len(durations) == 0:
        raise ValueError("durations and events must be nonempty equal-length vectors")
    if tau <= 0.0 or np.any(durations < 0.0) or np.any(durations > tau + 1e-10):
        raise ValueError("durations must lie in the declared RMST interval")
    survival = 1.0
    previous = 0.0
    area = 0.0
    rows = []
    sorted_durations = np.sort(durations)
    event_times, event_counts = np.unique(durations[events], return_counts=True)
    at_risk_counts = len(durations) - np.searchsorted(
        sorted_durations, event_times, side="left"
    )
    for event_time, at_risk, event_count in zip(
        event_times, at_risk_counts, event_counts, strict=True
    ):
        if event_time > tau:
            break
        area += survival * (event_time - previous)
        survival *= 1.0 - event_count / at_risk
        rows.append((float(event_time), survival, int(at_risk), int(event_count)))
        previous = float(event_time)
    area += survival * (tau - previous)
    return float(area), rows


def _survival_at(rows, checkpoint):
    survival = 1.0
    for event_time, value, _, _ in rows:
        if event_time > checkpoint:
            break
        survival = value
    return float(survival)


def _logrank(left_durations, left_events, right_durations, right_events):
    left_durations = np.asarray(left_durations, dtype=float)
    left_events = np.asarray(left_events, dtype=bool)
    right_durations = np.asarray(right_durations, dtype=float)
    right_events = np.asarray(right_events, dtype=bool)
    times = np.unique(
        np.concatenate((left_durations[left_events], right_durations[right_events]))
    )
    left_sorted = np.sort(left_durations)
    right_sorted = np.sort(right_durations)
    n_left = len(left_durations) - np.searchsorted(left_sorted, times, side="left")
    n_right = len(right_durations) - np.searchsorted(right_sorted, times, side="left")

    def event_counts(durations, events):
        event_times, counts = np.unique(durations[events], return_counts=True)
        output = np.zeros(len(times), dtype=float)
        indices = np.searchsorted(times, event_times)
        output[indices] = counts
        return output

    d_left = event_counts(left_durations, left_events)
    d_right = event_counts(right_durations, right_events)
    n_total = n_left + n_right
    d_total = d_left + d_right
    observed_minus_expected = float(
        np.sum(d_left - d_total * n_left / n_total)
    )
    usable = n_total > 1
    variance = float(
        np.sum(
            n_left[usable]
            * n_right[usable]
            * d_total[usable]
            * (n_total[usable] - d_total[usable])
            / (n_total[usable] ** 2 * (n_total[usable] - 1))
        )
    )
    statistic = (
        observed_minus_expected**2 / variance if variance > 0.0 else 0.0
    )
    return float(statistic), float(chi2.sf(statistic, 1))


def _bootstrap_rmst_difference(
    extra_durations,
    extra_events,
    core_durations,
    core_events,
    *,
    tau,
    samples,
    confidence,
    seed,
):
    generator = np.random.default_rng(seed)
    extra_durations = np.asarray(extra_durations, dtype=float)
    extra_events = np.asarray(extra_events, dtype=bool)
    core_durations = np.asarray(core_durations, dtype=float)
    core_events = np.asarray(core_events, dtype=bool)
    differences = np.empty(samples, dtype=float)
    for index in range(samples):
        extra_ids = generator.integers(0, len(extra_durations), len(extra_durations))
        core_ids = generator.integers(0, len(core_durations), len(core_durations))
        # All censoring in this experiment is administrative at ``tau``, so
        # the KM restricted mean equals the mean observed/censored duration.
        differences[index] = float(
            np.mean(extra_durations[extra_ids]) - np.mean(core_durations[core_ids])
        )
    tail = 0.5 * (1.0 - confidence)
    return tuple(float(value) for value in np.quantile(differences, (tail, 1 - tail)))


def _landmark_samples(result, *, branch_definition, landmark, window, horizon):
    ids = result.all_midpoint_trajectory_ids
    times = result.all_midpoint_times
    states = result.all_midpoint_states
    selected = (times >= window[0]) & (times <= window[1])
    ids = ids[selected]
    times = times[selected]
    states = states[selected]
    order = np.lexsort((times, ids))
    ids = ids[order]
    times = times[order]
    states = states[order]
    if len(ids):
        last = np.r_[ids[1:] != ids[:-1], True]
        ids = ids[last]
        times = times[last]
        states = states[last]
    capture_times = result.capture_times[ids]
    at_risk = np.isnan(capture_times) | (capture_times > landmark)
    at_risk &= ~result.failed[ids]
    ids = ids[at_risk]
    times = times[at_risk]
    states = states[at_risk]
    capture_times = capture_times[at_risk]

    coordinate = states[:, int(branch_definition["axis"])]
    intervals = np.asarray(branch_definition["critical_intervals"], dtype=float)
    if intervals.shape != (2, 2) or np.any(intervals[:, 0] > intervals[:, 1]):
        raise ValueError("three-branch definition requires two ordered intervals")
    branch = np.full(len(ids), -1, dtype=np.int8)
    branch[coordinate < intervals[0, 0]] = 0
    branch[(coordinate > intervals[0, 1]) & (coordinate < intervals[1, 0])] = 1
    branch[coordinate > intervals[1, 1]] = 2
    event = np.isfinite(capture_times)
    duration = np.where(event, capture_times - landmark, horizon - landmark)
    return {
        "trajectory_id": ids,
        "assignment_time": times,
        "coordinate": coordinate,
        "branch": branch,
        "duration": duration,
        "event": event,
    }


def _summarize_run(run_id, samples, manifest):
    acceptance = manifest["acceptance"]
    survival = manifest["survival_analysis"]
    tau = float(survival["rmst_tau"])
    checkpoints = tuple(float(value) for value in survival["checkpoints"])
    rows = {}
    for branch in (-1, 0, 1, 2):
        chosen = samples["branch"] == branch
        if branch == -1:
            rows["ambiguous"] = {"count": int(np.count_nonzero(chosen))}
            continue
        durations = samples["duration"][chosen]
        events = samples["event"][chosen]
        if len(durations) == 0:
            rows[str(branch)] = {
                "count": 0,
                "event_count": 0,
                "event_fraction": None,
                "restricted_mean_survival_time": None,
                "survival_at_checkpoints": {},
            }
            continue
        rmst, curve = _kaplan_meier(durations, events, tau)
        rows[str(branch)] = {
            "count": len(durations),
            "event_count": int(np.count_nonzero(events)),
            "event_fraction": float(np.mean(events)),
            "restricted_mean_survival_time": rmst,
            "survival_at_checkpoints": {
                str(value): _survival_at(curve, value) for value in checkpoints
            },
        }

    extra = samples["branch"] == int(manifest["branch_definition"]["extra_branch"])
    core = samples["branch"] >= 0
    core &= ~extra
    if not np.any(extra) or not np.any(core):
        return {
            "id": run_id,
            "risk_set_count": len(samples["branch"]),
            "assigned_count": int(np.count_nonzero(samples["branch"] >= 0)),
            "branch_summaries": rows,
            "extra_branch_fraction_among_assigned": None,
            "extra_minus_core_rmst": None,
            "extra_minus_core_rmst_interval": (None, None),
            "logrank_statistic": None,
            "logrank_p_value": None,
            "supports_faster_extra_branch": False,
            "quality_passed": False,
        }
    extra_rmst, _ = _kaplan_meier(
        samples["duration"][extra], samples["event"][extra], tau
    )
    core_rmst, _ = _kaplan_meier(
        samples["duration"][core], samples["event"][core], tau
    )
    interval = _bootstrap_rmst_difference(
        samples["duration"][extra],
        samples["event"][extra],
        samples["duration"][core],
        samples["event"][core],
        tau=tau,
        samples=int(survival["bootstrap_samples"]),
        confidence=float(survival["confidence"]),
        seed=int(survival["bootstrap_seed"]) + sum(run_id.encode("utf-8")),
    )
    statistic, p_value = _logrank(
        samples["duration"][extra],
        samples["event"][extra],
        samples["duration"][core],
        samples["event"][core],
    )
    assigned = int(np.count_nonzero(samples["branch"] >= 0))
    quality = bool(
        len(samples["branch"]) > 0
        and np.count_nonzero(extra) >= acceptance["minimum_extra_assignments"]
        and np.count_nonzero(core) >= acceptance["minimum_core_assignments"]
        and np.count_nonzero(samples["branch"] < 0) / len(samples["branch"])
        <= acceptance["maximum_ambiguous_fraction"]
    )
    return {
        "id": run_id,
        "risk_set_count": len(samples["branch"]),
        "assigned_count": assigned,
        "branch_summaries": rows,
        "extra_branch_fraction_among_assigned": float(np.mean(extra[samples["branch"] >= 0])),
        "extra_minus_core_rmst": extra_rmst - core_rmst,
        "extra_minus_core_rmst_interval": interval,
        "logrank_statistic": statistic,
        "logrank_p_value": p_value,
        "supports_faster_extra_branch": bool(
            interval[1] < 0.0
            and p_value <= acceptance["maximum_logrank_p_value"]
        ),
        "quality_passed": quality,
    }


def _run(manifest, samples_output):
    parameters = RosslerParameters(**manifest["parameters"])
    section = barrio_rossler_section(parameters)
    solver = SolverConfig(**manifest["reference_solver"])
    reference = manifest["cycle_reference"]
    crossings = collect_crossings(
        parameters,
        manifest["cycle_initial_state"],
        section,
        transient=float(reference["transient"]),
        observation_horizon=float(reference["observation_horizon"]),
        max_crossings=int(reference["max_crossings"]),
        config=solver,
    )
    classification = classify_fundamental_period(
        crossings.states, **reference["recurrence"]
    )
    period = int(manifest["stable_period"])
    cycle = crossings.states[-period:]
    ensemble = manifest["ensemble"]
    capture = manifest["capture"]
    landmark = float(manifest["landmark"]["time"])
    window = tuple(float(value) for value in manifest["landmark"]["assignment_window"])
    horizon = float(ensemble["horizon"])
    arrays = {}
    rows = []
    raw_results = {}
    for declared in manifest["runs"]:
        initial = scrambled_sobol_section_states(
            section,
            first_coordinate_range=tuple(ensemble["y_range"]),
            second_coordinate_range=tuple(ensemble["z_range"]),
            sample_power=int(declared["sample_power"]),
            scramble_seed=int(declared["scramble_seed"]),
        )
        result = sprinkler_survivors(
            parameters,
            initial,
            section,
            cycle,
            dt=float(declared.get("dt", ensemble["dt"])),
            horizon=horizon,
            capture_coordinate_axes=tuple(capture["coordinate_axes"]),
            capture_coordinate_scales=tuple(capture["coordinate_scales"]),
            capture_radius=float(capture["radius"]),
            required_capture_crossings=int(capture["required_crossings"]),
            checkpoint_times=ensemble["checkpoint_times"],
            midpoint_window=window,
            escape_radius=float(ensemble["escape_radius"]),
        )
        samples = _landmark_samples(
            result,
            branch_definition=manifest["branch_definition"],
            landmark=landmark,
            window=window,
            horizon=horizon,
        )
        row = _summarize_run(declared["id"], samples, manifest)
        row.update(
            {
                "configuration": declared,
                "ensemble_size": len(initial),
                "failed_count": int(np.count_nonzero(result.failed)),
                "checkpoint_times": result.checkpoint_times.tolist(),
                "survivor_counts": result.survivor_counts.tolist(),
            }
        )
        row["quality_passed"] = bool(
            row["quality_passed"]
            and row["failed_count"] <= manifest["acceptance"]["maximum_failed_count"]
        )
        rows.append(row)
        raw_results[declared["id"]] = samples
        for name, values in samples.items():
            arrays[f"{declared['id']}__{name}"] = values
        print(
            json.dumps(
                {
                    "run": row["id"],
                    "risk_set": row["risk_set_count"],
                    "branches": {
                        key: value["count"]
                        for key, value in row["branch_summaries"].items()
                    },
                    "rmst_difference": row["extra_minus_core_rmst"],
                    "interval": row["extra_minus_core_rmst_interval"],
                    "faster": row["supports_faster_extra_branch"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    by_id = {row["id"]: row for row in rows}
    comparison = manifest["numerical_comparison"]
    baseline = by_id[comparison["baseline_run_id"]]
    alternate = by_id[comparison["alternate_run_id"]]
    numerical = {
        "baseline_run_id": baseline["id"],
        "alternate_run_id": alternate["id"],
        "absolute_rmst_difference_change": abs(
            baseline["extra_minus_core_rmst"] - alternate["extra_minus_core_rmst"]
        ),
        "absolute_extra_fraction_change": abs(
            baseline["extra_branch_fraction_among_assigned"]
            - alternate["extra_branch_fraction_among_assigned"]
        ),
    }
    numerical["passed"] = bool(
        numerical["absolute_rmst_difference_change"]
        <= comparison["maximum_absolute_rmst_difference_change"]
        and numerical["absolute_extra_fraction_change"]
        <= comparison["maximum_absolute_extra_fraction_change"]
    )
    evidence = [by_id[value] for value in manifest["evidence_run_ids"]]
    faster = all(row["supports_faster_extra_branch"] for row in evidence)
    quality = bool(
        crossings.integration_success
        and classification.label == OrbitLabel.PERIODIC
        and classification.fundamental_period == period
        and all(row["quality_passed"] for row in rows)
        and numerical["passed"]
    )
    state_buffer = io.BytesIO()
    np.savez_compressed(state_buffer, **arrays)
    state_bytes = state_buffer.getvalue()
    atomic_write(samples_output, state_bytes)
    return {
        "cycle_reference": {
            "classification": asdict(classification),
            "states": cycle.tolist(),
        },
        "runs": rows,
        "numerical_comparison": numerical,
        "quality_passed": quality,
        "supports_faster_extra_branch": faster,
        "passed": bool(
            quality
            and (
                faster
                or not manifest["acceptance"]["require_faster_extra_branch"]
            )
        ),
        "samples_artifact": str(samples_output),
        "samples_artifact_bytes": len(state_bytes),
        "samples_artifact_sha256": sha256_bytes(state_bytes),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--samples-output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.branch-conditioned-escape-manifest.v1":
        raise SystemExit("unsupported branch-conditioned escape manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("branch-conditioned escape qualification requires clean source")
    started = time.perf_counter()
    result = _run(manifest, args.samples_output)
    receipt = {
        "schema": "butterfly.branch-conditioned-escape-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        **result,
        "elapsed_seconds": time.perf_counter() - started,
        "interpretation_limit": (
            "Branch-conditioned finite capture times test an escape mechanism; "
            "they do not continue an infinite-lifetime TBA curve."
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({"output": str(args.output), "passed": receipt["passed"]}))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

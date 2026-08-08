#!/usr/bin/env python3
"""Qualify saddle topology with ensemble and oracle convergence gates."""
from __future__ import annotations

import argparse
import json
import platform
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    OrbitLabel,
    RosslerParameters,
    SolverConfig,
    barrio_rossler_section,
    classify_fundamental_period,
    collect_crossings,
    infer_return_map_branches_robust,
    scrambled_sobol_section_states,
    sprinkler_survivors,
    survivor_return_pairs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _grid(section, ensemble, run):
    if run.get("sampler", "grid") == "sobol":
        return scrambled_sobol_section_states(
            section,
            first_coordinate_range=tuple(ensemble["y_range"]),
            second_coordinate_range=tuple(ensemble["z_range"]),
            sample_power=int(run["sample_power"]),
            scramble_seed=int(run["scramble_seed"]),
        )
    if run.get("sampler", "grid") != "grid":
        raise ValueError("sampler must be grid or sobol")
    y_count = int(run.get("y_count", ensemble["y_count"]))
    z_count = int(run.get("z_count", ensemble["z_count"]))
    phase = float(run.get("grid_phase", 0.0))
    if phase == 0.0:
        y_values = np.linspace(*ensemble["y_range"], y_count)
        z_values = np.linspace(*ensemble["z_range"], z_count)
    elif phase == 0.5:
        y_step = (ensemble["y_range"][1] - ensemble["y_range"][0]) / y_count
        z_step = (ensemble["z_range"][1] - ensemble["z_range"][0]) / z_count
        y_values = ensemble["y_range"][0] + (np.arange(y_count) + phase) * y_step
        z_values = ensemble["z_range"][0] + (np.arange(z_count) + phase) * z_step
    else:
        raise ValueError("grid_phase must be 0 or 0.5")
    y_grid, z_grid = np.meshgrid(y_values, z_values, indexing="ij")
    return np.column_stack(
        (
            np.full(y_grid.size, section.offset),
            y_grid.ravel(),
            z_grid.ravel(),
        )
    )


def _run_config(ensemble, run):
    return {
        "dt": float(run.get("dt", ensemble["dt"])),
        "horizon": float(run.get("horizon", ensemble["horizon"])),
        "checkpoint_times": run.get(
            "checkpoint_times", ensemble["checkpoint_times"]
        ),
        "midpoint_window": run.get("midpoint_window", ensemble["midpoint_window"]),
    }


def _short_horizon_audit(parameters, section, cycle, initial, manifest, solver):
    audit = manifest["short_horizon_audit"]
    if "trajectory_fractions" in audit:
        fractions = np.asarray(audit["trajectory_fractions"], dtype=float)
        if np.any((fractions < 0.0) | (fractions > 1.0)):
            raise ValueError("trajectory_fractions must lie in [0,1]")
        ids = np.rint(fractions * (len(initial) - 1)).astype(int)
    else:
        ids = np.asarray(audit["trajectory_ids"], dtype=int)
    selected = initial[ids]
    fixed = sprinkler_survivors(
        parameters,
        selected,
        section,
        cycle,
        dt=float(audit["dt"]),
        horizon=float(audit["horizon"]),
        capture_coordinate_axes=tuple(manifest["capture"]["coordinate_axes"]),
        capture_coordinate_scales=tuple(
            manifest["capture"]["coordinate_scales"]
        ),
        capture_radius=float(audit["disabled_capture_radius"]),
        required_capture_crossings=int(audit["disabled_capture_crossings"]),
        checkpoint_times=(float(audit["horizon"]),),
        midpoint_window=(0.0, float(audit["horizon"])),
        escape_radius=float(manifest["ensemble"]["escape_radius"]),
    )
    rows = []
    axes = np.asarray(manifest["capture"]["coordinate_axes"], dtype=int)
    scales = np.asarray(manifest["capture"]["coordinate_scales"], dtype=float)
    for local_id, trajectory_id in enumerate(ids):
        selected_fixed = fixed.midpoint_trajectory_ids == local_id
        fixed_times = fixed.midpoint_times[selected_fixed]
        fixed_states = fixed.midpoint_states[selected_fixed]
        adaptive = collect_crossings(
            parameters,
            initial[trajectory_id],
            section,
            transient=0.0,
            observation_horizon=float(audit["horizon"]),
            max_crossings=int(audit["max_crossings"]),
            config=solver,
        )
        retained = adaptive.times > 0.5 * float(audit["dt"])
        adaptive_times = adaptive.times[retained]
        adaptive_states = adaptive.states[retained]
        count = min(
            len(fixed_times),
            len(adaptive_times),
            int(audit["comparison_crossings"]),
        )
        if count:
            differences = (
                adaptive_states[:count, axes] - fixed_states[:count, axes]
            ) / scales
            maximum_state_error = float(
                np.max(np.linalg.norm(differences, axis=1))
            )
            maximum_time_error = float(
                np.max(np.abs(adaptive_times[:count] - fixed_times[:count]))
            )
        else:
            maximum_state_error = float("inf")
            maximum_time_error = float("inf")
        rows.append(
            {
                "trajectory_id": int(trajectory_id),
                "comparison_crossings": count,
                "maximum_scaled_state_error": maximum_state_error,
                "maximum_time_error": maximum_time_error,
                "integration_success": adaptive.integration_success,
            }
        )
    return rows


def _survival_comparisons(runs, baseline_id):
    baseline = next(run for run in runs if run["id"] == baseline_id)
    baseline_by_time = dict(
        zip(
            baseline["checkpoint_times"],
            baseline["survivor_fractions"],
            strict=True,
        )
    )
    comparisons = []
    for run in runs:
        common = sorted(set(baseline_by_time) & set(run["checkpoint_times"]))
        run_by_time = dict(
            zip(run["checkpoint_times"], run["survivor_fractions"], strict=True)
        )
        differences = [abs(run_by_time[value] - baseline_by_time[value]) for value in common]
        comparisons.append(
            {
                "run_id": run["id"],
                "common_checkpoint_times": common,
                "maximum_absolute_survivor_fraction_difference": max(
                    differences, default=0.0
                ),
            }
        )
    return comparisons


def _critical_convergence(runs, coordinates, expected_branch_count):
    output = {}
    for coordinate in coordinates:
        name = coordinate["name"]
        run_rows = [run["coordinates"][name] for run in runs]
        if any(
            not row["robust_oracle"]["resolved"]
            or row["robust_oracle"]["branch_count"] != expected_branch_count
            for row in run_rows
        ):
            output[name] = {
                "critical_point_intervals": [],
                "normalized_critical_point_spans": [],
                "maximum_normalized_critical_point_span": 1e300,
                "reason": "one or more runs lack the expected resolved count",
            }
            continue
        domain_range = max(row["source_maximum"] for row in run_rows) - min(
            row["source_minimum"] for row in run_rows
        )
        spans = []
        intervals = []
        for index in range(expected_branch_count - 1):
            lower = min(
                row["robust_oracle"]["critical_point_intervals"][index][0]
                for row in run_rows
            )
            upper = max(
                row["robust_oracle"]["critical_point_intervals"][index][1]
                for row in run_rows
            )
            intervals.append((lower, upper))
            spans.append((upper - lower) / max(domain_range, np.finfo(float).eps))
        output[name] = {
            "critical_point_intervals": intervals,
            "normalized_critical_point_spans": spans,
            "maximum_normalized_critical_point_span": max(spans, default=0.0),
            "reason": "resolved across runs",
        }
    return output


def _observed_branch_count(runs, coordinates, allowed_counts):
    """Return one fully resolved branch count across every run/coordinate."""
    counts = []
    for run in runs:
        for coordinate in coordinates:
            robust = run["coordinates"][coordinate["name"]]["robust_oracle"]
            if not robust["resolved"] or robust["branch_count"] is None:
                return None
            counts.append(int(robust["branch_count"]))
    unique = set(counts)
    if len(unique) != 1:
        return None
    observed = unique.pop()
    return observed if observed in allowed_counts else None


def _coverage_censor_evaluation(
    robust,
    *,
    source_minimum,
    source_maximum,
    expected_branch_count,
    oracle_common,
    acceptance,
):
    """Accept only declared coverage censors with matching nominal geometry."""
    variants = robust.get("variant_results", ())
    expected_critical_count = expected_branch_count - 1
    resolved_indices = []
    censored_indices = []
    rejected = []
    accepted_critical = []
    for index, variant in enumerate(variants):
        critical = tuple(float(value) for value in variant["critical_points"])
        if (
            variant["resolved"]
            and variant["branch_count"] == expected_branch_count
            and len(critical) == expected_critical_count
        ):
            resolved_indices.append(index)
            accepted_critical.append(critical)
            continue
        coverage_only = bool(
            not variant["resolved"]
            and variant["reason"] == "insufficient invariant-domain coverage"
            and variant["domain_coverage"]
            >= acceptance["minimum_censored_domain_coverage"]
            and variant["conditional_spread_ratio"]
            <= oracle_common["maximum_conditional_spread_ratio"]
            and len(critical) == expected_critical_count
        )
        if coverage_only:
            censored_indices.append(index)
            accepted_critical.append(critical)
        else:
            rejected.append(
                {
                    "variant_index": index,
                    "resolved": bool(variant["resolved"]),
                    "branch_count": variant["branch_count"],
                    "nominal_branch_count": len(critical) + 1,
                    "reason": variant["reason"],
                    "domain_coverage": float(variant["domain_coverage"]),
                    "conditional_spread_ratio": float(
                        variant["conditional_spread_ratio"]
                    ),
                }
            )
    source_range = max(
        float(source_maximum) - float(source_minimum), np.finfo(float).eps
    )
    intervals = tuple(
        (
            min(points[index] for points in accepted_critical),
            max(points[index] for points in accepted_critical),
        )
        for index in range(expected_critical_count)
    ) if accepted_critical else ()
    normalized_spans = tuple(
        (upper - lower) / source_range for lower, upper in intervals
    )
    maximum_span = max(normalized_spans, default=float("inf"))
    minimum_resolved = int(acceptance["minimum_fully_resolved_variants"])
    passed = bool(
        len(variants) > 0
        and len(resolved_indices) >= minimum_resolved
        and len(resolved_indices) + len(censored_indices) == len(variants)
        and not rejected
        and maximum_span
        <= acceptance["maximum_within_run_normalized_critical_span"]
    )
    if rejected:
        reason = "one or more variants contradict or fail beyond coverage"
    elif len(resolved_indices) < minimum_resolved:
        reason = "too few fully resolved variants"
    elif maximum_span > acceptance["maximum_within_run_normalized_critical_span"]:
        reason = "critical-point location is variant-unstable"
    elif passed:
        reason = "resolved with prospectively admissible coverage censoring"
    else:
        reason = "coverage-censor evaluation failed"
    return {
        "passed": passed,
        "branch_count": expected_branch_count if passed else None,
        "fully_resolved_variant_indices": resolved_indices,
        "coverage_censored_variant_indices": censored_indices,
        "rejected_variants": rejected,
        "critical_point_intervals": intervals,
        "normalized_critical_point_spans": normalized_spans,
        "maximum_normalized_critical_point_span": maximum_span,
        "reason": reason,
    }


def _blind_coverage_censor_evaluation(
    robust,
    *,
    source_minimum,
    source_maximum,
    allowed_branch_counts,
    oracle_common,
    acceptance,
):
    """Select exactly one branch count under the frozen censor rule."""
    candidates = {
        int(branch_count): _coverage_censor_evaluation(
            robust,
            source_minimum=source_minimum,
            source_maximum=source_maximum,
            expected_branch_count=int(branch_count),
            oracle_common=oracle_common,
            acceptance=acceptance,
        )
        for branch_count in allowed_branch_counts
    }
    passing = [count for count, row in candidates.items() if row["passed"]]
    diagnostics = {
        str(count): {
            "passed": row["passed"],
            "reason": row["reason"],
            "fully_resolved_variant_count": len(
                row["fully_resolved_variant_indices"]
            ),
            "coverage_censored_variant_count": len(
                row["coverage_censored_variant_indices"]
            ),
            "rejected_variant_count": len(row["rejected_variants"]),
        }
        for count, row in candidates.items()
    }
    if len(passing) == 1:
        selected = dict(candidates[passing[0]])
        selected["candidate_diagnostics"] = diagnostics
        selected["reason"] = "one blind branch count passes the coverage-censor rule"
        return selected
    return {
        "passed": False,
        "branch_count": None,
        "fully_resolved_variant_indices": [],
        "coverage_censored_variant_indices": [],
        "rejected_variants": [],
        "critical_point_intervals": [],
        "normalized_critical_point_spans": [],
        "maximum_normalized_critical_point_span": 1e300,
        "candidate_diagnostics": diagnostics,
        "reason": "blind branch count is unresolved or ambiguous",
    }


def _coverage_critical_convergence(runs, coordinates, expected_branch_count):
    output = {}
    for coordinate in coordinates:
        name = coordinate["name"]
        rows = [run["coordinates"][name] for run in runs]
        evaluations = [row["coverage_censor_evaluation"] for row in rows]
        if any(not row["passed"] for row in evaluations):
            output[name] = {
                "critical_point_intervals": [],
                "normalized_critical_point_spans": [],
                "maximum_normalized_critical_point_span": 1e300,
                "reason": "one or more runs fail coverage-censor evaluation",
            }
            continue
        domain_range = max(row["source_maximum"] for row in rows) - min(
            row["source_minimum"] for row in rows
        )
        intervals = []
        spans = []
        for index in range(expected_branch_count - 1):
            lower = min(
                row["critical_point_intervals"][index][0]
                for row in evaluations
            )
            upper = max(
                row["critical_point_intervals"][index][1]
                for row in evaluations
            )
            intervals.append((lower, upper))
            spans.append((upper - lower) / max(domain_range, np.finfo(float).eps))
        output[name] = {
            "critical_point_intervals": intervals,
            "normalized_critical_point_spans": spans,
            "maximum_normalized_critical_point_span": max(spans, default=0.0),
            "reason": "resolved across runs including admissible coverage censors",
        }
    return output


def _coverage_observed_branch_count(runs, coordinates, allowed_counts):
    counts = []
    for run in runs:
        for coordinate in coordinates:
            evaluation = run["coordinates"][coordinate["name"]][
                "coverage_censor_evaluation"
            ]
            if not evaluation["passed"] or evaluation["branch_count"] is None:
                return None
            counts.append(int(evaluation["branch_count"]))
    unique = set(counts)
    if len(unique) != 1:
        return None
    observed = unique.pop()
    return observed if observed in allowed_counts else None


def _path_evaluation(cases, manifest):
    """Evaluate the prospective ordered topology path without fitting a boundary."""
    path = manifest["path_acceptance"]
    ordered_cases = sorted(cases, key=lambda row: row["parameters"]["a"])
    observed = [row["observed_saddle_branch_count"] for row in ordered_cases]
    all_resolved = all(value is not None for value in observed)
    nondecreasing = all_resolved and all(
        left <= right for left, right in zip(observed, observed[1:], strict=False)
    )
    required = {int(value) for value in path["required_observed_counts"]}
    required_present = all_resolved and required.issubset(set(observed))
    controls_passed = all(
        row["expected_saddle_branch_count"] is None
        or row["observed_saddle_branch_count"]
        == row["expected_saddle_branch_count"]
        for row in ordered_cases
    )
    transitions = []
    if all_resolved:
        for left, right in zip(ordered_cases, ordered_cases[1:], strict=False):
            if (
                left["observed_saddle_branch_count"]
                != right["observed_saddle_branch_count"]
            ):
                transitions.append(
                    {
                        "lower_a": left["parameters"]["a"],
                        "upper_a": right["parameters"]["a"],
                        "lower_branch_count": left[
                            "observed_saddle_branch_count"
                        ],
                        "upper_branch_count": right[
                            "observed_saddle_branch_count"
                        ],
                    }
                )
    passed = bool(
        all(row["passed"] for row in ordered_cases)
        and all_resolved
        and nondecreasing
        and required_present
        and controls_passed
        and len(transitions) == int(path["required_transition_count"])
    )
    return {
        "a_values": [row["parameters"]["a"] for row in ordered_cases],
        "observed_branch_counts": observed,
        "all_resolved": all_resolved,
        "nondecreasing": nondecreasing,
        "required_counts_present": required_present,
        "published_controls_passed": controls_passed,
        "transitions": transitions,
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    supported_schemas = {
        "butterfly.sprinkler-convergence-manifest.v1",
        "butterfly.sprinkler-path-continuation-manifest.v1",
        "butterfly.sprinkler-coverage-censor-manifest.v1",
    }
    if manifest.get("schema") not in supported_schemas:
        raise SystemExit("unsupported sprinkler-convergence manifest")
    path_mode = bool(
        manifest.get("path_acceptance")
        and manifest["schema"]
        in {
            "butterfly.sprinkler-path-continuation-manifest.v1",
            "butterfly.sprinkler-coverage-censor-manifest.v1",
        }
    )
    coverage_censor_mode = (
        manifest["schema"] == "butterfly.sprinkler-coverage-censor-manifest.v1"
    )
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    solver = SolverConfig(**manifest["reference_solver"])
    fixed = manifest["fixed_parameters"]
    capture = manifest["capture"]
    ensemble = manifest["ensemble"]
    acceptance = manifest["acceptance"]
    all_cases = []
    started = time.perf_counter()
    for case in manifest["cases"]:
        parameters = RosslerParameters(
            a=float(case["a"]), b=float(fixed["b"]), c=float(fixed["c"])
        )
        section = barrio_rossler_section(parameters)
        cycle_crossings = collect_crossings(
            parameters,
            manifest["cycle_initial_state"],
            section,
            transient=float(manifest["cycle_reference"]["transient"]),
            observation_horizon=float(
                manifest["cycle_reference"]["observation_horizon"]
            ),
            max_crossings=int(manifest["cycle_reference"]["max_crossings"]),
            config=solver,
        )
        cycle_classification = classify_fundamental_period(
            cycle_crossings.states, **manifest["cycle_reference"]["recurrence"]
        )
        cycle_period = int(case["stable_period"])
        cycle = cycle_crossings.states[-cycle_period:]
        sample_power_offset = int(case.get("sample_power_offset", 0))
        declared_runs = []
        for shared_run in manifest["runs"]:
            declared_run = dict(shared_run)
            if "sample_power" in declared_run:
                declared_run["sample_power"] = (
                    int(declared_run["sample_power"]) + sample_power_offset
                )
            declared_runs.append(declared_run)
        run_rows = []
        for declared_run in declared_runs:
            initial = _grid(section, ensemble, declared_run)
            config = _run_config(ensemble, declared_run)
            result = sprinkler_survivors(
                parameters,
                initial,
                section,
                cycle,
                dt=config["dt"],
                horizon=config["horizon"],
                capture_coordinate_axes=tuple(capture["coordinate_axes"]),
                capture_coordinate_scales=tuple(capture["coordinate_scales"]),
                capture_radius=float(capture["radius"]),
                required_capture_crossings=int(capture["required_crossings"]),
                checkpoint_times=config["checkpoint_times"],
                midpoint_window=tuple(config["midpoint_window"]),
                escape_radius=float(ensemble["escape_radius"]),
            )
            coordinate_rows = {}
            for coordinate in manifest["coordinates"]:
                source_values, target_values = survivor_return_pairs(
                    result, int(coordinate["axis"])
                )
                if len(source_values) >= acceptance["minimum_return_pairs"]:
                    robust = asdict(
                        infer_return_map_branches_robust(
                            source_values,
                            target_values,
                            variants=manifest["oracle_variants"],
                            common_options=manifest["oracle_common"],
                            minimum_variant_consensus=float(
                                acceptance["minimum_oracle_variant_consensus"]
                            ),
                            maximum_normalized_critical_point_span=float(
                                acceptance[
                                    "maximum_within_run_normalized_critical_span"
                                ]
                            ),
                        )
                    )
                else:
                    robust = {
                        "resolved": False,
                        "branch_count": None,
                        "critical_point_intervals": (),
                        "reason": "insufficient survivor return pairs",
                    }
                coordinate_rows[coordinate["name"]] = {
                    "pair_count": len(source_values),
                    "source_minimum": float(np.min(source_values))
                    if len(source_values)
                    else None,
                    "source_maximum": float(np.max(source_values))
                    if len(source_values)
                    else None,
                    "robust_oracle": robust,
                }
                if coverage_censor_mode and len(source_values) >= acceptance[
                    "minimum_return_pairs"
                ]:
                    expected_count = case.get("expected_saddle_branch_count")
                    if expected_count is None:
                        evaluation = _blind_coverage_censor_evaluation(
                            robust,
                            source_minimum=float(np.min(source_values)),
                            source_maximum=float(np.max(source_values)),
                            allowed_branch_counts=acceptance[
                                "allowed_branch_counts"
                            ],
                            oracle_common=manifest["oracle_common"],
                            acceptance=acceptance,
                        )
                    else:
                        evaluation = _coverage_censor_evaluation(
                            robust,
                            source_minimum=float(np.min(source_values)),
                            source_maximum=float(np.max(source_values)),
                            expected_branch_count=int(expected_count),
                            oracle_common=manifest["oracle_common"],
                            acceptance=acceptance,
                        )
                    coordinate_rows[coordinate["name"]][
                        "coverage_censor_evaluation"
                    ] = evaluation
                elif coverage_censor_mode:
                    coordinate_rows[coordinate["name"]][
                        "coverage_censor_evaluation"
                    ] = {
                        "passed": False,
                        "branch_count": None,
                        "fully_resolved_variant_indices": [],
                        "coverage_censored_variant_indices": [],
                        "rejected_variants": [],
                        "critical_point_intervals": [],
                        "normalized_critical_point_spans": [],
                        "maximum_normalized_critical_point_span": 1e300,
                        "reason": "insufficient survivor return pairs",
                    }
            run_row = {
                "id": declared_run["id"],
                "configuration": {**declared_run, **config},
                "ensemble_size": len(initial),
                "checkpoint_times": result.checkpoint_times.tolist(),
                "survivor_counts": result.survivor_counts.tolist(),
                "survivor_fractions": (
                    result.survivor_counts / len(initial)
                ).tolist(),
                "final_survivor_count": len(result.survivor_ids),
                "failed_count": int(np.count_nonzero(result.failed)),
                "midpoint_crossing_count": len(result.midpoint_times),
                "coordinates": coordinate_rows,
            }
            run_rows.append(run_row)
            print(
                json.dumps(
                    {
                        "case": case["id"],
                        "run": run_row["id"],
                        "survivor_counts": run_row["survivor_counts"],
                        "branch_counts": {
                            name: (
                                value["coverage_censor_evaluation"].get(
                                    "branch_count"
                                )
                                if coverage_censor_mode
                                else value["robust_oracle"].get("branch_count")
                            )
                            for name, value in coordinate_rows.items()
                        },
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        baseline_initial = _grid(section, ensemble, declared_runs[0])
        short_audit = _short_horizon_audit(
            parameters,
            section,
            cycle,
            baseline_initial,
            manifest,
            solver,
        )
        survival = _survival_comparisons(
            run_rows, acceptance["baseline_run_id"]
        )
        expected = case.get("expected_saddle_branch_count")
        expected = int(expected) if expected is not None else None
        allowed_counts = {
            int(value)
            for value in manifest.get("path_acceptance", {}).get(
                "allowed_branch_counts",
                acceptance.get("allowed_branch_counts", [expected]),
            )
            if value is not None
        }
        observed = (
            _coverage_observed_branch_count(
                run_rows, manifest["coordinates"], allowed_counts
            )
            if coverage_censor_mode
            else _observed_branch_count(
                run_rows, manifest["coordinates"], allowed_counts
            )
        )
        required_count = expected if expected is not None else observed
        if required_count is None:
            critical = {
                coordinate["name"]: {
                    "critical_point_intervals": [],
                    "normalized_critical_point_spans": [],
                    "maximum_normalized_critical_point_span": 1e300,
                    "reason": "no common allowed branch count",
                }
                for coordinate in manifest["coordinates"]
            }
        else:
            critical = (
                _coverage_critical_convergence(
                    run_rows, manifest["coordinates"], required_count
                )
                if coverage_censor_mode
                else _critical_convergence(
                    run_rows, manifest["coordinates"], required_count
                )
            )
        case_passed = bool(
            cycle_crossings.integration_success
            and cycle_classification.label == OrbitLabel.PERIODIC
            and cycle_classification.fundamental_period == cycle_period
            and all(
                run["failed_count"] == 0
                and run["final_survivor_count"]
                >= acceptance["minimum_final_survivors"]
                and all(
                    coordinate["pair_count"] >= acceptance["minimum_return_pairs"]
                    and (
                        (
                            coordinate["coverage_censor_evaluation"]["passed"]
                            and coordinate["coverage_censor_evaluation"][
                                "branch_count"
                            ]
                            == required_count
                        )
                        if coverage_censor_mode
                        else (
                            coordinate["robust_oracle"]["resolved"]
                            and coordinate["robust_oracle"]["branch_count"]
                            == required_count
                        )
                    )
                    for coordinate in run["coordinates"].values()
                )
                for run in run_rows
            )
            and all(
                row["maximum_absolute_survivor_fraction_difference"]
                <= acceptance["maximum_survivor_fraction_difference"]
                for row in survival
            )
            and all(
                row["maximum_normalized_critical_point_span"]
                <= acceptance["maximum_across_run_normalized_critical_span"]
                for row in critical.values()
            )
            and all(
                row["integration_success"]
                and row["comparison_crossings"]
                >= manifest["short_horizon_audit"]["comparison_crossings"]
                and row["maximum_scaled_state_error"]
                <= acceptance["maximum_short_horizon_scaled_state_error"]
                and row["maximum_time_error"]
                <= acceptance["maximum_short_horizon_time_error"]
                for row in short_audit
            )
        )
        all_cases.append(
            {
                "id": case["id"],
                "parameters": asdict(parameters),
                "expected_saddle_branch_count": expected,
                "observed_saddle_branch_count": observed,
                "cycle_reference": {
                    "classification": asdict(cycle_classification),
                    "states": cycle.tolist(),
                },
                "runs": run_rows,
                "survival_convergence": survival,
                "critical_point_convergence": critical,
                "short_horizon_audit": short_audit,
                "passed": case_passed,
            }
        )

    path_evaluation = _path_evaluation(all_cases, manifest) if path_mode else None
    output = {
        "schema": (
            "butterfly.sprinkler-coverage-censor.v1"
            if coverage_censor_mode
            else (
                "butterfly.sprinkler-path-continuation.v1"
                if path_mode
                else "butterfly.sprinkler-convergence.v1"
            )
        ),
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "elapsed_seconds": time.perf_counter() - started,
        "cases": all_cases,
        "path_evaluation": path_evaluation,
        "passed": bool(
            all(case["passed"] for case in all_cases)
            and (path_evaluation is None or path_evaluation["passed"])
        ),
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "experiment_id": manifest["experiment_id"],
                "passed": output["passed"],
                "elapsed_seconds": output["elapsed_seconds"],
                "output": str(args.output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

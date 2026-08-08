#!/usr/bin/env python3
"""Qualify chaotic saddles with censor-aware, nested-horizon PIM straddles."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import io
import json
import platform
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    PIMLifetimeBatch,
    RosslerParameters,
    SolverConfig,
    advance_censor_aware_pim_straddle,
    barrio_rossler_section,
    infer_lower_support_slope_robust,
    infer_return_map_branches_robust,
    refine_censor_aware_pim_segment,
    section_return_map,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from qualify_pim_saddle_controls import (
    _combined_critical_spans,
    _cycle_reference,
    _measure_lifetime,
)


class CensoredLifetimeEvaluator:
    """Memoized adaptive lifetime oracle retaining right-censored bounds."""

    def __init__(self, parameters, section, cycle, manifest, solver, profile):
        self.parameters = parameters
        self.section = section
        self.cycle = cycle
        self.capture = manifest["capture"]
        self.pim = dict(manifest["pim"])
        self.pim["maximum_escape_returns"] = int(
            profile["maximum_escape_returns"]
        )
        self.solver = solver
        self.cache: dict[bytes, tuple[float, bool, bool, int]] = {}
        self.request_count = 0
        self.integration_count = 0
        self.executor = ProcessPoolExecutor(
            max_workers=int(self.pim["lifetime_workers"])
        )

    def close(self):
        self.executor.shutdown(wait=True)

    def __call__(self, points):
        points = np.asarray(points, dtype=np.float64)
        self.request_count += len(points)
        keys = [point.tobytes() for point in points]
        missing_indices = [
            index for index, key in enumerate(keys) if key not in self.cache
        ]
        if missing_indices:
            arguments = [
                (
                    self.parameters,
                    self.section,
                    self.cycle,
                    self.capture,
                    self.pim,
                    self.solver,
                    points[index],
                )
                for index in missing_indices
            ]
            measured = list(self.executor.map(_measure_lifetime, arguments))
            self.integration_count += len(measured)
            for source_index, value in zip(
                missing_indices, measured, strict=True
            ):
                self.cache[keys[source_index]] = value
        values = [self.cache[key] for key in keys]
        return PIMLifetimeBatch(
            lifetimes=np.asarray([value[0] for value in values]),
            censored=np.asarray(
                [not value[1] and not value[2] for value in values], dtype=bool
            ),
            failed=np.asarray([value[2] for value in values], dtype=bool),
        )

    def diagnostics_since(self, keys_before):
        new = [value for key, value in self.cache.items() if key not in keys_before]
        return {
            "unique_lifetime_evaluations": len(new),
            "censored_evaluations": sum(
                not value[1] and not value[2] for value in new
            ),
            "failed_evaluations": sum(value[2] for value in new),
            "maximum_return_count": max((value[3] for value in new), default=0),
            "maximum_lifetime": max((value[0] for value in new), default=0.0),
        }


def _nested_critical_spans(profile_rows, coordinate_name):
    coordinate_rows = [
        profile["coordinates"][coordinate_name] for profile in profile_rows
    ]
    if any(
        row["source_minimum"] is None
        or row["source_maximum"] is None
        or not row["robust_oracle"]["resolved"]
        for row in coordinate_rows
    ):
        return {
            "resolved": False,
            "critical_point_intervals": [],
            "normalized_spans": [],
            "maximum_normalized_span": 1e300,
        }
    intervals = [
        row["robust_oracle"]["critical_point_intervals"]
        for row in coordinate_rows
    ]
    if (
        not intervals
        or not intervals[0]
        or len({len(value) for value in intervals}) != 1
    ):
        return {
            "resolved": False,
            "critical_point_intervals": [],
            "normalized_spans": [],
            "maximum_normalized_span": 1e300,
        }
    domain_minimum = min(row["source_minimum"] for row in coordinate_rows)
    domain_maximum = max(row["source_maximum"] for row in coordinate_rows)
    domain_range = max(domain_maximum - domain_minimum, np.finfo(float).eps)
    combined = []
    spans = []
    for critical_index in range(len(intervals[0])):
        lower = min(value[critical_index][0] for value in intervals)
        upper = max(value[critical_index][1] for value in intervals)
        combined.append((lower, upper))
        spans.append((upper - lower) / domain_range)
    return {
        "resolved": True,
        "critical_point_intervals": combined,
        "normalized_spans": spans,
        "maximum_normalized_span": max(spans, default=0.0),
    }


def _common_resolved_branch_count(coordinate_rows, allowed_branch_counts):
    """Return one allowed count only when every coordinate resolves to it."""
    counts = []
    for row in coordinate_rows.values():
        robust = row["robust_oracle"]
        if not robust["resolved"] or robust["branch_count"] is None:
            return None
        counts.append(int(robust["branch_count"]))
    if len(set(counts)) != 1 or counts[0] not in set(allowed_branch_counts):
        return None
    return counts[0]


def _slope_predicted_branch_count(coordinate_rows, slope_config):
    """Map one unanimous, resolved coordinate slope sign to a branch count."""
    mapping = {
        int(sign): int(count)
        for sign, count in slope_config["sign_to_branch_count"].items()
    }
    counts = []
    for row in coordinate_rows.values():
        result = row.get("lower_support_slope")
        if not result or not result["resolved"] or result["slope_sign"] is None:
            return None
        predicted = mapping.get(int(result["slope_sign"]))
        if predicted is None:
            return None
        counts.append(predicted)
    return counts[0] if counts and len(set(counts)) == 1 else None


def _infer_boundary_slope(source, target, manifest):
    slope_config = manifest["boundary_slope"]
    return asdict(
        infer_lower_support_slope_robust(
            source,
            target,
            variants=manifest["oracle_variants"],
            minimum_bin_points=int(manifest["oracle_common"]["minimum_bin_points"]),
            minimum_absolute_slope=float(
                slope_config["minimum_absolute_normalized_slope"]
            ),
        )
    )


def _evaluate_slope_calibration(calibration, manifest):
    """Recompute a frozen slope-sign control from a hashed PIM state archive."""
    path = Path(calibration["states_artifact"])
    artifact_bytes = path.read_bytes()
    observed_hash = sha256_bytes(artifact_bytes)
    expected_hash = calibration["states_artifact_sha256"]
    prefix = (
        f"{calibration['case_id']}__horizon-{int(calibration['horizon'])}__"
    )
    with np.load(io.BytesIO(artifact_bytes)) as archive:
        keys = sorted(key for key in archive.files if key.startswith(prefix))
        states = [archive[key] for key in keys]
    burn_in = int(manifest["pim"]["burn_in_returns"])
    coordinate_rows = {}
    for coordinate in manifest["coordinates"]:
        axis = int(coordinate["axis"])
        source = np.concatenate(
            [values[burn_in:-1, axis] for values in states]
        ) if states else np.empty(0)
        target = np.concatenate(
            [values[burn_in + 1 :, axis] for values in states]
        ) if states else np.empty(0)
        slope = (
            _infer_boundary_slope(source, target, manifest)
            if len(source) >= int(manifest["acceptance"]["minimum_return_pairs"])
            else {
                "resolved": False,
                "slope_sign": None,
                "reason": "insufficient calibration return pairs",
            }
        )
        coordinate_rows[coordinate["name"]] = {
            "pair_count": len(source),
            "source_minimum": float(np.min(source)) if len(source) else None,
            "source_maximum": float(np.max(source)) if len(source) else None,
            "lower_support_slope": slope,
        }
    predicted = _slope_predicted_branch_count(
        coordinate_rows, manifest["boundary_slope"]
    )
    expected_sign = int(calibration["expected_slope_sign"])
    expected_count = int(calibration["expected_branch_count"])
    minimum_lines = int(manifest["acceptance"]["minimum_successful_straddles"])
    passed = (
        observed_hash == expected_hash
        and len(states) >= minimum_lines
        and predicted == expected_count
        and all(
            row["lower_support_slope"]["resolved"]
            and int(row["lower_support_slope"]["slope_sign"]) == expected_sign
            for row in coordinate_rows.values()
        )
    )
    return {
        "id": calibration["id"],
        "states_artifact": str(path),
        "states_artifact_sha256": observed_hash,
        "states_artifact_hash_matches": observed_hash == expected_hash,
        "case_id": calibration["case_id"],
        "horizon": int(calibration["horizon"]),
        "access_line_count": len(states),
        "expected_slope_sign": expected_sign,
        "expected_branch_count": expected_count,
        "slope_predicted_branch_count": predicted,
        "coordinates": coordinate_rows,
        "passed": passed,
    }


def _run_profile(
    case, profile, manifest, solver, parameters, section, cycle
):
    evaluator = CensoredLifetimeEvaluator(
        parameters, section, cycle, manifest, solver, profile
    )
    pim = manifest["pim"]
    scales = np.asarray(pim["state_coordinate_scales"], dtype=np.float64)
    successful_states = []
    line_rows = []
    state_artifacts = {}

    def mapped(points):
        states, _times, success = section_return_map(
            parameters,
            points,
            section,
            config=solver,
            maximum_flight_time=float(pim["maximum_flight_time"]),
        )
        if not np.all(success):
            raise RuntimeError("one or more PIM triple points failed to return")
        return states

    try:
        for line in pim["initial_segments"]:
            left = np.asarray(
                (section.offset, float(line["y_range"][0]), float(line["z"])),
                dtype=np.float64,
            )
            right = np.asarray(
                (section.offset, float(line["y_range"][1]), float(line["z"])),
                dtype=np.float64,
            )
            keys_before = set(evaluator.cache)
            started = time.perf_counter()
            try:
                initial = refine_censor_aware_pim_segment(
                    left,
                    right,
                    evaluator,
                    coordinate_scales=scales,
                    sample_count=int(pim["refinement_sample_count"]),
                    width_tolerance=float(pim["width_tolerance"]),
                    max_refinements=int(pim["maximum_initial_refinements"]),
                )
                straddle = advance_censor_aware_pim_straddle(
                    initial.triple,
                    mapped,
                    evaluator,
                    coordinate_scales=scales,
                    return_count=int(pim["straddle_returns"]),
                    sample_count=int(pim["refinement_sample_count"]),
                    width_tolerance=float(pim["width_tolerance"]),
                    max_refinements_per_event=int(
                        pim["maximum_refinements_per_event"]
                    ),
                )
                retained = straddle.states[int(pim["burn_in_returns"]) :]
                successful_states.append(retained)
                state_artifacts[line["id"]] = straddle.states
                row = {
                    "id": line["id"],
                    "resolved": True,
                    "initial_refinement_count": initial.refinement_count,
                    "initial_widths": initial.normalized_widths.tolist(),
                    "straddle_return_count": len(straddle.states),
                    "retained_return_count": len(retained),
                    "refinement_event_count": len(straddle.refinement_events),
                    "maximum_recorded_width": float(
                        np.max(straddle.normalized_widths)
                    ),
                    "certified_censor_block_selections": (
                        initial.certified_censor_block_selections
                        + straddle.certified_censor_block_selections
                    ),
                    "elapsed_seconds": time.perf_counter() - started,
                }
            except (RuntimeError, ValueError) as error:
                row = {
                    "id": line["id"],
                    "resolved": False,
                    "reason": str(error),
                    "elapsed_seconds": time.perf_counter() - started,
                }
            row["lifetime_diagnostics"] = evaluator.diagnostics_since(keys_before)
            line_rows.append(row)
            print(
                json.dumps(
                    {
                        "case": case["id"],
                        "profile": profile["id"],
                        "line": line["id"],
                        "resolved": row["resolved"],
                        "reason": row.get("reason"),
                        "elapsed_seconds": row["elapsed_seconds"],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    finally:
        evaluator.close()

    coordinate_rows = {}
    acceptance = manifest["acceptance"]
    expected_raw = case.get("expected_saddle_branch_count")
    expected = None if expected_raw is None else int(expected_raw)
    cpu_reference = case.get("cpu_reference")
    for coordinate in manifest["coordinates"]:
        axis = int(coordinate["axis"])
        sources = [states[:-1, axis] for states in successful_states]
        targets = [states[1:, axis] for states in successful_states]
        source = np.concatenate(sources) if sources else np.empty(0)
        target = np.concatenate(targets) if targets else np.empty(0)
        if len(source) >= int(acceptance["minimum_return_pairs"]):
            robust = asdict(
                infer_return_map_branches_robust(
                    source,
                    target,
                    variants=manifest["oracle_variants"],
                    common_options=manifest["oracle_common"],
                    minimum_variant_consensus=float(
                        acceptance["minimum_oracle_variant_consensus"]
                    ),
                    maximum_normalized_critical_point_span=float(
                        acceptance["maximum_within_pim_critical_span"]
                    ),
                )
            )
        else:
            robust = {
                "resolved": False,
                "branch_count": None,
                "critical_point_intervals": (),
                "maximum_normalized_critical_point_span": 1e300,
                "variant_consensus": 0.0,
                "reason": "insufficient censor-aware PIM return pairs",
            }
        row = {
            "pair_count": len(source),
            "source_minimum": float(np.min(source)) if len(source) else None,
            "source_maximum": float(np.max(source)) if len(source) else None,
            "robust_oracle": robust,
        }
        if "boundary_slope" in manifest and len(source) >= int(
            acceptance["minimum_return_pairs"]
        ):
            row["lower_support_slope"] = _infer_boundary_slope(
                source, target, manifest
            )
        elif "boundary_slope" in manifest:
            row["lower_support_slope"] = {
                "resolved": False,
                "slope_sign": None,
                "reason": "insufficient censor-aware PIM return pairs",
            }
        if len(source) and cpu_reference is not None:
            row["cpu_comparison"] = _combined_critical_spans(
                row, cpu_reference[coordinate["name"]]
            )
        elif cpu_reference is not None:
            row["cpu_comparison"] = {
                "resolved": False,
                "maximum_normalized_span": 1e300,
            }
        coordinate_rows[coordinate["name"]] = row

    successful_lines = sum(row["resolved"] for row in line_rows)
    censor_count = sum(
        row["lifetime_diagnostics"]["censored_evaluations"] for row in line_rows
    )
    failure_count = sum(
        row["lifetime_diagnostics"]["failed_evaluations"] for row in line_rows
    )
    certified_count = sum(
        row.get("certified_censor_block_selections", 0) for row in line_rows
    )
    allowed_branch_counts = acceptance.get(
        "allowed_branch_counts", [expected] if expected is not None else [2, 3]
    )
    observed = _common_resolved_branch_count(
        coordinate_rows, allowed_branch_counts
    )
    slope_predicted = (
        _slope_predicted_branch_count(coordinate_rows, manifest["boundary_slope"])
        if "boundary_slope" in manifest
        else None
    )
    passed = (
        successful_lines >= int(acceptance["minimum_successful_straddles"])
        and failure_count == 0
        and observed is not None
        and (expected is None or observed == expected)
        and (
            "boundary_slope" not in manifest or slope_predicted == observed
        )
        and all(
            row["pair_count"] >= int(acceptance["minimum_return_pairs"])
            and row["robust_oracle"]["resolved"]
            and (
                cpu_reference is None
                or (
                    row["cpu_comparison"]["resolved"]
                    and row["cpu_comparison"]["maximum_normalized_span"]
                    <= float(acceptance["maximum_cpu_pim_critical_span"])
                )
            )
            for row in coordinate_rows.values()
        )
    )
    return (
        {
            "id": profile["id"],
            "maximum_escape_returns": int(profile["maximum_escape_returns"]),
            "lines": line_rows,
            "successful_straddles": successful_lines,
            "censored_lifetime_evaluations": censor_count,
            "failed_lifetime_evaluations": failure_count,
            "certified_censor_block_selections": certified_count,
            "coordinates": coordinate_rows,
            "observed_saddle_branch_count": observed,
            "slope_predicted_branch_count": slope_predicted,
            "passed": passed,
        },
        state_artifacts,
    )


def _run_case(case, manifest, solver):
    fixed = manifest["fixed_parameters"]
    parameters = RosslerParameters(
        a=float(case["a"]),
        b=float(case["b"] if "b" in case else fixed["b"]),
        c=float(case["c"] if "c" in case else fixed["c"]),
    )
    section = barrio_rossler_section(parameters)
    cycle_crossings, cycle_classification = _cycle_reference(
        parameters, section, manifest, solver
    )
    stable_period = int(case["stable_period"])
    cycle = cycle_crossings.states[-stable_period:]
    profiles = []
    state_artifacts = {}
    for profile in manifest["censor_profiles"]:
        row, states = _run_profile(
            case, profile, manifest, solver, parameters, section, cycle
        )
        profiles.append(row)
        for line_id, values in states.items():
            state_artifacts[f"{profile['id']}__{line_id}"] = values

    nested = {
        coordinate["name"]: _nested_critical_spans(
            profiles, coordinate["name"]
        )
        for coordinate in manifest["coordinates"]
    }
    acceptance = manifest["acceptance"]
    profile_counts = [
        profile["observed_saddle_branch_count"] for profile in profiles
    ]
    observed = (
        profile_counts[0]
        if profile_counts
        and profile_counts[0] is not None
        and len(set(profile_counts)) == 1
        else None
    )
    profile_slope_counts = [
        profile["slope_predicted_branch_count"] for profile in profiles
    ]
    slope_predicted = (
        profile_slope_counts[0]
        if "boundary_slope" in manifest
        and profile_slope_counts
        and profile_slope_counts[0] is not None
        and len(set(profile_slope_counts)) == 1
        else None
    )
    expected_raw = case.get("expected_saddle_branch_count")
    expected = None if expected_raw is None else int(expected_raw)
    passed = (
        cycle_classification.fundamental_period == stable_period
        and all(profile["passed"] for profile in profiles)
        and observed is not None
        and (expected is None or observed == expected)
        and (
            "boundary_slope" not in manifest or slope_predicted == observed
        )
        and all(
            row["resolved"]
            and row["maximum_normalized_span"]
            <= float(acceptance["maximum_nested_horizon_critical_span"])
            for row in nested.values()
        )
    )
    return (
        {
            "id": case["id"],
            "parameters": asdict(parameters),
            "expected_saddle_branch_count": expected,
            "observed_saddle_branch_count": observed,
            "slope_predicted_branch_count": slope_predicted,
            "stable_cycle_classification": asdict(cycle_classification),
            "profiles": profiles,
            "nested_horizon_comparison": nested,
            "passed": passed,
        },
        state_artifacts,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--states-output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    allowed_schemas = {
        "butterfly.censored-pim-controls-manifest.v1",
        "butterfly.blind-censored-pim-midpoint-manifest.v1",
    }
    if manifest.get("schema") not in allowed_schemas:
        raise SystemExit("unsupported censor-aware PIM manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    slope_calibrations = []
    if "boundary_slope" in manifest:
        slope_calibrations = [
            _evaluate_slope_calibration(row, manifest)
            for row in manifest["boundary_slope"]["calibrations"]
        ]
        print(
            json.dumps(
                {
                    "boundary_slope_calibrations": [
                        {"id": row["id"], "passed": row["passed"]}
                        for row in slope_calibrations
                    ]
                },
                sort_keys=True,
            ),
            flush=True,
        )
        if not all(row["passed"] for row in slope_calibrations):
            raise SystemExit("one or more frozen boundary-slope calibrations failed")

    solver = SolverConfig(**manifest["reference_solver"])
    cases = []
    arrays = {}
    started = time.perf_counter()
    for case in manifest["cases"]:
        row, state_artifacts = _run_case(case, manifest, solver)
        cases.append(row)
        for artifact_id, states in state_artifacts.items():
            arrays[f"{case['id']}__{artifact_id}"] = states
    state_buffer = io.BytesIO()
    np.savez_compressed(state_buffer, **arrays)
    state_bytes = state_buffer.getvalue()
    atomic_write(args.states_output, state_bytes)
    receipt_schema = (
        "butterfly.blind-censored-pim-midpoint-receipt.v1"
        if manifest["schema"]
        == "butterfly.blind-censored-pim-midpoint-manifest.v1"
        else "butterfly.censored-pim-controls-receipt.v1"
    )
    receipt = {
        "schema": receipt_schema,
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "lifetime_workers": int(manifest["pim"]["lifetime_workers"]),
        },
        "states_artifact": str(args.states_output),
        "states_artifact_bytes": len(state_bytes),
        "states_artifact_sha256": sha256_bytes(state_bytes),
        "boundary_slope_calibrations": slope_calibrations,
        "cases": cases,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(case["passed"] for case in cases),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True), flush=True)
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

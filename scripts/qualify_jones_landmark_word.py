#!/usr/bin/env python3
"""Encode one held-out Jones Figure 6 landmark under a frozen alphabet."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy
from scipy.interpolate import UnivariateSpline

from butterfly import (
    OperationalPartition,
    OrbitLabel,
    PoincareSection,
    RosslerParameters,
    SolverConfig,
    classify_fundamental_period,
    collect_crossings,
    compare_cyclic_words,
    correct_periodic_orbit,
    encode_periodic_itinerary,
    infer_return_map_branches_robust,
    legacy_rossler_section,
    sprinkler_survivors,
    survivor_return_pairs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-landmark-word-manifest.v1"


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


def _historical_partition(
    coordinate: str,
    domain: tuple[float, float],
    critical_intervals: tuple[tuple[float, float], ...],
    branch_count: int,
) -> OperationalPartition:
    """Build the immutable EXP-185 historical alphabet for 2 or 3 branches."""

    if branch_count == 2:
        branch_symbols = ("1", "0")
        critical_symbols = ("C",)
    elif branch_count == 3:
        branch_symbols = ("2", "1", "0")
        critical_symbols = ("D", "C")
    else:
        raise ValueError("historical word requires a two- or three-branch map")
    return OperationalPartition(
        coordinate_name=coordinate,
        domain=domain,
        critical_intervals=critical_intervals,
        branch_symbols=branch_symbols,
        critical_symbols=critical_symbols,
        section_orientation=-1,
    )


def _binned_relation(source, target, *, bin_count: int, minimum_bin_points: int):
    source = np.asarray(source, dtype=float)
    target = np.asarray(target, dtype=float)
    edges = np.linspace(0.0, 1.0, bin_count + 1)
    indices = np.clip(np.digitize(source, edges) - 1, 0, bin_count - 1)
    x_values = []
    y_values = []
    for index in range(bin_count):
        selected = indices == index
        if np.count_nonzero(selected) < minimum_bin_points:
            continue
        x_values.append(float(np.median(source[selected])))
        y_values.append(float(np.median(target[selected])))
    order = np.argsort(x_values)
    return np.asarray(x_values)[order], np.asarray(y_values)[order]


def _spline_residuals(source, target, query, variants) -> tuple[float, ...]:
    """Return worst normalized zero-slope residual at each query point."""

    source = np.asarray(source, dtype=float)
    target = np.asarray(target, dtype=float)
    query = np.asarray(query, dtype=float)
    source_minimum = float(np.min(source))
    target_minimum = float(np.min(target))
    source_range = float(np.ptp(source))
    target_range = float(np.ptp(target))
    if source_range == 0.0 or target_range == 0.0:
        return tuple(float("inf") for _ in query)
    normalized_source = (source - source_minimum) / source_range
    normalized_target = (target - target_minimum) / target_range
    normalized_query = (query - source_minimum) / source_range
    per_variant = []
    for variant in variants:
        x_values, y_values = _binned_relation(
            normalized_source,
            normalized_target,
            bin_count=int(variant["bin_count"]),
            minimum_bin_points=int(variant.get("minimum_bin_points", 4)),
        )
        if len(x_values) < 6:
            per_variant.append(np.full(len(query), np.inf))
            continue
        spline = UnivariateSpline(
            x_values,
            y_values,
            k=3,
            s=float(variant["smoothing"]) * len(x_values),
            ext=3,
        )
        per_variant.append(np.abs(spline.derivative()(normalized_query)))
    return tuple(float(value) for value in np.max(np.asarray(per_variant), axis=0))


def _phase_aligned_error(left, right, scales) -> dict:
    """Compare equal-cardinality section cycles over cyclic phase shifts."""

    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    scales = np.asarray(scales, dtype=float)
    if left.shape != right.shape or left.ndim != 2 or left.shape[1] != 3:
        return {"resolved": False, "shift": None, "maximum_scaled_error": float("inf")}
    errors = []
    for shift in range(len(left)):
        delta = (left - np.roll(right, shift, axis=0))[:, (0, 2)] / scales
        errors.append(float(np.max(np.linalg.norm(delta, axis=1))))
    best = int(np.argmin(errors))
    return {"resolved": True, "shift": best, "maximum_scaled_error": errors[best]}


def _orbit_crossings(parameters, section, correction, solver, expected_period):
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
    return crossings.times[keep], crossings.states[keep], crossings.integration_success


def _correction_row(correction, times, states, integration_success) -> dict:
    return {
        "success": correction.success,
        "optimizer_success": correction.optimizer_success,
        "closure_error": correction.closure_error,
        "phase_residual": correction.phase_residual,
        "correction_norm": correction.correction_norm,
        "evaluations": correction.evaluations,
        "period_time": correction.period_time,
        "initial_state": correction.initial_state.tolist(),
        "section_crossing_count": len(states),
        "section_times": times.tolist(),
        "section_states": states.tolist(),
        "section_integration_success": integration_success,
    }


def _ensemble(section, options) -> np.ndarray:
    x_values = np.linspace(*options["x_range"], int(options["x_count"]))
    z_values = np.linspace(*options["z_range"], int(options["z_count"]))
    x_grid, z_grid = np.meshgrid(x_values, z_values, indexing="ij")
    return np.column_stack(
        (x_grid.ravel(), np.full(x_grid.size, section.offset), z_grid.ravel())
    )


def _coordinate_partition(result, coordinate, manifest) -> dict:
    source_values, target_values = survivor_return_pairs(result, int(coordinate["axis"]))
    variants = tuple(
        {**manifest["oracle_common"], **variant["options"]}
        for variant in manifest["oracle_variants"]
    )
    if len(source_values) < int(manifest["acceptance"]["minimum_return_pairs"]):
        return {
            "pair_count": len(source_values),
            "source_values": source_values,
            "target_values": target_values,
            "robust": {"resolved": False, "branch_count": None, "reason": "insufficient pairs"},
        }
    robust = infer_return_map_branches_robust(
        source_values,
        target_values,
        variants=variants,
        minimum_variant_consensus=1.0,
        maximum_normalized_critical_point_span=float(
            manifest["acceptance"]["maximum_normalized_critical_span"]
        ),
    )
    return {
        "pair_count": len(source_values),
        "source_values": source_values,
        "target_values": target_values,
        "robust": asdict(robust),
    }


def _word_row(partition_row, coordinate, orbit_states, solver_name, profile, manifest):
    robust = partition_row["robust"]
    branch_count = robust.get("branch_count")
    if not robust.get("resolved") or branch_count not in (2, 3):
        return {
            "profile": profile,
            "coordinate": coordinate["name"],
            "solver": solver_name,
            "resolved": False,
            "raw_word": None,
            "reason": "partition is not a resolved two- or three-branch map",
        }
    domain = (
        float(np.min(partition_row["source_values"])),
        float(np.max(partition_row["source_values"])),
    )
    intervals = tuple(tuple(pair) for pair in robust["critical_point_intervals"])
    partition = _historical_partition(
        coordinate["name"], domain, intervals, int(branch_count)
    )
    values = np.asarray(orbit_states, dtype=float)[:, int(coordinate["axis"])]
    variants = tuple(
        {**manifest["oracle_common"], **variant["options"]}
        for variant in manifest["oracle_variants"]
    )
    residuals = _spline_residuals(
        partition_row["source_values"],
        partition_row["target_values"],
        values,
        variants,
    )
    itinerary = encode_periodic_itinerary(
        values,
        partition,
        zero_slope_residuals=residuals,
        maximum_abs_zero_slope_residual=float(
            manifest["acceptance"]["maximum_abs_zero_slope_residual"]
        ),
    )
    raw = tuple(symbol for symbol in itinerary.raw_symbols if symbol is not None)
    return {
        "profile": profile,
        "coordinate": coordinate["name"],
        "solver": solver_name,
        "resolved": itinerary.resolved,
        "raw_word": "".join(raw) if itinerary.resolved else None,
        "raw_symbols": list(itinerary.raw_symbols),
        "zero_slope_residuals": list(residuals),
        "point_reasons": [point.reason for point in itinerary.points],
        "reason": itinerary.reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--states-output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Jones landmark-word manifest")
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

    transcription_bytes = Path(manifest["target"]["path"]).read_bytes()
    if sha256_bytes(transcription_bytes) != manifest["target"]["sha256"]:
        raise SystemExit("target transcription hash mismatch")
    transcription = json.loads(transcription_bytes)
    landmark = transcription["figure6"]["parameter_landmarks"][
        int(manifest["target"]["landmark_index"])
    ]
    if landmark != manifest["parameters"]:
        raise SystemExit("manifest parameters differ from the frozen source landmark")

    started = time.perf_counter()
    parameters = RosslerParameters(**manifest["parameters"])
    section = _section(parameters)
    reference_options = manifest["attractor_reference"]
    reference_solver = SolverConfig(**reference_options["solver"])
    reference = collect_crossings(
        parameters,
        reference_options["initial_state"],
        section,
        transient=float(reference_options["transient"]),
        observation_horizon=float(reference_options["observation_horizon"]),
        max_crossings=int(reference_options["max_crossings"]),
        config=reference_solver,
    )
    recurrence = classify_fundamental_period(
        reference.states, **reference_options["recurrence"]
    )
    expected_period = int(manifest["target"]["expected_period"])
    seed_state = reference.states[-expected_period - 1]
    period_seed = float(reference.times[-1] - reference.times[-expected_period - 1])

    correction_rows = {}
    orbit_states = {}
    for name, options in manifest["correction_solvers"].items():
        solver = SolverConfig(**options)
        correction = correct_periodic_orbit(
            parameters,
            seed_state,
            period_seed,
            config=solver,
            max_evaluations=int(manifest["corrector"]["maximum_evaluations"]),
            tolerance=float(manifest["corrector"]["tolerance"]),
        )
        times, states, integration_success = _orbit_crossings(
            parameters, section, correction, solver, expected_period
        )
        correction_rows[name] = _correction_row(
            correction, times, states, integration_success
        )
        orbit_states[name] = states

    orbit_parity = _phase_aligned_error(
        orbit_states["dop853"],
        orbit_states["radau"],
        manifest["capture"]["coordinate_scales"],
    )
    acceptance = manifest["acceptance"]
    reference_passed = bool(
        reference.integration_success
        and len(reference.times) >= int(reference_options["minimum_crossings"])
        and recurrence.label == OrbitLabel.PERIODIC
        and recurrence.fundamental_period == expected_period
    )
    corrections_passed = bool(
        all(
            row["success"]
            and row["section_integration_success"]
            and row["section_crossing_count"] == expected_period
            and row["closure_error"] <= float(acceptance["maximum_flow_closure"])
            and row["phase_residual"] <= float(acceptance["maximum_phase_residual"])
            for row in correction_rows.values()
        )
        and orbit_parity["resolved"]
        and orbit_parity["maximum_scaled_error"]
        <= float(acceptance["maximum_solver_orbit_scaled_error"])
    )

    initial = _ensemble(section, manifest["ensemble"])
    profile_rows = []
    state_payload = {
        "reference_times": reference.times,
        "reference_states": reference.states,
        "dop853_orbit_states": orbit_states["dop853"],
        "radau_orbit_states": orbit_states["radau"],
    }
    word_rows = []
    for profile in manifest["sprinkler_profiles"]:
        result = sprinkler_survivors(
            parameters,
            initial,
            section,
            reference.states,
            dt=float(profile["dt"]),
            horizon=float(manifest["ensemble"]["horizon"]),
            capture_coordinate_axes=tuple(manifest["capture"]["coordinate_axes"]),
            capture_coordinate_scales=tuple(manifest["capture"]["coordinate_scales"]),
            capture_radius=float(manifest["capture"]["radius"]),
            required_capture_crossings=int(manifest["capture"]["required_crossings"]),
            checkpoint_times=manifest["ensemble"]["checkpoint_times"],
            midpoint_window=tuple(manifest["ensemble"]["midpoint_window"]),
            escape_radius=float(manifest["ensemble"]["escape_radius"]),
        )
        coordinates = {}
        for coordinate in manifest["coordinates"]:
            partition_row = _coordinate_partition(result, coordinate, manifest)
            source_values = partition_row.pop("source_values")
            target_values = partition_row.pop("target_values")
            coordinates[coordinate["name"]] = partition_row
            working = {
                **partition_row,
                "source_values": source_values,
                "target_values": target_values,
            }
            for solver_name, states in orbit_states.items():
                word_rows.append(
                    _word_row(
                        working,
                        coordinate,
                        states,
                        solver_name,
                        profile["name"],
                        manifest,
                    )
                )
        profile_row = {
            "name": profile["name"],
            "dt": profile["dt"],
            "survivor_counts": result.survivor_counts.tolist(),
            "failure_count": int(np.count_nonzero(result.failed)),
            "coordinates": coordinates,
        }
        profile_rows.append(profile_row)
        state_payload[f"{profile['name']}_midpoint_states"] = result.midpoint_states
        state_payload[f"{profile['name']}_midpoint_times"] = result.midpoint_times
        state_payload[f"{profile['name']}_midpoint_ids"] = result.midpoint_trajectory_ids
        print(
            json.dumps(
                {
                    "profile": profile["name"],
                    "survivor_counts": profile_row["survivor_counts"],
                    "branch_counts": {
                        name: row["robust"].get("branch_count")
                        for name, row in coordinates.items()
                    },
                },
                sort_keys=True,
            ),
            flush=True,
        )

    checkpoint_fractions = [
        np.asarray(row["survivor_counts"], dtype=float) / len(initial)
        for row in profile_rows
    ]
    survivor_fraction_difference = float(
        np.max(np.abs(checkpoint_fractions[0] - checkpoint_fractions[1]))
    )
    partition_step_rows = []
    for coordinate in manifest["coordinates"]:
        name = coordinate["name"]
        left = profile_rows[0]["coordinates"][name]["robust"]
        right = profile_rows[1]["coordinates"][name]["robust"]
        same_count = bool(
            left.get("resolved")
            and right.get("resolved")
            and left.get("branch_count") == right.get("branch_count")
        )
        if same_count and left["branch_count"] in (2, 3):
            left_domain = profile_rows[0]["coordinates"][name]["robust"]
            left_intervals = left_domain["critical_point_intervals"]
            right_intervals = right["critical_point_intervals"]
            # Normalize each profile to its own survivor source domain.
            state_left = state_payload[f"{profile_rows[0]['name']}_midpoint_states"]
            state_right = state_payload[f"{profile_rows[1]['name']}_midpoint_states"]
            axis = int(coordinate["axis"])
            domains = [
                (float(np.min(state_left[:, axis])), float(np.max(state_left[:, axis]))),
                (float(np.min(state_right[:, axis])), float(np.max(state_right[:, axis]))),
            ]
            normalized = []
            for intervals, domain in zip((left_intervals, right_intervals), domains, strict=True):
                width = domain[1] - domain[0]
                normalized.append(
                    [((lo + hi) / 2.0 - domain[0]) / width for lo, hi in intervals]
                )
            location_difference = max(
                (abs(a - b) for a, b in zip(*normalized, strict=True)), default=0.0
            )
        else:
            location_difference = float("inf")
        partition_step_rows.append(
            {
                "coordinate": name,
                "same_branch_count": same_count,
                "maximum_normalized_critical_midpoint_difference": location_difference,
                "passed": bool(
                    same_count
                    and left.get("branch_count") in (2, 3)
                    and location_difference
                    <= float(acceptance["maximum_step_critical_location_difference"])
                ),
            }
        )

    cross_coordinate_rows = []
    for row in profile_rows:
        x_count = row["coordinates"]["x"]["robust"].get("branch_count")
        z_count = row["coordinates"]["z"]["robust"].get("branch_count")
        cross_coordinate_rows.append(
            {
                "profile": row["name"],
                "x_branch_count": x_count,
                "z_branch_count": z_count,
                "passed": bool(x_count in (2, 3) and x_count == z_count),
            }
        )

    target_words = [
        row["word"]
        for row in transcription["figure6"]["nodes"]
        if int(row["period"]) == expected_period
    ]
    for row in word_rows:
        if row["resolved"]:
            comparisons = {
                target: asdict(compare_cyclic_words(tuple(row["raw_word"]), tuple(target)))
                for target in target_words
            }
            matches = [target for target, result in comparisons.items() if result["cyclic_match"]]
            reversal_matches = [
                target
                for target, result in comparisons.items()
                if result["reversal_cyclic_match"] and not result["cyclic_match"]
            ]
        else:
            comparisons = {}
            matches = []
            reversal_matches = []
        row["target_comparisons"] = comparisons
        row["cyclic_target_matches"] = matches
        row["reversal_only_target_matches"] = reversal_matches
        row["target_membership_passed"] = len(matches) == 1

    resolved_words = [tuple(row["raw_word"]) for row in word_rows if row["resolved"]]
    word_agreement = bool(
        len(resolved_words) == len(word_rows)
        and all(
            compare_cyclic_words(resolved_words[0], word).cyclic_match
            for word in resolved_words[1:]
        )
    )
    profiles_passed = bool(
        all(
            row["failure_count"] == 0
            and row["survivor_counts"][-1] >= int(acceptance["minimum_final_survivors"])
            and row["survivor_counts"][-1] < row["survivor_counts"][0]
            and all(
                value["pair_count"] >= int(acceptance["minimum_return_pairs"])
                and value["robust"].get("resolved")
                for value in row["coordinates"].values()
            )
            for row in profile_rows
        )
    )
    partition_parity_passed = bool(
        survivor_fraction_difference
        <= float(acceptance["maximum_survivor_fraction_difference"])
        and all(row["passed"] for row in partition_step_rows)
        and all(row["passed"] for row in cross_coordinate_rows)
    )
    words_passed = bool(
        word_agreement and all(row["target_membership_passed"] for row in word_rows)
    )
    passed = bool(
        reference_passed
        and corrections_passed
        and profiles_passed
        and partition_parity_passed
        and words_passed
    )

    args.states_output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.states_output, **state_payload)
    states_hash = sha256_file(args.states_output)
    output = {
        "schema": "butterfly.jones-landmark-word.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "parameters": manifest["parameters"],
        "landmark_index": manifest["target"]["landmark_index"],
        "target_words_of_same_period": target_words,
        "reference": {
            "crossing_count": len(reference.times),
            "integration_success": reference.integration_success,
            "recurrence": asdict(recurrence),
            "passed": reference_passed,
        },
        "corrections": correction_rows,
        "orbit_parity": orbit_parity,
        "profiles": profile_rows,
        "survivor_fraction_difference": survivor_fraction_difference,
        "partition_step_parity": partition_step_rows,
        "cross_coordinate_parity": cross_coordinate_rows,
        "words": word_rows,
        "word_agreement": word_agreement,
        "gates": {
            "reference_passed": reference_passed,
            "corrections_passed": corrections_passed,
            "profiles_passed": profiles_passed,
            "partition_parity_passed": partition_parity_passed,
            "words_passed": words_passed,
            "passed": passed,
        },
        "states_artifact": str(args.states_output),
        "states_artifact_sha256": states_hash,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": passed,
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "experiment_id": manifest["experiment_id"],
                "gates": output["gates"],
                "cross_coordinate_parity": cross_coordinate_rows,
                "words": [
                    {
                        "profile": row["profile"],
                        "coordinate": row["coordinate"],
                        "solver": row["solver"],
                        "resolved": row["resolved"],
                        "raw_word": row["raw_word"],
                        "matches": row["cyclic_target_matches"],
                    }
                    for row in word_rows
                ],
                "output": str(args.output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

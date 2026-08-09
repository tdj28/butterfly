#!/usr/bin/env python3
"""Prospectively track the pre-existing Jones return-map critical point."""

from __future__ import annotations

import argparse
import json
import platform
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    OrbitLabel,
    PoincareSection,
    RosslerParameters,
    SolverConfig,
    classify_fundamental_period,
    collect_crossings,
    infer_local_critical_point_robust,
    infer_return_map_branches_robust,
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-local-critical-track-manifest.v1"


def _evaluate_case(manifest: dict, profile: dict, a_value: float) -> dict:
    fixed = manifest["fixed_parameters"]
    parameters = RosslerParameters(
        a=float(a_value), b=float(fixed["b"]), c=float(fixed["c"])
    )
    base = legacy_rossler_section(parameters)
    section = PoincareSection(
        normal=base.normal,
        offset=base.offset,
        direction=int(manifest["section"]["direction"]),
        gate_axis=base.gate_axis,
        gate_upper=base.gate_upper,
        name="legacy-small-equilibrium-half-plane:negative",
    )
    crossing_options = manifest["crossings"]
    crossings = collect_crossings(
        parameters,
        manifest["initial_state"],
        section,
        transient=float(crossing_options["transient"]),
        observation_horizon=float(crossing_options["observation_horizon"]),
        max_crossings=int(crossing_options["max_crossings"]),
        config=SolverConfig(**profile["solver"]),
    )
    recurrence = classify_fundamental_period(
        crossings.states, **manifest["recurrence"]
    )
    variants = tuple(
        {**manifest["oracle_common"], **variant["options"]}
        for variant in manifest["oracle_variants"]
    )
    coordinates = {}
    for coordinate in manifest["coordinates"]:
        name = coordinate["name"]
        values = crossings.states[:, int(coordinate["axis"])]
        source = values[:-1]
        target = values[1:]
        domain = [float(np.min(source)), float(np.max(source))]
        global_result = asdict(
            infer_return_map_branches_robust(
                source,
                target,
                variants=variants,
                minimum_variant_consensus=1.0,
                maximum_normalized_critical_point_span=float(
                    manifest["global_oracle_reporting"][
                        "maximum_normalized_critical_point_span"
                    ]
                ),
            )
        )
        local_result = asdict(
            infer_local_critical_point_robust(
                source,
                target,
                expected_normalized_location=float(coordinate["frozen_anchor"]),
                variants=variants,
                **manifest["local_critical_rule"],
            )
        )
        coordinates[name] = {
            "domain": domain,
            "global_branch_oracle": global_result,
            "local_critical": local_result,
        }
    return {
        "profile": profile["name"],
        "a": parameters.a,
        "b": parameters.b,
        "c": parameters.c,
        "crossing_count": len(crossings.times),
        "integration_success": crossings.integration_success,
        "integration_message": crossings.integration_message,
        "recurrence": asdict(recurrence),
        "coordinates": coordinates,
    }


def match_endpoint_descendant(
    coordinate: dict, expected_index: int, minimum_runner_up_margin: float
) -> dict:
    """Match a local track to a globally resolved endpoint partition."""

    local = coordinate["local_critical"]
    global_oracle = coordinate["global_branch_oracle"]
    domain_lower, domain_upper = coordinate["domain"]
    intervals = global_oracle["critical_point_intervals"]
    if not (
        local["resolved"]
        and global_oracle["resolved"]
        and global_oracle["branch_count"] == len(intervals) + 1
        and len(intervals) >= 2
    ):
        return {"resolved": False, "reason": "endpoint inputs are unresolved"}
    candidates = tuple(
        ((float(lower) + float(upper)) / 2.0 - float(domain_lower))
        / (float(domain_upper) - float(domain_lower))
        for lower, upper in intervals
    )
    location = float(local["normalized_location"])
    distances = tuple(abs(candidate - location) for candidate in candidates)
    order = sorted(range(len(candidates)), key=lambda index: (distances[index], index))
    best = order[0]
    margin = distances[order[1]] - distances[best]
    resolved = bool(best == expected_index and margin >= minimum_runner_up_margin)
    if margin < minimum_runner_up_margin:
        reason = "endpoint descendant lacks the runner-up margin"
    elif best != expected_index:
        reason = "local track selects the wrong endpoint critical"
    else:
        reason = "local track selects the frozen endpoint descendant"
    return {
        "resolved": resolved,
        "local_normalized_location": location,
        "candidate_normalized_midpoints": candidates,
        "distances": distances,
        "descendant_index": best if resolved else None,
        "runner_up_margin": margin,
        "reason": reason,
    }


def _row_lookup(rows: list[dict]) -> dict[tuple[str, float], dict]:
    return {(row["profile"], row["a"]): row for row in rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Jones local-critical manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    jobs = [
        (profile, float(a_value))
        for profile in manifest["solver_profiles"]
        for a_value in profile["a_values"]
    ]
    rows = []
    with ProcessPoolExecutor(max_workers=int(manifest["parallel_workers"])) as pool:
        futures = {
            pool.submit(_evaluate_case, manifest, profile, a_value): (
                profile["name"],
                a_value,
            )
            for profile, a_value in jobs
        }
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            print(
                json.dumps(
                    {
                        "profile": row["profile"],
                        "a": row["a"],
                        "crossing_count": row["crossing_count"],
                        "recurrence_label": row["recurrence"]["label"],
                        "global_branch_counts": {
                            name: value["global_branch_oracle"]["branch_count"]
                            for name, value in row["coordinates"].items()
                        },
                        "local_locations": {
                            name: value["local_critical"]["normalized_location"]
                            for name, value in row["coordinates"].items()
                        },
                        "local_reasons": {
                            name: value["local_critical"]["reason"]
                            for name, value in row["coordinates"].items()
                        },
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    profile_order = {
        profile["name"]: index for index, profile in enumerate(manifest["solver_profiles"])
    }
    rows.sort(key=lambda row: (profile_order[row["profile"]], row["a"]))
    acceptance = manifest["acceptance"]
    minimum_crossings = int(manifest["crossings"]["minimum_crossings"])
    integrations_passed = all(
        row["integration_success"] and row["crossing_count"] >= minimum_crossings
        for row in rows
    )
    recurrence_passed = all(
        row["recurrence"]["label"] != OrbitLabel.PERIODIC for row in rows
    )
    local_resolution_passed = all(
        value["local_critical"]["resolved"]
        for row in rows
        for value in row["coordinates"].values()
    )

    adjacent_steps = {}
    maximum_adjacent = float(acceptance["maximum_adjacent_location_step"])
    adjacent_steps_passed = True
    for profile in manifest["solver_profiles"]:
        profile_rows = [row for row in rows if row["profile"] == profile["name"]]
        for coordinate in manifest["coordinates"]:
            name = coordinate["name"]
            locations = [
                row["coordinates"][name]["local_critical"]["normalized_location"]
                for row in profile_rows
            ]
            if any(location is None for location in locations):
                steps = []
                passed = False
            else:
                steps = [
                    abs(float(right) - float(left))
                    for left, right in zip(locations[:-1], locations[1:], strict=True)
                ]
                passed = max(steps, default=0.0) <= maximum_adjacent
            adjacent_steps[f"{profile['name']}:{name}"] = {
                "steps": steps,
                "maximum": max(steps, default=None),
                "passed": passed,
            }
            adjacent_steps_passed = adjacent_steps_passed and passed

    lookup = _row_lookup(rows)
    primary_profile = acceptance["primary_profile"]
    independent_profile = acceptance["independent_profile"]
    solver_comparisons = []
    solver_parity_passed = True
    maximum_solver_delta = float(acceptance["maximum_solver_location_delta"])
    independent_a_values = next(
        profile["a_values"]
        for profile in manifest["solver_profiles"]
        if profile["name"] == independent_profile
    )
    for a_value in independent_a_values:
        for coordinate in manifest["coordinates"]:
            name = coordinate["name"]
            primary_location = lookup[(primary_profile, float(a_value))]["coordinates"][
                name
            ]["local_critical"]["normalized_location"]
            independent_location = lookup[(independent_profile, float(a_value))][
                "coordinates"
            ][name]["local_critical"]["normalized_location"]
            delta = (
                abs(float(primary_location) - float(independent_location))
                if primary_location is not None and independent_location is not None
                else float("inf")
            )
            passed = delta <= maximum_solver_delta
            solver_comparisons.append(
                {
                    "a": float(a_value),
                    "coordinate": name,
                    "primary_location": primary_location,
                    "independent_location": independent_location,
                    "absolute_delta": delta,
                    "passed": passed,
                }
            )
            solver_parity_passed = solver_parity_passed and passed

    endpoint_a = float(acceptance["three_branch_endpoint_a"])
    endpoint_identity = {}
    endpoint_identity_passed = True
    for profile in manifest["solver_profiles"]:
        row = lookup.get((profile["name"], endpoint_a))
        if row is None:
            endpoint_identity[profile["name"]] = {
                "resolved": False,
                "reason": "profile does not include the endpoint",
            }
            endpoint_identity_passed = False
            continue
        endpoint_identity[profile["name"]] = {}
        for coordinate in manifest["coordinates"]:
            name = coordinate["name"]
            result = match_endpoint_descendant(
                row["coordinates"][name],
                int(acceptance["expected_descendant_index"]),
                float(acceptance["minimum_endpoint_runner_up_margin"]),
            )
            endpoint_identity[profile["name"]][name] = result
            endpoint_identity_passed = endpoint_identity_passed and result["resolved"]

    two_endpoint_a = float(acceptance["two_branch_endpoint_a"])
    endpoint_branch_counts_passed = all(
        lookup[(profile["name"], a_value)]["coordinates"][coordinate["name"]][
            "global_branch_oracle"
        ]["resolved"]
        and lookup[(profile["name"], a_value)]["coordinates"][coordinate["name"]][
            "global_branch_oracle"
        ]["branch_count"]
        == expected_count
        for profile in manifest["solver_profiles"]
        for a_value, expected_count in ((two_endpoint_a, 2), (endpoint_a, 3))
        for coordinate in manifest["coordinates"]
    )

    passed = bool(
        integrations_passed
        and recurrence_passed
        and local_resolution_passed
        and adjacent_steps_passed
        and solver_parity_passed
        and endpoint_identity_passed
        and endpoint_branch_counts_passed
    )
    output = {
        "schema": "butterfly.jones-local-critical-track.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "rows": rows,
        "adjacent_steps": adjacent_steps,
        "solver_comparisons": solver_comparisons,
        "endpoint_identity": endpoint_identity,
        "gates": {
            "integrations_passed": integrations_passed,
            "recurrence_passed": recurrence_passed,
            "local_resolution_passed": local_resolution_passed,
            "adjacent_steps_passed": adjacent_steps_passed,
            "solver_parity_passed": solver_parity_passed,
            "endpoint_identity_passed": endpoint_identity_passed,
            "endpoint_branch_counts_passed": endpoint_branch_counts_passed,
            "passed": passed,
        },
        "passed": passed,
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "experiment_id": manifest["experiment_id"],
                "gates": output["gates"],
                "endpoint_identity": endpoint_identity,
                "output": str(args.output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

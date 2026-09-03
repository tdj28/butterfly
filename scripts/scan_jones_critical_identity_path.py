#!/usr/bin/env python3
"""Track neutral critical identity across an attracting Jones-section path."""

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
    infer_return_map_branches_robust,
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-critical-identity-path-manifest.v1"


def _unresolved_coordinate(reason: str) -> dict:
    return {
        "resolved": False,
        "branch_count": None,
        "critical_point_intervals": (),
        "maximum_normalized_critical_point_span": float("inf"),
        "variant_consensus": 0.0,
        "variant_counts": (),
        "reason": reason,
    }


def _evaluate_case(manifest: dict, a_value: float) -> dict:
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
        config=SolverConfig(**manifest["solver"]),
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
        domain = (
            [float(np.min(values[:-1])), float(np.max(values[:-1]))]
            if len(values) > 1
            else None
        )
        if recurrence.label == OrbitLabel.PERIODIC:
            coordinates[name] = {
                **_unresolved_coordinate(
                    "attractor is periodic; chaotic invariant set not sampled"
                ),
                "domain": domain,
            }
            continue
        try:
            robust = asdict(
                infer_return_map_branches_robust(
                    values[:-1],
                    values[1:],
                    variants=variants,
                    minimum_variant_consensus=1.0,
                    maximum_normalized_critical_point_span=0.03,
                )
            )
        except ValueError as error:
            robust = _unresolved_coordinate(f"oracle precondition failed: {error}")
        coordinates[name] = {**robust, "domain": domain}
    return {
        "a": parameters.a,
        "b": parameters.b,
        "c": parameters.c,
        "crossing_count": len(crossings.times),
        "integration_success": crossings.integration_success,
        "integration_message": crossings.integration_message,
        "recurrence": asdict(recurrence),
        "coordinates": coordinates,
    }


def _normalized_midpoint(coordinate: dict, critical_index: int) -> float:
    domain_lower, domain_upper = coordinate["domain"]
    lower, upper = coordinate["critical_point_intervals"][critical_index]
    return ((float(lower) + float(upper)) / 2.0 - float(domain_lower)) / (
        float(domain_upper) - float(domain_lower)
    )


def match_persistent_critical(
    two_coordinate: dict, three_coordinate: dict, rule: dict
) -> dict:
    """Apply the frozen normalized-nearest-descendant identity rule."""

    if not (
        two_coordinate["resolved"]
        and two_coordinate["branch_count"] == 2
        and len(two_coordinate["critical_point_intervals"]) == 1
        and three_coordinate["resolved"]
        and three_coordinate["branch_count"] == 3
        and len(three_coordinate["critical_point_intervals"]) == 2
    ):
        return {"resolved": False, "reason": "bracket coordinate is unresolved"}
    source = _normalized_midpoint(two_coordinate, 0)
    candidates = tuple(_normalized_midpoint(three_coordinate, index) for index in range(2))
    distances = tuple(abs(candidate - source) for candidate in candidates)
    order = sorted(range(2), key=lambda index: (distances[index], index))
    best, runner_up = order
    margin = distances[runner_up] - distances[best]
    resolved = bool(
        distances[best] <= float(rule["maximum_normalized_step"])
        and margin >= float(rule["minimum_runner_up_margin"])
    )
    if distances[best] > float(rule["maximum_normalized_step"]):
        reason = "nearest descendant exceeds the normalized-step gate"
    elif margin < float(rule["minimum_runner_up_margin"]):
        reason = "nearest descendant lacks the runner-up margin"
    else:
        reason = "unique normalized-nearest descendant"
    return {
        "resolved": resolved,
        "source_normalized_midpoint": source,
        "candidate_normalized_midpoints": candidates,
        "distances": distances,
        "descendant_index": best if resolved else None,
        "descendant_symbol": (
            rule["three_branch_critical_symbols_in_increasing_coordinate_order"][best]
            if resolved
            else None
        ),
        "runner_up_margin": margin,
        "reason": reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported Jones critical-identity path manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    rows = []
    with ProcessPoolExecutor(max_workers=int(manifest["parallel_workers"])) as pool:
        futures = {
            pool.submit(_evaluate_case, manifest, a_value): float(a_value)
            for a_value in manifest["a_values"]
        }
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            print(
                json.dumps(
                    {
                        "a": row["a"],
                        "crossing_count": row["crossing_count"],
                        "recurrence_label": row["recurrence"]["label"],
                        "fundamental_period": row["recurrence"]["fundamental_period"],
                        "branch_counts": {
                            name: value["branch_count"]
                            for name, value in row["coordinates"].items()
                        },
                        "reasons": {
                            name: value["reason"]
                            for name, value in row["coordinates"].items()
                        },
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    rows.sort(key=lambda row: row["a"])

    acceptance = manifest["acceptance"]
    primary = acceptance["primary_coordinate"]
    minimum_crossings = int(manifest["crossings"]["minimum_crossings"])
    resolved_primary = [
        row
        for row in rows
        if row["integration_success"]
        and row["crossing_count"] >= minimum_crossings
        and row["coordinates"][primary]["resolved"]
    ]
    two_rows = [
        row for row in resolved_primary if row["coordinates"][primary]["branch_count"] == 2
    ]
    three_rows = [
        row for row in resolved_primary if row["coordinates"][primary]["branch_count"] == 3
    ]
    ordered = bool(two_rows and three_rows and two_rows[-1]["a"] < three_rows[0]["a"])
    bracket_rows = (two_rows[-1], three_rows[0]) if ordered else None
    bracket = (
        [bracket_rows[0]["a"], bracket_rows[1]["a"]] if bracket_rows else None
    )
    rule = manifest["identity_rule"]
    identity = {}
    if bracket_rows:
        for coordinate in manifest["coordinates"]:
            name = coordinate["name"]
            identity[name] = match_persistent_critical(
                bracket_rows[0]["coordinates"][name],
                bracket_rows[1]["coordinates"][name],
                rule,
            )
    descendant_indices = {
        value.get("descendant_index")
        for value in identity.values()
        if value.get("resolved")
    }
    identity_agreement = bool(
        len(identity) == len(manifest["coordinates"])
        and all(value.get("resolved") for value in identity.values())
        and len(descendant_indices) == 1
    )
    bracket_width_passed = bool(
        bracket
        and bracket[1] - bracket[0]
        <= float(rule["maximum_parameter_bracket_width"])
    )
    endpoints = {
        float(item["a"]): int(item["branch_count"])
        for item in acceptance["expected_endpoints"]
    }
    endpoints_passed = all(
        any(
            row["a"] == a_value
            and row["coordinates"][primary]["resolved"]
            and row["coordinates"][primary]["branch_count"] == branch_count
            for row in rows
        )
        for a_value, branch_count in endpoints.items()
    )
    coordinate_agreement = all(
        len(
            {
                value["branch_count"]
                for value in row["coordinates"].values()
                if value["resolved"]
            }
        )
        <= 1
        for row in rows
    )
    passed = bool(
        ordered
        and bracket_width_passed
        and endpoints_passed
        and coordinate_agreement
        and identity_agreement
    )
    output = {
        "schema": "butterfly.jones-critical-identity-path.v1",
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
        "resolved_two_a_values": [row["a"] for row in two_rows],
        "resolved_three_a_values": [row["a"] for row in three_rows],
        "ordered_bracket": bracket,
        "identity": identity,
        "identity_agreement": identity_agreement,
        "bracket_width_passed": bracket_width_passed,
        "coordinate_agreement": coordinate_agreement,
        "endpoints_passed": endpoints_passed,
        "passed": passed,
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "experiment_id": manifest["experiment_id"],
                "ordered_bracket": bracket,
                "identity": identity,
                "identity_agreement": identity_agreement,
                "passed": passed,
                "output": str(args.output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

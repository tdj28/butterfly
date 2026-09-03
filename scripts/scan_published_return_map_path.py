#!/usr/bin/env python3
"""Scan a published-section Rössler path for an attracting branch transition."""
from __future__ import annotations

import argparse
import json
import platform
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
    infer_return_map_branches,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _unresolved_oracle(reason):
    return {
        "resolved": False,
        "branch_count": None,
        "critical_points": (),
        "conditional_spread_ratio": None,
        "domain_coverage": None,
        "bootstrap_consensus": None,
        "bootstrap_counts": (),
        "reason": reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.return-map-path-manifest.v1":
        raise SystemExit("unsupported return-map path manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    solver = SolverConfig(**manifest["solver"])
    crossing_config = manifest["crossings"]
    recurrence_config = manifest["recurrence"]
    fixed = manifest["fixed_parameters"]
    rows = []
    for a_value in manifest["a_values"]:
        parameters = RosslerParameters(
            a=float(a_value), b=float(fixed["b"]), c=float(fixed["c"])
        )
        crossings = collect_crossings(
            parameters,
            manifest["initial_state"],
            barrio_rossler_section(parameters),
            transient=float(crossing_config["transient"]),
            observation_horizon=float(crossing_config["observation_horizon"]),
            max_crossings=int(crossing_config["max_crossings"]),
            config=solver,
        )
        recurrence = classify_fundamental_period(
            crossings.states, **recurrence_config
        )
        coordinate_results = {}
        for coordinate in manifest["coordinates"]:
            name = coordinate["name"]
            if recurrence.label == OrbitLabel.PERIODIC:
                coordinate_results[name] = _unresolved_oracle(
                    "attractor is periodic; chaotic invariant set not sampled"
                )
                continue
            values = crossings.states[:, int(coordinate["axis"])]
            try:
                coordinate_results[name] = asdict(
                    infer_return_map_branches(
                        values[:-1], values[1:], **manifest["oracle"]
                    )
                )
            except ValueError as error:
                coordinate_results[name] = _unresolved_oracle(
                    f"oracle precondition failed: {error}"
                )
        row = {
            "a": parameters.a,
            "b": parameters.b,
            "c": parameters.c,
            "crossing_count": len(crossings.times),
            "integration_success": crossings.integration_success,
            "integration_message": crossings.integration_message,
            "recurrence": asdict(recurrence),
            "coordinates": coordinate_results,
        }
        rows.append(row)
        print(
            json.dumps(
                {
                    "a": row["a"],
                    "crossing_count": row["crossing_count"],
                    "recurrence_label": recurrence.label.value,
                    "fundamental_period": recurrence.fundamental_period,
                    "branch_counts": {
                        name: result["branch_count"]
                        for name, result in coordinate_results.items()
                    },
                    "reasons": {
                        name: result["reason"]
                        for name, result in coordinate_results.items()
                    },
                },
                sort_keys=True,
            ),
            flush=True,
        )

    acceptance = manifest["acceptance"]
    primary_name = acceptance["primary_coordinate"]
    resolved_primary = [
        row
        for row in rows
        if row["coordinates"][primary_name]["resolved"]
        and row["integration_success"]
        and row["crossing_count"] >= acceptance["minimum_crossings"]
    ]
    two_values = [
        row["a"]
        for row in resolved_primary
        if row["coordinates"][primary_name]["branch_count"] == 2
    ]
    three_values = [
        row["a"]
        for row in resolved_primary
        if row["coordinates"][primary_name]["branch_count"] == 3
    ]
    ordered = bool(two_values and three_values and max(two_values) < min(three_values))
    bracket = [max(two_values), min(three_values)] if ordered else None
    coordinate_agreement = all(
        len(
            {
                result["branch_count"]
                for result in row["coordinates"].values()
                if result["resolved"]
            }
        )
        <= 1
        for row in rows
    )
    expected_endpoints = {
        float(item["a"]): int(item["branch_count"])
        for item in acceptance["expected_endpoints"]
    }
    endpoints_passed = all(
        any(
            row["a"] == a_value
            and row["coordinates"][primary_name]["resolved"]
            and row["coordinates"][primary_name]["branch_count"] == branch_count
            for row in rows
        )
        for a_value, branch_count in expected_endpoints.items()
    )
    passed = bool(ordered and coordinate_agreement and endpoints_passed)
    output = {
        "schema": "butterfly.return-map-path.v1",
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
        "resolved_two_a_values": two_values,
        "resolved_three_a_values": three_values,
        "ordered_bracket": bracket,
        "coordinate_agreement": coordinate_agreement,
        "endpoints_passed": endpoints_passed,
        "passed": passed,
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "experiment_id": manifest["experiment_id"],
                "resolved_two_a_values": two_values,
                "resolved_three_a_values": three_values,
                "ordered_bracket": bracket,
                "coordinate_agreement": coordinate_agreement,
                "endpoints_passed": endpoints_passed,
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

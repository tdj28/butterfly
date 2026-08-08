#!/usr/bin/env python3
"""Audit a Rössler return-map branch result across representation choices."""
from __future__ import annotations

import argparse
import json
import platform
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy

from butterfly import (
    PoincareSection,
    RosslerParameters,
    SolverConfig,
    collect_crossings,
    infer_return_map_branches,
    legacy_rossler_section,
    rossler_rhs,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def _oracle_result(source, target, options):
    try:
        return asdict(infer_return_map_branches(source, target, **options))
    except ValueError as error:
        return {
            "resolved": False,
            "branch_count": None,
            "critical_points": (),
            "conditional_spread_ratio": float("inf"),
            "domain_coverage": 0.0,
            "bootstrap_consensus": 0.0,
            "bootstrap_counts": (),
            "reason": f"oracle precondition failed: {error}",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.return-map-sensitivity-manifest.v1":
        raise SystemExit("unsupported return-map sensitivity manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    solver = SolverConfig(**manifest["solver"])
    crossing_config = manifest["crossings"]
    orientation_tolerance = float(crossing_config["orientation_tolerance"])
    rows = []
    integrations = []
    for case in manifest["parameter_cases"]:
        parameters = RosslerParameters(**case["parameters"])
        base_section = legacy_rossler_section(parameters)
        for offset_delta in manifest["section_offset_deltas"]:
            section = PoincareSection(
                normal=base_section.normal,
                offset=base_section.offset + float(offset_delta),
                direction=0,
                name=f"full-plane:offset{float(offset_delta):+.6g}",
            )
            crossings = collect_crossings(
                parameters,
                manifest["initial_state"],
                section,
                transient=float(crossing_config["transient"]),
                observation_horizon=float(crossing_config["observation_horizon"]),
                max_crossings=int(crossing_config["max_full_plane_crossings"]),
                config=solver,
            )
            derivatives = np.asarray(
                [
                    np.dot(
                        section.normal,
                        rossler_rhs(time, state, parameters),
                    )
                    for time, state in zip(
                        crossings.times, crossings.states, strict=True
                    )
                ]
            )
            integration = {
                "parameter_case": case["name"],
                "parameters": case["parameters"],
                "section_offset_delta": float(offset_delta),
                "section_offset": section.offset,
                "full_plane_crossing_count": len(crossings.times),
                "integration_success": crossings.integration_success,
                "integration_message": crossings.integration_message,
                "near_tangent_crossing_count": int(
                    np.count_nonzero(np.abs(derivatives) <= orientation_tolerance)
                ),
            }
            integrations.append(integration)
            print(json.dumps(integration, sort_keys=True), flush=True)

            for orientation in manifest["orientations"]:
                sign = int(orientation["sign"])
                selected = derivatives * sign > orientation_tolerance
                oriented_states = crossings.states[selected]
                for coordinate in manifest["coordinates"]:
                    values = oriented_states[:, int(coordinate["axis"])]
                    for oracle_variant in manifest["oracle_variants"]:
                        options = {
                            **manifest["oracle_baseline"],
                            **oracle_variant.get("overrides", {}),
                        }
                        result = _oracle_result(values[:-1], values[1:], options)
                        rows.append(
                            {
                                "parameter_case": case["name"],
                                "parameters": case["parameters"],
                                "section_offset_delta": float(offset_delta),
                                "orientation": orientation["name"],
                                "orientation_sign": sign,
                                "crossing_count": len(oriented_states),
                                "coordinate": coordinate["name"],
                                "coordinate_axis": int(coordinate["axis"]),
                                "coordinate_minimum": (
                                    float(np.min(values)) if len(values) else None
                                ),
                                "coordinate_maximum": (
                                    float(np.max(values)) if len(values) else None
                                ),
                                "oracle_variant": oracle_variant["name"],
                                "oracle_options": options,
                                "oracle": result,
                            }
                        )

    acceptance = manifest["acceptance"]

    def accepted(row):
        oracle = row["oracle"]
        return bool(
            row["crossing_count"] >= acceptance["minimum_oriented_crossings"]
            and oracle["resolved"]
            and oracle["branch_count"] == acceptance["expected_branch_count"]
        )

    primary_rows = [
        row
        for row in rows
        if row["orientation"] == acceptance["primary_orientation"]
        and row["coordinate"] == acceptance["primary_coordinate"]
    ]
    primary_passed = bool(primary_rows) and all(accepted(row) for row in primary_rows)
    representation_invariance_passed = bool(rows) and all(
        accepted(row) for row in rows
    )
    counts_by_representation = {}
    for orientation in manifest["orientations"]:
        for coordinate in manifest["coordinates"]:
            key = f"{orientation['name']}:{coordinate['name']}"
            selected_rows = [
                row
                for row in rows
                if row["orientation"] == orientation["name"]
                and row["coordinate"] == coordinate["name"]
            ]
            counts_by_representation[key] = {
                "row_count": len(selected_rows),
                "resolved_count": sum(row["oracle"]["resolved"] for row in selected_rows),
                "branch_count_histogram": {
                    str(count): sum(
                        row["oracle"]["branch_count"] == count
                        for row in selected_rows
                    )
                    for count in sorted(
                        {
                            row["oracle"]["branch_count"]
                            for row in selected_rows
                            if row["oracle"]["branch_count"] is not None
                        }
                    )
                },
            }
    output = {
        "schema": "butterfly.return-map-sensitivity.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "acceptance": acceptance,
        "integrations": integrations,
        "rows": rows,
        "counts_by_representation": counts_by_representation,
        "primary_passed": primary_passed,
        "representation_invariance_passed": representation_invariance_passed,
        "passed": primary_passed,
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "experiment_id": manifest["experiment_id"],
                "integration_count": len(integrations),
                "row_count": len(rows),
                "counts_by_representation": counts_by_representation,
                "primary_passed": primary_passed,
                "representation_invariance_passed": representation_invariance_passed,
                "output": str(args.output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if primary_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

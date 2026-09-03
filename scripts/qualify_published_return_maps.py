#!/usr/bin/env python3
"""Qualify the published Rössler unimodal/bimodal return-map controls."""
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
    barrio_rossler_section,
    collect_crossings,
    infer_return_map_branches,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.published-return-map-manifest.v1":
        raise SystemExit("unsupported published return-map manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    solver = SolverConfig(**manifest["solver"])
    rows = []
    integrations = []
    for case in manifest["parameter_cases"]:
        parameters = RosslerParameters(**case["parameters"])
        published_section = barrio_rossler_section(parameters)
        for offset_delta in manifest["section_offset_deltas"]:
            section = PoincareSection(
                normal=published_section.normal,
                offset=published_section.offset + float(offset_delta),
                direction=published_section.direction,
                name=f"{published_section.name}:offset{float(offset_delta):+.6g}",
            )
            crossings = collect_crossings(
                parameters,
                manifest["initial_state"],
                section,
                transient=float(manifest["crossings"]["transient"]),
                observation_horizon=float(
                    manifest["crossings"]["observation_horizon"]
                ),
                max_crossings=int(manifest["crossings"]["max_crossings"]),
                config=solver,
            )
            integration = {
                "parameter_case": case["name"],
                "parameters": case["parameters"],
                "expected_branch_count": int(case["expected_branch_count"]),
                "section_offset_delta": float(offset_delta),
                "section_offset": section.offset,
                "crossing_count": len(crossings.times),
                "integration_success": crossings.integration_success,
                "integration_message": crossings.integration_message,
            }
            integrations.append(integration)
            print(json.dumps(integration, sort_keys=True), flush=True)
            for coordinate in manifest["coordinates"]:
                values = crossings.states[:, int(coordinate["axis"])]
                for oracle_variant in manifest["oracle_variants"]:
                    options = {
                        **manifest["oracle_baseline"],
                        **oracle_variant.get("overrides", {}),
                    }
                    result = infer_return_map_branches(
                        values[:-1], values[1:], **options
                    )
                    rows.append(
                        {
                            **integration,
                            "coordinate": coordinate["name"],
                            "coordinate_axis": int(coordinate["axis"]),
                            "coordinate_minimum": float(np.min(values)),
                            "coordinate_maximum": float(np.max(values)),
                            "oracle_variant": oracle_variant["name"],
                            "oracle_options": options,
                            "oracle": asdict(result),
                        }
                    )

    acceptance = manifest["acceptance"]

    def accepted(row):
        return bool(
            row["integration_success"]
            and row["crossing_count"] >= acceptance["minimum_crossings"]
            and row["oracle"]["resolved"]
            and row["oracle"]["branch_count"] == row["expected_branch_count"]
        )

    primary_rows = [
        row for row in rows if row["coordinate"] == acceptance["primary_coordinate"]
    ]
    primary_passed = bool(primary_rows) and all(accepted(row) for row in primary_rows)
    coordinate_crosscheck_passed = bool(rows) and all(accepted(row) for row in rows)
    output = {
        "schema": "butterfly.published-return-map-qualification.v1",
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
        "primary_passed": primary_passed,
        "coordinate_crosscheck_passed": coordinate_crosscheck_passed,
        "passed": primary_passed,
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "experiment_id": manifest["experiment_id"],
                "integration_count": len(integrations),
                "row_count": len(rows),
                "primary_passed": primary_passed,
                "coordinate_crosscheck_passed": coordinate_crosscheck_passed,
                "output": str(args.output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if primary_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

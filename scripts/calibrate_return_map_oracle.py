#!/usr/bin/env python3
"""Calibrate the gated branch oracle on a frozen chaotic Rössler control."""
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
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.return-map-oracle-calibration-manifest.v1":
        raise SystemExit("unsupported return-map calibration manifest")
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    parameters = RosslerParameters(**manifest["parameters"])
    solver = SolverConfig(**manifest["solver"])
    base_section = legacy_rossler_section(parameters)
    rows = []
    for offset_delta in manifest["section_offset_deltas"]:
        section = PoincareSection(
            normal=base_section.normal,
            offset=base_section.offset + float(offset_delta),
            direction=base_section.direction,
            gate_axis=base_section.gate_axis,
            gate_upper=base_section.gate_upper,
            name=f"{base_section.name}:offset{float(offset_delta):+.6g}",
        )
        crossings = collect_crossings(
            parameters,
            manifest["initial_state"],
            section,
            transient=float(manifest["crossings"]["transient"]),
            observation_horizon=float(manifest["crossings"]["observation_horizon"]),
            max_crossings=int(manifest["crossings"]["max_crossings"]),
            config=solver,
        )
        coordinate = crossings.states[:, int(manifest["coordinate_axis"])]
        result = infer_return_map_branches(
            coordinate[:-1], coordinate[1:], **manifest["oracle"]
        )
        row = {
            "section_offset_delta": float(offset_delta),
            "section_offset": section.offset,
            "crossing_count": len(crossings.times),
            "integration_success": crossings.integration_success,
            "integration_message": crossings.integration_message,
            "coordinate_minimum": float(np.min(coordinate)),
            "coordinate_maximum": float(np.max(coordinate)),
            "oracle": asdict(result),
        }
        rows.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
    acceptance = manifest["acceptance"]
    output = {
        "schema": "butterfly.return-map-oracle-calibration.v1",
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
        "coordinate_axis": manifest["coordinate_axis"],
        "rows": rows,
    }
    output["passed"] = bool(
        all(
            row["integration_success"]
            and row["crossing_count"] >= acceptance["minimum_crossings"]
            and row["oracle"]["resolved"]
            and row["oracle"]["branch_count"] == acceptance["expected_branch_count"]
            for row in rows
        )
    )
    atomic_write(args.output, canonical_json(output))
    print(json.dumps(output, sort_keys=True), flush=True)
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

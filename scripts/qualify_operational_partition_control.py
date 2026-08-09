#!/usr/bin/env python3
"""Qualify a neutral Jones-section partition on split dense return clouds."""

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
    OperationalPartition,
    PoincareSection,
    RosslerParameters,
    SolverConfig,
    collect_crossings,
    infer_return_map_branches_robust,
    legacy_rossler_section,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.operational-partition-control-manifest.v1"


def segment_pairs(values, *, pair_start: int, pair_count: int):
    """Return exactly ``pair_count`` consecutive map pairs."""

    values = np.asarray(values, dtype=float)
    if pair_start < 0 or pair_count < 1:
        raise ValueError("pair_start must be nonnegative and pair_count positive")
    stop = pair_start + pair_count
    if len(values) < stop + 1:
        raise ValueError("insufficient crossing values for frozen segment")
    return values[pair_start:stop], values[pair_start + 1 : stop + 1]


def compile_joint_partition(
    coordinate_name: str,
    segment_summaries: list[dict],
    *,
    branch_symbols: tuple[str, ...],
    critical_symbols: tuple[str, ...],
    section_orientation: int,
) -> dict:
    """Compile calibration/validation intervals without historical relabeling."""

    if not segment_summaries:
        raise ValueError("at least one segment summary is required")
    expected_branch_count = len(branch_symbols)
    resolved = all(
        row["resolved"]
        and row["branch_count"] == expected_branch_count
        and len(row["critical_point_intervals"]) == len(critical_symbols)
        for row in segment_summaries
    )
    domain = (
        min(float(row["domain"][0]) for row in segment_summaries),
        max(float(row["domain"][1]) for row in segment_summaries),
    )
    intervals = (
        tuple(
            (
                min(
                    float(row["critical_point_intervals"][index][0])
                    for row in segment_summaries
                ),
                max(
                    float(row["critical_point_intervals"][index][1])
                    for row in segment_summaries
                ),
            )
            for index in range(len(critical_symbols))
        )
        if resolved
        else ()
    )
    domain_range = max(domain[1] - domain[0], np.finfo(float).eps)
    normalized_spans = tuple(
        (upper - lower) / domain_range for lower, upper in intervals
    )
    maximum_span = max(normalized_spans, default=float("inf"))
    payload = {
        "resolved": resolved,
        "coordinate_name": coordinate_name,
        "domain": domain,
        "critical_intervals": intervals,
        "normalized_critical_spans": normalized_spans,
        "maximum_normalized_critical_span": maximum_span,
        "branch_symbols": branch_symbols,
        "critical_symbols": critical_symbols,
        "section_orientation": section_orientation,
        "historical_mapping": None,
    }
    if resolved:
        OperationalPartition(
            coordinate_name=coordinate_name,
            domain=domain,
            critical_intervals=intervals,
            branch_symbols=branch_symbols,
            critical_symbols=critical_symbols,
            section_orientation=section_orientation,
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported operational-partition manifest")

    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    started = time.perf_counter()
    parameters = RosslerParameters(**manifest["parameters"])
    base_section = legacy_rossler_section(parameters)
    section = PoincareSection(
        normal=base_section.normal,
        offset=base_section.offset,
        direction=int(manifest["section"]["direction"]),
        gate_axis=base_section.gate_axis,
        gate_upper=base_section.gate_upper,
        name="legacy-small-equilibrium-half-plane:negative",
    )
    integration = manifest["integration"]
    crossings = collect_crossings(
        parameters,
        manifest["initial_state"],
        section,
        transient=float(integration["transient"]),
        observation_horizon=float(integration["observation_horizon"]),
        max_crossings=int(integration["max_crossings"]),
        config=SolverConfig(**manifest["solver"]),
    )
    print(
        json.dumps(
            {
                "integration_success": crossings.integration_success,
                "crossing_count": len(crossings.times),
            },
            sort_keys=True,
        ),
        flush=True,
    )

    variant_options = tuple(
        {
            **manifest["oracle_common"],
            **variant["options"],
        }
        for variant in manifest["oracle_variants"]
    )
    rows = []
    by_coordinate: dict[str, list[dict]] = {
        coordinate["name"]: [] for coordinate in manifest["coordinates"]
    }
    for segment_name in ("calibration", "validation"):
        segment = manifest["segments"][segment_name]
        for coordinate in manifest["coordinates"]:
            values = crossings.states[:, int(coordinate["axis"])]
            source_values, target_values = segment_pairs(values, **segment)
            robust = infer_return_map_branches_robust(
                source_values,
                target_values,
                variants=variant_options,
                minimum_variant_consensus=1.0,
                maximum_normalized_critical_point_span=float(
                    manifest["acceptance"][
                        "maximum_within_segment_normalized_critical_span"
                    ]
                ),
            )
            summary = {
                "segment": segment_name,
                "coordinate": coordinate["name"],
                "pair_count": len(source_values),
                "domain": [float(np.min(source_values)), float(np.max(source_values))],
                **asdict(robust),
            }
            rows.append(summary)
            by_coordinate[coordinate["name"]].append(summary)
            print(
                json.dumps(
                    {
                        "segment": segment_name,
                        "coordinate": coordinate["name"],
                        "resolved": robust.resolved,
                        "branch_count": robust.branch_count,
                        "critical_point_intervals": robust.critical_point_intervals,
                        "maximum_normalized_critical_point_span": (
                            robust.maximum_normalized_critical_point_span
                        ),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )

    symbols = manifest["operational_symbols"]
    branch_symbols = tuple(symbols["branch_symbols_in_increasing_coordinate_order"])
    critical_symbols = tuple(
        symbols["critical_symbols_in_increasing_coordinate_order"]
    )
    partitions = {
        coordinate: compile_joint_partition(
            coordinate,
            summaries,
            branch_symbols=branch_symbols,
            critical_symbols=critical_symbols,
            section_orientation=int(manifest["section"]["direction"]),
        )
        for coordinate, summaries in by_coordinate.items()
    }
    acceptance = manifest["acceptance"]
    minimum_pairs = int(acceptance["minimum_segment_pairs"])
    passed = bool(
        crossings.integration_success
        and len(crossings.times) >= int(integration["minimum_total_crossings"])
        and all(
            row["resolved"]
            and row["branch_count"] == int(acceptance["expected_branch_count"])
            and row["pair_count"] >= minimum_pairs
            for row in rows
        )
        and all(
            partition["resolved"]
            and partition["maximum_normalized_critical_span"]
            <= float(acceptance["maximum_joint_normalized_critical_span"])
            for partition in partitions.values()
        )
    )
    output = {
        "schema": "butterfly.operational-partition-control.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "integration": {
            "success": crossings.integration_success,
            "message": crossings.integration_message,
            "crossing_count": len(crossings.times),
            "section_offset": section.offset,
            "section_gate_upper": section.gate_upper,
        },
        "segments": manifest["segments"],
        "variant_names": [row["name"] for row in manifest["oracle_variants"]],
        "rows": rows,
        "joint_partitions": partitions,
        "acceptance": acceptance,
        "historical_mapping": None,
        "passed": passed,
        "elapsed_seconds": time.perf_counter() - started,
    }
    atomic_write(args.output, canonical_json(output))
    print(
        json.dumps(
            {
                "experiment_id": manifest["experiment_id"],
                "crossing_count": len(crossings.times),
                "partitions": partitions,
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

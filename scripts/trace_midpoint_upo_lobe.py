#!/usr/bin/env python3
"""Trace a capture-truncated UPO unstable-lobe atlas at one blind midpoint."""

from __future__ import annotations

import argparse
import json
import platform
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import scipy

from butterfly import RosslerParameters, SolverConfig
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from trace_upo_unstable_lobe_atlas import _group_summaries, _stable_cycle, _trace_task


def _left_lobe_points(traces, amplitude_indices, axis, upper):
    allowed = set(int(value) for value in amplitude_indices)
    count = 0
    minimum = None
    for trace in traces:
        if trace["amplitude_index"] not in allowed:
            continue
        retained = np.asarray(
            trace["states"][: trace["retained_pre_capture_returns"]], dtype=float
        )
        if not len(retained):
            continue
        values = retained[retained[:, axis] < upper, axis]
        count += len(values)
        if len(values):
            value = float(np.min(values))
            minimum = value if minimum is None else min(minimum, value)
    return count, minimum


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.upo-midpoint-lobe-manifest.v1":
        raise SystemExit("unsupported midpoint UPO-lobe manifest")
    seed_source = manifest["source_seed_receipt"]
    seed_bytes = Path(seed_source["path"]).read_bytes()
    if sha256_bytes(seed_bytes) != seed_source["sha256"]:
        raise SystemExit("source midpoint seed receipt hash mismatch")
    seed_receipt = json.loads(seed_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    case = manifest["case"]
    solver = SolverConfig(**manifest["reference_solver"])
    parameters = RosslerParameters(**case["parameters"])
    cycle, cycle_audit = _stable_cycle(parameters, manifest, solver)
    cycle_audit["case_id"] = case["id"]
    if cycle is None or not cycle_audit["passed"]:
        raise SystemExit("stable-cycle qualification failed")
    seed_lookup = {
        row["family_id"]: row
        for row in seed_receipt["instances"]
        if row["case_id"] == case["seed_case_id"] and row["passed"]
    }
    tasks = []
    for family in manifest["families"]:
        seed = seed_lookup[family["id"]]
        for amplitude_index, epsilon in enumerate(manifest["seed_grid"]["amplitudes"]):
            for sign in (-1, 1):
                tasks.append(
                    {
                        "case_id": case["id"],
                        "family_id": family["id"],
                        "sign": sign,
                        "amplitude_index": amplitude_index,
                        "amplitude": sign * float(epsilon),
                        "parameters": case["parameters"],
                        "base_state": seed["base_section_state"],
                        "direction": seed["section_unstable_direction"],
                        "stable_cycle": cycle.tolist(),
                        "coordinate_scales": manifest["coordinate_scales"],
                        "solver": manifest["reference_solver"],
                        "return_horizon": manifest["return_horizon"],
                        "maximum_flight_time": manifest["maximum_flight_time"],
                        "capture_radius": manifest["capture"]["scaled_radius"],
                        "required_capture_crossings": manifest["capture"][
                            "required_consecutive_crossings"
                        ],
                    }
                )
    started = time.perf_counter()
    traces = []
    with ProcessPoolExecutor(max_workers=int(manifest["workers"])) as executor:
        futures = [executor.submit(_trace_task, task) for task in tasks]
        for index, future in enumerate(as_completed(futures), start=1):
            traces.append(future.result())
            if index % 20 == 0 or index == len(futures):
                print(
                    json.dumps(
                        {
                            "completed_traces": index,
                            "total_traces": len(futures),
                            "integration_failures": sum(
                                not row["integration_success"] for row in traces
                            ),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
    traces.sort(
        key=lambda row: (row["family_id"], row["sign"], row["amplitude_index"])
    )
    summary_manifest = {**manifest, "cases": [{"id": case["id"]}]}
    summaries, _ = _group_summaries(traces, summary_manifest)
    left = manifest["left_lobe"]
    fine_count, fine_minimum = _left_lobe_points(
        traces,
        manifest["seed_grid"]["fine_indices"],
        int(left["coordinate_axis"]),
        float(left["upper_bound"]),
    )
    coarse_count, coarse_minimum = _left_lobe_points(
        traces,
        manifest["seed_grid"]["coarse_indices"],
        int(left["coordinate_axis"]),
        float(left["upper_bound"]),
    )
    acceptance = manifest["acceptance"]
    lobe_passed = bool(
        fine_count >= int(acceptance["minimum_fine_lobe_points"])
        and coarse_count >= int(acceptance["minimum_coarse_lobe_points"])
    )
    receipt = {
        "schema": "butterfly.upo-midpoint-lobe-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_seed_receipt_sha256": sha256_bytes(seed_bytes),
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "stable_cycle": cycle_audit,
        "traces": traces,
        "group_summaries": summaries,
        "left_lobe": {
            "upper_bound": float(left["upper_bound"]),
            "fine_point_count": fine_count,
            "coarse_point_count": coarse_count,
            "fine_minimum_y": fine_minimum,
            "coarse_minimum_y": coarse_minimum,
            "passed": lobe_passed,
        },
        "elapsed_seconds": time.perf_counter() - started,
        "passed": bool(
            traces
            and all(row["integration_success"] for row in traces)
            and all(row["passed"] for row in summaries)
            and lobe_passed
        ),
        "scientific_scope": (
            "blind midpoint UPO lobe support, without PIM saddle classification"
        ),
    }
    atomic_write(args.output, canonical_json(receipt))
    print(
        json.dumps(
            {
                "experiment_id": receipt["experiment_id"],
                "manifest_sha256": receipt["manifest_sha256"],
                "trace_count": len(traces),
                "group_count": len(summaries),
                "left_lobe": receipt["left_lobe"],
                "elapsed_seconds": receipt["elapsed_seconds"],
                "passed": receipt["passed"],
            },
            sort_keys=True,
        )
    )
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

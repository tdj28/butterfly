#!/usr/bin/env python3
"""Run a provenance-bound initial-condition basin-plane reconnaissance."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from datetime import UTC, datetime
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from butterfly.basins import (
    BasinPlaneManifest,
    evaluate_initial_condition,
    initial_condition_grid,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def run_task(task: tuple[BasinPlaneManifest, int, tuple[float, float, float]]) -> dict:
    return evaluate_initial_condition(*task)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    if args.workers < 1:
        raise SystemExit("--workers must be positive")
    raw_manifest = args.manifest.read_bytes()
    manifest = BasinPlaneManifest.from_dict(json.loads(raw_manifest))
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("basin-plane scans require clean source")

    started_at = datetime.now(UTC)
    started = time.perf_counter()
    tasks = [
        (manifest, point_index, initial_state)
        for point_index, initial_state in initial_condition_grid(manifest)
    ]
    if args.workers == 1:
        rows = [run_task(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            rows = list(executor.map(run_task, tasks))
    rows.sort(key=lambda row: row["point_index"])
    expected_indices = list(range(manifest.x_count * manifest.y_count))
    if [row["point_index"] for row in rows] != expected_indices:
        raise RuntimeError("basin-plane workers did not return the exact grid")
    result = {
        "schema": "butterfly.basin-plane-result.v1",
        "experiment_id": manifest.experiment_id,
        "parameters": asdict(manifest.parameters),
        "shape": [manifest.x_count, manifest.y_count],
        "plane": {
            "x": [manifest.x_min, manifest.x_max, manifest.x_count],
            "y": [manifest.y_min, manifest.y_max, manifest.y_count],
            "z": manifest.z,
        },
        "row_count": len(rows),
        "rows": rows,
    }
    result_bytes = canonical_json(result)
    label_counts = {
        label: sum(row["label"] == label for row in rows)
        for label in sorted({row["label"] for row in rows})
    }
    period_counts = {
        str(period): sum(row["fundamental_period"] == period for row in rows)
        for period in sorted(
            {
                row["fundamental_period"]
                for row in rows
                if row["fundamental_period"] is not None
            }
        )
    }
    receipt = {
        "schema": "butterfly.basin-plane-receipt.v1",
        "experiment_id": manifest.experiment_id,
        "manifest_sha256": sha256_bytes(raw_manifest),
        "result_sha256": sha256_bytes(result_bytes),
        "row_count": len(rows),
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now(UTC).isoformat(),
        "elapsed_seconds": time.perf_counter() - started,
        "workers": args.workers,
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "label_counts": label_counts,
        "period_counts": period_counts,
        "all_integrations_succeeded": all(row["integration_success"] for row in rows),
    }
    atomic_write(args.output_dir / "result.json", result_bytes)
    atomic_write(args.output_dir / "receipt.json", canonical_json(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["all_integrations_succeeded"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

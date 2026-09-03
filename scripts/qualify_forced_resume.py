#!/usr/bin/env python3
"""Kill one owned tile worker mid-run, restart it, and emit a receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from butterfly.tiles import TileSpec, verify_completed_tile
from butterfly.scan import ScanManifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--tile-count", type=int, required=True)
    parser.add_argument("--tile-index", type=int, required=True)
    parser.add_argument("--kill-after", type=float, default=0.5)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.kill_after <= 0.0:
        raise SystemExit("--kill-after must be positive")

    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("forced-resume qualification requires a clean Git source")

    manifest = ScanManifest.from_path(args.manifest)
    spec = TileSpec.for_manifest(
        manifest, index=args.tile_index, count=args.tile_count
    )
    directory = args.output_root / spec.directory_name
    if directory.exists() and any(directory.iterdir()):
        raise SystemExit(f"qualification tile directory is not empty: {directory}")

    command = [
        sys.executable,
        "-m",
        "butterfly",
        "tiled-scan",
        "--manifest",
        str(args.manifest),
        "--output-root",
        str(args.output_root),
        "--tile-count",
        str(args.tile_count),
        "--tile-index",
        str(args.tile_index),
        "--resume",
    ]
    worker = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    time.sleep(args.kill_after)
    completed_before_kill = worker.poll() is not None
    if not completed_before_kill:
        worker.kill()
    first_stdout, first_stderr = worker.communicate(timeout=10)
    completion_existed_after_kill = (directory / "complete.json").exists()
    if completed_before_kill or completion_existed_after_kill:
        raise SystemExit("worker completed before the forced-kill gate could be exercised")

    restarted_at = time.perf_counter()
    restarted = subprocess.run(
        command, capture_output=True, text=True, check=False, timeout=300
    )
    restart_elapsed = time.perf_counter() - restarted_at
    if restarted.returncode != 0:
        raise SystemExit(f"restart failed: {restarted.stderr.strip()}")
    tile_receipt = verify_completed_tile(directory)
    result_path = directory / "result.json"
    completion_path = directory / "complete.json"
    receipt = {
        "schema": "butterfly.forced-resume-qualification.v1",
        "experiment_id": manifest.experiment_id,
        "source": source,
        "plan_hash": manifest.plan_hash,
        "tile_id": tile_receipt["tile_id"],
        "tile_index": args.tile_index,
        "tile_count": args.tile_count,
        "point_indices": list(spec.point_indices),
        "kill_after_seconds": args.kill_after,
        "killed_worker_returncode": worker.returncode,
        "killed_worker_stdout": first_stdout,
        "killed_worker_stderr": first_stderr,
        "completion_existed_after_kill": completion_existed_after_kill,
        "restart_returncode": restarted.returncode,
        "restart_elapsed_seconds": restart_elapsed,
        "restart_row_count": tile_receipt["row_count"],
        "result_sha256": sha256_bytes(result_path.read_bytes()),
        "completion_sha256": sha256_bytes(completion_path.read_bytes()),
        "passed": (
            not completed_before_kill
            and not completion_existed_after_kill
            and restarted.returncode == 0
        ),
    }
    atomic_write(args.receipt, canonical_json(receipt))
    print(json.dumps({"receipt": str(args.receipt), "passed": receipt["passed"]}))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

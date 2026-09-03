#!/usr/bin/env python3
"""Generate resumable GPU `(a,c)` period-atlas frames across frozen `b` values."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import platform
import time

import numpy as np
import scipy
import torch
import triton

from butterfly import classify_fundamental_period
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes
from gpu_crossing_qualify import integrate_gpu_crossings


def axis(config: dict) -> np.ndarray:
    values = np.linspace(float(config["min"]), float(config["max"]), int(config["count"]))
    if len(values) < 2:
        raise ValueError("atlas axes require at least two points")
    return values


def valid_completed_frame(
    result_path: Path,
    receipt_path: Path,
    *,
    manifest_hash: str,
    source_commit: str,
    frame_index: int,
) -> dict | None:
    if not result_path.exists() and not receipt_path.exists():
        return None
    if not result_path.exists() or not receipt_path.exists():
        raise RuntimeError(f"incomplete existing frame {frame_index}")
    result_bytes = result_path.read_bytes()
    receipt = json.loads(receipt_path.read_bytes())
    expected = (
        receipt.get("manifest_sha256") == manifest_hash
        and receipt.get("source_commit") == source_commit
        and receipt.get("frame_index") == frame_index
        and receipt.get("result_sha256") == sha256_bytes(result_bytes)
        and receipt.get("complete") is True
    )
    if not expected:
        raise RuntimeError(f"existing frame {frame_index} failed provenance validation")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    raw_manifest = args.manifest.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get("schema") != "butterfly.gpu-ac-atlas-manifest.v1":
        raise SystemExit("unsupported GPU atlas manifest")
    for evidence in manifest.get("evidence", ()):
        path = Path(evidence["path"])
        if sha256_bytes(path.read_bytes()) != evidence["sha256"]:
            raise SystemExit(f"evidence hash mismatch: {path}")
    if len(args.source_commit) != 40 or any(
        character not in "0123456789abcdef" for character in args.source_commit.lower()
    ):
        raise SystemExit("--source-commit must be a full hexadecimal Git commit")
    observed_commit = git_value("rev-parse", "HEAD")
    if observed_commit is not None and observed_commit != args.source_commit:
        raise SystemExit("declared source commit differs from the checked-out commit")
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is not available")

    manifest_hash = sha256_bytes(raw_manifest)
    a_values = axis(manifest["grid"]["a"])
    c_values = axis(manifest["grid"]["c"])
    b_values = list(map(float, manifest["grid"]["b_values"]))
    if not b_values or any(right <= left for left, right in zip(b_values, b_values[1:])):
        raise SystemExit("b_values must be nonempty and strictly increasing")
    point_count = len(a_values) * len(c_values)
    a_grid = np.repeat(a_values, len(c_values))
    c_grid = np.tile(c_values, len(a_values))
    initial_state = np.asarray(manifest["integration"]["initial_state"], dtype=np.float64)
    initial_states = np.tile(initial_state, (point_count, 1))
    classifier = manifest["classifier"]
    integration = manifest["integration"]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame_receipts = []
    started = time.perf_counter()
    for frame_index, b in enumerate(b_values):
        result_path = args.output_dir / f"frame-{frame_index:03d}.json"
        receipt_path = args.output_dir / f"frame-{frame_index:03d}.receipt.json"
        completed = valid_completed_frame(
            result_path,
            receipt_path,
            manifest_hash=manifest_hash,
            source_commit=args.source_commit,
            frame_index=frame_index,
        )
        if completed is not None:
            frame_receipts.append(completed)
            continue

        parameters = np.column_stack(
            (a_grid, np.full(point_count, b, dtype=np.float64), c_grid)
        )
        crossings, performance = integrate_gpu_crossings(
            parameters,
            initial_states,
            transient=float(integration["transient"]),
            observation_horizon=float(integration["observation_horizon"]),
            dt=float(integration["dt"]),
            chunk_steps=int(integration["chunk_steps"]),
            max_crossings=int(integration["max_crossings"]),
            dtype=torch.float64,
        )
        rows = []
        label_counts: Counter[str] = Counter()
        period_counts: Counter[int] = Counter()
        for point_index, (a, c, states) in enumerate(
            zip(a_grid, c_grid, crossings, strict=True)
        ):
            classification = classify_fundamental_period(
                states,
                max_period=int(classifier["max_period"]),
                required_repeats=int(classifier["required_repeats"]),
                atol=float(classifier["atol"]),
                rtol=float(classifier["rtol"]),
            )
            label = classification.label.value
            label_counts[label] += 1
            if classification.fundamental_period is not None:
                period_counts[classification.fundamental_period] += 1
            rows.append(
                {
                    "point_index": point_index,
                    "a": float(a),
                    "b": b,
                    "c": float(c),
                    "label": label,
                    "fundamental_period": classification.fundamental_period,
                    "recurrence_error": classification.recurrence_error,
                    "recurrence_tolerance": classification.recurrence_tolerance,
                    "crossing_count": len(states),
                }
            )
        result = {
            "schema": "butterfly.gpu-ac-atlas-frame.v1",
            "experiment_id": manifest["experiment_id"],
            "frame_index": frame_index,
            "b": b,
            "shape": [len(a_values), len(c_values)],
            "plan_hash": manifest_hash,
            "selection": manifest.get("selection"),
            "rows": rows,
        }
        result_bytes = canonical_json(result)
        failure_fraction = label_counts.get("numerical_failure", 0) / point_count
        receipt = {
            "schema": "butterfly.gpu-ac-atlas-frame-receipt.v1",
            "experiment_id": manifest["experiment_id"],
            "frame_index": frame_index,
            "b": b,
            "shape": result["shape"],
            "point_count": point_count,
            "manifest_sha256": manifest_hash,
            "source_commit": args.source_commit,
            "result_sha256": sha256_bytes(result_bytes),
            "label_counts": dict(sorted(label_counts.items())),
            "period_counts": {str(key): value for key, value in sorted(period_counts.items())},
            "performance": performance,
            "numerical_failure_fraction": failure_fraction,
            "passed": failure_fraction
            <= float(manifest["acceptance"]["maximum_numerical_failure_fraction"]),
            "complete": True,
        }
        atomic_write(result_path, result_bytes)
        atomic_write(receipt_path, canonical_json(receipt))
        frame_receipts.append(receipt)
        print(
            json.dumps(
                {
                    "frame_index": frame_index,
                    "b": b,
                    "passed": receipt["passed"],
                    "period_counts": receipt["period_counts"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    properties = torch.cuda.get_device_properties(0)
    summary = {
        "schema": "butterfly.gpu-ac-atlas-sweep-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": manifest_hash,
        "source": {
            "commit": args.source_commit,
            "observed_git_commit": observed_commit,
            "branch": git_value("branch", "--show-current"),
            "dirty": bool(git_value("status", "--porcelain")),
        },
        "frame_count": len(frame_receipts),
        "b_values": b_values,
        "shape_per_frame": [len(a_values), len(c_values)],
        "point_count_per_frame": point_count,
        "total_point_count": point_count * len(b_values),
        "frame_receipts": frame_receipts,
        "elapsed_seconds": time.perf_counter() - started,
        "passed": all(receipt["passed"] for receipt in frame_receipts),
        "environment": {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "triton": triton.__version__,
            "gpu_name": torch.cuda.get_device_name(0),
            "gpu_memory_bytes": properties.total_memory,
            "gpu_compute_capability": [properties.major, properties.minor],
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "scientific_scope": manifest.get(
            "claim_scope",
            "Single-initial-condition periodic recurrence atlas. Unresolved pixels are "
            "not classified as chaotic, and raster adjacency is not continuation.",
        ),
    }
    summary_bytes = canonical_json(summary)
    atomic_write(args.output_dir / "receipt.json", summary_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output_dir / "receipt.json"),
                "sha256": sha256_bytes(summary_bytes),
                "passed": summary["passed"],
            },
            sort_keys=True,
        )
    )
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

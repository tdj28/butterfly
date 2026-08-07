#!/usr/bin/env python3
"""Track same-period 26-neighbor raster components through a multi-b atlas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy import ndimage

from butterfly.plotting import parameter_plane
from butterfly.scan import atomic_write, canonical_json, sha256_bytes


def load_verified_frames(frame_dir: Path) -> tuple[list[dict], dict[str, str]]:
    results = []
    hashes = {}
    for result_path in sorted(frame_dir.glob("frame-[0-9][0-9][0-9].json")):
        raw = result_path.read_bytes()
        receipt = json.loads(result_path.with_suffix(".receipt.json").read_bytes())
        if receipt.get("complete") is not True or receipt.get("result_sha256") != sha256_bytes(raw):
            raise RuntimeError(f"frame provenance failed: {result_path}")
        result = json.loads(raw)
        results.append(result)
        hashes[str(result["frame_index"])] = sha256_bytes(raw)
    if not results or [result["frame_index"] for result in results] != list(range(len(results))):
        raise RuntimeError("frames must be contiguous and zero based")
    return results, hashes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-period", type=int, default=32)
    args = parser.parse_args()
    results, frame_hashes = load_verified_frames(args.frame_dir)
    planes = [parameter_plane(result, max_period=args.max_period) for result in results]
    a_values = planes[0].a_values
    c_values = planes[0].c_values
    if any(
        not np.array_equal(plane.a_values, a_values)
        or not np.array_equal(plane.c_values, c_values)
        for plane in planes[1:]
    ):
        raise RuntimeError("all frames must use identical a and c axes")
    b_values = np.asarray([result["b"] for result in results], dtype=float)
    values = np.stack([plane.values for plane in planes], axis=0)
    periods = sorted(int(value) for value in np.unique(values) if 1 <= value <= args.max_period)
    structure = np.ones((3, 3, 3), dtype=np.int8)
    components = []
    next_id = 0
    for period in periods:
        labels, count = ndimage.label(values == period, structure=structure)
        for local_label in range(1, count + 1):
            b_indices, c_indices, a_indices = np.nonzero(labels == local_label)
            frame_indices = np.unique(b_indices)
            centroids = []
            for frame_index in frame_indices:
                selected = b_indices == frame_index
                centroids.append(
                    {
                        "frame_index": int(frame_index),
                        "b": float(b_values[frame_index]),
                        "a": float(np.mean(a_values[a_indices[selected]])),
                        "c": float(np.mean(c_values[c_indices[selected]])),
                        "pixel_count": int(np.sum(selected)),
                    }
                )
            components.append(
                {
                    "component_id": next_id,
                    "period": period,
                    "voxel_count": len(b_indices),
                    "frame_count": len(frame_indices),
                    "frame_index_range": [int(frame_indices[0]), int(frame_indices[-1])],
                    "b_range": [float(b_values[frame_indices[0]]), float(b_values[frame_indices[-1]])],
                    "a_range": [float(a_values[a_indices.min()]), float(a_values[a_indices.max()])],
                    "c_range": [float(c_values[c_indices.min()]), float(c_values[c_indices.max()])],
                    "touches_boundary": {
                        "b_min": bool(np.any(b_indices == 0)),
                        "b_max": bool(np.any(b_indices == len(b_values) - 1)),
                        "a_min": bool(np.any(a_indices == 0)),
                        "a_max": bool(np.any(a_indices == len(a_values) - 1)),
                        "c_min": bool(np.any(c_indices == 0)),
                        "c_max": bool(np.any(c_indices == len(c_values) - 1)),
                    },
                    "centroid_by_frame": centroids,
                }
            )
            next_id += 1
    ranked = sorted(
        components,
        key=lambda row: (-row["frame_count"], -row["voxel_count"], row["period"], row["component_id"]),
    )
    per_period = {}
    for period in periods:
        selected = [row for row in components if row["period"] == period]
        per_period[str(period)] = {
            "component_count": len(selected),
            "components_all_frames": sum(row["frame_count"] == len(results) for row in selected),
            "components_at_least_six_frames": sum(row["frame_count"] >= 6 for row in selected),
            "voxel_count": sum(row["voxel_count"] for row in selected),
        }
    summary = {
        "schema": "butterfly.multi-b-raster-components.v1",
        "experiment_id": results[0]["experiment_id"],
        "source_frame_sha256": frame_hashes,
        "adjacency": "same-period 26-neighbor adjacency in regular (b,c,a) raster indices",
        "interpretation_limit": "components are candidates for continuation, not proof of dynamical-family connectivity",
        "shape": list(values.shape),
        "a_range": [float(a_values[0]), float(a_values[-1])],
        "b_values": b_values.tolist(),
        "c_range": [float(c_values[0]), float(c_values[-1])],
        "periods": periods,
        "component_count": len(components),
        "components_all_frames": sum(row["frame_count"] == len(results) for row in components),
        "components_at_least_six_frames": sum(row["frame_count"] >= 6 for row in components),
        "per_period": per_period,
        "components": ranked,
    }
    output_bytes = canonical_json(summary)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256_bytes(output_bytes),
                "component_count": summary["component_count"],
                "components_all_frames": summary["components_all_frames"],
                "components_at_least_six_frames": summary["components_at_least_six_frames"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

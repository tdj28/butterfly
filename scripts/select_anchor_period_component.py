#!/usr/bin/env python3
"""Select the eight-connected target-period component containing a frozen anchor."""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

import numpy as np

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


SCHEMA = "butterfly.gpu-ac-atlas-manifest.v1"


def anchor_component(period_grid, anchor_index, target_period: int) -> list[tuple[int, int]]:
    """Return one deterministic eight-connected component or an empty list."""

    values = np.asarray(period_grid)
    if values.ndim != 2:
        raise ValueError("period grid must be two-dimensional")
    start = tuple(map(int, anchor_index))
    if not (0 <= start[0] < values.shape[0] and 0 <= start[1] < values.shape[1]):
        raise ValueError("anchor index is outside the period grid")
    if values[start] != target_period:
        return []
    visited = {start}
    queue = deque((start,))
    while queue:
        i, j = queue.popleft()
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                neighbor = (i + di, j + dj)
                if (
                    0 <= neighbor[0] < values.shape[0]
                    and 0 <= neighbor[1] < values.shape[1]
                    and neighbor not in visited
                    and values[neighbor] == target_period
                ):
                    visited.add(neighbor)
                    queue.append(neighbor)
    return sorted(visited)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--frame", type=Path, required=True)
    parser.add_argument("--frame-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    frame_bytes = args.frame.read_bytes()
    frame_receipt_bytes = args.frame_receipt.read_bytes()
    manifest = json.loads(manifest_bytes)
    frame = json.loads(frame_bytes)
    receipt = json.loads(frame_receipt_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported GPU atlas manifest")
    if receipt.get("result_sha256") != sha256_bytes(frame_bytes):
        raise SystemExit("frame hash mismatch")
    if receipt.get("manifest_sha256") != sha256_bytes(manifest_bytes):
        raise SystemExit("manifest hash mismatch")
    if frame.get("experiment_id") != manifest.get("experiment_id"):
        raise SystemExit("experiment mismatch")
    shape = tuple(map(int, frame["shape"]))
    if len(frame["rows"]) != shape[0] * shape[1]:
        raise SystemExit("frame row count does not match shape")
    a_values = np.asarray(sorted({float(row["a"]) for row in frame["rows"]}))
    c_values = np.asarray(sorted({float(row["c"]) for row in frame["rows"]}))
    if shape != (len(a_values), len(c_values)):
        raise SystemExit("frame axes do not match shape")
    periods = np.full(shape, -1, dtype=int)
    for row in frame["rows"]:
        point_index = int(row["point_index"])
        if not 0 <= point_index < periods.size:
            raise SystemExit("point index outside frame")
        i, j = divmod(point_index, shape[1])
        value = row.get("fundamental_period")
        periods[i, j] = -1 if value is None else int(value)
    selection = manifest["selection"]
    anchor = selection["anchor"]
    anchor_index = (
        int(np.argmin(np.abs(a_values - float(anchor["a"])))),
        int(np.argmin(np.abs(c_values - float(anchor["c"])))),
    )
    target_period = int(selection["target_period"])
    points = anchor_component(periods, anchor_index, target_period)
    if points:
        point_indices = [i * shape[1] + j for i, j in points]
        a_range = [float(a_values[min(i for i, _ in points)]), float(a_values[max(i for i, _ in points)])]
        c_range = [float(c_values[min(j for _, j in points)]), float(c_values[max(j for _, j in points)])]
        touches = {
            "a_min": any(i == 0 for i, _ in points),
            "a_max": any(i == shape[0] - 1 for i, _ in points),
            "c_min": any(j == 0 for _, j in points),
            "c_max": any(j == shape[1] - 1 for _, j in points),
        }
    else:
        point_indices = []
        a_range = None
        c_range = None
        touches = None
    output = {
        "schema": "butterfly.anchor-period-component.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "frame_sha256": sha256_bytes(frame_bytes),
        "frame_receipt_sha256": sha256_bytes(frame_receipt_bytes),
        "source_commit": receipt.get("source_commit"),
        "target_period": target_period,
        "anchor": anchor,
        "anchor_index": list(anchor_index),
        "anchor_grid_parameters": {
            "a": float(a_values[anchor_index[0]]),
            "b": float(frame["b"]),
            "c": float(c_values[anchor_index[1]]),
        },
        "anchor_period": int(periods[anchor_index]),
        "component_point_count": len(points),
        "point_indices": point_indices,
        "a_range": a_range,
        "c_range": c_range,
        "touches_boundary": touches,
        "passed": bool(points),
        "claim_scope": "deterministic raster component selection only; adjacency is not periodic-orbit continuation or a center claim",
    }
    atomic_write(args.output, canonical_json(output))
    print(json.dumps({key: output[key] for key in ("passed", "anchor_period", "component_point_count", "a_range", "c_range", "touches_boundary")}, sort_keys=True))
    return 0 if output["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

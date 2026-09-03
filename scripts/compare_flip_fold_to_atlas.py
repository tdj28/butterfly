#!/usr/bin/env python3
"""Compare the refined flip fold line with independent coarse atlas frames."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import scipy

from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def predicted_fold(fold: dict, target_b: float) -> tuple[float, float]:
    fit = fold["quadratic_fit"]
    b_coefficients = np.asarray(fit["b_coefficients"], dtype=float).copy()
    b_coefficients[-1] -= target_b
    roots = np.roots(b_coefficients)
    candidates = [
        float(root.real)
        for root in roots
        if abs(root.imag) < 1e-10
        and 4.9 - float(fit["c_center"]) <= root.real <= 5.3 - float(fit["c_center"])
    ]
    if len(candidates) != 1:
        raise RuntimeError(f"b={target_b} has {len(candidates)} fold-line roots")
    centered_c = candidates[0]
    c = centered_c + float(fit["c_center"])
    a = float(np.polyval(np.asarray(fit["a_coefficients"], dtype=float), centered_c))
    return a, c


def nearest_distance(mask: np.ndarray, a_grid: np.ndarray, c_grid: np.ndarray, a: float, c: float, da: float, dc: float) -> float:
    indices = np.argwhere(mask)
    if not len(indices):
        return float("inf")
    distances = np.sqrt(
        ((a_grid[indices[:, 0]] - a) / da) ** 2
        + ((c_grid[indices[:, 1]] - c) / dc) ** 2
    )
    return float(np.min(distances))


def adjacency_distance(periods: np.ndarray, a_grid: np.ndarray, c_grid: np.ndarray, a: float, c: float, da: float, dc: float) -> float:
    midpoints = []
    for di, dj in ((1, 0), (0, 1), (1, 1), (1, -1)):
        i0 = slice(max(0, -di), min(periods.shape[0], periods.shape[0] - di))
        j0 = slice(max(0, -dj), min(periods.shape[1], periods.shape[1] - dj))
        i1 = slice(max(0, di), min(periods.shape[0], periods.shape[0] + di))
        j1 = slice(max(0, dj), min(periods.shape[1], periods.shape[1] + dj))
        left = periods[i0, j0]
        right = periods[i1, j1]
        matches = ((left == 5) & (right == 10)) | ((left == 10) & (right == 5))
        for local_i, local_j in np.argwhere(matches):
            base_i = local_i + max(0, -di)
            base_j = local_j + max(0, -dj)
            midpoints.append(
                ((a_grid[base_i] + a_grid[base_i + di]) / 2.0, (c_grid[base_j] + c_grid[base_j + dj]) / 2.0)
            )
    if not midpoints:
        return float("inf")
    return min(
        float(np.hypot((mid_a - a) / da, (mid_c - c) / dc))
        for mid_a, mid_c in midpoints
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--fold-receipt", type=Path, required=True)
    parser.add_argument("--atlas-receipt", type=Path, required=True)
    parser.add_argument("--frames", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--figure", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.flip-fold-atlas-comparison-manifest.v1":
        raise SystemExit("unsupported fold-atlas comparison manifest")
    fold_bytes = args.fold_receipt.read_bytes()
    atlas_bytes = args.atlas_receipt.read_bytes()
    if sha256_bytes(fold_bytes) != manifest["source_receipt_sha256"]["fold"]:
        raise SystemExit("fold receipt hash does not match manifest")
    if sha256_bytes(atlas_bytes) != manifest["source_receipt_sha256"]["atlas"]:
        raise SystemExit("atlas receipt hash does not match manifest")
    fold = json.loads(fold_bytes)
    atlas = json.loads(atlas_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("fold-atlas comparison requires clean source")

    selected_b = list(map(float, manifest["b_values"]))
    frame_receipts = {float(row["b"]): row for row in atlas["frame_receipts"]}
    started = time.perf_counter()
    rows = []
    plot_data = []
    for target_b in selected_b:
        frame_info = frame_receipts[target_b]
        frame_path = args.frames / f"frame-{int(frame_info['frame_index']):03d}.json"
        raw = frame_path.read_bytes()
        if sha256_bytes(raw) != frame_info["result_sha256"]:
            raise SystemExit(f"frame b={target_b} hash mismatch")
        frame = json.loads(raw)
        a_values = np.asarray(sorted({float(row["a"]) for row in frame["rows"]}))
        c_values = np.asarray(sorted({float(row["c"]) for row in frame["rows"]}))
        by_coordinate = {(float(row["a"]), float(row["c"])): row for row in frame["rows"]}
        periods = np.full((len(a_values), len(c_values)), -1, dtype=int)
        labels = np.empty(periods.shape, dtype=object)
        for i, a in enumerate(a_values):
            for j, c in enumerate(c_values):
                datum = by_coordinate[(a, c)]
                labels[i, j] = datum["label"]
                if datum["fundamental_period"] is not None:
                    periods[i, j] = int(datum["fundamental_period"])
        predicted_a, predicted_c = predicted_fold(fold, target_b)
        da = float(a_values[1] - a_values[0])
        dc = float(c_values[1] - c_values[0])
        distance_5 = nearest_distance(periods == 5, a_values, c_values, predicted_a, predicted_c, da, dc)
        distance_10 = nearest_distance(periods == 10, a_values, c_values, predicted_a, predicted_c, da, dc)
        edge_distance = adjacency_distance(periods, a_values, c_values, predicted_a, predicted_c, da, dc)
        rows.append(
            {
                "b": target_b,
                "predicted_a": predicted_a,
                "predicted_c": predicted_c,
                "nearest_period5_grid_distance": distance_5,
                "nearest_period10_grid_distance": distance_10,
                "nearest_period5_10_adjacency_grid_distance": edge_distance,
                "frame_sha256": sha256_bytes(raw),
            }
        )
        plot_data.append((target_b, predicted_a, predicted_c, a_values, c_values, periods, labels))

    fig, axes = plt.subplots(2, 3, figsize=(12.0, 7.2), constrained_layout=True)
    cmap = ListedColormap(["#d9d9d9", "#4c78a8", "#f58518", "#9ecae1"])
    crop = manifest["plot_half_width"]
    for axis, data in zip(axes.ravel(), plot_data, strict=True):
        target_b, predicted_a, predicted_c, a_values, c_values, periods, labels = data
        encoded = np.zeros(periods.shape, dtype=int)
        encoded[periods == 5] = 1
        encoded[periods == 10] = 2
        encoded[(periods > 0) & (periods != 5) & (periods != 10)] = 3
        a_mask = np.abs(a_values - predicted_a) <= float(crop["a"])
        c_mask = np.abs(c_values - predicted_c) <= float(crop["c"])
        image = encoded[np.ix_(a_mask, c_mask)].T
        axis.imshow(
            image,
            origin="lower",
            aspect="auto",
            interpolation="nearest",
            extent=[a_values[a_mask][0], a_values[a_mask][-1], c_values[c_mask][0], c_values[c_mask][-1]],
            cmap=cmap,
            vmin=0,
            vmax=3,
        )
        axis.scatter([predicted_a], [predicted_c], marker="x", s=80, linewidths=2.0, color="crimson")
        axis.set_title(f"b={target_b:.2f}")
        axis.set_xlabel("a")
        axis.set_ylabel("c")
    fig.suptitle("Independent EXP-021 atlas near the predicted flip fold line\n(gray unresolved, blue period 5, orange period 10, pale other periodic; red x prediction)")
    args.figure.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.figure.with_name(f".{args.figure.stem}.tmp{args.figure.suffix}")
    fig.savefig(temporary, dpi=int(manifest["figure_dpi"]))
    plt.close(fig)
    temporary.replace(args.figure)
    figure_bytes = args.figure.read_bytes()

    acceptance = manifest["acceptance"]
    both_near = sum(
        row["nearest_period5_grid_distance"] <= float(acceptance["maximum_grid_distance"])
        and row["nearest_period10_grid_distance"] <= float(acceptance["maximum_grid_distance"])
        for row in rows
    )
    adjacency_near = sum(
        row["nearest_period5_10_adjacency_grid_distance"] <= float(acceptance["maximum_grid_distance"])
        for row in rows
    )
    receipt = {
        "schema": "butterfly.flip-fold-atlas-comparison-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": {"fold": sha256_bytes(fold_bytes), "atlas": sha256_bytes(atlas_bytes)},
        "source": source,
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "numpy": np.__version__, "scipy": scipy.__version__},
        "rows": rows,
        "frames_with_both_periods_near": both_near,
        "frames_with_period5_10_adjacency_near": adjacency_near,
        "figure": {"path": str(args.figure), "sha256": hashlib.sha256(figure_bytes).hexdigest(), "bytes": len(figure_bytes), "dpi": int(manifest["figure_dpi"])},
        "elapsed_seconds": time.perf_counter() - started,
    }
    receipt["passed"] = bool(
        len(rows) == int(acceptance["required_frames"])
        and both_near >= int(acceptance["minimum_frames_with_both_periods_near"])
        and adjacency_near >= int(acceptance["minimum_frames_with_adjacency_near"])
    )
    receipt["interpretation_limit"] = "A coarse finite-time single-basin raster comparison is only an independent alignment screen; targeted converged scans and orbit boundaries are required for causal geometry."
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

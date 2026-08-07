#!/usr/bin/env python3
"""Refine, fit, and plot the sampled fold line of the flip surface."""

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
import numpy as np
import scipy

from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def vector(row: dict) -> np.ndarray:
    return np.concatenate(
        (
            np.asarray(row["initial_state"], dtype=float),
            (float(row["period_time"]), float(row["a"]), float(row["b"])),
            np.asarray(row["event_eigenvector"], dtype=float),
        )
    )


def seed_row(values: list[float], c: float) -> dict:
    return {
        "initial_state": values[:3],
        "period_time": values[3],
        "a": values[4],
        "b": values[5],
        "c": c,
        "event_eigenvector": values[6:9],
    }


def fit_quality(observed: np.ndarray, predicted: np.ndarray) -> tuple[float, float]:
    residual = observed - predicted
    denominator = float(np.sum((observed - np.mean(observed)) ** 2))
    r_squared = 1.0 - float(np.sum(residual**2)) / denominator
    return float(np.max(np.abs(residual))), r_squared


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-slices", type=Path, required=True)
    parser.add_argument("--source-extension", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--figure", type=Path, required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "butterfly.flip-fold-line-manifest.v1":
        raise SystemExit("unsupported flip fold-line manifest")
    slices_bytes = args.source_slices.read_bytes()
    extension_bytes = args.source_extension.read_bytes()
    if sha256_bytes(slices_bytes) != manifest["source_receipt_sha256"]["slices"]:
        raise SystemExit("source slices receipt hash does not match manifest")
    if sha256_bytes(extension_bytes) != manifest["source_receipt_sha256"]["extension"]:
        raise SystemExit("source extension receipt hash does not match manifest")
    slices_receipt = json.loads(slices_bytes)
    extension_receipt = json.loads(extension_bytes)
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("fold-line analysis requires clean source")

    local_points = int(manifest["local_fit_points"])
    started = time.perf_counter()
    traces: dict[float, list[dict]] = {}
    folds = []
    for result in slices_receipt["slices"]:
        c = float(result["c"])
        rows = [seed_row(values, c) for values in result["seed_variables"]] + result["rows"]
        if abs(c - float(extension_receipt["fixed_c"])) < 1e-12:
            rows += extension_receipt["new_rows"]
        traces[c] = rows
        vectors = np.asarray([vector(row) for row in rows])
        increments = np.linalg.norm(np.diff(vectors, axis=0), axis=1)
        arc = np.concatenate(([0.0], np.cumsum(increments)))
        b_values = np.asarray([row["b"] for row in rows], dtype=float)
        a_values = np.asarray([row["a"] for row in rows], dtype=float)
        minimum = int(np.argmin(b_values))
        radius = local_points // 2
        if minimum - radius < 0 or minimum + radius >= len(rows):
            raise SystemExit(f"c={c} minimum lacks the frozen local fit stencil")
        selection = slice(minimum - radius, minimum + radius + 1)
        center = arc[minimum]
        local_arc = arc[selection] - center
        b_coefficients = np.polyfit(local_arc, b_values[selection], 2)
        if b_coefficients[0] <= 0.0:
            raise SystemExit(f"c={c} local b curvature is not positive")
        vertex_offset = float(-b_coefficients[1] / (2.0 * b_coefficients[0]))
        if not float(local_arc[0]) <= vertex_offset <= float(local_arc[-1]):
            raise SystemExit(f"c={c} fitted vertex leaves the frozen stencil")
        a_coefficients = np.polyfit(local_arc, a_values[selection], 2)
        refined_a = float(np.polyval(a_coefficients, vertex_offset))
        refined_b = float(np.polyval(b_coefficients, vertex_offset))
        folds.append(
            {
                "c": c,
                "a": refined_a,
                "b": refined_b,
                "sample_index": minimum,
                "sample_a": float(a_values[minimum]),
                "sample_b": float(b_values[minimum]),
                "vertex_arc_offset": vertex_offset,
                "local_b_curvature": float(2.0 * b_coefficients[0]),
                "local_stencil_points": local_points,
            }
        )

    folds.sort(key=lambda row: row["c"])
    c_values = np.asarray([row["c"] for row in folds])
    centered_c = c_values - float(manifest["fit_c_center"])
    fold_a = np.asarray([row["a"] for row in folds])
    fold_b = np.asarray([row["b"] for row in folds])
    a_coefficients = np.polyfit(centered_c, fold_a, 2)
    b_coefficients = np.polyfit(centered_c, fold_b, 2)
    predicted_a = np.polyval(a_coefficients, centered_c)
    predicted_b = np.polyval(b_coefficients, centered_c)
    max_a_residual, a_r_squared = fit_quality(fold_a, predicted_a)
    max_b_residual, b_r_squared = fit_quality(fold_b, predicted_b)
    monotone_a = bool(np.all(np.diff(fold_a) < 0.0))
    monotone_b = bool(np.all(np.diff(fold_b) < 0.0))

    fig = plt.figure(figsize=(11.8, 5.1), constrained_layout=True)
    surface_axis = fig.add_subplot(1, 2, 1, projection="3d")
    projection_axis = fig.add_subplot(1, 2, 2)
    colors = plt.cm.viridis(np.linspace(0.05, 0.95, len(traces)))
    for color, (c, rows) in zip(colors, sorted(traces.items()), strict=True):
        surface_axis.plot(
            [row["a"] for row in rows],
            np.full(len(rows), c),
            [row["b"] for row in rows],
            color=color,
            linewidth=1.5,
        )
    surface_axis.plot(fold_a, c_values, fold_b, color="crimson", marker="o", linewidth=2.4, label="refined fold line")
    surface_axis.set_xlabel("a")
    surface_axis.set_ylabel("c")
    surface_axis.set_zlabel(r"flip parameter $b_*$")
    surface_axis.set_title("Fold-safe slices of the period-doubling surface")
    surface_axis.view_init(elev=26, azim=-126)
    surface_axis.legend(fontsize=8)

    projection_axis.plot(c_values, fold_a, color="tab:blue", marker="o", label="fold a")
    twin = projection_axis.twinx()
    twin.plot(c_values, fold_b, color="tab:red", marker="s", label="fold b")
    projection_axis.set_xlabel("c")
    projection_axis.set_ylabel("fold a", color="tab:blue")
    twin.set_ylabel("fold b", color="tab:red")
    projection_axis.tick_params(axis="y", labelcolor="tab:blue")
    twin.tick_params(axis="y", labelcolor="tab:red")
    projection_axis.set_title("Smooth drift of the sampled fold line")
    projection_axis.grid(True, alpha=0.25)

    args.figure.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.figure.with_name(f".{args.figure.stem}.tmp{args.figure.suffix}")
    fig.savefig(temporary, dpi=int(manifest["figure_dpi"]))
    plt.close(fig)
    temporary.replace(args.figure)
    figure_bytes = args.figure.read_bytes()

    acceptance = manifest["acceptance"]
    receipt = {
        "schema": "butterfly.flip-fold-line-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source_receipt_sha256": {
            "slices": sha256_bytes(slices_bytes),
            "extension": sha256_bytes(extension_bytes),
        },
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "fold_rows": folds,
        "quadratic_fit": {
            "c_center": float(manifest["fit_c_center"]),
            "a_coefficients": a_coefficients.tolist(),
            "b_coefficients": b_coefficients.tolist(),
            "a_max_absolute_residual": max_a_residual,
            "b_max_absolute_residual": max_b_residual,
            "a_r_squared": a_r_squared,
            "b_r_squared": b_r_squared,
        },
        "monotone_decreasing_a_with_c": monotone_a,
        "monotone_decreasing_b_with_c": monotone_b,
        "figure": {
            "path": str(args.figure),
            "sha256": hashlib.sha256(figure_bytes).hexdigest(),
            "bytes": len(figure_bytes),
            "dpi": int(manifest["figure_dpi"]),
        },
        "elapsed_seconds": time.perf_counter() - started,
    }
    receipt["passed"] = bool(
        len(folds) == int(acceptance["required_fold_points"])
        and all(row["local_b_curvature"] > 0.0 for row in folds)
        and monotone_a
        and monotone_b
        and max_a_residual <= float(acceptance["max_quadratic_a_residual"])
        and max_b_residual <= float(acceptance["max_quadratic_b_residual"])
        and a_r_squared >= float(acceptance["minimum_r_squared"])
        and b_r_squared >= float(acceptance["minimum_r_squared"])
    )
    receipt["interpretation_limit"] = "Five refined fold points establish a smooth local fold line over c=4.9..5.3, not global continuation, a cusp classification, or atlas-window causality."
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

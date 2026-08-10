#!/usr/bin/env python3
"""Build publication figures for parameter-plane and local-mesh geometry."""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import BoundaryNorm, ListedColormap, Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
import numpy as np

from butterfly.plotting import parameter_plane, pixel_edges
from butterfly.scan import atomic_write, canonical_json, sha256_bytes
from scripts.animate_ac_atlas import colors, load_frames


def _write_figure(fig, path: Path, dpi: int) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    fig.savefig(temporary, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    temporary.replace(path)
    raw = path.read_bytes()
    return {
        "path": str(path),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "dpi": dpi,
    }


def render_multib(frames: list[dict], output: Path, *, dpi: int, max_period: int):
    cmap, norm = colors(max_period)
    fig, axes = plt.subplots(3, 4, figsize=(13.0, 8.7), constrained_layout=True)
    for axis, frame in zip(axes.ravel(), frames, strict=False):
        plane = parameter_plane(frame, max_period=max_period)
        a_left, a_right = pixel_edges(plane.a_values)
        c_bottom, c_top = pixel_edges(plane.c_values)
        axis.imshow(
            plane.values,
            origin="lower",
            interpolation="nearest",
            aspect="auto",
            extent=(a_left, a_right, c_bottom, c_top),
            cmap=cmap,
            norm=norm,
            rasterized=True,
        )
        axis.set_title(rf"$b={frame['b']:.2f}$", fontsize=10)
        axis.set_xlabel(r"$a$", fontsize=9)
        axis.set_ylabel(r"$c$", fontsize=9)
        axis.tick_params(labelsize=8)
    for axis in axes.ravel()[len(frames) :]:
        axis.set_visible(False)
    colorbar = fig.colorbar(
        ScalarMappable(norm=norm, cmap=cmap),
        ax=axes,
        ticks=[1, 2, 3, 4, 5, 6, 8, 10, 12, 14],
        fraction=0.018,
        pad=0.01,
    )
    colorbar.set_label("Detected fundamental period")
    fig.suptitle(
        r"Rössler periodic-window superstructure across $b$",
        fontsize=16,
    )
    return _write_figure(fig, output, dpi)


def _draw_plane(axis, plane, cmap, norm):
    a_left, a_right = pixel_edges(plane.a_values)
    c_bottom, c_top = pixel_edges(plane.c_values)
    return axis.imshow(
        plane.values,
        origin="lower",
        interpolation="nearest",
        aspect="auto",
        extent=(a_left, a_right, c_bottom, c_top),
        cmap=cmap,
        norm=norm,
        rasterized=True,
    )


def render_global_and_zoom(
    frame: dict,
    zoom_frame: dict,
    zoom_component: dict,
    output: Path,
    *,
    dpi: int,
    max_period: int,
):
    cmap, norm = colors(max_period)
    global_plane = parameter_plane(frame, max_period=max_period)
    zoom_plane = parameter_plane(zoom_frame, max_period=max_period)
    fig, axes = plt.subplots(1, 2, figsize=(13.4, 5.7), constrained_layout=True)
    _draw_plane(axes[0], global_plane, cmap, norm)
    axes[0].scatter(
        [0.1798], [10.3084], marker="*", s=125, c="#e31a1c", edgecolor="black",
        linewidth=0.7, zorder=6,
    )
    axes[0].scatter(
        [0.215], [7.6], marker="*", s=115, c="#ffd92f", edgecolor="black",
        linewidth=0.7, zorder=6,
    )
    axes[0].scatter(
        [0.21564], [6.124], marker="X", s=80, c="#f72585", edgecolor="black",
        linewidth=0.7, zorder=6,
    )
    axes[0].add_patch(
        Rectangle(
            (0.2135, 5.9), 0.004, 2.3, fill=False, edgecolor="black",
            linewidth=1.4, linestyle="--", zorder=5,
        )
    )
    axes[0].set_title(r"Global $b=0.2$ recurrence atlas")
    axes[0].set_xlabel(r"$a$")
    axes[0].set_ylabel(r"$c$")

    _draw_plane(axes[1], zoom_plane, cmap, norm)
    component_mask = np.zeros(zoom_frame["shape"], dtype=float)
    for point_index in zoom_component["point_indices"]:
        i, j = divmod(int(point_index), zoom_frame["shape"][1])
        component_mask[i, j] = 1.0
    axes[1].contour(
        zoom_plane.a_values,
        zoom_plane.c_values,
        component_mask.T,
        levels=(0.5,),
        colors=("black",),
        linewidths=(1.2,),
    )
    axes[1].scatter(
        [0.215], [7.6], marker="*", s=125, c="#ffd92f", edgecolor="black",
        linewidth=0.7, zorder=6,
    )
    axes[1].scatter(
        [0.21564], [6.124], marker="X", s=85, c="#f72585", edgecolor="black",
        linewidth=0.7, zorder=6,
    )
    axes[1].set_title("Period-6 landmark band (50x axis refinement)")
    axes[1].set_xlabel(r"$a$")
    axes[1].set_ylabel(r"$c$")
    colorbar = fig.colorbar(
        ScalarMappable(norm=norm, cmap=cmap),
        ax=axes,
        ticks=[1, 2, 3, 4, 5, 6, 8, 10, 12, 14],
        fraction=0.025,
        pad=0.01,
    )
    colorbar.set_label("Detected fundamental period")
    handles = [
        Line2D((0,), (0,), marker="*", linestyle="none", markerfacecolor="#e31a1c",
               markeredgecolor="black", markersize=10, label="reported hub"),
        Line2D((0,), (0,), marker="*", linestyle="none", markerfacecolor="#ffd92f",
               markeredgecolor="black", markersize=10, label="second period-6 landmark"),
        Line2D((0,), (0,), marker="X", linestyle="none", markerfacecolor="#f72585",
               markeredgecolor="black", markersize=8, label="first period-6 landmark"),
        Line2D((0,), (0,), color="black", linewidth=1.2,
               label="second-landmark period-6 component"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=True, fontsize=9)
    fig.suptitle("Global structure and resolved period-6 landmarks", fontsize=16)
    return _write_figure(fig, output, dpi)


def _center_component(document: dict) -> set[tuple[int, int]]:
    passed = {
        tuple(row["grid_index"])
        for row in document["candidates"]
        if row["passed"]
    }
    center = document["grid"]["required_center"]
    center_index = min(
        passed,
        key=lambda ij: (
            abs(document["grid"]["a_values"][ij[0]] - center["a"])
            + abs(document["grid"]["c_values"][ij[1]] - center["c"])
        ),
    )
    queue = deque([center_index])
    selected = {center_index}
    while queue:
        i, j = queue.popleft()
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                neighbor = (i + di, j + dj)
                if di == dj == 0 or neighbor not in passed or neighbor in selected:
                    continue
                selected.add(neighbor)
                queue.append(neighbor)
    return selected


def render_local_mesh(document: dict, output: Path, *, dpi: int):
    a_values = np.asarray(document["grid"]["a_values"], dtype=float)
    c_values = np.asarray(document["grid"]["c_values"], dtype=float)
    shape = tuple(document["grid"]["shape"])
    status = np.zeros(shape, dtype=int)
    modulus = np.full(shape, np.nan)
    rows = {tuple(row["grid_index"]): row for row in document["candidates"]}
    center_component = _center_component(document)
    for index, row in rows.items():
        if row["passed"]:
            status[index] = 2 if index in center_component else 1
            modulus[index] = row["dominant_nontrivial_multiplier"]["modulus"]
    a_left, a_right = pixel_edges(a_values)
    c_bottom, c_top = pixel_edges(c_values)
    extent = (a_left, a_right, c_bottom, c_top)
    fig, axes = plt.subplots(1, 2, figsize=(12.7, 5.5), constrained_layout=True)
    status_cmap = ListedColormap(("#d9d9d9", "#3182bd", "#ffd92f"))
    status_norm = BoundaryNorm((-0.5, 0.5, 1.5, 2.5), status_cmap.N)
    axes[0].imshow(
        status.T, origin="lower", interpolation="nearest", aspect="auto",
        extent=extent, cmap=status_cmap, norm=status_norm, rasterized=True,
    )
    center_mask = np.zeros(shape, dtype=float)
    for index in center_component:
        center_mask[index] = 1.0
    axes[0].contour(
        a_values, c_values, center_mask.T, levels=(0.5,), colors="black",
        linewidths=1.1,
    )
    axes[0].scatter([0.21555], [7.372], marker="*", s=125, c="#e31a1c",
                    edgecolor="black", linewidth=0.7, zorder=5)
    axes[0].set_title("Qualified local orbit mesh")
    axes[0].set_xlabel(r"$a$")
    axes[0].set_ylabel(r"$c$")
    axes[0].legend(
        handles=[
            Patch(facecolor="#d9d9d9", label="failed at least one gate"),
            Patch(facecolor="#3182bd", label="qualified orbit"),
            Patch(facecolor="#ffd92f", edgecolor="black", label="center component"),
        ],
        loc="upper right", fontsize=8,
    )
    masked = np.ma.masked_invalid(modulus.T)
    image = axes[1].imshow(
        masked, origin="lower", interpolation="nearest", aspect="auto",
        extent=extent, cmap="viridis", norm=Normalize(0.0, 1.0), rasterized=True,
    )
    axes[1].contour(
        a_values, c_values, center_mask.T, levels=(0.5,), colors="white",
        linewidths=1.0,
    )
    axes[1].scatter([0.21555], [7.372], marker="*", s=125, c="#e31a1c",
                    edgecolor="white", linewidth=0.7, zorder=5)
    axes[1].set_title("Stable dominant Floquet modulus")
    axes[1].set_xlabel(r"$a$")
    axes[1].set_ylabel(r"$c$")
    colorbar = fig.colorbar(image, ax=axes[1], fraction=0.045, pad=0.02)
    colorbar.set_label(r"$|\lambda_{\mathrm{dom}}|$")
    fig.suptitle(
        "Dense period-6 correction near the direct-critical localization",
        fontsize=15,
    )
    return _write_figure(fig, output, dpi)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame-dir", type=Path, required=True)
    parser.add_argument("--zoom-frame", type=Path, required=True)
    parser.add_argument("--zoom-receipt", type=Path, required=True)
    parser.add_argument("--zoom-component", type=Path, required=True)
    parser.add_argument("--local-mesh", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=240)
    parser.add_argument("--max-period", type=int, default=32)
    args = parser.parse_args()
    frames, frame_hashes = load_frames(args.frame_dir)
    zoom_bytes = args.zoom_frame.read_bytes()
    zoom_receipt_bytes = args.zoom_receipt.read_bytes()
    zoom_component_bytes = args.zoom_component.read_bytes()
    local_mesh_bytes = args.local_mesh.read_bytes()
    zoom_frame = json.loads(zoom_bytes)
    zoom_receipt = json.loads(zoom_receipt_bytes)
    zoom_component = json.loads(zoom_component_bytes)
    local_mesh = json.loads(local_mesh_bytes)
    if zoom_receipt["result_sha256"] != sha256_bytes(zoom_bytes):
        raise SystemExit("zoom frame receipt mismatch")
    if zoom_component["frame_sha256"] != sha256_bytes(zoom_bytes):
        raise SystemExit("zoom component mismatch")
    if sha256_bytes(local_mesh_bytes) != "db4c3a0f46ac972c44424a8370f1a0bac4d5545f2a5fe73c86097306463efa6a":
        raise SystemExit("local mesh hash mismatch")
    results = {
        "superstructure": render_multib(
            frames,
            args.output_dir / "fig01-multib-superstructure.png",
            dpi=args.dpi,
            max_period=args.max_period,
        ),
        "global_and_zoom": render_global_and_zoom(
            frames[5],
            zoom_frame,
            zoom_component,
            args.output_dir / "fig02-global-and-period6-zoom.png",
            dpi=args.dpi,
            max_period=args.max_period,
        ),
        "local_mesh": render_local_mesh(
            local_mesh,
            args.output_dir / "fig08-local-period6-mesh.png",
            dpi=args.dpi,
        ),
    }
    receipt = {
        "schema": "butterfly.paper-parameter-figures.v1",
        "frame_sha256": frame_hashes,
        "zoom_frame_sha256": sha256_bytes(zoom_bytes),
        "zoom_receipt_sha256": sha256_bytes(zoom_receipt_bytes),
        "zoom_component_sha256": sha256_bytes(zoom_component_bytes),
        "local_mesh_sha256": sha256_bytes(local_mesh_bytes),
        "outputs": results,
    }
    atomic_write(
        args.output_dir / "parameter-figures.receipt.json",
        canonical_json(receipt),
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

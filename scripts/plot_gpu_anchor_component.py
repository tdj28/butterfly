#!/usr/bin/env python3
"""Render a verified GPU atlas frame with its frozen anchor component outlined."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

from butterfly.plotting import SPECIAL_CODES, parameter_plane, pixel_edges
from butterfly.scan import atomic_write, canonical_json, sha256_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--frame", type=Path, required=True)
    parser.add_argument("--frame-receipt", type=Path, required=True)
    parser.add_argument("--component", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--max-period", type=int, default=32)
    args = parser.parse_args()
    if args.output.suffix.lower() not in (".png", ".pdf", ".svg"):
        raise SystemExit("output must be PNG, PDF, or SVG")
    manifest_bytes = args.manifest.read_bytes()
    frame_bytes = args.frame.read_bytes()
    frame_receipt_bytes = args.frame_receipt.read_bytes()
    component_bytes = args.component.read_bytes()
    manifest = json.loads(manifest_bytes)
    frame = json.loads(frame_bytes)
    receipt = json.loads(frame_receipt_bytes)
    component = json.loads(component_bytes)
    if receipt.get("manifest_sha256") != sha256_bytes(manifest_bytes):
        raise SystemExit("manifest hash mismatch")
    if receipt.get("result_sha256") != sha256_bytes(frame_bytes):
        raise SystemExit("frame hash mismatch")
    if component.get("manifest_sha256") != sha256_bytes(manifest_bytes):
        raise SystemExit("component manifest hash mismatch")
    if component.get("frame_sha256") != sha256_bytes(frame_bytes):
        raise SystemExit("component frame hash mismatch")
    plane = parameter_plane(frame, max_period=args.max_period)
    special_order = ("numerical_failure", "escaping", "unresolved", "quasiperiodic")
    special_colors = ("#7f0000", "#ffffff", "#d9d9d9", "#35b779")
    period_colors = plt.colormaps["turbo"](
        np.linspace(0.05, 0.95, args.max_period)
    )
    colors = (
        list(special_colors)
        + [tuple(map(float, color)) for color in period_colors]
        + ["#081d58", "#54278f"]
    )
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(
        np.arange(
            SPECIAL_CODES["numerical_failure"] - 0.5,
            SPECIAL_CODES["multistable"] + 1.5,
        ),
        cmap.N,
    )
    a_left, a_right = pixel_edges(plane.a_values)
    c_bottom, c_top = pixel_edges(plane.c_values)
    component_mask = np.zeros(frame["shape"], dtype=float)
    for point_index in component["point_indices"]:
        i, j = divmod(int(point_index), frame["shape"][1])
        component_mask[i, j] = 1.0
    fig, axis = plt.subplots(figsize=(8.0, 6.2), constrained_layout=True)
    image = axis.imshow(
        plane.values,
        origin="lower",
        interpolation="nearest",
        aspect="auto",
        extent=(a_left, a_right, c_bottom, c_top),
        cmap=cmap,
        norm=norm,
        rasterized=True,
    )
    axis.contour(
        plane.a_values,
        plane.c_values,
        component_mask.T,
        levels=(0.5,),
        colors=("#111111",),
        linewidths=(1.25,),
    )
    anchor = component["anchor_grid_parameters"]
    axis.scatter(
        [anchor["a"]],
        [anchor["c"]],
        marker="*",
        s=120,
        facecolor="#fff176",
        edgecolor="#111111",
        linewidth=0.8,
        zorder=5,
    )
    axis.set_xlabel(r"$a$")
    axis.set_ylabel(r"$c$")
    axis.set_title(rf"Jones second period-6 window, $b={frame['b']:.1f}$")
    axis.set_xlim(float(plane.a_values[0]), float(plane.a_values[-1]))
    axis.set_ylim(float(plane.c_values[0]), float(plane.c_values[-1]))
    colorbar = fig.colorbar(
        image,
        ax=axis,
        boundaries=np.arange(0.5, args.max_period + 1.5),
        ticks=list(plane.periods_present),
        fraction=0.045,
        pad=0.03,
    )
    colorbar.set_label("Detected fundamental period")
    handles = [
        Patch(facecolor="#d9d9d9", edgecolor="#333333", label="unresolved"),
        Line2D(
            (0,),
            (0,),
            color="#111111",
            linewidth=1.25,
            label="anchor period-6 component",
        ),
        Line2D(
            (0,),
            (0,),
            marker="*",
            linestyle="none",
            markerfacecolor="#fff176",
            markeredgecolor="#111111",
            markersize=11,
            label="Jones landmark",
        ),
    ]
    axis.legend(handles=handles, loc="upper right", frameon=True, fontsize=8)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    output_receipt = {
        "schema": "butterfly.gpu-anchor-component-figure.v1",
        "experiment_id": frame["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "frame_sha256": sha256_bytes(frame_bytes),
        "frame_receipt_sha256": sha256_bytes(frame_receipt_bytes),
        "component_sha256": sha256_bytes(component_bytes),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "shape": frame["shape"],
        "periods_present": list(plane.periods_present),
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(output_receipt),
    )
    print(json.dumps(output_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

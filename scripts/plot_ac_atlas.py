#!/usr/bin/env python3
"""Render a verified scan as a provenance-bound `(a,c)` period atlas."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
import numpy as np

from butterfly.plotting import SPECIAL_CODES, parameter_plane, pixel_edges
from butterfly.scan import atomic_write, canonical_json, sha256_bytes
from butterfly.tiles import verify_completed_aggregate


def period_colors(max_period: int) -> list[tuple[float, float, float, float]]:
    sampled = plt.colormaps["turbo"](np.linspace(0.05, 0.95, max_period))
    return [tuple(map(float, color)) for color in sampled]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aggregate-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--title")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--max-period", type=int, default=32)
    args = parser.parse_args()
    if args.output.suffix.lower() not in (".png", ".pdf", ".svg"):
        raise SystemExit("--output must end in .png, .pdf, or .svg")

    aggregate_receipt = verify_completed_aggregate(args.aggregate_dir)
    result_path = args.aggregate_dir / "result.json"
    result_bytes = result_path.read_bytes()
    result = json.loads(result_bytes)
    plane = parameter_plane(result, max_period=args.max_period)

    special_order = [
        "numerical_failure",
        "escaping",
        "unresolved",
        "quasiperiodic",
    ]
    special_colors = ["#7f0000", "#ffffff", "#d9d9d9", "#35b779"]
    colors = special_colors + period_colors(args.max_period) + ["#081d58", "#54278f"]
    code_min = SPECIAL_CODES["numerical_failure"]
    code_max = SPECIAL_CODES["multistable"]
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(np.arange(code_min - 0.5, code_max + 1.5), cmap.N)
    a_left, a_right = pixel_edges(plane.a_values)
    c_bottom, c_top = pixel_edges(plane.c_values)

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
    axis.set_xlabel(r"$a$")
    axis.set_ylabel(r"$c$")
    axis.set_title(args.title or f"Rössler period atlas at b = {result['rows'][0]['b']:g}")
    axis.set_xlim(float(plane.a_values[0]), float(plane.a_values[-1]))
    axis.set_ylim(float(plane.c_values[0]), float(plane.c_values[-1]))

    if plane.periods_present:
        colorbar = fig.colorbar(
            image,
            ax=axis,
            boundaries=np.arange(0.5, args.max_period + 1.5),
            ticks=list(plane.periods_present),
            fraction=0.045,
            pad=0.03,
        )
        colorbar.set_label("Detected fundamental period")
    labels = set(plane.labels_present)
    legend_colors = dict(zip(special_order, special_colors, strict=True))
    legend_colors.update({"chaotic": "#081d58", "multistable": "#54278f"})
    handles = [
        Patch(facecolor=legend_colors[label], edgecolor="#333333", label=label.replace("_", " "))
        for label in legend_colors
        if label in labels
    ]
    if handles:
        axis.legend(
            handles=handles,
            loc="upper right",
            frameon=True,
            fontsize=8,
            title="Nonperiodic status",
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    figure_receipt = {
        "schema": "butterfly.ac-atlas-figure-receipt.v1",
        "experiment_id": result["experiment_id"],
        "source_result_sha256": sha256_bytes(result_bytes),
        "source_plan_hash": result["plan_hash"],
        "verified_aggregate_result_sha256": aggregate_receipt["result_sha256"],
        "output_file": args.output.name,
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "output_bytes": len(output_bytes),
        "shape": result["shape"],
        "a_range": [float(plane.a_values[0]), float(plane.a_values[-1])],
        "b": float(result["rows"][0]["b"]),
        "c_range": [float(plane.c_values[0]), float(plane.c_values[-1])],
        "periods_present": list(plane.periods_present),
        "labels_present": list(plane.labels_present),
        "max_period": args.max_period,
        "dpi": args.dpi,
    }
    receipt_path = args.output.with_suffix(args.output.suffix + ".receipt.json")
    atomic_write(receipt_path, canonical_json(figure_receipt))
    print(
        json.dumps(
            {
                "output": str(args.output),
                "receipt": str(receipt_path),
                "sha256": figure_receipt["output_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

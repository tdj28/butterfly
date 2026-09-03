#!/usr/bin/env python3
"""Plot a provenance-bound local surface of coupled periodic unit events."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()
    raw = args.receipt.read_bytes()
    receipt = json.loads(raw)
    if receipt.get("schema") != "butterfly.unit-event-surface-patch-receipt.v1":
        raise SystemExit("unsupported event-surface receipt")

    a_values = np.asarray(receipt["a_values"], dtype=float)
    c_values = np.asarray(receipt["c_values"], dtype=float)
    by_coordinate = {(row["a"], row["c"]): row for row in receipt["rows"]}
    b_grid = np.asarray(
        [[by_coordinate[(a, c)]["b"] for a in a_values] for c in c_values],
        dtype=float,
    )
    a_grid, c_grid = np.meshgrid(a_values, c_values)

    fig = plt.figure(figsize=(11.4, 4.9), constrained_layout=True)
    surface_axis = fig.add_subplot(1, 2, 1, projection="3d")
    contour_axis = fig.add_subplot(1, 2, 2)
    surface = surface_axis.plot_surface(
        a_grid,
        c_grid,
        b_grid,
        cmap="viridis",
        edgecolor="black",
        linewidth=0.35,
        antialiased=True,
        alpha=0.92,
    )
    surface_axis.scatter(a_grid, c_grid, b_grid, color="black", s=8)
    surface_axis.set_xlabel("a")
    surface_axis.set_ylabel("c")
    surface_axis.set_zlabel(r"event $b_*(a,c)$")
    surface_axis.set_title("Corrected period-5 +1 event surface")
    surface_axis.view_init(elev=27, azim=-130)
    fig.colorbar(surface, ax=surface_axis, pad=0.08, shrink=0.72, label=r"$b_*$")

    levels = np.linspace(float(np.min(b_grid)), float(np.max(b_grid)), 13)
    contour = contour_axis.contourf(a_grid, c_grid, b_grid, levels=levels, cmap="viridis")
    contour_axis.contour(
        a_grid, c_grid, b_grid, levels=levels, colors="black", linewidths=0.35, alpha=0.65
    )
    contour_axis.scatter(a_grid, c_grid, color="white", edgecolor="black", s=22)
    contour_axis.set_xlabel("Rössler parameter a")
    contour_axis.set_ylabel("Rössler parameter c")
    contour_axis.set_title(r"$(a,c)$ contours of the corrected event parameter $b_*$")
    fig.colorbar(contour, ax=contour_axis, label=r"$b_*(a,c)$")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    figure_receipt = {
        "schema": "butterfly.unit-event-surface-figure-receipt.v1",
        "experiment_id": receipt["experiment_id"],
        "source_receipt_sha256": sha256_bytes(raw),
        "output_file": args.output.name,
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "output_bytes": len(output_bytes),
        "dpi": args.dpi,
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(figure_receipt),
    )
    print(json.dumps(figure_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

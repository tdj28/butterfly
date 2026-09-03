#!/usr/bin/env python3
"""Render an initial-condition basin-plane result with categorical periods."""

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

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


SPECIAL = {"numerical_failure": -2, "unresolved": -1}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()
    result_bytes = args.result.read_bytes()
    result = json.loads(result_bytes)
    if result.get("schema") != "butterfly.basin-plane-result.v1":
        raise SystemExit("unsupported basin-plane result")
    x_count, y_count = result["shape"]
    values = np.full((y_count, x_count), SPECIAL["unresolved"], dtype=np.int16)
    labels = set()
    periods = set()
    for row in result["rows"]:
        x_index, y_index = divmod(row["point_index"], y_count)
        labels.add(row["label"])
        if row["label"] == "periodic":
            values[y_index, x_index] = int(row["fundamental_period"])
            periods.add(int(row["fundamental_period"]))
        else:
            values[y_index, x_index] = SPECIAL.get(row["label"], SPECIAL["unresolved"])
    max_period = max(periods, default=1)
    colors = ["#7f0000", "#d9d9d9", "#ffffff"] + [
        tuple(color) for color in plt.colormaps["turbo"](np.linspace(0.05, 0.95, max_period))
    ]
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(np.arange(-2.5, max_period + 1.5), cmap.N)
    x_min, x_max, _ = result["plane"]["x"]
    y_min, y_max, _ = result["plane"]["y"]
    parameters = result["parameters"]
    fig, axis = plt.subplots(figsize=(7.2, 6.2), constrained_layout=True)
    image = axis.imshow(
        values,
        origin="lower",
        interpolation="nearest",
        extent=(x_min, x_max, y_min, y_max),
        aspect="equal",
        cmap=cmap,
        norm=norm,
        rasterized=True,
    )
    axis.set_xlabel(r"initial $x_0$")
    axis.set_ylabel(r"initial $y_0$")
    axis.set_title(
        rf"Basin section at $z_0={result['plane']['z']:g}$, "
        rf"$(a,b,c)=({parameters['a']:g},{parameters['b']:g},{parameters['c']:g})$"
    )
    if periods:
        colorbar = fig.colorbar(image, ax=axis, ticks=sorted(periods), fraction=0.05, pad=0.03)
        colorbar.set_label("Detected fundamental period")
    handles = []
    if "unresolved" in labels:
        handles.append(Patch(facecolor="#d9d9d9", edgecolor="#333333", label="unresolved"))
    if "numerical_failure" in labels:
        handles.append(Patch(facecolor="#7f0000", edgecolor="#333333", label="numerical failure"))
    if handles:
        axis.legend(handles=handles, loc="upper right", fontsize=8)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    receipt = {
        "schema": "butterfly.basin-plane-figure-receipt.v1",
        "experiment_id": result["experiment_id"],
        "source_result_sha256": sha256_bytes(result_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "output_bytes": len(output_bytes),
        "periods_present": sorted(periods),
        "labels_present": sorted(labels),
        "dpi": args.dpi,
    }
    atomic_write(args.output.with_suffix(args.output.suffix + ".receipt.json"), canonical_json(receipt))
    print(json.dumps({"output": str(args.output), "sha256": receipt["output_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

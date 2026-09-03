#!/usr/bin/env python3
"""Plot the scale-ensemble critical-membership residual field from EXP-202."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.ticker import MaxNLocator
import numpy as np

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


def _axis(rows: list[dict], index: int, name: str) -> np.ndarray:
    pairs = sorted(
        {
            (int(row["grid_index"][index]), float(row["parameters"][name]))
            for row in rows
        }
    )
    indices = np.asarray([pair[0] for pair in pairs], dtype=float)
    values = np.asarray([pair[1] for pair in pairs], dtype=float)
    slope, intercept = np.polyfit(indices, values, 1)
    return intercept + slope * np.arange(int(max(indices)) + 1, dtype=float)


def _edges(values: np.ndarray) -> np.ndarray:
    edges = np.empty(values.size + 1, dtype=float)
    edges[1:-1] = 0.5 * (values[:-1] + values[1:])
    edges[0] = values[0] - 0.5 * (values[1] - values[0])
    edges[-1] = values[-1] + 0.5 * (values[-1] - values[-2])
    return edges


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--expected-receipt-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    receipt_bytes = args.receipt.read_bytes()
    if sha256_bytes(receipt_bytes) != args.expected_receipt_sha256:
        raise SystemExit("receipt hash mismatch")
    manifest = json.loads(manifest_bytes)
    receipt = json.loads(receipt_bytes)
    if receipt.get("manifest_sha256") != sha256_bytes(manifest_bytes):
        raise SystemExit("manifest hash mismatch")

    rows = [row for row in receipt["combined_candidates"] if row["eligible"]]
    a_values = _axis(rows, 0, "a")
    c_values = _axis(rows, 1, "c")
    shape = (c_values.size, a_values.size)
    mean_residuals = [np.full(shape, np.nan), np.full(shape, np.nan)]
    gate_ratio = np.full(shape, np.nan)
    gate = float(manifest["acceptance"]["maximum_direct_absolute_residual"])
    for row in rows:
        i, j = map(int, row["grid_index"])
        for residual_index in (0, 1):
            values = [
                reconstruction["normalized_signed_residuals"][residual_index]
                for reconstruction in row["reconstructions"].values()
            ]
            mean_residuals[residual_index][j, i] = float(np.mean(values))
        gate_ratio[j, i] = float(row["maximum_absolute_residual"]) / gate

    fig, axes = plt.subplots(1, 3, figsize=(12.0, 4.0), constrained_layout=True)
    a_edges, c_edges = _edges(a_values), _edges(c_values)
    panels = (
        (mean_residuals[0], r"mean scale-ensemble residual $r_1$"),
        (mean_residuals[1], r"mean scale-ensemble residual $r_2$"),
    )
    for axis, (values, title) in zip(axes[:2], panels):
        magnitude = float(np.nanmax(np.abs(values)))
        image = axis.pcolormesh(
            a_edges,
            c_edges,
            np.ma.masked_invalid(values),
            cmap="RdBu_r",
            norm=TwoSlopeNorm(vmin=-magnitude, vcenter=0.0, vmax=magnitude),
            shading="flat",
            rasterized=True,
        )
        fig.colorbar(image, ax=axis, shrink=0.84, pad=0.02)
        axis.set_title(title)
    image = axes[2].pcolormesh(
        a_edges,
        c_edges,
        np.ma.masked_invalid(gate_ratio),
        cmap="viridis",
        vmin=1.0,
        vmax=float(np.nanmax(gate_ratio)),
        shading="flat",
        rasterized=True,
    )
    fig.colorbar(image, ax=axes[2], shrink=0.84, pad=0.02)
    axes[2].set_title("worst residual / direct gate\n" + r"(minimum $1.436$)")
    selected = receipt["selected_candidate"]["parameters"]
    for axis in axes:
        axis.scatter(
            [selected["a"]],
            [selected["c"]],
            marker="*",
            s=80,
            facecolor="#fff176",
            edgecolor="#111111",
            linewidth=0.7,
        )
        axis.set_xlabel(r"$a$")
        axis.xaxis.set_major_locator(MaxNLocator(4))
        axis.ticklabel_format(axis="x", style="plain", useOffset=False)
    axes[0].set_ylabel(r"$c$")
    for axis in axes[1:]:
        axis.tick_params(labelleft=False)
    fig.suptitle(
        "EXP-202: scale-ensemble critical-membership residuals",
        fontsize=12,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)

    output_bytes = args.output.read_bytes()
    output_receipt = {
        "schema": "butterfly.exp202-scale-ensemble-residual-figure.v1",
        "experiment_id": "EXP-202",
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "input_receipt_sha256": sha256_bytes(receipt_bytes),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "eligible_candidate_count": len(rows),
        "minimum_gate_ratio": float(np.nanmin(gate_ratio)),
        "first_mean_residual_range": [
            float(np.nanmin(mean_residuals[0])),
            float(np.nanmax(mean_residuals[0])),
        ],
        "second_mean_residual_range": [
            float(np.nanmin(mean_residuals[1])),
            float(np.nanmax(mean_residuals[1])),
        ],
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(output_receipt),
    )
    print(json.dumps(output_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

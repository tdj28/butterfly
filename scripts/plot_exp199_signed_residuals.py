#!/usr/bin/env python3
"""Plot the two-step EXP-199 signed critical-residual field."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize, TwoSlopeNorm
import numpy as np

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


def _linear_grid(rows: list[dict], index: int, parameter: str) -> np.ndarray:
    pairs = sorted(
        {
            (int(row["grid_index"][index]), float(row["parameters"][parameter]))
            for row in rows
        }
    )
    indices = np.asarray([pair[0] for pair in pairs], dtype=float)
    values = np.asarray([pair[1] for pair in pairs], dtype=float)
    slope, intercept = np.polyfit(indices, values, 1)
    maximum_index = int(max(indices))
    return intercept + slope * np.arange(maximum_index + 1, dtype=float)


def _edges(values: np.ndarray) -> np.ndarray:
    if values.size < 2:
        raise ValueError("at least two grid values are required")
    edges = np.empty(values.size + 1, dtype=float)
    edges[1:-1] = 0.5 * (values[:-1] + values[1:])
    edges[0] = values[0] - 0.5 * (values[1] - values[0])
    edges[-1] = values[-1] + 0.5 * (values[-1] - values[-2])
    return edges


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-receipt-sha256")
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()
    if args.output.suffix.lower() not in (".png", ".pdf", ".svg"):
        raise SystemExit("output must be PNG, PDF, or SVG")

    manifest_bytes = args.manifest.read_bytes()
    receipt_bytes = args.receipt.read_bytes()
    receipt_sha256 = sha256_bytes(receipt_bytes)
    if (
        args.expected_receipt_sha256 is not None
        and receipt_sha256 != args.expected_receipt_sha256
    ):
        raise SystemExit("receipt hash mismatch")
    manifest = json.loads(manifest_bytes)
    receipt = json.loads(receipt_bytes)
    if receipt.get("experiment_id") != "EXP-199":
        raise SystemExit("expected an EXP-199 receipt")
    if receipt.get("manifest_sha256") != sha256_bytes(manifest_bytes):
        raise SystemExit("manifest hash mismatch")
    if receipt.get("candidate_input_sha256") != manifest.get(
        "candidate_input_sha256"
    ):
        raise SystemExit("candidate input hash mismatch")

    rows = receipt["combined_candidates"]
    eligible = [row for row in rows if row["eligible"]]
    if len(eligible) < manifest["acceptance"]["minimum_eligible_candidates"]:
        raise SystemExit("eligible-candidate gate unexpectedly failed")

    a_values = _linear_grid(rows, 0, "a")
    c_values = _linear_grid(rows, 1, "c")
    shape = (c_values.size, a_values.size)
    residual_1 = np.full(shape, np.nan, dtype=float)
    residual_2 = np.full(shape, np.nan, dtype=float)
    gate_ratio = np.full(shape, np.nan, dtype=float)
    for row in eligible:
        i, j = map(int, row["grid_index"])
        residuals = np.mean(
            np.asarray(row["signed_midpoint_residuals_by_profile"], dtype=float),
            axis=0,
        )
        residual_1[j, i] = residuals[0]
        residual_2[j, i] = residuals[1]
        ranking = row["ranking"]
        gate_ratio[j, i] = min(
            ranking["maximum_normalized_midpoint_distance"]
            / manifest["acceptance"]["maximum_selected_midpoint_distance"],
            ranking["maximum_normalized_interval_distance"]
            / manifest["acceptance"]["maximum_selected_interval_distance"],
            ranking["maximum_zero_slope_residual"]
            / manifest["acceptance"]["maximum_selected_zero_slope_residual"],
        )

    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 10,
        }
    )
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 4.3), constrained_layout=True)
    a_edges = _edges(a_values)
    c_edges = _edges(c_values)
    first_limit = float(np.nanmax(np.abs(residual_1)))
    panels = (
        (
            residual_1,
            "coolwarm",
            TwoSlopeNorm(vmin=-first_limit, vcenter=0.0, vmax=first_limit),
            r"mean signed residual $r_1$",
            r"$r_1$ crosses zero",
        ),
        (
            residual_2,
            "viridis",
            Normalize(vmin=0.0, vmax=float(np.nanmax(residual_2))),
            r"mean signed residual $r_2$",
            r"$r_2>0$ at all 126 points",
        ),
        (
            gate_ratio,
            "magma",
            LogNorm(vmin=1.0, vmax=float(np.nanmax(gate_ratio))),
            "best direct-gate ratio",
            "even the nearest gate ratio exceeds one",
        ),
    )
    selected = receipt["selected_candidate"]["parameters"]
    for axis, (values, cmap, norm, colorbar_label, subtitle) in zip(axes, panels):
        axis.set_facecolor("#ececec")
        image = axis.pcolormesh(
            a_edges,
            c_edges,
            np.ma.masked_invalid(values),
            shading="flat",
            cmap=cmap,
            norm=norm,
            rasterized=True,
        )
        axis.scatter(
            [selected["a"]],
            [selected["c"]],
            marker="*",
            s=90,
            facecolor="#fff176",
            edgecolor="#111111",
            linewidth=0.7,
            zorder=4,
        )
        axis.set_title(subtitle)
        axis.set_xlabel(r"$a$")
        axis.ticklabel_format(axis="x", style="plain", useOffset=False)
        colorbar = fig.colorbar(image, ax=axis, fraction=0.05, pad=0.025)
        colorbar.set_label(colorbar_label)
    axes[0].set_ylabel(r"$c$")
    for axis in axes[1:]:
        axis.tick_params(labelleft=False)
    fig.suptitle(
        r"EXP-199: incomplete two-step double-critical diagnostic at $b=0.2$",
        fontsize=12,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)

    output_bytes = args.output.read_bytes()
    first_by_profile = [
        [row["signed_midpoint_residuals_by_profile"][p][0] for row in eligible]
        for p in range(2)
    ]
    second_by_profile = [
        [row["signed_midpoint_residuals_by_profile"][p][1] for row in eligible]
        for p in range(2)
    ]
    output_receipt = {
        "schema": "butterfly.exp199-signed-residual-figure.v1",
        "experiment_id": "EXP-199",
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "input_receipt_sha256": receipt_sha256,
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "eligible_candidates": len(eligible),
        "first_residual_ranges_by_profile": [
            [float(min(values)), float(max(values))] for values in first_by_profile
        ],
        "second_residual_ranges_by_profile": [
            [float(min(values)), float(max(values))] for values in second_by_profile
        ],
        "selected_candidate_id": receipt["selected_candidate"]["id"],
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(output_receipt),
    )
    print(json.dumps(output_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

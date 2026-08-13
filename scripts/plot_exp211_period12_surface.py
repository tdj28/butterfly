#!/usr/bin/env python3
"""Plot the EXP-211 period-12 surface and EXP-210 recovery map."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
import numpy as np

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


SCHEMA = "butterfly.exp211-period12-surface-figure.v1"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--failed-receipt", type=Path, required=True)
    parser.add_argument("--expected-failed-sha256", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--expected-receipt-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    failed_bytes = args.failed_receipt.read_bytes()
    receipt_bytes = args.receipt.read_bytes()
    if sha256_bytes(failed_bytes) != args.expected_failed_sha256:
        raise SystemExit("EXP-210 receipt hash mismatch")
    if sha256_bytes(receipt_bytes) != args.expected_receipt_sha256:
        raise SystemExit("EXP-211 receipt hash mismatch")
    manifest = json.loads(manifest_bytes)
    failed = json.loads(failed_bytes)
    receipt = json.loads(receipt_bytes)
    if receipt["manifest_sha256"] != sha256_bytes(manifest_bytes):
        raise SystemExit("EXP-211 manifest hash mismatch")

    c_values = np.asarray(receipt["c_values"], dtype=float)
    offsets = 1e6 * np.asarray(receipt["offset_a_values"], dtype=float)
    opening = np.asarray(
        [[row["opening_identity"]["rms"] for row in line["rows"]] for line in receipt["lines"]]
    )
    parent_modulus = np.asarray(
        [
            [row["parent"]["dominant_transverse_multiplier"]["modulus"] for row in line["rows"]]
            for line in receipt["lines"]
        ]
    )
    child_modulus = np.asarray(
        [
            [row["child"]["dominant_transverse_multiplier"]["modulus"] for row in line["rows"]]
            for line in receipt["lines"]
        ]
    )

    figure = plt.figure(figsize=(13.2, 8.6), constrained_layout=True)
    grid = figure.add_gridspec(2, 2)
    surface_axis = figure.add_subplot(grid[0, 0], projection="3d")
    exponent_axis = figure.add_subplot(grid[0, 1])
    stability_axis = figure.add_subplot(grid[1, 0])
    recovery_axis = figure.add_subplot(grid[1, 1])

    c_mesh, offset_mesh = np.meshgrid(c_values, offsets)
    normalization = Normalize(vmin=float(opening.min()), vmax=float(opening.max()))
    colors = cm.viridis(normalization(opening))
    surface_axis.plot_surface(
        c_mesh,
        offset_mesh,
        opening,
        facecolors=colors,
        linewidth=0.25,
        edgecolor="#333333",
        antialiased=True,
        shade=False,
    )
    surface_axis.scatter(c_mesh, offset_mesh, opening, s=5, color="#222222", alpha=0.55)
    surface_axis.set_xlabel(r"$c$")
    surface_axis.set_ylabel(r"post-flip $\Delta a$ ($10^{-6}$)")
    surface_axis.set_zlabel("child opening RMS", labelpad=7)
    surface_axis.view_init(elev=25, azim=-58)
    surface_axis.set_title("124-point primitive period-12 sheet\nwhole-orbit opening above the flip curve")

    exponents = np.asarray(
        [row["opening_power_law"]["exponent"] for row in receipt["opening_fits_by_c"]]
    )
    r_squared = np.asarray(
        [row["opening_power_law"]["r_squared"] for row in receipt["opening_fits_by_c"]]
    )
    exponent_axis.axhspan(0.4, 0.6, color="#d9f0d3", alpha=0.65, label="frozen exponent gate")
    exponent_axis.axhline(0.5, color="#222222", linestyle="--", linewidth=1.0, label=r"square-root limit $q=1/2$")
    exponent_axis.plot(c_values, exponents, "o-", color="#2166ac", markersize=3.5, linewidth=1.2)
    exponent_axis.set_xlabel(r"$c$")
    exponent_axis.set_ylabel(r"opening exponent $q$")
    exponent_axis.set_ylim(0.495, 0.51)
    exponent_axis.set_title(r"31 independent $\Delta a$ fits" + "\n" + r"$q=0.50264$--$0.50309$")
    r_axis = exponent_axis.twinx()
    r_axis.plot(c_values, 1.0 - r_squared, "s", color="#d95f02", markersize=3.0, alpha=0.8)
    r_axis.set_yscale("log")
    r_axis.set_ylabel(r"fit deficit $1-R^2$", color="#d95f02")
    r_axis.tick_params(axis="y", colors="#d95f02")
    exponent_axis.legend(fontsize=7.0, loc="lower left")

    line_colors = cm.plasma(np.linspace(0.12, 0.88, len(offsets)))
    for offset, parents, children, color in zip(
        offsets, parent_modulus, child_modulus, line_colors, strict=True
    ):
        stability_axis.plot(c_values, parents, "--", color=color, linewidth=1.0)
        stability_axis.plot(
            c_values,
            children,
            "-",
            color=color,
            linewidth=1.25,
            label=rf"$\Delta a={offset:.0f}\times10^{{-6}}$",
        )
    stability_axis.axhline(1.0, color="#222222", linewidth=1.0, label="unit-modulus boundary")
    stability_axis.set_xlabel(r"$c$")
    stability_axis.set_ylabel("dominant transverse multiplier modulus")
    stability_axis.set_title("stability exchange across the sampled sheet\nsolid: period 12; dashed: period 6")
    stability_axis.legend(fontsize=6.5, ncol=2, loc="center right")

    for line in failed["lines"]:
        y_value = 1e6 * float(line["offset_a"])
        for row in line["rows"]:
            if row["passed"]:
                recovery_axis.scatter(row["c"], y_value, s=18, marker="o", color="#bdbdbd", zorder=1)
            else:
                recovery_axis.scatter(row["c"], y_value, s=54, marker="x", color="#b2182b", linewidth=1.8, zorder=3)
    for line in receipt["lines"]:
        y_value = 1e6 * float(line["offset_a"])
        recovery_axis.scatter(
            [row["c"] for row in line["rows"]],
            np.full(len(line["rows"]), y_value),
            s=12,
            marker="o",
            facecolor="#1b7837",
            edgecolor="white",
            linewidth=0.25,
            zorder=2,
        )
    recovery_axis.scatter([], [], s=18, marker="o", color="#bdbdbd", label="EXP-210 direct child root")
    recovery_axis.scatter([], [], s=54, marker="x", color="#b2182b", label="EXP-210 doubled-parent collapse")
    recovery_axis.scatter([], [], s=18, marker="o", color="#1b7837", label="EXP-211 primitive child selected")
    recovery_axis.set_xlabel(r"$c$")
    recovery_axis.set_ylabel(r"post-flip $\Delta a$ ($10^{-6}$)")
    recovery_axis.set_yticks(offsets)
    recovery_axis.set_title("identity-safe recovery of the failed surface\n16 collapses replaced; 124/124 cells pass")
    recovery_axis.legend(fontsize=6.8, loc="upper left")

    figure.suptitle(
        "EXP-211: dense sampled period-6-to-12 bifurcation surface at $b=0.2$",
        fontsize=13,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    figure.savefig(temporary, dpi=args.dpi)
    plt.close(figure)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    figure_receipt = {
        "schema": SCHEMA,
        "experiment_id": "EXP-211",
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "failed_receipt_sha256": sha256_bytes(failed_bytes),
        "input_receipt_sha256": sha256_bytes(receipt_bytes),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "surface_points": receipt["surface_point_count"],
        "recovered_cells": sum(
            not row["passed"] for line in failed["lines"] for row in line["rows"]
        ),
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(figure_receipt),
    )
    print(json.dumps(figure_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

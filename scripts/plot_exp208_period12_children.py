#!/usr/bin/env python3
"""Plot EXP-208 parameter geometry, stability exchange, and primitivity."""

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
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--curve-receipt", type=Path, required=True)
    parser.add_argument("--expected-curve-sha256", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--expected-receipt-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    curve_bytes = args.curve_receipt.read_bytes()
    receipt_bytes = args.receipt.read_bytes()
    if sha256_bytes(curve_bytes) != args.expected_curve_sha256:
        raise SystemExit("EXP-206 curve receipt hash mismatch")
    if sha256_bytes(receipt_bytes) != args.expected_receipt_sha256:
        raise SystemExit("EXP-208 receipt hash mismatch")
    manifest = json.loads(manifest_bytes)
    curve = json.loads(curve_bytes)
    receipt = json.loads(receipt_bytes)
    if receipt["manifest_sha256"] != sha256_bytes(manifest_bytes):
        raise SystemExit("manifest hash mismatch")
    if receipt["event_receipt_sha256"] != sha256_bytes(curve_bytes):
        raise SystemExit("curve-receipt binding mismatch")

    curve_c = np.asarray([row["c"] for row in curve["rows"]], dtype=float)
    curve_a = np.asarray([row["a"] for row in curve["rows"]], dtype=float)
    rows = receipt["rows"]
    child_c = np.asarray([row["c"] for row in rows], dtype=float)
    child_a = np.asarray([row["a"] for row in rows], dtype=float)
    event_a = np.interp(child_c, curve_c, curve_a)

    colors = ("#2166ac", "#7b3294", "#d95f02")
    figure, axes = plt.subplots(1, 3, figsize=(13.2, 4.25), constrained_layout=True)

    a_origin = 0.21575
    plotted_curve_a = 1e5 * (curve_a - a_origin)
    plotted_event_a = 1e5 * (event_a - a_origin)
    plotted_child_a = 1e5 * (child_a - a_origin)
    axes[0].plot(
        plotted_curve_a, curve_c, color="#222222", linewidth=1.5,
        label="period-6 flip",
    )
    axes[0].scatter(
        plotted_event_a, child_c, marker="D", s=38, color="#222222", zorder=4
    )
    axes[0].scatter(
        plotted_child_a,
        child_c,
        marker="o",
        s=50,
        color="#2166ac",
        edgecolor="white",
        linewidth=0.7,
        zorder=5,
        label="qualified period-12 child",
    )
    for x0, x1, y in zip(plotted_event_a, plotted_child_a, child_c, strict=True):
        axes[0].annotate(
            "",
            xy=(x1, y),
            xytext=(x0, y),
            arrowprops={"arrowstyle": "->", "color": "#2166ac", "lw": 1.4},
        )
    axes[0].set_xlabel(r"$10^5(a-0.21575)$")
    axes[0].set_ylabel(r"$c$")
    axes[0].set_title("three post-flip samples\nall qualify independently")
    axes[0].legend(fontsize=7, loc="lower left", frameon=True)

    parent_signed = np.asarray(
        [
            row["independent_radau"]["parent"]["dominant_transverse_multiplier"][
                "real"
            ]
            for row in rows
        ],
        dtype=float,
    )
    child_signed = np.asarray(
        [
            row["independent_radau"]["child"]["dominant_transverse_multiplier"][
                "real"
            ]
            for row in rows
        ],
        dtype=float,
    )
    axes[1].axhspan(-1.0, 1.0, color="#d9f0d3", alpha=0.75, label="stable transverse band")
    axes[1].axhline(-1.0, color="#555555", linestyle="--", linewidth=0.9)
    axes[1].axhline(1.0, color="#555555", linestyle="--", linewidth=0.9)
    axes[1].plot(child_c, parent_signed, "D-", color="#b2182b", label="period-6 parent")
    axes[1].plot(child_c, child_signed, "o-", color="#2166ac", label="period-12 child")
    axes[1].set_xlabel(r"$c$")
    axes[1].set_ylabel("dominant transverse multiplier")
    axes[1].set_title("sampled stability exchange\nRadau monodromy")
    axes[1].legend(fontsize=7, loc="center left", frameon=True)

    fractions = np.asarray(
        [item["fraction"] for item in rows[0]["proper_subperiod_closures"]] + [1.0]
    )
    for row, color in zip(rows, colors, strict=True):
        closures = np.asarray(
            [item["closure"] for item in row["proper_subperiod_closures"]]
            + [row["independent_radau"]["child"]["closure_error"]]
        )
        axes[2].semilogy(
            fractions,
            closures,
            marker="o",
            linewidth=1.2,
            color=color,
            label=rf"$c={row['c']:.2f}$",
        )
    axes[2].axhline(
        manifest["acceptance"]["minimum_proper_subperiod_closure"],
        color="#555555",
        linestyle="--",
        linewidth=0.9,
        label="proper-subperiod gate",
    )
    axes[2].set_xticks(fractions, ("1/12", "1/6", "1/4", "1/3", "1/2", "1"))
    axes[2].set_xlabel("fraction of candidate period")
    axes[2].set_ylabel("return distance")
    axes[2].set_title("proper subperiods stay open\nfull period closes below $5.3\\times10^{-11}$")
    axes[2].legend(fontsize=6.8, loc="lower left", frameon=True)

    figure.suptitle(
        "EXP-208: primitive stable period-12 children at three period-6 flips",
        fontsize=12,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    figure.savefig(temporary, dpi=args.dpi)
    plt.close(figure)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    figure_receipt = {
        "schema": "butterfly.exp208-period12-children-figure.v1",
        "experiment_id": "EXP-208",
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "curve_receipt_sha256": sha256_bytes(curve_bytes),
        "input_receipt_sha256": sha256_bytes(receipt_bytes),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "qualified_targets": len(rows),
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(figure_receipt),
    )
    print(json.dumps(figure_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

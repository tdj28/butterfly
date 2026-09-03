#!/usr/bin/env python3
"""Plot EXP-206's dense coupled flip curve and numerical quality."""

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
import numpy as np

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


def _edges(values):
    values = np.asarray(values, dtype=float)
    edges = np.empty(values.size + 1, dtype=float)
    edges[1:-1] = 0.5 * (values[:-1] + values[1:])
    edges[0] = values[0] - 0.5 * (values[1] - values[0])
    edges[-1] = values[-1] + 0.5 * (values[-1] - values[-2])
    return edges


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--field", type=Path, required=True)
    parser.add_argument("--expected-field-sha256", required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--expected-receipt-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    field_bytes = args.field.read_bytes()
    source_bytes = args.source_receipt.read_bytes()
    receipt_bytes = args.receipt.read_bytes()
    if sha256_bytes(field_bytes) != args.expected_field_sha256:
        raise SystemExit("EXP-203 field hash mismatch")
    if sha256_bytes(source_bytes) != args.expected_source_sha256:
        raise SystemExit("EXP-205 receipt hash mismatch")
    if sha256_bytes(receipt_bytes) != args.expected_receipt_sha256:
        raise SystemExit("EXP-206 receipt hash mismatch")
    manifest = json.loads(manifest_bytes)
    field = json.loads(field_bytes)
    source = json.loads(source_bytes)
    receipt = json.loads(receipt_bytes)
    if receipt["manifest_sha256"] != sha256_bytes(manifest_bytes):
        raise SystemExit("manifest hash mismatch")
    if receipt["source_receipt_sha256"] != sha256_bytes(source_bytes):
        raise SystemExit("source-receipt binding mismatch")

    a_values = np.asarray(field["grid"]["a_values"], dtype=float)
    c_values = np.asarray(field["grid"]["c_values"], dtype=float)
    status = np.zeros((len(c_values), len(a_values)), dtype=float)
    for row in field["candidates"]:
        i, j = map(int, row["grid_index"])
        if row.get("passed", False):
            status[j, i] = 2.0
        elif row.get("checks", {}).get("correction", False):
            status[j, i] = 1.0

    rows = receipt["rows"]
    curve_c = np.asarray([row["c"] for row in rows], dtype=float)
    curve_a = np.asarray([row["a"] for row in rows], dtype=float)
    periods = np.asarray([row["period_time"] for row in rows], dtype=float)
    source_c = np.asarray([row["c"] for row in source["results"]], dtype=float)
    source_a = np.asarray([row["a_estimate"] for row in source["results"]], dtype=float)

    figure, axes = plt.subplots(1, 3, figsize=(13.0, 4.2), constrained_layout=True)
    field_cmap = ListedColormap(("#e0e0e0", "#d95f02", "#2166ac"))
    field_norm = BoundaryNorm((-0.5, 0.5, 1.5, 2.5), field_cmap.N)
    axes[0].pcolormesh(
        _edges(a_values), _edges(c_values), status,
        cmap=field_cmap, norm=field_norm, shading="flat", rasterized=True,
    )
    axes[0].plot(curve_a, curve_c, color="#111111", linewidth=1.5, zorder=4)
    axes[0].scatter(
        source_a, source_c, marker="D", s=25, facecolor="#fff176",
        edgecolor="#111111", linewidth=0.6, zorder=5,
    )
    axes[0].set_ylim(7.15, 7.325)
    axes[0].set_xlabel(r"$a$")
    axes[0].set_ylabel(r"$c$")
    axes[0].ticklabel_format(axis="x", style="plain", useOffset=False)
    axes[0].set_title("orbit-defined flip curve\n41/41 coupled solves pass")
    axes[0].legend(
        handles=[
            Line2D((0,), (0,), marker="s", linestyle="none", color="#2166ac", label="qualified stable"),
            Line2D((0,), (0,), marker="s", linestyle="none", color="#d95f02", label="corrected, unstable"),
            Line2D((0,), (0,), color="#111111", label="EXP-206 coupled curve"),
            Line2D((0,), (0,), marker="D", linestyle="none", markerfacecolor="#fff176", markeredgecolor="#111111", label="EXP-205 scalar roots"),
        ],
        fontsize=6.8,
        loc="lower left",
        frameon=True,
    )

    parameter_line = axes[1].plot(
        curve_c, 1e5 * (curve_a - curve_a[len(curve_a) // 2]),
        color="#2166ac", marker="o", markersize=2.5,
        label=r"$10^5(a_*-a_*(7.24))$",
    )[0]
    axes[1].set_xlabel(r"$c$")
    axes[1].set_ylabel(r"centered event $a$", color="#2166ac")
    axes[1].tick_params(axis="y", labelcolor="#2166ac")
    period_axis = axes[1].twinx()
    period_line = period_axis.plot(
        curve_c, periods, color="#d95f02", linewidth=1.3,
        label="flow period",
    )[0]
    period_axis.set_ylabel("flow period", color="#d95f02")
    period_axis.tick_params(axis="y", labelcolor="#d95f02")
    axes[1].legend(
        handles=[parameter_line, period_line], fontsize=7, loc="upper right", frameon=True
    )
    axes[1].set_title("event geometry and orbit time\nmonotone on the sampled segment")

    quality = {
        "orbit": np.asarray([row["residuals"]["orbit"] for row in rows]),
        "tangent": np.asarray([row["residuals"]["tangent"] for row in rows]),
        r"$|\lambda+1|$": np.abs(
            np.asarray([row["residuals"]["independent_multiplier"] for row in rows])
        ),
        "neutral": np.asarray(
            [row["residuals"]["neutral_multiplier_error"] for row in rows]
        ),
    }
    for label, values in quality.items():
        axes[2].semilogy(curve_c, values, marker="o", markersize=2.3, linewidth=1.0, label=label)
    axes[2].axhline(1e-8, color="#777777", linestyle="--", linewidth=0.8, label=r"$10^{-8}$ gate")
    axes[2].axhline(1e-5, color="#222222", linestyle=":", linewidth=0.8, label=r"$10^{-5}$ gate")
    axes[2].set_xlabel(r"$c$")
    axes[2].set_ylabel("absolute residual")
    axes[2].set_title("coupled and independent checks\nall remain below frozen gates")
    axes[2].legend(fontsize=6.7, loc="lower left", ncol=2, frameon=True)
    figure.suptitle(
        r"EXP-206: dense exact-Jacobian continuation of the period-6 flip boundary",
        fontsize=12,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    figure.savefig(temporary, dpi=args.dpi)
    plt.close(figure)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    figure_receipt = {
        "schema": "butterfly.exp206-period6-flip-curve-figure.v1",
        "experiment_id": "EXP-206",
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "field_sha256": sha256_bytes(field_bytes),
        "source_receipt_sha256": sha256_bytes(source_bytes),
        "input_receipt_sha256": sha256_bytes(receipt_bytes),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "point_count": len(rows),
        "c_range": [float(curve_c.min()), float(curve_c.max())],
        "a_range": [float(curve_a.min()), float(curve_a.max())],
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(figure_receipt),
    )
    print(json.dumps(figure_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

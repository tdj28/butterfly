#!/usr/bin/env python3
"""Plot EXP-205's refined period-6 flip events over the EXP-203 field."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap, Normalize
from matplotlib.lines import Line2D
import numpy as np

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


def _edges(values: np.ndarray) -> np.ndarray:
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
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--expected-receipt-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    field_bytes = args.field.read_bytes()
    receipt_bytes = args.receipt.read_bytes()
    if sha256_bytes(field_bytes) != args.expected_field_sha256:
        raise SystemExit("EXP-203 field hash mismatch")
    if sha256_bytes(receipt_bytes) != args.expected_receipt_sha256:
        raise SystemExit("EXP-205 receipt hash mismatch")
    manifest = json.loads(manifest_bytes)
    field = json.loads(field_bytes)
    receipt = json.loads(receipt_bytes)
    if receipt.get("manifest_sha256") != sha256_bytes(manifest_bytes):
        raise SystemExit("EXP-205 manifest hash mismatch")
    if receipt.get("candidate_input_sha256") != sha256_bytes(field_bytes):
        raise SystemExit("EXP-205 candidate-input hash mismatch")

    a_values = np.asarray(field["grid"]["a_values"], dtype=float)
    c_values = np.asarray(field["grid"]["c_values"], dtype=float)
    status = np.zeros((c_values.size, a_values.size), dtype=float)
    lookup = {}
    for row in field["candidates"]:
        lookup[row["id"]] = row
        i, j = map(int, row["grid_index"])
        if row.get("passed", False):
            status[j, i] = 2.0
        elif row.get("checks", {}).get("correction", False):
            status[j, i] = 1.0

    events = {row["id"]: row for row in receipt["results"]}
    curve_c = np.asarray([event["c"] for event in manifest["events"]], dtype=float)
    curve_a = np.asarray(
        [events[event["id"]]["a_estimate"] for event in manifest["events"]],
        dtype=float,
    )

    figure, axes = plt.subplots(1, 2, figsize=(11.8, 4.35), constrained_layout=True)
    field_cmap = ListedColormap(("#e0e0e0", "#d95f02", "#2166ac"))
    field_norm = BoundaryNorm((-0.5, 0.5, 1.5, 2.5), field_cmap.N)
    axes[0].pcolormesh(
        _edges(a_values),
        _edges(c_values),
        status,
        cmap=field_cmap,
        norm=field_norm,
        shading="flat",
        rasterized=True,
    )
    axes[0].plot(curve_a, curve_c, color="#111111", linewidth=1.25, zorder=4)
    axes[0].scatter(
        curve_a,
        curve_c,
        marker="D",
        s=30,
        facecolor="#fff176",
        edgecolor="#111111",
        linewidth=0.7,
        zorder=5,
    )
    axes[0].legend(
        handles=[
            Line2D((0,), (0,), marker="s", linestyle="none", color="#2166ac", label="qualified stable"),
            Line2D((0,), (0,), marker="s", linestyle="none", color="#d95f02", label="corrected, unstable"),
            Line2D((0,), (0,), marker="D", markerfacecolor="#fff176", markeredgecolor="#111111", linestyle="-", color="#111111", label=r"refined $\lambda=-1$ event"),
        ],
        fontsize=7.5,
        loc="lower left",
        frameon=True,
    )
    axes[0].set_xlabel(r"$a$")
    axes[0].set_ylabel(r"$c$")
    axes[0].ticklabel_format(axis="x", style="plain", useOffset=False)
    axes[0].set_title("period-6 stability edge\nseven refined flip events")

    color_norm = Normalize(vmin=float(np.min(curve_c)), vmax=float(np.max(curve_c)))
    color_map = plt.get_cmap("viridis")
    maximum_residual = 0.0
    for event in manifest["events"]:
        result = events[event["id"]]
        root_a = float(result["a_estimate"])
        points = []
        for endpoint_id in (event["left_id"], event["right_id"]):
            endpoint = lookup[endpoint_id]
            points.append(
                (
                    1e6 * (float(endpoint["parameters"]["a"]) - root_a),
                    float(endpoint["dominant_nontrivial_multiplier"]["real"]) + 1.0,
                )
            )
        best = result["best_evaluation"]
        points.append(
            (
                1e6 * (float(best["a"]) - root_a),
                float(best["multiplier_residual"]),
            )
        )
        points.sort()
        x, y = map(np.asarray, zip(*points))
        maximum_residual = max(maximum_residual, abs(float(best["multiplier_residual"])))
        color = color_map(color_norm(float(event["c"])))
        axes[1].plot(x, y, color=color, linewidth=1.15, alpha=0.9)
        axes[1].scatter(x, y, color=[color], s=(15, 26, 15), zorder=3)
    axes[1].axhline(0.0, color="#222222", linewidth=0.8, linestyle="--")
    scalar = plt.cm.ScalarMappable(norm=color_norm, cmap=color_map)
    figure.colorbar(scalar, ax=axes[1], pad=0.02, shrink=0.86, label=r"fixed $c$")
    axes[1].set_xlabel(r"$10^6(a-a_*)$")
    axes[1].set_ylabel(r"$\lambda_{\mathrm{dom}}+1$")
    axes[1].set_title("independent sign brackets\nall seven cross zero")
    figure.suptitle(
        r"EXP-205: the lower-$c$ period-6 strip terminates on a real flip boundary",
        fontsize=12,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    figure.savefig(temporary, dpi=args.dpi)
    plt.close(figure)
    temporary.replace(args.output)

    output_bytes = args.output.read_bytes()
    output_receipt = {
        "schema": "butterfly.exp205-period6-flip-curve-figure.v1",
        "experiment_id": "EXP-205",
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "field_sha256": sha256_bytes(field_bytes),
        "input_receipt_sha256": sha256_bytes(receipt_bytes),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "event_count": len(curve_a),
        "c_range": [float(np.min(curve_c)), float(np.max(curve_c))],
        "a_range": [float(np.min(curve_a)), float(np.max(curve_a))],
        "maximum_a_bracket_width": max(row["bracket_width"] for row in events.values()),
        "maximum_absolute_multiplier_residual": maximum_residual,
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(output_receipt),
    )
    print(json.dumps(output_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

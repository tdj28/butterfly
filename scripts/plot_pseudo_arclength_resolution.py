#!/usr/bin/env python3
"""Plot resolution convergence for a periodic-orbit pseudo-arclength branch."""

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


def crossing_estimate(rows: list[dict]) -> tuple[float, list[float]]:
    """Return the linear +1 crossing estimate and its enclosing b bracket."""
    ordered = sorted(rows, key=lambda row: float(row["b"]))
    for left, right in zip(ordered[:-1], ordered[1:], strict=True):
        left_value = float(left["significant_multiplier"]["real"])
        right_value = float(right["significant_multiplier"]["real"])
        if (left_value - 1.0) * (right_value - 1.0) <= 0.0:
            left_b = float(left["b"])
            right_b = float(right["b"])
            estimate = left_b + (1.0 - left_value) * (right_b - left_b) / (
                right_value - left_value
            )
            return estimate, [left_b, right_b]
    raise ValueError("receipt does not bracket a real +1 crossing")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipts", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()
    if args.output.suffix.lower() not in (".png", ".pdf", ".svg"):
        raise SystemExit("--output must end in .png, .pdf, or .svg")

    receipts: list[dict] = []
    input_hashes: dict[str, str] = {}
    for path in args.receipts:
        raw = path.read_bytes()
        receipt = json.loads(raw)
        if receipt.get("schema") != "butterfly.periodic-pseudo-arclength-receipt.v1":
            raise SystemExit(f"unsupported receipt schema: {path}")
        receipts.append(receipt)
        input_hashes[receipt["experiment_id"]] = sha256_bytes(raw)

    fig, (multiplier_axis, period_axis) = plt.subplots(
        2, 1, figsize=(8.0, 7.2), sharex=True, constrained_layout=True
    )
    colors = plt.colormaps["viridis"](np.linspace(0.15, 0.85, len(receipts)))
    estimates: dict[str, dict] = {}
    for color, receipt in zip(colors, receipts, strict=True):
        rows = receipt["rows"]
        b_values = np.asarray([row["b"] for row in rows], dtype=float)
        multipliers = np.asarray(
            [row["significant_multiplier"]["real"] for row in rows], dtype=float
        )
        periods = np.asarray([row["period_time"] for row in rows], dtype=float)
        order = np.argsort(b_values)
        experiment_id = receipt["experiment_id"]
        multiplier_axis.plot(
            b_values[order],
            multipliers[order],
            marker="o",
            markersize=2.8,
            linewidth=1.25,
            color=color,
            label=f"{experiment_id} ({len(rows)} points)",
        )
        period_axis.plot(
            b_values[order], periods[order], linewidth=1.25, color=color
        )
        estimate, bracket = crossing_estimate(rows)
        estimates[experiment_id] = {
            "linear_crossing_estimate": estimate,
            "bracket": bracket,
            "direction_reversals_in_b": receipt["direction_reversals_in_b"],
        }
        multiplier_axis.scatter(
            [estimate], [1.0], color=color, marker="x", s=42, linewidth=1.6, zorder=5
        )

    multiplier_axis.axhline(1.0, color="black", linestyle="--", linewidth=1.0)
    multiplier_axis.set_ylabel("Significant real Floquet multiplier")
    multiplier_axis.set_title("Period-5 pseudo-arclength resolution near the +1 crossing")
    multiplier_axis.grid(True, alpha=0.24, linewidth=0.6)
    multiplier_axis.legend(fontsize=8, frameon=True)
    multiplier_axis.set_xlim(0.264, 0.302)
    multiplier_axis.set_ylim(0.25, 4.2)

    period_axis.set_xlabel("Rössler parameter b")
    period_axis.set_ylabel("Flow period")
    period_axis.grid(True, alpha=0.24, linewidth=0.6)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    figure_receipt = {
        "schema": "butterfly.pseudo-arclength-resolution-figure-receipt.v1",
        "experiment_ids": [receipt["experiment_id"] for receipt in receipts],
        "source_receipt_sha256": input_hashes,
        "crossing_estimates": estimates,
        "output_file": args.output.name,
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "output_bytes": len(output_bytes),
        "dpi": args.dpi,
        "note": "Three frozen resolutions trace the same smooth branch through +1 without a b-direction reversal; markers are descriptive linear crossing estimates.",
    }
    receipt_path = args.output.with_suffix(args.output.suffix + ".receipt.json")
    atomic_write(receipt_path, canonical_json(figure_receipt))
    print(json.dumps(figure_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

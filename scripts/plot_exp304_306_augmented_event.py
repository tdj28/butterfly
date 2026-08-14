#!/usr/bin/env python3
"""Plot the two-tableau augmented qualification of event eight."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, getcontext
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


SCHEMA = "butterfly.exp304-306-augmented-event-figure.v1"
getcontext().prec = 50


def read_bound(path: Path, expected_hash: str, schema: str, passed: bool):
    data = path.read_bytes()
    if sha256_bytes(data) != expected_hash:
        raise SystemExit(f"receipt hash mismatch: {path}")
    receipt = json.loads(data)
    if receipt.get("schema") != schema or receipt.get("passed") is not passed:
        raise SystemExit(f"unexpected receipt status: {path}")
    return data, receipt


def final_residuals(receipt):
    return np.asarray(
        [
            max(
                float(profile["history"][-1]["orbit_residual"]),
                float(profile["history"][-1]["tangent_residual"]),
            )
            for profile in receipt["profiles"]
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classical", type=Path, required=True)
    parser.add_argument("--classical-sha256", required=True)
    parser.add_argument("--independent", type=Path, required=True)
    parser.add_argument("--independent-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    classical_bytes, classical = read_bound(
        args.classical,
        args.classical_sha256,
        "butterfly.jones-period1536-decimal-augmented-refinement-receipt.v1",
        False,
    )
    independent_bytes, independent = read_bound(
        args.independent,
        args.independent_sha256,
        "butterfly.jones-period1536-decimal-augmented-independent-receipt.v1",
        True,
    )
    if [name for name, passed in classical["checks"].items() if not passed] != [
        "extrapolated_a_bounds"
    ]:
        raise SystemExit("classical source no longer has the sole inherited-bracket failure")

    steps = np.asarray([1024, 2048, 4096], dtype=float)
    classical_a = np.asarray([float(row["a_decimal"]) for row in classical["profiles"]])
    independent_a = np.asarray([float(row["a_decimal"]) for row in independent["profiles"]])
    extrapolated_decimal = [
        Decimal(classical["extrapolated_a_decimal"]),
        Decimal(independent["extrapolated_a_decimal"]),
    ]
    extrapolated = np.asarray([float(value) for value in extrapolated_decimal])
    consensus_decimal = sum(extrapolated_decimal) / Decimal(2)
    consensus = float(consensus_decimal)
    coordinate_errors = np.vstack(
        [abs(classical_a - extrapolated[0]), abs(independent_a - extrapolated[1])]
    )
    event_decimals = [
            Decimal("0.24070118147582764"),
            Decimal("0.24070104611236293"),
            Decimal("0.24070101640878155"),
            Decimal("0.24070101008421760"),
            Decimal("0.24070100861338276"),
            Decimal("0.24070100830924687"),
            Decimal("0.24070100823759041937"),
            consensus_decimal,
    ]
    spacings = [left - right for left, right in zip(event_decimals, event_decimals[1:])]
    ratios = np.asarray(
        [float(left / right) for left, right in zip(spacings, spacings[1:])]
    )

    figure, axes = plt.subplots(2, 2, figsize=(13.2, 8.8), constrained_layout=True)
    colors = ("#2166ac", "#d6604d")
    labels = ("classical RK4", "RK4 3/8")
    markers = ("o", "s")
    for index, (label, color, marker) in enumerate(zip(labels, colors, markers)):
        axes[0, 0].semilogy(
            steps,
            coordinate_errors[index],
            marker=marker,
            linewidth=2,
            markersize=7,
            color=color,
            label=label,
        )
    guide = coordinate_errors[0, 0] * (steps[0] / steps) ** 4
    axes[0, 0].semilogy(steps, guide, "--", color="#555555", label="fourth-order guide")
    axes[0, 0].set_xticks(steps, labels=["1,024", "2,048", "4,096"])
    axes[0, 0].set_xlabel("RK steps per segment")
    axes[0, 0].set_ylabel(r"$|a_h-a_{\rm Richardson}|$")
    axes[0, 0].set_title("independent tableaux converge at order four")
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(alpha=0.2, which="both")

    residuals = np.vstack([final_residuals(classical), final_residuals(independent)])
    width = 0.34
    positions = np.arange(3)
    for index, (label, color) in enumerate(zip(labels, colors)):
        axes[0, 1].bar(
            positions + (index - 0.5) * width,
            residuals[index],
            width,
            color=color,
            label=label,
        )
    axes[0, 1].axhline(1e-22, linestyle="--", color="#222222", label="frozen gate")
    axes[0, 1].set_yscale("log")
    axes[0, 1].set_xticks(positions, ["1,024", "2,048", "4,096"])
    axes[0, 1].set_xlabel("RK steps per segment")
    axes[0, 1].set_ylabel("final max orbit/tangent residual")
    axes[0, 1].set_title("all augmented roots close below the gate")
    axes[0, 1].legend(fontsize=7.5)
    axes[0, 1].grid(alpha=0.2, axis="y")

    ratio_labels = [
        "12/24/48",
        "24/48/96",
        "48/96/192",
        "96/192/384",
        "192/384/768",
        "384/768/1536",
    ]
    bars = axes[1, 0].bar(
        np.arange(6),
        ratios,
        color=["#2166ac", "#4393c3", "#92c5de", "#fddbc7", "#f4a582", "#d6604d"],
    )
    axes[1, 0].set_xticks(np.arange(6), ratio_labels, rotation=20, ha="right")
    axes[1, 0].set_ylabel("finite event-spacing ratio")
    axes[1, 0].set_ylim(0, max(ratios) * 1.18)
    axes[1, 0].set_title("event eight adds a sixth finite ratio")
    for bar, value in zip(bars, ratios):
        axes[1, 0].annotate(
            f"{value:.3f}",
            (bar.get_x() + bar.get_width() / 2, value),
            ha="center",
            va="bottom",
            xytext=(0, 4),
            textcoords="offset points",
            fontsize=8,
        )
    axes[1, 0].grid(alpha=0.2, axis="y")

    lower_decimal = Decimal(independent["continuation_envelope"]["lower_a_decimal"])
    upper_decimal = Decimal(independent["continuation_envelope"]["upper_a_decimal"])
    old_lower_decimal = Decimal("0.24070100823770973")
    old_upper_decimal = Decimal("0.24070100823781396")
    transform = lambda value: float((value - consensus_decimal) * Decimal("1e11"))
    axes[1, 1].axvspan(transform(lower_decimal), transform(upper_decimal), color="#d9f0d3", label="accepted continuation envelope")
    axes[1, 1].axvspan(transform(old_lower_decimal), transform(old_upper_decimal), color="#f4a582", alpha=0.9, label="rejected EXP-302 micro-bracket")
    axes[1, 1].axvline(transform(extrapolated_decimal[0]), color=colors[0], linewidth=2, label="classical Richardson")
    axes[1, 1].axvline(transform(extrapolated_decimal[1]), color=colors[1], linewidth=2, linestyle="--", label="3/8 Richardson")
    axes[1, 1].axvline(0, color="#222222", linewidth=1, alpha=0.6)
    axes[1, 1].set_yticks([])
    axes[1, 1].set_xlabel(r"$(a-a_{\rm consensus})\times10^{11}$")
    axes[1, 1].set_title("exact roots agree while the old micro-bracket does not")
    axes[1, 1].legend(fontsize=7.5, loc="upper left")
    axes[1, 1].grid(alpha=0.2, axis="x")

    figure.suptitle(
        "EXP-304--306: two-tableau augmented qualification of event eight",
        fontsize=13,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    figure.savefig(temporary, dpi=args.dpi)
    plt.close(figure)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    receipt = {
        "schema": SCHEMA,
        "classical_receipt_sha256": sha256_bytes(classical_bytes),
        "independent_receipt_sha256": sha256_bytes(independent_bytes),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "classical_a": classical_a.tolist(),
        "independent_a": independent_a.tolist(),
        "extrapolated_a": extrapolated.tolist(),
        "consensus_a": consensus,
        "consensus_a_decimal": str(consensus_decimal),
        "finite_spacing_ratios": ratios.tolist(),
        "continuation_envelope": [float(lower_decimal), float(upper_decimal)],
        "rejected_micro_bracket": [float(old_lower_decimal), float(old_upper_decimal)],
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(receipt),
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

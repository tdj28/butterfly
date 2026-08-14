#!/usr/bin/env python3
"""Plot the two-tableau augmented qualification of event seven."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


SCHEMA = "butterfly.exp293-295-augmented-event-figure.v1"


def read_bound(path: Path, expected_hash: str, schema: str, passed: bool):
    data = path.read_bytes()
    if sha256_bytes(data) != expected_hash:
        raise SystemExit(f"receipt hash mismatch: {path}")
    receipt = json.loads(data)
    if receipt.get("schema") != schema or receipt.get("passed") is not passed:
        raise SystemExit(f"unexpected receipt status: {path}")
    return data, receipt


def final_residuals(receipt):
    orbit = []
    tangent = []
    for profile in receipt["profiles"]:
        final = profile["history"][-1]
        orbit.append(float(final["orbit_residual"]))
        tangent.append(float(final["tangent_residual"]))
    return np.maximum(orbit, tangent)


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
        "butterfly.jones-period768-decimal-augmented-refinement-receipt.v1",
        False,
    )
    independent_bytes, independent = read_bound(
        args.independent,
        args.independent_sha256,
        "butterfly.jones-period768-decimal-augmented-independent-receipt.v1",
        True,
    )

    steps = np.asarray([1024, 2048, 4096], dtype=float)
    classical_a = np.asarray(
        [float(row["a_decimal"]) for row in classical["profiles"]]
    )
    independent_a = np.asarray(
        [float(row["a_decimal"]) for row in independent["profiles"]]
    )
    extrapolated = np.asarray(
        [float(classical["extrapolated_a"]), float(independent["extrapolated_a"])]
    )
    coordinate_errors = np.vstack(
        [abs(classical_a - extrapolated[0]), abs(independent_a - extrapolated[1])]
    )

    events = np.asarray(
        [
            0.24070118147582764,
            0.24070104611236293,
            0.24070101640878155,
            0.24070101008421760,
            0.24070100861338276,
            0.24070100830924687,
            float(np.mean(extrapolated)),
        ]
    )
    spacings = events[:-1] - events[1:]
    ratios = spacings[:-1] / spacings[1:]

    metrics = independent["tangent_line_metrics"]
    utilizations = np.asarray(
        [
            independent["cross_tableau_extrapolated_a_difference"] / 1e-10,
            independent["cross_tableau_extrapolated_period_difference"] / 1e-6,
            independent["node_maximum_difference"] / 1e-5,
            independent["node_rms_difference"] / 1e-6,
            metrics["base_maximum_difference"] / 1e-3,
            float(
                (Decimal(1) - Decimal(metrics["global_cosine_decimal"]))
                / Decimal("0.0001")
            ),
            float(
                (
                    Decimal(1)
                    - Decimal(metrics["median_absolute_pointwise_cosine_decimal"])
                )
                / Decimal("0.000001")
            ),
        ]
    )
    utilization_labels = [
        "$a$ extrap.",
        "$T$ extrap.",
        "node max",
        "node RMS",
        "base tangent",
        "global angle",
        "median angle",
    ]

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
    axes[0, 0].set_title("two tableaux converge at order four")
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
    axes[0, 1].set_title("every augmented system closes below the gate")
    axes[0, 1].legend(fontsize=7.5)
    axes[0, 1].grid(alpha=0.2, axis="y")

    ratio_labels = ["12/24/48", "24/48/96", "48/96/192", "96/192/384", "192/384/768"]
    bars = axes[1, 0].bar(
        np.arange(5),
        ratios,
        color=["#2166ac", "#4393c3", "#92c5de", "#f4a582", "#d6604d"],
    )
    axes[1, 0].set_xticks(np.arange(5), ratio_labels, rotation=18, ha="right")
    axes[1, 0].set_ylabel("finite event-spacing ratio")
    axes[1, 0].set_ylim(0, max(ratios) * 1.18)
    axes[1, 0].set_title("corrected seventh event gives fifth ratio 4.244")
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

    axes[1, 1].barh(
        np.arange(len(utilizations)), utilizations, color="#5ab4ac"
    )
    axes[1, 1].axvline(1.0, color="#222222", linestyle="--", label="gate")
    axes[1, 1].set_xscale("log")
    axes[1, 1].set_yticks(np.arange(len(utilizations)), utilization_labels)
    axes[1, 1].invert_yaxis()
    axes[1, 1].set_xlabel("observed discrepancy / allowed discrepancy")
    axes[1, 1].set_title("independent identity margins are far below one")
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].grid(alpha=0.2, axis="x", which="both")

    figure.suptitle(
        "EXP-293--295: two-tableau augmented qualification of event seven",
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
        "finite_spacing_ratios": ratios.tolist(),
        "gate_utilizations": utilizations.tolist(),
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(receipt),
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

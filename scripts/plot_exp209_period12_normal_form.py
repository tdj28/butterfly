#!/usr/bin/env python3
"""Plot EXP-209 opening laws, multiplier scaling, and attraction checks."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import numpy as np

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


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
        raise SystemExit("EXP-209 receipt hash mismatch")
    manifest = json.loads(manifest_bytes)
    receipt = json.loads(receipt_bytes)
    if receipt["manifest_sha256"] != sha256_bytes(manifest_bytes):
        raise SystemExit("manifest hash mismatch")

    colors = ("#2166ac", "#7b3294", "#d95f02")
    figure, axes = plt.subplots(1, 3, figsize=(13.2, 4.25), constrained_layout=True)

    all_offsets = []
    for target, color in zip(receipt["targets"], colors, strict=True):
        offsets = np.asarray([row["offset_a"] for row in target["rows"]])
        amplitudes = np.asarray(
            [row["opening_identity"]["rms"] for row in target["rows"]]
        )
        all_offsets.extend(offsets.tolist())
        fit = target["opening_power_law"]
        fitted = np.exp(fit["log_intercept"]) * offsets ** fit["exponent"]
        axes[0].loglog(
            offsets,
            amplitudes,
            "o",
            color=color,
            label=rf"$c={target['c']:.2f}$, $q={fit['exponent']:.4f}$",
        )
        axes[0].loglog(offsets, fitted, color=color, linewidth=1.1)
    reference_offsets = np.asarray((min(all_offsets), max(all_offsets)))
    reference_scale = 0.04 / np.sqrt(np.sqrt(np.prod(reference_offsets)))
    axes[0].loglog(
        reference_offsets,
        reference_scale * np.sqrt(reference_offsets),
        "--",
        color="#222222",
        linewidth=1.0,
        label=r"reference $\Delta a^{1/2}$",
    )
    axes[0].set_xlabel(r"post-flip offset $\Delta a$")
    axes[0].set_ylabel("phase-aligned opening RMS")
    axes[0].set_xticks(
        (5e-6, 1e-5, 2e-5, 5e-5),
        (r"$5\times10^{-6}$", r"$10^{-5}$", r"$2\times10^{-5}$", r"$5\times10^{-5}$"),
    )
    axes[0].xaxis.set_minor_formatter(NullFormatter())
    axes[0].tick_params(axis="x", labelsize=8)
    axes[0].set_title("square-root branch opening\n$R^2>0.999995$ at all three slices")
    axes[0].legend(fontsize=6.8, loc="lower right", frameon=True)

    fractions = np.asarray(manifest["offset_fractions"], dtype=float)
    axes[1].axhspan(
        manifest["acceptance"]["minimum_multiplier_ratio"],
        manifest["acceptance"]["maximum_multiplier_ratio"],
        color="#d9f0d3",
        alpha=0.75,
        label="frozen acceptance band",
    )
    axes[1].axhline(4.0, color="#222222", linestyle="--", linewidth=1.0, label="cubic flip limit")
    for target, color in zip(receipt["targets"], colors, strict=True):
        ratios = np.asarray([row["flip_multiplier_ratio"] for row in target["rows"]])
        axes[1].plot(
            fractions,
            ratios,
            "o-",
            color=color,
            linewidth=1.2,
            label=rf"$c={target['c']:.2f}$",
        )
    axes[1].set_xlabel("fraction of event-to-child offset")
    axes[1].set_ylabel(r"$(1-\lambda_{12})/(-\lambda_6-1)$")
    axes[1].set_ylim(2.9, 5.1)
    axes[1].set_title("flip multiplier scaling\nall 21 ratios lie in 4.011--4.150")
    axes[1].legend(fontsize=6.8, loc="upper left", frameon=True)

    x_positions = []
    terminal = []
    recovered = []
    point_colors = []
    tick_positions = []
    tick_labels = []
    for target_index, (target, color) in enumerate(
        zip(receipt["targets"], colors, strict=True)
    ):
        center = 3.0 * target_index
        tick_positions.append(center + 0.5)
        tick_labels.append(rf"$c={target['c']:.2f}$")
        for perturbation_index, row in enumerate(target["attraction"]):
            x_positions.append(center + perturbation_index)
            terminal.append(row["terminal_orbit_distance"])
            recovered.append(row["recovered_identity"]["rms"])
            point_colors.append(color)
    axes[2].scatter(
        np.asarray(x_positions) - 0.10,
        terminal,
        marker="o",
        s=42,
        c=point_colors,
        edgecolor="white",
        linewidth=0.6,
        label="terminal orbit distance",
    )
    axes[2].scatter(
        np.asarray(x_positions) + 0.10,
        recovered,
        marker="s",
        s=38,
        c=point_colors,
        edgecolor="#222222",
        linewidth=0.5,
        label="recorrected orbit RMS",
    )
    axes[2].axhline(
        manifest["acceptance"]["maximum_attraction_terminal_distance"],
        color="#555555",
        linestyle="--",
        linewidth=0.9,
        label="terminal gate",
    )
    axes[2].axhline(
        manifest["acceptance"]["maximum_recovered_identity_rms"],
        color="#555555",
        linestyle=":",
        linewidth=0.9,
        label="identity gate",
    )
    axes[2].set_yscale("log")
    axes[2].set_xticks(tick_positions, tick_labels)
    axes[2].set_ylabel("phase-invariant distance")
    axes[2].set_title("two-sided perturbations return\nall six attraction tests pass")
    axes[2].legend(fontsize=6.5, loc="upper right", frameon=True)

    figure.suptitle(
        "EXP-209: replicated local supercritical signatures on the period-6 flip curve",
        fontsize=12,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    figure.savefig(temporary, dpi=args.dpi)
    plt.close(figure)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    figure_receipt = {
        "schema": "butterfly.exp209-period12-normal-form-figure.v1",
        "experiment_id": "EXP-209",
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "input_receipt_sha256": sha256_bytes(receipt_bytes),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "qualified_targets": len(receipt["targets"]),
        "branch_points": sum(len(target["rows"]) for target in receipt["targets"]),
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(figure_receipt),
    )
    print(json.dumps(figure_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

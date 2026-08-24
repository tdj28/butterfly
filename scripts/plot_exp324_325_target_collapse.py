#!/usr/bin/env python3
"""Plot the resolution-doubled collapse of the old EXP-299 child seed."""

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


SCHEMA = "butterfly.exp324-325-target-collapse-figure.v1"
RECEIPT_SCHEMA = "butterfly.jones-period1536-decimal-target-correction-receipt.v1"


def read_bound(path: Path, expected_hash: str, expected_steps: int):
    data = path.read_bytes()
    if sha256_bytes(data) != expected_hash:
        raise SystemExit(f"receipt hash mismatch: {path}")
    receipt = json.loads(data)
    if receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("passed") is not True:
        raise SystemExit(f"unexpected receipt status: {path}")
    if receipt.get("steps_per_segment") != expected_steps:
        raise SystemExit(f"unexpected step count: {path}")
    if receipt.get("periodicity_classification") != "doubled_period768_parent":
        raise SystemExit(f"target did not collapse to the parent: {path}")
    return data, receipt


def accepted_factors(receipt: dict) -> list[float]:
    """Recover each accepted trial by matching it to the next history row."""
    factors = []
    for row in receipt["history"][1:]:
        trials = [trial for trial in receipt["trial_history"] if trial["update"] == row["iteration"]]
        accepted = [
            trial
            for trial in trials
            if trial["matching_residual_decimal"] == row["matching_residual_decimal"]
        ]
        if len(accepted) != 1:
            raise SystemExit(f"could not identify accepted update {row['iteration']}")
        factors.append(accepted[0]["factor"])
    return factors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp324", type=Path, required=True)
    parser.add_argument("--exp324-sha256", required=True)
    parser.add_argument("--exp325", type=Path, required=True)
    parser.add_argument("--exp325-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    bytes324, exp324 = read_bound(args.exp324, args.exp324_sha256, 4096)
    bytes325, exp325 = read_bound(args.exp325, args.exp325_sha256, 8192)
    receipts = [(4096, exp324), (8192, exp325)]
    colors = {4096: "#2166ac", 8192: "#b2182b"}

    figure, axes = plt.subplots(2, 2, figsize=(13.2, 8.8), constrained_layout=True)
    for steps, receipt in receipts:
        iterations = [row["iteration"] for row in receipt["history"]]
        residuals = [row["matching_residual"] for row in receipt["history"]]
        amplitudes = [row["half_node_rms"] for row in receipt["history"]]
        axes[0, 0].semilogy(
            iterations, residuals, marker="o", markersize=4.5,
            color=colors[steps], linewidth=1.7, label=f"{steps:,} steps",
        )
        axes[0, 1].semilogy(
            iterations, amplitudes, marker="o", markersize=4.5,
            color=colors[steps], linewidth=1.7, label=f"{steps:,} steps",
        )
        factors = accepted_factors(receipt)
        axes[1, 0].step(
            range(1, len(factors) + 1), factors, where="mid",
            color=colors[steps], linewidth=1.7, label=f"{steps:,} steps",
        )
        axes[1, 1].loglog(
            amplitudes, residuals, marker="o", markersize=4.5,
            color=colors[steps], linewidth=1.7, label=f"{steps:,} steps",
        )

    axes[0, 0].axhline(1e-20, color="#333333", linestyle=":", label="closure gate")
    axes[0, 0].set_xlabel("accepted Newton update")
    axes[0, 0].set_ylabel("matching residual")
    axes[0, 0].set_title("both exact maps close the original seed")
    axes[0, 0].grid(alpha=0.2, which="both")
    axes[0, 0].legend(fontsize=8)

    axes[0, 1].axhline(1e-10, color="#333333", linestyle=":", label="parent-collapse gate")
    axes[0, 1].set_xlabel("accepted Newton update")
    axes[0, 1].set_ylabel("primitive half-node RMS amplitude")
    axes[0, 1].set_title("the alleged daughter amplitude vanishes")
    axes[0, 1].grid(alpha=0.2, which="both")
    axes[0, 1].legend(fontsize=8)

    axes[1, 0].set_yscale("log", base=2)
    axes[1, 0].set_xlabel("accepted Newton update")
    axes[1, 0].set_ylabel(r"accepted Armijo factor $\alpha$")
    axes[1, 0].set_title("globalization resolves near-flip conditioning")
    axes[1, 0].set_yticks([1 / 512, 1 / 128, 1 / 32, 1 / 8, 1 / 2, 1])
    axes[1, 0].set_yticklabels(["1/512", "1/128", "1/32", "1/8", "1/2", "1"])
    axes[1, 0].grid(alpha=0.2, which="both")
    axes[1, 0].legend(fontsize=8)

    axes[1, 1].axhline(1e-20, color="#333333", linestyle=":", linewidth=1)
    axes[1, 1].axvline(1e-10, color="#333333", linestyle=":", linewidth=1)
    axes[1, 1].set_xlabel("primitive half-node RMS amplitude")
    axes[1, 1].set_ylabel("matching residual")
    axes[1, 1].set_title("independent paths reach the same parent class")
    axes[1, 1].grid(alpha=0.2, which="both")
    axes[1, 1].legend(fontsize=8)

    figure.suptitle(
        "EXP-324/325: the nominal higher-a period-1536 seed collapses at two resolutions",
        fontsize=13,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    figure.savefig(temporary, dpi=args.dpi)
    plt.close(figure)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    summary = {
        str(steps): {
            "accepted_updates": len(receipt["history"]) - 1,
            "initial_matching_residual": receipt["history"][0]["matching_residual"],
            "final_matching_residual": receipt["history"][-1]["matching_residual"],
            "initial_half_node_rms": receipt["history"][0]["half_node_rms"],
            "final_half_node_rms": receipt["history"][-1]["half_node_rms"],
            "accepted_factors": accepted_factors(receipt),
        }
        for steps, receipt in receipts
    }
    figure_receipt = {
        "schema": SCHEMA,
        "exp324_receipt_sha256": sha256_bytes(bytes324),
        "exp325_receipt_sha256": sha256_bytes(bytes325),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "summary": summary,
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(figure_receipt),
    )
    print(json.dumps(figure_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

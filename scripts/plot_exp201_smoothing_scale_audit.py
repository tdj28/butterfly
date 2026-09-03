#!/usr/bin/env python3
"""Plot the nested-support smoothing-scale qualification from EXP-201."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


def _profile_rows(receipt: dict) -> dict[tuple[str, str], dict]:
    return {
        (profile["name"], row["id"]): row
        for profile in receipt["profiles"]
        for row in profile["rows"]
    }


def _transition_counts(receipt: dict, passing_ids: set[str]) -> dict[tuple[int, int], int]:
    counts: dict[tuple[int, int], int] = {}
    for profile in receipt["profiles"]:
        for row in profile["rows"]:
            if row["id"] not in passing_ids:
                continue
            for support in row["supports"]:
                transition = support["transition"]
                key = (int(transition["lower_index"]), int(transition["upper_index"]))
                counts[key] = counts.get(key, 0) + 1
    return counts


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
        raise SystemExit("receipt hash mismatch")
    manifest = json.loads(manifest_bytes)
    receipt = json.loads(receipt_bytes)
    if receipt.get("manifest_sha256") != sha256_bytes(manifest_bytes):
        raise SystemExit("manifest hash mismatch")

    candidates = receipt["combined_candidates"]
    passing = [row for row in candidates if row["passed"]]
    failing = [row for row in candidates if not row["passed"]]
    passing_ids = {row["id"] for row in passing}
    transition_counts = _transition_counts(receipt, passing_ids)
    smoothing = [float(value) for value in manifest["smoothing_values"]]
    transition_keys = sorted(transition_counts)
    transition_labels = [
        rf"${smoothing[lower]:.2g}\,\to\,{smoothing[upper]:.2g}$"
        for lower, upper in transition_keys
    ]

    fig, axes = plt.subplots(1, 3, figsize=(12.2, 4.0), constrained_layout=True)

    axes[0].scatter(
        [row["parameters"]["a"] for row in passing],
        [row["parameters"]["c"] for row in passing],
        s=28,
        color="#1976d2",
        edgecolor="white",
        linewidth=0.35,
        label=f"qualified ({len(passing)})",
    )
    axes[0].scatter(
        [row["parameters"]["a"] for row in failing],
        [row["parameters"]["c"] for row in failing],
        s=34,
        marker="x",
        color="#d95f02",
        linewidth=1.1,
        label=f"unresolved transition ({len(failing)})",
    )
    axes[0].set_xlabel(r"$a$")
    axes[0].set_ylabel(r"$c$")
    axes[0].set_title("nested-support qualification\n94/104 candidates")
    axes[0].ticklabel_format(axis="x", style="plain", useOffset=False)
    axes[0].legend(loc="lower left", fontsize=7, frameon=True)

    colors = ["#8c6bb1", "#67a9cf", "#2166ac"]
    axes[1].barh(
        np.arange(len(transition_keys)),
        [transition_counts[key] for key in transition_keys],
        color=colors[: len(transition_keys)],
        edgecolor="white",
    )
    axes[1].set_yticks(np.arange(len(transition_keys)), transition_labels)
    axes[1].set_xlabel("support-profile reconstructions")
    axes[1].set_ylabel("last 3-branch $\to$ first 2-branch smoothing")
    axes[1].set_title("transition-scale brackets\n376 qualified reconstructions")
    for index, key in enumerate(transition_keys):
        axes[1].text(
            transition_counts[key] + 4,
            index,
            str(transition_counts[key]),
            va="center",
            fontsize=8,
        )
    axes[1].set_xlim(0, max(transition_counts.values()) * 1.14)

    pass_spans = np.asarray(
        [row["normalized_second_critical_span"] for row in passing], dtype=float
    )
    fail_spans = np.asarray(
        [row["normalized_second_critical_span"] for row in failing], dtype=float
    )
    bins = np.linspace(0.0, float(manifest["acceptance"]["maximum_normalized_second_critical_span"]), 13)
    axes[2].hist(
        pass_spans,
        bins=bins,
        color="#1976d2",
        alpha=0.82,
        edgecolor="white",
        label="qualified",
    )
    axes[2].scatter(
        fail_spans,
        np.full(fail_spans.size, -0.6),
        marker="x",
        color="#d95f02",
        linewidth=1.0,
        clip_on=False,
        label="unresolved transition",
    )
    gate = float(manifest["acceptance"]["maximum_normalized_second_critical_span"])
    axes[2].axvline(gate, color="#222222", linestyle="--", linewidth=1.0)
    axes[2].text(gate * 0.985, axes[2].get_ylim()[1] * 0.9, "gate", ha="right", fontsize=8)
    axes[2].set_xlabel("normalized second-critical span")
    axes[2].set_ylabel("candidates")
    axes[2].set_title(
        "critical-location stability\n"
        + rf"median {np.median(pass_spans):.5f}; max {np.max(pass_spans):.5f}"
    )
    axes[2].legend(
        handles=[
            Line2D((0,), (0,), marker="s", linestyle="none", color="#1976d2", label="qualified"),
            Line2D((0,), (0,), marker="x", linestyle="none", color="#d95f02", label="unresolved transition"),
        ],
        loc="upper right",
        fontsize=7,
        frameon=True,
    )

    fig.suptitle(
        r"EXP-201: the lower-$c$ shallow critical has a reproducible finite-data scale",
        fontsize=12,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)

    output_bytes = args.output.read_bytes()
    output_receipt = {
        "schema": "butterfly.exp201-smoothing-scale-audit-figure.v1",
        "experiment_id": "EXP-201",
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "input_receipt_sha256": sha256_bytes(receipt_bytes),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "qualified_candidate_count": len(passing),
        "unresolved_candidate_count": len(failing),
        "transition_bracket_counts": {
            f"{lower}-{upper}": transition_counts[(lower, upper)]
            for lower, upper in transition_keys
        },
        "median_normalized_second_critical_span": float(np.median(pass_spans)),
        "maximum_normalized_second_critical_span": float(np.max(pass_spans)),
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(output_receipt),
    )
    print(json.dumps(output_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

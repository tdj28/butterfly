#!/usr/bin/env python3
"""Plot the cross-step oracle-vote structure exposed by EXP-200."""

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


def _axis(rows: list[dict], index: int, name: str) -> np.ndarray:
    pairs = sorted(
        {
            (int(row["grid_index"][index]), float(row["parameters"][name]))
            for row in rows
        }
    )
    indices = np.asarray([pair[0] for pair in pairs], dtype=float)
    values = np.asarray([pair[1] for pair in pairs], dtype=float)
    slope, intercept = np.polyfit(indices, values, 1)
    return intercept + slope * np.arange(int(max(indices)) + 1, dtype=float)


def _edges(values: np.ndarray) -> np.ndarray:
    edges = np.empty(values.size + 1, dtype=float)
    edges[1:-1] = 0.5 * (values[:-1] + values[1:])
    edges[0] = values[0] - 0.5 * (values[1] - values[0])
    edges[-1] = values[-1] + 0.5 * (values[-1] - values[-2])
    return edges


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

    profiles = receipt["profiles"]
    by_profile = [{row["id"]: row for row in profile["rows"]} for profile in profiles]
    candidates = receipt["combined_candidates"]
    a_values = _axis(candidates, 0, "a")
    c_values = _axis(candidates, 1, "c")
    shape = (c_values.size, a_values.size)
    baseline = np.full(shape, np.nan)
    smooth = np.full(shape, np.nan)
    strict = np.full(shape, np.nan)
    pattern_count = 0
    baseline_count = 0
    strict_count = 0
    for candidate in candidates:
        i, j = map(int, candidate["grid_index"])
        rows = [profile[candidate["id"]] for profile in by_profile]
        votes = [row["robust_partition"]["variant_counts"] for row in rows]
        baseline_three = all(
            all(vote[index] == 3 for index in (0, 1, 2, 4)) for vote in votes
        )
        smooth_votes = [vote[3] for vote in votes]
        strict_eligible = bool(candidate["eligible"])
        baseline[j, i] = 1.0 if baseline_three else 0.0
        if smooth_votes == [2, 2]:
            smooth[j, i] = 0.0
        elif smooth_votes == [3, 3]:
            smooth[j, i] = 2.0
        else:
            smooth[j, i] = 1.0
        strict[j, i] = 1.0 if strict_eligible else 0.0
        baseline_count += int(baseline_three)
        strict_count += int(strict_eligible)
        pattern_count += int(baseline_three and smooth_votes == [2, 2])

    fig, axes = plt.subplots(1, 3, figsize=(11.8, 4.0), constrained_layout=True)
    a_edges, c_edges = _edges(a_values), _edges(c_values)
    binary_cmap = ListedColormap(("#d9d9d9", "#1976d2"))
    binary_norm = BoundaryNorm((-0.5, 0.5, 1.5), binary_cmap.N)
    smooth_cmap = ListedColormap(("#ef8a62", "#d9d9d9", "#67a9cf"))
    smooth_norm = BoundaryNorm((-0.5, 0.5, 1.5, 2.5), smooth_cmap.N)
    panels = (
        (baseline, binary_cmap, binary_norm, f"four baseline variants: 3 branches\n{baseline_count}/168 at both steps"),
        (smooth, smooth_cmap, smooth_norm, f"high-smoothing variant\n{pattern_count} baseline-three points collapse to 2"),
        (strict, binary_cmap, binary_norm, f"five-variant strict eligibility\n{strict_count}/168 at both steps"),
    )
    selected = receipt["selected_candidate"]["parameters"]
    for axis, (values, cmap, norm, title) in zip(axes, panels):
        axis.pcolormesh(
            a_edges,
            c_edges,
            np.ma.masked_invalid(values),
            cmap=cmap,
            norm=norm,
            shading="flat",
            rasterized=True,
        )
        axis.scatter(
            [selected["a"]],
            [selected["c"]],
            marker="*",
            s=80,
            facecolor="#fff176",
            edgecolor="#111111",
            linewidth=0.7,
        )
        axis.set_xlabel(r"$a$")
        axis.set_title(title)
        axis.ticklabel_format(axis="x", style="plain", useOffset=False)
    axes[0].set_ylabel(r"$c$")
    for axis in axes[1:]:
        axis.tick_params(labelleft=False)
    axes[0].legend(
        handles=[
            Line2D((0,), (0,), marker="s", linestyle="none", color="#1976d2", label="passes panel condition"),
            Line2D((0,), (0,), marker="s", linestyle="none", color="#d9d9d9", label="does not pass"),
        ],
        loc="lower left",
        fontsize=7,
        frameon=True,
    )
    axes[1].legend(
        handles=[
            Line2D((0,), (0,), marker="s", linestyle="none", color="#ef8a62", label="2 at both steps"),
            Line2D((0,), (0,), marker="s", linestyle="none", color="#67a9cf", label="3 at both steps"),
            Line2D((0,), (0,), marker="s", linestyle="none", color="#d9d9d9", label="mixed/unresolved"),
        ],
        loc="lower left",
        fontsize=7,
        frameon=True,
    )
    fig.suptitle(
        r"EXP-200: quadrupled support exposes smoothing sensitivity at $b=0.2$",
        fontsize=12,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    output_receipt = {
        "schema": "butterfly.exp200-oracle-sensitivity-figure.v1",
        "experiment_id": "EXP-200",
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "input_receipt_sha256": sha256_bytes(receipt_bytes),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "baseline_three_both_steps": baseline_count,
        "baseline_three_smooth_two_both_steps": pattern_count,
        "strict_eligible_both_steps": strict_count,
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(output_receipt),
    )
    print(json.dumps(output_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

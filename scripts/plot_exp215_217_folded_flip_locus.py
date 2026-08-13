#!/usr/bin/env python3
"""Plot the qualified lower turn and broad returning period-6 flip arm."""

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


SCHEMA = "butterfly.exp215-217-folded-flip-locus-figure.v1"


def _read_bound(path, expected, label):
    data = path.read_bytes()
    if sha256_bytes(data) != expected:
        raise SystemExit(f"{label} receipt hash mismatch")
    return data, json.loads(data)


def _sorted_ca(rows):
    values = sorted(((float(row["c"]), float(row["a"])) for row in rows))
    return np.asarray([value[0] for value in values]), np.asarray(
        [value[1] for value in values]
    )


def arm_separation(original_rows, returning_rows, c_values):
    original_c, original_a = _sorted_ca(original_rows)
    returning_c, returning_a = _sorted_ca(returning_rows)
    query = np.asarray(c_values, dtype=float)
    return np.interp(query, returning_c, returning_a) - np.interp(
        query, original_c, original_a
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = (
        "curve",
        "child",
        "extension",
        "grazing",
        "through",
        "turn",
        "returning",
    )
    for name in inputs:
        parser.add_argument(f"--{name}-receipt", type=Path, required=True)
        parser.add_argument(f"--expected-{name}-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    bound = {}
    for name in inputs:
        bound[name] = _read_bound(
            getattr(args, f"{name}_receipt"),
            getattr(args, f"expected_{name}_sha256"),
            name,
        )
    curve = bound["curve"][1]
    child = bound["child"][1]
    extension = bound["extension"][1]
    grazing = bound["grazing"][1]
    through = bound["through"][1]
    turn = bound["turn"][1]
    returning = bound["returning"][1]

    original_rows = (
        extension["directions"]["down"]["rows"]
        + curve["rows"]
        + extension["directions"]["up"]["rows"]
    )
    crossing_rows = extension["directions"]["down"]["rows"][-1:] + through["rows"]
    returning_rows = turn["rows"] + returning["rows"]
    original_c, original_a = _sorted_ca(original_rows)
    crossing_c = np.asarray([row["c"] for row in crossing_rows], dtype=float)
    crossing_a = np.asarray([row["a"] for row in crossing_rows], dtype=float)
    returning_c = np.asarray([row["c"] for row in returning_rows], dtype=float)
    returning_a = np.asarray([row["a"] for row in returning_rows], dtype=float)
    child_rows = [row for line in child["lines"] for row in line["rows"]]

    figure, axes = plt.subplots(2, 2, figsize=(13.2, 8.6), constrained_layout=True)
    axes[0, 0].scatter(
        [row["a"] for row in child_rows],
        [row["c"] for row in child_rows],
        s=8,
        color="#8073ac",
        alpha=0.32,
        label="qualified period-12 child sheet",
        zorder=1,
    )
    axes[0, 0].plot(original_a, original_c, color="#2166ac", linewidth=2.2, label="original flip arm")
    axes[0, 0].plot(crossing_a, crossing_c, "o-", color="#1b9e77", markersize=2.5, linewidth=1.4, label="through grazing")
    axes[0, 0].plot(returning_a, returning_c, "o-", color="#d95f02", markersize=2.0, linewidth=1.5, label="returning arm")
    minimum_index = int(np.argmin(np.r_[crossing_c, returning_c]))
    combined_a = np.r_[crossing_a, returning_a]
    combined_c = np.r_[crossing_c, returning_c]
    axes[0, 0].scatter(
        [combined_a[minimum_index]], [combined_c[minimum_index]], marker="D", s=55,
        color="#fdb863", edgecolor="#7f3b08", linewidth=0.7, zorder=5,
        label="sampled lower-$c$ turn",
    )
    axes[0, 0].scatter(
        [grazing["best_evaluation"]["a"]], [grazing["c_estimate"]], marker="*", s=105,
        color="#b2182b", edgecolor="white", linewidth=0.6, zorder=5,
        label="historical-section grazing",
    )
    axes[0, 0].set_xlabel(r"$a$")
    axes[0, 0].set_ylabel(r"$c$")
    axes[0, 0].set_title("one exact event locus, two widely separated arms")
    axes[0, 0].legend(fontsize=6.7, loc="upper left")

    lower_rows = extension["directions"]["down"]["rows"][-8:]
    axes[0, 1].plot(
        [row["a"] for row in lower_rows], [row["c"] for row in lower_rows],
        "o-", color="#2166ac", markersize=3.2, linewidth=1.5,
        label="six historical phases",
    )
    axes[0, 1].plot(
        crossing_a, crossing_c, "o-", color="#1b9e77", markersize=3.0,
        linewidth=1.5, label="seven after grazing",
    )
    turn_zoom = turn["rows"][:12]
    axes[0, 1].plot(
        [row["a"] for row in turn_zoom], [row["c"] for row in turn_zoom],
        "o-", color="#d95f02", markersize=3.0, linewidth=1.5,
        label="seven on returning arm",
    )
    axes[0, 1].scatter(
        [grazing["best_evaluation"]["a"]], [grazing["c_estimate"]], marker="*",
        s=100, color="#b2182b", edgecolor="white", linewidth=0.6, zorder=5,
    )
    axes[0, 1].scatter(
        [combined_a[minimum_index]], [combined_c[minimum_index]], marker="D",
        s=55, color="#fdb863", edgecolor="#7f3b08", linewidth=0.7, zorder=5,
    )
    axes[0, 1].set_xlim(0.21575, 0.2193)
    axes[0, 1].set_ylim(6.81, 6.955)
    axes[0, 1].set_xlabel(r"$a$")
    axes[0, 1].set_ylabel(r"$c$")
    axes[0, 1].set_title("grazing and lower projection turn are distinct")
    axes[0, 1].legend(fontsize=7.0, loc="lower right")

    common_c = np.linspace(7.01, 8.25, 240)
    separation = arm_separation(original_rows, returning_rows, common_c)
    axes[1, 0].plot(common_c, separation, color="#7b3294", linewidth=2.2)
    axes[1, 0].fill_between(common_c, 0.0, separation, color="#c2a5cf", alpha=0.35)
    for value in (7.16, 7.30, 8.00, 8.25):
        delta = float(arm_separation(original_rows, returning_rows, [value])[0])
        axes[1, 0].scatter([value], [delta], color="#7b3294", s=30, zorder=3)
        axes[1, 0].annotate(f"{delta:.4f}", (value, delta), xytext=(3, 4), textcoords="offset points", fontsize=7)
    axes[1, 0].set_xlabel(r"common $c$")
    axes[1, 0].set_ylabel(r"$a_{\rm returning}-a_{\rm original}$")
    axes[1, 0].set_title("arm separation grows across the shared $c$ range")
    axes[1, 0].grid(alpha=0.2)

    index = np.arange(1, len(returning["rows"]) + 1)
    orbit = np.asarray([row["orbit_residual"] for row in returning["rows"]])
    tangent = np.asarray([row["tangent_residual"] for row in returning["rows"]])
    arclength = np.asarray([row["arclength_residual"] for row in returning["rows"]])
    section = np.asarray([
        row["extremum_partitioned"]["maximum_section_residual"]
        for row in returning["rows"]
    ])
    floor = np.finfo(float).tiny
    axes[1, 1].plot(index, np.maximum(orbit, floor), color="#2166ac", label="orbit closure")
    axes[1, 1].plot(index, np.maximum(tangent, floor), color="#d95f02", label="event eigenvector")
    axes[1, 1].plot(index, np.maximum(arclength, floor), color="#1b9e77", label="arclength")
    axes[1, 1].plot(index, np.maximum(section, floor), color="#7570b3", label="section roots")
    axes[1, 1].axhline(1e-8, color="#222222", linestyle="--", linewidth=1.0, label="strict event gate")
    axes[1, 1].axhline(1e-9, color="#777777", linestyle=":", linewidth=1.0, label="section gate")
    axes[1, 1].set_yscale("log")
    axes[1, 1].set_xlabel("EXP-217 accepted-point index")
    axes[1, 1].set_ylabel("absolute residual")
    axes[1, 1].set_title("all 135 returning-arm events pass strict gates")
    axes[1, 1].legend(fontsize=6.8, loc="lower right", ncol=2)

    figure.suptitle(
        "EXP-215--217: the period-6 flip locus turns and forms a broad returning arm",
        fontsize=13,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    figure.savefig(temporary, dpi=args.dpi)
    plt.close(figure)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    figure_receipt = {
        "schema": SCHEMA,
        "experiment_ids": ["EXP-206", "EXP-211", "EXP-212", "EXP-213", "EXP-215", "EXP-216", "EXP-217"],
        **{f"{name}_receipt_sha256": sha256_bytes(bound[name][0]) for name in inputs},
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "returning_point_count": len(returning["rows"]),
        "returning_terminal": {"a": returning["rows"][-1]["a"], "c": returning["rows"][-1]["c"]},
        "sampled_turn_c": float(np.min(combined_c)),
        "shared_c_separation": {
            str(value): float(arm_separation(original_rows, returning_rows, [value])[0])
            for value in (7.16, 7.30, 8.00, 8.25)
        },
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(figure_receipt),
    )
    print(json.dumps(figure_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

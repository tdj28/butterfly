#!/usr/bin/env python3
"""Plot the broad flip-curve extension and qualified section grazing."""

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


SCHEMA = "butterfly.exp212-214-flip-extension-grazing-figure.v1"


def _read_bound(path, expected, label):
    data = path.read_bytes()
    if sha256_bytes(data) != expected:
        raise SystemExit(f"{label} receipt hash mismatch")
    return data, json.loads(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curve-receipt", type=Path, required=True)
    parser.add_argument("--expected-curve-sha256", required=True)
    parser.add_argument("--extension-receipt", type=Path, required=True)
    parser.add_argument("--expected-extension-sha256", required=True)
    parser.add_argument("--grazing-receipt", type=Path, required=True)
    parser.add_argument("--expected-grazing-sha256", required=True)
    parser.add_argument("--count-receipt", type=Path, required=True)
    parser.add_argument("--expected-count-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()
    curve_bytes, curve = _read_bound(
        args.curve_receipt, args.expected_curve_sha256, "EXP-206"
    )
    extension_bytes, extension = _read_bound(
        args.extension_receipt, args.expected_extension_sha256, "EXP-212"
    )
    grazing_bytes, grazing = _read_bound(
        args.grazing_receipt, args.expected_grazing_sha256, "EXP-213"
    )
    count_bytes, count = _read_bound(
        args.count_receipt, args.expected_count_sha256, "EXP-214"
    )

    figure, axes = plt.subplots(2, 2, figsize=(13.2, 8.4), constrained_layout=True)
    source_c = np.asarray([row["c"] for row in curve["rows"]])
    source_a = np.asarray([row["a"] for row in curve["rows"]])
    axes[0, 0].plot(source_c, source_a, color="#2166ac", linewidth=2.2, label="EXP-206 source segment")
    for direction, color, label in (
        ("down", "#1b7837", "EXP-212 lower accepted arm"),
        ("up", "#762a83", "EXP-212 upper 100-point arm"),
    ):
        rows = sorted(extension["directions"][direction]["rows"], key=lambda row: row["c"])
        axes[0, 0].plot(
            [row["c"] for row in rows],
            [row["a"] for row in rows],
            "o-",
            color=color,
            markersize=2.3,
            linewidth=1.1,
            label=label,
        )
    axes[0, 0].axvspan(7.18, 7.30, color="#fdae61", alpha=0.18, label="EXP-211 child-sheet span")
    axes[0, 0].scatter(
        [grazing["c_estimate"]],
        [grazing["best_evaluation"]["a"]],
        marker="*",
        s=110,
        color="#d73027",
        edgecolor="white",
        linewidth=0.6,
        zorder=5,
        label="qualified historical-section grazing",
    )
    axes[0, 0].set_xlabel(r"$c$")
    axes[0, 0].set_ylabel(r"flip-event $a$")
    axes[0, 0].set_title("orbit-defined period-6 flip curve\nupper arm reaches $c=8.40309$")
    axes[0, 0].legend(fontsize=6.7, loc="lower left")

    offsets = np.asarray([row["c"] - count["center_c"] for row in count["rows"]])
    signed_log_offsets = np.sign(offsets) * np.log10(np.abs(offsets) / 1e-7)
    offset_ticks = np.asarray((-4, -3, -2, -1, 1, 2, 3, 4), dtype=float)
    offset_labels = (
        r"$-10^{-3}$",
        r"$-10^{-4}$",
        r"$-10^{-5}$",
        r"$-10^{-6}$",
        r"$10^{-6}$",
        r"$10^{-5}$",
        r"$10^{-4}$",
        r"$10^{-3}$",
    )
    clearances = np.asarray([row["grazing"]["signed_y_clearance"] for row in count["rows"]])
    axes[0, 1].axhline(0.0, color="#444444", linewidth=0.9)
    axes[0, 1].axvline(0.0, color="#444444", linewidth=0.9)
    axes[0, 1].plot(signed_log_offsets, clearances, "o-", color="#2166ac", linewidth=1.1)
    axes[0, 1].set_xticks(offset_ticks, offset_labels)
    axes[0, 1].set_yscale("symlog", linthresh=5e-7)
    axes[0, 1].set_yticks(
        (-1e-3, -1e-4, -1e-5, -1e-6, 0.0, 1e-6, 1e-5, 1e-4, 1e-3)
    )
    axes[0, 1].set_xlabel(r"$c-c_{\rm grazing}$")
    axes[0, 1].set_ylabel(r"nearest-extremum $y-y_{\rm eq}$")
    axes[0, 1].set_title(
        "continuous nondegenerate tangency\n"
        r"DOP853/Radau clearance difference $<4.86\times10^{-12}$"
    )

    standard = np.asarray([row["standard_historical_count"] for row in count["rows"]])
    partitioned = np.asarray([row["extremum_partitioned"]["count"] for row in count["rows"]])
    barrio = np.asarray([row["barrio_count"] for row in count["rows"]])
    axes[1, 0].plot(signed_log_offsets, standard, "o--", color="#d95f02", label="standard historical counter")
    axes[1, 0].plot(signed_log_offsets, partitioned, "s-", color="#1b7837", label="extremum-partitioned count")
    axes[1, 0].plot(signed_log_offsets, barrio, "^-", color="#762a83", label="Barrio count")
    axes[1, 0].axvline(0.0, color="#444444", linewidth=0.9)
    axes[1, 0].set_xticks(offset_ticks, offset_labels)
    axes[1, 0].set_yticks((6, 7, 8))
    axes[1, 0].set_xlabel(r"$c-c_{\rm grazing}$")
    axes[1, 0].set_ylabel("section phases per flow period")
    axes[1, 0].set_title("representation changes; flow event persists\nstandard counter misses three close crossings")
    axes[1, 0].legend(fontsize=7.0, loc="center right")

    margins = np.asarray([row["grazing"]["gate_margin"] for row in count["rows"]])
    line_x = np.linspace(clearances.min(), clearances.max(), 200)
    axes[1, 1].plot(
        line_x,
        float(grazing["best_evaluation"]["a"]) * line_x,
        "--",
        color="#222222",
        linewidth=1.0,
        label=r"exact extremum relation $x_{\rm eq}-x=a(y-y_{\rm eq})$",
    )
    scatter = axes[1, 1].scatter(
        clearances,
        margins,
        c=np.log10(np.abs(offsets)),
        cmap="coolwarm",
        s=48,
        edgecolor="white",
        linewidth=0.6,
        zorder=3,
    )
    axes[1, 1].scatter([0.0], [0.0], marker="*", s=110, color="#d73027", zorder=4)
    axes[1, 1].set_xlabel(r"section-plane clearance $y-y_{\rm eq}$")
    axes[1, 1].set_ylabel(r"half-plane gate margin $x_{\rm eq}-x$")
    axes[1, 1].set_title("section plane and gate meet at one grazing\ncurvature $d^2y/dt^2=-13.6961$")
    axes[1, 1].legend(fontsize=7.0, loc="upper left")
    colorbar = figure.colorbar(scatter, ax=axes[1, 1], fraction=0.046, pad=0.04)
    colorbar.set_label(r"$\log_{10}|c-c_{\rm grazing}|$")

    figure.suptitle(
        "EXP-212--214: broad flip-curve continuation exposes a section-dependent phase change",
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
        "experiment_ids": ["EXP-206", "EXP-212", "EXP-213", "EXP-214"],
        "curve_receipt_sha256": sha256_bytes(curve_bytes),
        "extension_receipt_sha256": sha256_bytes(extension_bytes),
        "grazing_receipt_sha256": sha256_bytes(grazing_bytes),
        "count_receipt_sha256": sha256_bytes(count_bytes),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "accepted_extension_points": extension["new_point_count"],
        "count_audit_points": len(count["rows"]),
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(figure_receipt),
    )
    print(json.dumps(figure_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

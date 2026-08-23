#!/usr/bin/env python3
"""Plot the qualified seventh and eighth returning-arm birth directions."""

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


SCHEMA = "butterfly.exp316-320-birth-criticality-figure.v1"


def read_bound(path: Path, expected_hash: str, schema: str, passed: bool):
    data = path.read_bytes()
    if sha256_bytes(data) != expected_hash:
        raise SystemExit(f"receipt hash mismatch: {path}")
    receipt = json.loads(data)
    if receipt.get("schema") != schema or receipt.get("passed") is not passed:
        raise SystemExit(f"unexpected receipt status: {path}")
    return data, receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp316", type=Path, required=True)
    parser.add_argument("--exp316-sha256", required=True)
    parser.add_argument("--exp317", type=Path, required=True)
    parser.add_argument("--exp317-sha256", required=True)
    parser.add_argument("--exp319", type=Path, required=True)
    parser.add_argument("--exp319-sha256", required=True)
    parser.add_argument("--exp320", type=Path, required=True)
    parser.add_argument("--exp320-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    bytes316, exp316 = read_bound(
        args.exp316,
        args.exp316_sha256,
        "butterfly.jones-period3072-solver-relative-criticality-receipt.v1",
        False,
    )
    bytes317, exp317 = read_bound(
        args.exp317,
        args.exp317_sha256,
        "butterfly.jones-period3072-segmented-identity-receipt.v1",
        True,
    )
    bytes319, exp319 = read_bound(
        args.exp319,
        args.exp319_sha256,
        "butterfly.jones-period1536-decimal-child-switch-receipt.v1",
        True,
    )
    bytes320, exp320 = read_bound(
        args.exp320,
        args.exp320_sha256,
        "butterfly.jones-period1536-decimal-child-switch-receipt.v1",
        True,
    )
    if exp319["local_criticality_classification"] != "supercritical":
        raise SystemExit("EXP-319 supercritical nomination changed")
    if exp320["local_criticality_classification"] != "supercritical":
        raise SystemExit("EXP-320 supercritical replication changed")

    figure, axes = plt.subplots(2, 2, figsize=(13.2, 8.8), constrained_layout=True)
    colors = {4096: "#2166ac", 8192: "#b2182b"}
    markers = {-1: "o", 1: "s"}

    for steps, receipt in ((4096, exp319), (8192, exp320)):
        for direction in (-1, 1):
            rows = [row for row in receipt["candidates"] if row["direction"] == direction]
            axes[0, 0].loglog(
                [row["half_node_rms"] for row in rows],
                [abs(row["parameter_displacement"]) for row in rows],
                marker=markers[direction],
                linewidth=1.8,
                markersize=7,
                color=colors[steps],
                linestyle="-" if direction == -1 else "--",
                label=f"{steps:,} steps, sign {direction:+d}",
            )
    reference = exp320["candidates"][0]
    guide_x = np.geomspace(
        min(row["half_node_rms"] for row in exp320["candidates"]) * 0.9,
        max(row["half_node_rms"] for row in exp320["candidates"]) * 1.1,
        50,
    )
    guide_y = abs(reference["parameter_displacement"]) * (
        guide_x / reference["half_node_rms"]
    ) ** 2
    axes[0, 0].loglog(guide_x, guide_y, color="#555555", linewidth=1.2, label=r"$|\Delta a|\propto A^2$")
    axes[0, 0].set_xlabel("primitive half-node RMS amplitude")
    axes[0, 0].set_ylabel(r"event-relative $|\Delta a|$")
    axes[0, 0].set_title("seventh daughter opens quadratically toward lower a")
    axes[0, 0].legend(fontsize=7.4)
    axes[0, 0].grid(alpha=0.2, which="both")

    for steps, receipt in ((4096, exp319), (8192, exp320)):
        for direction in (-1, 1):
            rows = [row for row in receipt["candidates"] if row["direction"] == direction]
            axes[0, 1].plot(
                [row["half_node_rms"] for row in rows],
                [row["spectrum"]["dominant_modulus"] for row in rows],
                marker=markers[direction],
                linewidth=1.8,
                markersize=7,
                color=colors[steps],
                linestyle="-" if direction == -1 else "--",
                label=f"{steps:,} steps, sign {direction:+d}",
            )
    axes[0, 1].axhline(1.0, color="#222222", linestyle=":", label="stability boundary")
    axes[0, 1].set_xlabel("primitive half-node RMS amplitude")
    axes[0, 1].set_ylabel("dominant transverse modulus")
    axes[0, 1].set_title("immediate period-1536 daughters are stable")
    axes[0, 1].ticklabel_format(axis="x", style="sci", scilimits=(-2, 2))
    axes[0, 1].legend(fontsize=7.4)
    axes[0, 1].grid(alpha=0.2)

    rows319 = sorted(exp319["candidates"], key=lambda row: (row["step_length"], row["direction"]))
    rows320 = sorted(exp320["candidates"], key=lambda row: (row["step_length"], row["direction"]))
    metrics = {
        r"$|\Delta a|$": max(
            abs(abs(left["parameter_displacement"]) - abs(right["parameter_displacement"]))
            / abs(right["parameter_displacement"])
            for left, right in zip(rows319, rows320)
        ),
        "amplitude": max(
            abs(left["half_node_rms"] - right["half_node_rms"])
            / right["half_node_rms"]
            for left, right in zip(rows319, rows320)
        ),
        "child modulus": max(
            abs(left["spectrum"]["dominant_modulus"] - right["spectrum"]["dominant_modulus"])
            / right["spectrum"]["dominant_modulus"]
            for left, right in zip(rows319, rows320)
        ),
        "opening exponent": abs(
            exp319["scaling"]["parameter_amplitude_exponent"]
            - exp320["scaling"]["parameter_amplitude_exponent"]
        ) / exp320["scaling"]["parameter_amplitude_exponent"],
    }
    bars = axes[1, 0].bar(
        np.arange(len(metrics)),
        list(metrics.values()),
        color=["#2166ac", "#4393c3", "#f4a582", "#b2182b"],
    )
    axes[1, 0].set_yscale("log")
    axes[1, 0].set_xticks(np.arange(len(metrics)), list(metrics), rotation=14, ha="right")
    axes[1, 0].set_ylabel("maximum 4,096/8,192 relative difference")
    axes[1, 0].set_title("resolution doubling reproduces the local branch")
    for bar, value in zip(bars, metrics.values()):
        axes[1, 0].annotate(
            f"{value:.1e}",
            (bar.get_x() + bar.get_width() / 2, value),
            ha="center",
            va="bottom",
            xytext=(0, 3),
            textcoords="offset points",
            fontsize=8,
        )
    axes[1, 0].grid(alpha=0.2, axis="y", which="both")

    solver_names = ["DOP853", "Radau"]
    parent = [exp316["results"][name.lower()]["parent"]["dominant_modulus"] for name in solver_names]
    child = [exp316["results"][name.lower()]["child"]["dominant_modulus"] for name in solver_names]
    positions = np.arange(2)
    width = 0.34
    axes[1, 1].bar(positions - width / 2, parent, width, color="#2166ac", label="period-1536 parent")
    axes[1, 1].bar(positions + width / 2, child, width, color="#b2182b", label="period-3072 daughter")
    axes[1, 1].axhline(1.0, color="#222222", linestyle=":", label="stability boundary")
    axes[1, 1].set_yscale("log")
    axes[1, 1].set_xticks(positions, solver_names)
    axes[1, 1].set_ylabel("dominant transverse modulus")
    axes[1, 1].set_title("eighth daughter is unstable on the stable-parent side")
    axes[1, 1].legend(fontsize=7.4)
    axes[1, 1].grid(alpha=0.2, axis="y", which="both")
    axes[1, 1].text(
        0.03,
        0.95,
        f"segmented identity separation/error = {exp317['separation_error_ratio']:,.1f}",
        transform=axes[1, 1].transAxes,
        ha="left",
        va="top",
        fontsize=8,
    )

    figure.suptitle(
        "EXP-316--320: opposite criticality at the seventh and eighth returning-arm births",
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
        "exp316_receipt_sha256": sha256_bytes(bytes316),
        "exp317_receipt_sha256": sha256_bytes(bytes317),
        "exp319_receipt_sha256": sha256_bytes(bytes319),
        "exp320_receipt_sha256": sha256_bytes(bytes320),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "event7_exponents": [
            exp319["scaling"]["parameter_amplitude_exponent"],
            exp320["scaling"]["parameter_amplitude_exponent"],
        ],
        "cross_resolution_metrics": metrics,
        "event8_parent_moduli": parent,
        "event8_child_moduli": child,
        "event8_identity_separation_error_ratio": exp317["separation_error_ratio"],
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(receipt),
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Plot the qualified returning-child strip and its second flip crossing."""

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


SCHEMA = "butterfly.exp223-226-returning-child-endpoint-figure.v1"


def _read_bound(path, expected, label):
    data = path.read_bytes()
    if sha256_bytes(data) != expected:
        raise SystemExit(f"{label} receipt hash mismatch")
    return data, json.loads(data)


def _root_evaluations(root_result):
    rows = sorted(root_result["evaluations"], key=lambda row: float(row["c"]))
    return (
        np.asarray([row["c"] for row in rows], dtype=float),
        np.asarray([row["flip_residual"] for row in rows], dtype=float),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-receipt", type=Path, required=True)
    parser.add_argument("--expected-event-sha256", required=True)
    parser.add_argument("--adaptive-receipt", type=Path, required=True)
    parser.add_argument("--expected-adaptive-sha256", required=True)
    parser.add_argument("--endpoint-receipt", type=Path, required=True)
    parser.add_argument("--expected-endpoint-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    event_bytes, event = _read_bound(
        args.event_receipt, args.expected_event_sha256, "event"
    )
    adaptive_bytes, adaptive = _read_bound(
        args.adaptive_receipt, args.expected_adaptive_sha256, "adaptive"
    )
    endpoint_bytes, endpoint = _read_bound(
        args.endpoint_receipt, args.expected_endpoint_sha256, "endpoint"
    )
    if endpoint.get("passed") is not True:
        raise SystemExit("endpoint receipt must have passed")

    accepted = adaptive["accepted_rows"]
    accepted = sorted(accepted, key=lambda row: float(row["c"]))
    child_c = np.asarray([row["c"] for row in accepted], dtype=float)
    child_a = np.asarray([row["a"] for row in accepted], dtype=float)
    parent_modulus = np.asarray(
        [row["parent"]["dominant_transverse_multiplier"]["modulus"] for row in accepted]
    )
    child_modulus = np.asarray(
        [row["child"]["dominant_transverse_multiplier"]["modulus"] for row in accepted]
    )
    subperiod = np.asarray(
        [row["minimum_proper_subperiod_closure"] for row in accepted], dtype=float
    )
    arm = sorted(
        [row for row in event["rows"] if 7.13 <= float(row["c"]) <= 7.66],
        key=lambda row: float(row["c"]),
    )
    arm_c = np.asarray([row["c"] for row in arm], dtype=float)
    arm_a = np.asarray([row["a"] for row in arm], dtype=float)
    root_c = float(endpoint["root_results"]["dop853"]["root"]["c"])
    root_a = float(endpoint["root_results"]["dop853"]["root"]["a"])
    left = endpoint["primitive_left"]["row"]
    right_dop = endpoint["double_cover_right"]["dop853"]
    right_radau = endpoint["double_cover_right"]["radau"]

    figure, axes = plt.subplots(2, 2, figsize=(13.2, 8.8), constrained_layout=True)

    axes[0, 0].plot(
        arm_a,
        arm_c,
        color="#333333",
        linewidth=1.6,
        label="exact returning flip arm",
        zorder=1,
    )
    points = axes[0, 0].scatter(
        child_a,
        child_c,
        c=child_modulus,
        cmap="viridis",
        vmin=0.0,
        vmax=1.0,
        s=13,
        linewidth=0.0,
        label="qualified stable period-12 strip",
        zorder=3,
    )
    axes[0, 0].scatter(
        [root_a],
        [root_c],
        marker="*",
        s=125,
        color="#d73027",
        edgecolor="white",
        linewidth=0.7,
        label="second period-6 flip crossing",
        zorder=5,
    )
    axes[0, 0].set_xlabel(r"$a$")
    axes[0, 0].set_ylabel(r"$c$")
    axes[0, 0].set_title("stable child follows 45 exact returning-arm events")
    axes[0, 0].legend(fontsize=7.2, loc="upper left")
    colorbar = figure.colorbar(points, ax=axes[0, 0], pad=0.01)
    colorbar.set_label("child dominant multiplier modulus")

    for name, style, color in (
        ("dop853", "o-", "#2166ac"),
        ("radau", "s--", "#d95f02"),
    ):
        values_c, residual = _root_evaluations(endpoint["root_results"][name])
        axes[0, 1].plot(
            values_c,
            residual,
            style,
            color=color,
            linewidth=1.3,
            markersize=3.5,
            label=name.upper(),
        )
    axes[0, 1].axhline(0.0, color="#222222", linewidth=0.9)
    axes[0, 1].axvline(root_c, color="#d73027", linestyle=":", linewidth=1.2)
    axes[0, 1].annotate(
        f"roots differ by\n{endpoint['root_solver_c_difference']:.2e} in $c$",
        xy=(root_c, 0.0),
        xytext=(9, 30),
        textcoords="offset points",
        fontsize=8,
        arrowprops={"arrowstyle": "->", "color": "#555555", "linewidth": 0.8},
    )
    axes[0, 1].set_xlabel(r"$c$ on $a=a_{\rm event}(c)-5.73024\times10^{-7}$")
    axes[0, 1].set_ylabel(r"parent flip residual $\Re(\mu)+1$")
    axes[0, 1].set_title("two solvers independently localize the second crossing")
    axes[0, 1].legend(fontsize=7.5)
    axes[0, 1].grid(alpha=0.2)

    axes[1, 0].plot(
        child_c,
        parent_modulus,
        color="#d95f02",
        linewidth=1.1,
        label="period-6 parent",
    )
    axes[1, 0].plot(
        child_c,
        child_modulus,
        color="#2166ac",
        linewidth=1.1,
        label="primitive period-12 child",
    )
    axes[1, 0].scatter(
        [left["c"]],
        [left["child"]["dominant_transverse_multiplier"]["modulus"]],
        color="#2166ac",
        marker="D",
        s=38,
        zorder=4,
        label="independent left control",
    )
    axes[1, 0].scatter(
        [right_dop["row"]["c"]],
        [right_dop["metrics"]["parent_multiplier_modulus"]],
        color="#d95f02",
        marker="x",
        s=52,
        zorder=4,
        label="stable parent after crossing",
    )
    axes[1, 0].axhline(1.0, color="#222222", linestyle="--", linewidth=0.9)
    axes[1, 0].axvline(root_c, color="#d73027", linestyle=":", linewidth=1.2)
    axes[1, 0].set_xlabel(r"$c$")
    axes[1, 0].set_ylabel("dominant transverse multiplier modulus")
    axes[1, 0].set_title("the qualified child occupies the unstable-parent side")
    axes[1, 0].legend(fontsize=7.0, ncol=2, loc="upper left")
    axes[1, 0].grid(alpha=0.2)

    axes[1, 1].plot(
        child_c,
        subperiod,
        color="#7b3294",
        linewidth=1.2,
        label="primitive-child minimum proper-subperiod closure",
    )
    axes[1, 1].scatter(
        [left["c"]],
        [left["minimum_proper_subperiod_closure"]],
        color="#7b3294",
        marker="D",
        s=38,
        zorder=4,
        label="qualified primitive left control",
    )
    axes[1, 1].scatter(
        [right_dop["row"]["c"], right_radau["row"]["c"]],
        [
            right_dop["metrics"]["child_half_period_closure"],
            right_radau["metrics"]["child_half_period_closure"],
        ],
        color=["#2166ac", "#d95f02"],
        marker="x",
        s=55,
        zorder=4,
        label="DOP853/Radau double-cover half-period closure",
    )
    axes[1, 1].axhline(1e-4, color="#555555", linestyle="--", linewidth=0.9, label="primitive gate")
    axes[1, 1].axvline(root_c, color="#d73027", linestyle=":", linewidth=1.2)
    axes[1, 1].set_yscale("log")
    axes[1, 1].set_xlabel(r"$c$")
    axes[1, 1].set_ylabel("state-space closure distance")
    axes[1, 1].set_title("proper-subperiod separation collapses after the crossing")
    axes[1, 1].legend(fontsize=6.8, loc="lower left")
    axes[1, 1].grid(alpha=0.2, which="both")

    figure.suptitle(
        "EXP-223--226: a broad returning-arm period-12 strip ends at a second period-6 flip",
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
        "experiment_ids": ["EXP-217", "EXP-223", "EXP-226"],
        "event_receipt_sha256": sha256_bytes(event_bytes),
        "adaptive_receipt_sha256": sha256_bytes(adaptive_bytes),
        "endpoint_receipt_sha256": sha256_bytes(endpoint_bytes),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "accepted_point_count": len(accepted),
        "exact_event_count": int(adaptive["exact_event_count"]),
        "root": {"a": root_a, "c": root_c},
        "root_solver_c_difference": float(endpoint["root_solver_c_difference"]),
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(receipt),
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

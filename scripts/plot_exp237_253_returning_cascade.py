#!/usr/bin/env python3
"""Plot the exact returning-arm cascade through stable period 96."""

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


SCHEMA = "butterfly.exp237-253-returning-cascade-figure.v1"


def _read_bound(path: Path, expected: str, label: str) -> tuple[bytes, dict]:
    data = path.read_bytes()
    if sha256_bytes(data) != expected:
        raise SystemExit(f"{label} receipt hash mismatch")
    receipt = json.loads(data)
    if receipt.get("passed") is not True:
        raise SystemExit(f"{label} receipt must have passed")
    return data, receipt


def _event_metrics(receipt: dict) -> tuple[float, float, float, float]:
    if receipt["experiment_id"] == "EXP-251":
        reference = abs(
            float(receipt["source_flip_spectrum"]["direct_flip_residual"])
        )
        independent = abs(
            float(receipt["independent_flip_spectrum"]["direct_flip_residual"])
        )
    else:
        reference = abs(float(receipt["flip_spectrum"]["direct_flip_residual"]))
        independent = abs(
            float(receipt["independent_radau"]["flip_multiplier"]["real"]) + 1.0
        )
    return (
        float(receipt["corrected_a"]),
        float(receipt["period_time"]),
        reference,
        independent,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    labels = ("event12", "qual24", "event24", "qual48", "event48", "qual96")
    for label in labels:
        parser.add_argument(f"--{label}-receipt", type=Path, required=True)
        parser.add_argument(f"--expected-{label}-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    bound = {}
    for label in labels:
        bound[label] = _read_bound(
            getattr(args, f"{label}_receipt"),
            getattr(args, f"expected_{label}_sha256"),
            label,
        )

    events = [bound[name][1] for name in ("event12", "event24", "event48")]
    qualifications = [
        bound[name][1] for name in ("qual24", "qual48", "qual96")
    ]
    event = np.asarray([_event_metrics(row) for row in events])
    event_a = event[:, 0]
    event_period = event[:, 1]
    spacings = event_a[:-1] - event_a[1:]
    spacing_ratio = float(spacings[0] / spacings[1])
    parent_periods = np.asarray([12, 24, 48])
    transition_labels = ["12→24", "24→48", "48→96"]
    solver_names = ("dop853", "radau")
    parent_moduli = np.asarray(
        [
            [float(row["results"][name]["parent"]["dominant_modulus"]) for name in solver_names]
            for row in qualifications
        ]
    )
    child_moduli = np.asarray(
        [
            [float(row["results"][name]["child"]["dominant_modulus"]) for name in solver_names]
            for row in qualifications
        ]
    )

    figure, axes = plt.subplots(2, 2, figsize=(13.2, 8.8), constrained_layout=True)

    offset = (event_a - event_a[-1]) * 1e8
    axes[0, 0].plot(
        offset, parent_periods, "o-", color="#7b3294", linewidth=2.0, markersize=7
    )
    annotation_offsets = ((6, 7), (6, 7), (-116, 7))
    for x_value, period, a_value, period_time, text_offset in zip(
        offset, parent_periods, event_a, event_period, annotation_offsets
    ):
        axes[0, 0].annotate(
            f"$P={period}$\n$a={a_value:.12f}$\n$T={period_time:.3f}$",
            (x_value, period),
            xytext=text_offset,
            textcoords="offset points",
            fontsize=7.3,
        )
    axes[0, 0].invert_xaxis()
    axes[0, 0].set_yscale("log", base=2)
    axes[0, 0].set_yticks(parent_periods, labels=[str(value) for value in parent_periods])
    axes[0, 0].set_xlabel(r"$(a-a_{48\to96})\times10^8$")
    axes[0, 0].set_ylabel("parent section period")
    axes[0, 0].set_title("three exact real-$-1$ events accumulate in $a$")
    axes[0, 0].grid(alpha=0.2)

    bars = axes[0, 1].bar(
        ["12→24 to 24→48", "24→48 to 48→96"],
        spacings,
        color=["#2166ac", "#d95f02"],
        width=0.62,
    )
    axes[0, 1].set_yscale("log")
    axes[0, 1].set_ylim(2e-8, 2e-7)
    axes[0, 1].set_ylabel(r"successive event spacing $\Delta a$")
    axes[0, 1].set_title(f"one finite spacing ratio: {spacing_ratio:.3f}")
    for bar, value in zip(bars, spacings):
        axes[0, 1].annotate(
            f"{value:.3e}",
            (bar.get_x() + bar.get_width() / 2.0, value),
            ha="center",
            va="bottom",
            xytext=(0, 4),
            textcoords="offset points",
            fontsize=8,
        )
    axes[0, 1].text(
        0.5,
        0.48,
        "finite evidence; not a universality estimate",
        transform=axes[0, 1].transAxes,
        ha="center",
        fontsize=8,
    )
    axes[0, 1].grid(alpha=0.2, axis="y")

    x_values = np.arange(3)
    for solver_index, (solver_name, marker) in enumerate(zip(solver_names, ("o", "s"))):
        shift = -0.055 if solver_index == 0 else 0.055
        axes[1, 0].scatter(
            x_values + shift,
            parent_moduli[:, solver_index],
            marker=marker,
            s=48,
            color="#d95f02",
            edgecolor="white",
            linewidth=0.5,
            label=f"parent, {solver_name.upper()}",
            zorder=3,
        )
        axes[1, 0].scatter(
            x_values + shift,
            child_moduli[:, solver_index],
            marker=marker,
            s=48,
            color="#2166ac",
            edgecolor="white",
            linewidth=0.5,
            label=f"child, {solver_name.upper()}",
            zorder=3,
        )
    for index in x_values:
        axes[1, 0].plot(
            [index, index],
            [np.mean(child_moduli[index]), np.mean(parent_moduli[index])],
            color="#777777",
            linewidth=0.8,
            zorder=1,
        )
    axes[1, 0].axhline(1.0, color="#222222", linestyle="--", linewidth=1.0)
    axes[1, 0].set_xticks(x_values, transition_labels)
    axes[1, 0].set_ylabel("dominant transverse multiplier modulus")
    axes[1, 0].set_title("independent solvers recover supercritical exchange")
    axes[1, 0].legend(fontsize=6.8, ncol=2, loc="lower left")
    axes[1, 0].grid(alpha=0.2, axis="y")

    width = 0.34
    axes[1, 1].bar(
        x_values - width / 2,
        event[:, 2],
        width,
        color="#2166ac",
        label="DOP853 segmented",
    )
    axes[1, 1].bar(
        x_values + width / 2,
        event[:, 3],
        width,
        color="#d95f02",
        label="independent Radau",
    )
    axes[1, 1].set_yscale("log")
    axes[1, 1].set_xticks(x_values, transition_labels)
    axes[1, 1].set_ylabel(r"event multiplier residual $|\Re(\mu)+1|$")
    axes[1, 1].set_title("all three events survive independent integration")
    axes[1, 1].legend(fontsize=7.2)
    axes[1, 1].grid(alpha=0.2, axis="y")

    figure.suptitle(
        "EXP-237--253: exact returning-arm cascade through stable period 96",
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
        "experiment_ids": ["EXP-237", "EXP-241", "EXP-244", "EXP-246", "EXP-251", "EXP-253"],
        **{
            f"{label}_receipt_sha256": sha256_bytes(value[0])
            for label, value in bound.items()
        },
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "event_a": event_a.tolist(),
        "event_period_time": event_period.tolist(),
        "event_spacings": spacings.tolist(),
        "finite_spacing_ratio": spacing_ratio,
        "parent_moduli": parent_moduli.tolist(),
        "child_moduli": child_moduli.tolist(),
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(receipt),
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

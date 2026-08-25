#!/usr/bin/env python3
"""Plot the qualified Jones homoclinic curve and preserved solver failures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.exp342-382-homoclinic-continuation-figure.v1"
QUALIFIED_IDS = (342, 347, 350, 360, 361, 362, 363, 365, 366, 367, 368)
FAILED_IDS = (364, 369, 370, 371, 372, 373, 374, 375, 376, 377)
FIXED_C = {342: 10.3084, 347: 10.3104, 350: 10.3144}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def curve_point(experiment_id: int, receipt: dict) -> tuple[float, float]:
    variables = receipt["final_variables"]
    c_value = variables.get("c", receipt.get("fixed_c", FIXED_C.get(experiment_id)))
    if c_value is None:
        raise ValueError(f"EXP-{experiment_id} lacks a c coordinate")
    return float(c_value), float(variables["a"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")

    inputs = []
    receipts = {}
    for experiment_id in QUALIFIED_IDS + FAILED_IDS:
        path = args.receipt_dir / f"EXP-{experiment_id}.json"
        data = path.read_bytes()
        receipt = json.loads(data)
        if receipt.get("experiment_id") != f"EXP-{experiment_id}":
            raise SystemExit(f"receipt identity mismatch: {path}")
        expected_pass = experiment_id in QUALIFIED_IDS
        if bool(receipt.get("passed")) != expected_pass:
            raise SystemExit(f"receipt status mismatch: {path}")
        inputs.append(
            {
                "experiment_id": f"EXP-{experiment_id}",
                "path": str(path),
                "sha256": sha256_bytes(data),
            }
        )
        receipts[experiment_id] = receipt

    qualified = np.asarray(
        [curve_point(experiment_id, receipts[experiment_id]) for experiment_id in QUALIFIED_IDS]
    )
    failed_points = {
        experiment_id: curve_point(experiment_id, receipts[experiment_id])
        for experiment_id in FAILED_IDS
        if receipts[experiment_id].get("final_variables") is not None
    }
    last_c, last_a = qualified[-1]
    prior_c, prior_a = qualified[-2]
    slope = (last_a - prior_a) / (last_c - prior_c)
    historical_a = 0.1798
    projected_c = last_c + (historical_a - last_a) / slope

    figure, axes = plt.subplots(1, 3, figsize=(15.6, 5.2), constrained_layout=True)
    axis_curve, axis_zoom, axis_defect = axes
    curve_color = "#1768ac"
    pass_color = "#1b9e77"
    fail_color = "#d95f02"

    axis_curve.plot(qualified[:, 0], qualified[:, 1], color=curve_color, lw=1.8)
    axis_curve.scatter(qualified[:, 0], qualified[:, 1], color=pass_color, s=30, zorder=3)
    axis_curve.scatter([10.3084], [historical_a], marker="X", s=90, color="#c51b7d", label="Jones printed point")
    axis_curve.scatter([projected_c], [historical_a], marker="*", s=125, facecolors="none", edgecolors="#111111", label="local projected crossing")
    axis_curve.axhline(historical_a, color="#555555", ls="--", lw=1.0)
    axis_curve.set_title("A  Qualified homoclinic curve")
    axis_curve.set_xlabel("c")
    axis_curve.set_ylabel("a")
    axis_curve.grid(alpha=0.2)
    axis_curve.legend(fontsize=8, loc="best")

    zoom_mask = qualified[:, 0] >= 10.3143
    axis_zoom.plot(qualified[zoom_mask, 0], qualified[zoom_mask, 1], color=curve_color, lw=1.8)
    axis_zoom.scatter(qualified[zoom_mask, 0], qualified[zoom_mask, 1], color=pass_color, s=35, label="qualified root")
    for experiment_id, (c_value, a_value) in failed_points.items():
        marker = "D" if experiment_id == 369 else "x"
        color = "#e6ab02" if experiment_id == 369 else fail_color
        axis_zoom.scatter(c_value, a_value, marker=marker, color=color, s=35, alpha=0.78)
    axis_zoom.scatter([], [], marker="D", color="#e6ab02", label="wrong-direction root")
    axis_zoom.scatter([], [], marker="x", color=fail_color, label="unqualified iterate")
    axis_zoom.scatter([projected_c], [historical_a], marker="*", s=125, facecolors="none", edgecolors="#111111")
    axis_zoom.axhline(historical_a, color="#555555", ls="--", lw=1.0)
    axis_zoom.annotate(
        "EXP-368\n1.75e-5 above section",
        xy=(last_c, last_a),
        xytext=(10.31655, 0.179845),
        arrowprops={"arrowstyle": "->", "lw": 0.8},
        fontsize=8,
    )
    axis_zoom.set_xlim(10.31425, 10.31738)
    axis_zoom.set_ylim(0.17977, 0.18074)
    axis_zoom.set_title("B  Historical-section approach")
    axis_zoom.set_xlabel("c")
    axis_zoom.grid(alpha=0.2)
    axis_zoom.legend(fontsize=8, loc="upper right")

    defect_ids = QUALIFIED_IDS + FAILED_IDS
    defects = np.asarray(
        [receipts[experiment_id].get("final_maximum_block_residual", np.nan) for experiment_id in defect_ids],
        dtype=np.float64,
    )
    passed = np.asarray([experiment_id in QUALIFIED_IDS for experiment_id in defect_ids])
    positions = np.arange(len(defect_ids))
    axis_defect.scatter(positions[passed], defects[passed], color=pass_color, s=32, label="qualified")
    axis_defect.scatter(positions[~passed], defects[~passed], color=fail_color, marker="x", s=38, label="preserved failure")
    axis_defect.axhline(1e-8, color="#111111", ls="--", lw=1.0, label="root gate")
    axis_defect.set_yscale("log")
    axis_defect.set_xticks(positions[::2], [str(value) for value in defect_ids[::2]], rotation=55)
    axis_defect.set_xlabel("experiment number")
    axis_defect.set_ylabel("maximum matching-block defect")
    axis_defect.set_title("C  Gates expose method failures")
    axis_defect.grid(alpha=0.2, which="both")
    axis_defect.legend(fontsize=8, loc="upper left")
    axis_defect.text(
        0.98,
        0.04,
        "EXP-380/382: collocation escaped\n(not plotted on defect scale)",
        transform=axis_defect.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        color="#555555",
    )

    figure.suptitle(
        "Jones homoclinic mechanism: qualified continuation and honest section gap",
        fontsize=13,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=args.dpi, bbox_inches="tight")
    plt.close(figure)

    output = {
        "schema": SCHEMA,
        "source": source,
        "inputs": inputs,
        "qualified_experiments": [f"EXP-{value}" for value in QUALIFIED_IDS],
        "failed_experiments": [f"EXP-{value}" for value in FAILED_IDS],
        "qualified_points": [
            {"experiment_id": f"EXP-{experiment_id}", "c": float(point[0]), "a": float(point[1])}
            for experiment_id, point in zip(QUALIFIED_IDS, qualified, strict=True)
        ],
        "historical_section_a": historical_a,
        "projected_crossing_c": float(projected_c),
        "last_qualified_a_gap": float(last_a - historical_a),
        "last_secant_da_dc": float(slope),
        "output": str(args.output),
        "output_sha256": sha256_file(args.output),
        "dpi": args.dpi,
    }
    atomic_write(args.receipt, canonical_json(output))
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

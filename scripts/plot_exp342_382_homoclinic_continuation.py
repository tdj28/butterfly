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


SCHEMA = "butterfly.exp342-472-homoclinic-continuation-figure.v1"
QUALIFIED_IDS = (
    342,
    347,
    350,
    360,
    361,
    362,
    363,
    365,
    366,
    367,
    368,
    399,
    403,
    405,
    406,
    407,
    408,
    410,
    411,
    412,
    413,
    414,
    415,
    416,
    417,
    418,
    419,
    420,
    421,
    422,
    423,
    424,
    425,
    426,
    427,
    428,
    429,
    430,
    431,
    432,
    433,
    434,
    435,
    436,
    437,
    438,
    439,
    440,
    441,
    442,
    443,
    444,
    445,
    446,
    447,
    448,
    449,
    450,
    451,
    452,
    453,
    454,
    455,
    456,
    457,
    458,
    459,
    460,
    461,
    462,
    463,
    464,
    465,
    466,
    467,
    468,
    469,
    470,
    471,
    472,
)
FAILED_IDS = (
    364,
    369,
    370,
    371,
    372,
    373,
    374,
    375,
    376,
    377,
    385,
    386,
    387,
    389,
    390,
    392,
    393,
    394,
    395,
    397,
    398,
    400,
    401,
    402,
    404,
    409,
)
PROJECTION_IDS = (367, 368)
FOLD_IDS = (368, 399, 403, 405, 406, 407)
LOCAL_FAILED_IDS = (401, 402, 404)
OUTGOING_IDS = (
    403,
    405,
    406,
    407,
    408,
    410,
    411,
    412,
    413,
    414,
    415,
    416,
    417,
    418,
    419,
    420,
    421,
    422,
    423,
    424,
    425,
    426,
    427,
    428,
    429,
    430,
    431,
    432,
    433,
    434,
    435,
    436,
    437,
    438,
    439,
    440,
    441,
    442,
    443,
    444,
    445,
    446,
    447,
    448,
    449,
    450,
    451,
    452,
    453,
    454,
    455,
    456,
    457,
    458,
    459,
    460,
    461,
    462,
    463,
    464,
    465,
    466,
    467,
    468,
    469,
    470,
    471,
    472,
)
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
    projection_points = np.asarray(
        [curve_point(experiment_id, receipts[experiment_id]) for experiment_id in PROJECTION_IDS]
    )
    prior_c, prior_a = projection_points[0]
    projection_c, projection_a = projection_points[1]
    slope = (projection_a - prior_a) / (projection_c - prior_c)
    historical_a = 0.1798
    projected_c = projection_c + (historical_a - projection_a) / slope

    figure, axes = plt.subplots(2, 2, figsize=(15.6, 9.2), constrained_layout=True)
    axis_curve, axis_zoom, axis_outgoing, axis_defect = axes.flat
    curve_color = "#1768ac"
    pass_color = "#1b9e77"
    fail_color = "#d95f02"

    axis_curve.plot(qualified[:, 0], qualified[:, 1], color=curve_color, lw=1.8)
    axis_curve.scatter(qualified[:, 0], qualified[:, 1], color=pass_color, s=30, zorder=3)
    axis_curve.scatter([10.3084], [historical_a], marker="X", s=90, color="#c51b7d", label="Jones printed point")
    axis_curve.scatter([projected_c], [historical_a], marker="*", s=125, facecolors="none", edgecolors="#111111", label="pre-fold secant projection")
    axis_curve.axhline(historical_a, color="#555555", ls="--", lw=1.0)
    axis_curve.set_title("A  Qualified homoclinic curve")
    axis_curve.set_xlabel("c")
    axis_curve.set_ylabel("a")
    axis_curve.grid(alpha=0.2)
    axis_curve.legend(fontsize=8, loc="best")

    fold_reference_c, fold_reference_a = curve_point(399, receipts[399])

    def fold_coordinates(experiment_id: int) -> tuple[float, float]:
        c_value, a_value = curve_point(experiment_id, receipts[experiment_id])
        return (1e9 * (c_value - fold_reference_c), 1e9 * (a_value - fold_reference_a))

    fold_curve = np.asarray([fold_coordinates(experiment_id) for experiment_id in FOLD_IDS])
    axis_zoom.plot(fold_curve[:, 0], fold_curve[:, 1], color=curve_color, lw=1.8)
    axis_zoom.scatter(
        fold_curve[:, 0], fold_curve[:, 1], color=pass_color, s=42, label="qualified root"
    )
    for experiment_id in LOCAL_FAILED_IDS:
        c_offset, a_offset = fold_coordinates(experiment_id)
        axis_zoom.scatter(c_offset, a_offset, marker="x", color=fail_color, s=42, alpha=0.82)
    axis_zoom.scatter([], [], marker="x", color=fail_color, label="coordinate gate rejected")
    axis_zoom.annotate(
        "EXP-403: sampled\nlocal a minimum",
        xy=fold_coordinates(403),
        xytext=(-14.0, 1.0),
        arrowprops={"arrowstyle": "->", "lw": 0.8},
        fontsize=8,
    )
    axis_zoom.axvline(0.0, color="#777777", ls=":", lw=0.8)
    axis_zoom.axhline(0.0, color="#777777", ls=":", lw=0.8)
    axis_zoom.set_title("B  First local a minimum")
    axis_zoom.set_xlabel(r"$(c-c_{399})\times10^9$")
    axis_zoom.set_ylabel(r"$(a-a_{399})\times10^9$")
    axis_zoom.grid(alpha=0.2)
    axis_zoom.legend(fontsize=8, loc="best")

    outgoing_reference_c, outgoing_reference_a = curve_point(403, receipts[403])

    def outgoing_coordinates(experiment_id: int) -> tuple[float, float]:
        c_value, a_value = curve_point(experiment_id, receipts[experiment_id])
        return (
            1e9 * (c_value - outgoing_reference_c),
            1e9 * (a_value - outgoing_reference_a),
        )

    outgoing_curve = np.asarray(
        [outgoing_coordinates(experiment_id) for experiment_id in OUTGOING_IDS]
    )
    axis_outgoing.plot(outgoing_curve[:, 0], outgoing_curve[:, 1], color=curve_color, lw=1.8)
    axis_outgoing.scatter(
        outgoing_curve[:, 0], outgoing_curve[:, 1], color=pass_color, s=42, label="qualified root"
    )
    rejected_c, rejected_a = outgoing_coordinates(409)
    axis_outgoing.scatter(
        rejected_c,
        rejected_a,
        marker="x",
        color=fail_color,
        s=52,
        label="EXP-409 conditioning rejection",
    )
    axis_outgoing.annotate(
        "EXP-472: 80th qualified point\nconservative steps pass",
        xy=outgoing_curve[-1],
        xytext=(-14000.0, 5000.0),
        arrowprops={"arrowstyle": "->", "lw": 0.8},
        fontsize=8,
    )
    axis_outgoing.text(
        0.97,
        0.95,
        "historical a section is 17,493.5 offset units below (off scale)",
        transform=axis_outgoing.transAxes,
        ha="right",
        va="top",
        fontsize=8,
        color="#555555",
    )
    axis_outgoing.axvline(0.0, color="#777777", ls=":", lw=0.8)
    axis_outgoing.axhline(0.0, color="#777777", ls=":", lw=0.8)
    axis_outgoing.set_title("C  Conditioned outgoing branch")
    axis_outgoing.set_xlabel(r"$(c-c_{403})\times10^9$")
    axis_outgoing.set_ylabel(r"$(a-a_{403})\times10^9$")
    axis_outgoing.grid(alpha=0.2)
    axis_outgoing.legend(fontsize=8, loc="lower left")

    defect_ids = tuple(sorted(QUALIFIED_IDS + FAILED_IDS))
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
    axis_defect.set_xticks(positions[::3], [str(value) for value in defect_ids[::3]], rotation=55)
    axis_defect.set_xlabel("experiment number")
    axis_defect.set_ylabel("maximum matching-block defect")
    axis_defect.set_title("D  Gates expose method failures")
    axis_defect.grid(alpha=0.2, which="both")
    axis_defect.legend(fontsize=8, loc="upper left")
    axis_defect.text(
        0.98,
        0.10,
        "EXP-380/382: collocation escaped (off scale)\nEXP-409: conditioning-only rejection",
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
        "minimum_qualified_a_gap": float(np.min(qualified[:, 1] - historical_a)),
        "closest_qualified_experiment": f"EXP-{QUALIFIED_IDS[int(np.argmin(qualified[:, 1]))]}",
        "projection_experiments": [f"EXP-{value}" for value in PROJECTION_IDS],
        "projection_secant_da_dc": float(slope),
        "local_fold_experiments": [f"EXP-{value}" for value in FOLD_IDS],
        "outgoing_experiments": [f"EXP-{value}" for value in OUTGOING_IDS],
        "output": str(args.output),
        "output_sha256": sha256_file(args.output),
        "dpi": args.dpi,
    }
    atomic_write(args.receipt, canonical_json(output))
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

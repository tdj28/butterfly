#!/usr/bin/env python3
"""Plot EXP-476's incomplete grid and its one qualified refinement comparison.

All inputs come from the checked-in compact summary. Failed and skipped cases
remain visible; the failed parameter estimate is never shown as a qualified
radius comparison. This script performs no orbit or target computations.
"""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import LogLocator, NullLocator

from butterfly.homoclinic_refinement import (
    GRID_SCHEMA, nonfinite_numeric_paths, summarize_grid_sensitivity,
    validate_grid_manifest,
)
from butterfly.scan import atomic_write, canonical_json, git_value


ROOT = Path(__file__).resolve().parents[1]
FROZEN_BINDINGS = {
    "raw_receipt_sha256": "c9818275ed3c585934cdeaa85857b04a5e9a6e1a6400f426a5cbf6e06d5b95bc",
    "raw_receipt_bytes": 8649021,
    "source_commit": "af90d04e6b484733bb2535a453157c4830691a34",
    "manifest_sha256": "8a3657cc921b798eec34af1199d3e53b26aa89cf629f6ab3bf3c6d5f8c6498e5",
    "protocol_tag": "exp-476-protocol",
}
FROZEN_REFINEMENT = {
    "radii": [0.01, 0.005, 0.0025],
    "tolerances": [1e-6, 1e-7, 1e-8],
    "maximum_finest_a_difference": 1e-9,
    "maximum_contraction_ratio": 0.3,
    "contraction_absolute_slack": 1e-10,
    "endpoint_resolution_fraction": 0.25,
    "empirical_resolution": 1e-9,
}


def validate_controls(controls):
    """Verify the control qualification printed in the figure subtitle."""
    if not isinstance(controls, Mapping) or any(controls.get(key) is not True for key in (
        "passed", "complete", "negative_control_rejection_qualified", "shrinking_truncation_error",
    )):
        raise ValueError("the figure requires completed, passed analytic controls")
    if controls.get("collocation_tolerance") != 1e-8 or controls.get("boundary_tolerance") != 1e-9:
        raise ValueError("analytic control tolerances differ from the frozen protocol")
    positive = controls.get("positive_controls", [])
    if len(positive) != 3 or [row.get("radius") for row in positive] != [0.1, 0.05, 0.025]:
        raise ValueError("all three frozen analytic positive controls are required")
    for row in positive:
        if (any(row.get(key) is not True for key in ("passed", "passed_numerical_gates", "solver_success"))
                or row.get("solver_status") != 0
                or not abs(row["parameter"]) <= 1e-8
                or not 0 <= row["maximum_scaled_boundary_residual"] <= 1e-9
                or not 0 <= row["maximum_collocation_relative_rms"] <= 1e-8
                or not row["minimum_parameter_box_margin"] > 1e-4
                or not row["maximum_excursion"] > 1.4
                or not 0 <= row["maximum_analytic_state_error"] <= row["radius"]**2
                or row["replay"].get("success") is not True
                or not 0 <= row["replay"]["maximum_state_defect"] <= 1e-6):
            raise ValueError("analytic positive control diagnostics contradict qualification")
    errors = [row["maximum_analytic_state_error"] for row in positive]
    if not all(right <= 0.4 * left for left, right in zip(errors, errors[1:])):
        raise ValueError("analytic control truncation errors do not satisfy the shrinking gate")
    negative = controls.get("negative_control", {})
    if (negative.get("passed_numerical_gates") is not False
            or negative.get("solver_success") is not False
            or negative.get("solver_status") != 2):
        raise ValueError("analytic negative control does not retain its qualified rejection")


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_summary(summary):
    """Check grid identity and recompute sensitivity using only public scalars."""
    if not isinstance(summary, Mapping) or summary.get("schema") != "butterfly.projected-homoclinic-grid-summary.v1" or summary.get("experiment_id") != "EXP-476":
        raise ValueError("an EXP-476 compact grid summary is required")
    if nonfinite_numeric_paths(summary):
        raise ValueError("compact summary contains nonfinite numerical values")
    if any(summary.get(key) is not False for key in ("passed", "technical_passed", "discretization_passed", "nine_case_qualification_complete", "source_dirty")) or summary.get("execution_finished") is not True:
        raise ValueError("this figure must preserve the failed, incomplete study status")
    if any(summary.get(key) != expected for key, expected in FROZEN_BINDINGS.items()):
        raise ValueError("compact summary does not identify the frozen EXP-476 source and raw receipt")
    if any(summary["refinement"].get(key) != expected for key, expected in FROZEN_REFINEMENT.items()):
        raise ValueError("grid labels and sensitivity gates must match the frozen refinement protocol")
    if any(summary["budget"].get(key) != expected for key, expected in {
        "maximum_total_seconds": 300.0, "maximum_trial_seconds": 45.0,
        "maximum_nodes": 48000, "maximum_seed_step": 0.03,
        "maximum_state_norm": 1000.0,
    }.items()) or summary["budget"].get("stop_on_first_failed_case") is not True:
        raise ValueError("figure budget and stop-rule labels must match the frozen protocol")
    validate_controls(summary["controls"])
    cases = summary["cases"]
    manifest = {
        "schema": GRID_SCHEMA,
        "refinement": summary["refinement"],
        "cases": [{key: row[key] for key in ("name", "radius", "tolerance")} for row in cases],
    }
    validate_grid_manifest(manifest)
    counts = dict(Counter(row["status"] for row in cases))
    if counts != summary["case_counts"] or counts != {"passed": 5, "failed": 1, "skipped": 3}:
        raise ValueError("EXP-476 figure requires all five passed, one failed, and three skipped cases")
    if any(row.get("passed") is not (row["status"] == "passed") for row in cases):
        raise ValueError("case qualification flags disagree with recorded statuses")
    for row in cases:
        if row["status"] == "passed":
            if (row.get("solver_success") is not True or row.get("passed_numerical_gates") is not True
                    or row.get("solver_status") != 0 or not 0 < row["nodes"] <= 48000
                    or not 0 <= row["maximum_scaled_boundary_residual"] <= 1e-8
                    or not 0 <= row["maximum_collocation_relative_rms"] <= row["tolerance"]
                    or not row["minimum_parameter_box_margin"] > 1e-4
                    or not row["maximum_excursion"] >= 5.0
                    or not 0 <= row["source_a_difference"] <= 2e-5
                    or row["replay_acceptance_limit"] != row["tolerance"]
                    or row["replay"].get("success") is not True
                    or not 0 <= row["replay"]["maximum_state_defect"] <= row["tolerance"]):
                raise ValueError("passed target diagnostics contradict the all-gates figure label")
        elif row["status"] == "failed":
            if ((row["radius"], row["tolerance"]) != (0.005, 1e-8)
                    or row.get("solver_status") != 1 or row.get("solver_success") is not False
                    or row.get("passed_numerical_gates") is not False):
                raise ValueError("failed target does not retain the frozen node-cap failure")
        elif row["radius"] != 0.0025 or row.get("reason") != "earlier failure under the frozen stop rule" or "a" in row:
            raise ValueError("skipped targets must retain the frozen stop rule without invented estimates")
    rows = [{
        "case": manifest["cases"][index],
        "passed": row["passed"],
        "collocation": {"parameter": row.get("a")},
    } for index, row in enumerate(cases)]
    recomputed = summarize_grid_sensitivity(rows, manifest)
    if recomputed != summary["sensitivity"]:
        raise ValueError("compact summary sensitivity disagrees with its case scalars")
    qualified = [row for row in recomputed["radius_refinements"] if row["technical_passed"]]
    if len(qualified) != 1 or qualified[0]["radius"] != 0.01 or not qualified[0]["passed"]:
        raise ValueError("only the radius 0.01 group is qualified for the refinement panel")
    if any(row["classification"] != "unavailable" for row in recomputed["endpoint_comparisons"]):
        raise ValueError("no endpoint comparison may be qualified for EXP-476")
    return cases, qualified[0]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=ROOT / "docs/experiments/receipts/EXP-476.json")
    parser.add_argument("--output", type=Path, default=ROOT / "paper/figures/fig32-exp476-homoclinic-refinement.png")
    parser.add_argument("--receipt", type=Path, default=ROOT / "paper/figures/fig32-exp476-homoclinic-refinement.png.receipt.json")
    parser.add_argument("--dpi", type=int, default=240)
    args = parser.parse_args(argv)
    summary = json.loads(args.summary.read_bytes())
    try:
        cases, qualified = validate_summary(summary)
    except (KeyError, TypeError, ValueError) as error:
        raise SystemExit(f"invalid compact summary: {error}") from error
    radii, tolerances = summary["refinement"]["radii"], summary["refinement"]["tolerances"]
    by_pair = {(row["radius"], row["tolerance"]): row for row in cases}
    palette = {
        "passed": ("#E0F2E9", "#176344"),
        "failed": ("#FCE4DF", "#B33D2E"),
        "skipped": ("#EEF0F3", "#667085"),
    }
    with plt.rc_context({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.titlesize": 13, "axes.labelsize": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#667085", "xtick.color": "#344054", "ytick.color": "#344054",
        "savefig.facecolor": "white",
    }):
        fig, (left, right) = plt.subplots(1, 2, figsize=(12.4, 5.4), gridspec_kw={"width_ratios": [1.2, 1]})
        fig.subplots_adjust(left=0.105, right=0.98, bottom=0.28, top=0.76, wspace=0.35)
        left.set_title("A   Frozen nine-case qualification grid", loc="left", pad=18, weight="bold")
        for row_index, radius in enumerate(radii):
            for column_index, tolerance in enumerate(tolerances):
                row = by_pair[(radius, tolerance)]
                background, foreground = palette[row["status"]]
                left.add_patch(Rectangle((column_index - 0.47, row_index - 0.43), 0.94, 0.86, facecolor=background, edgecolor="white", linewidth=1.5))
                detail = "all gates" if row["status"] == "passed" else "node-cap stop" if row["status"] == "failed" else "frozen stop rule"
                left.text(column_index, row_index - 0.08, row["status"].upper(), ha="center", va="center", color=foreground, fontsize=11, weight="bold")
                left.text(column_index, row_index + 0.19, detail, ha="center", va="center", color=foreground, fontsize=8.5)
        left.set_xlim(-0.5, 2.5)
        left.set_ylim(2.5, -0.5)
        left.set_xticks([0, 1, 2], [r"$10^{-6}$", r"$10^{-7}$", r"$10^{-8}$"])
        left.set_yticks([0, 1, 2], [f"{radius:g}" for radius in radii])
        left.set_xlabel("Collocation tolerance (loose → tight)", labelpad=9)
        left.set_ylabel(r"Departure and arrival radius $\varepsilon$", labelpad=10)
        left.tick_params(length=0)
        for spine in left.spines.values():
            spine.set_visible(False)
        left.text(0.0, -0.31, "48,000-node cap; no retry or post-result retuning.\nThe failed solve is retained, not accepted.", transform=left.transAxes, va="top", fontsize=9.3, color="#667085", linespacing=1.6)

        differences = [qualified["D1"], qualified["D2"]]
        right.bar([0, 1], differences, width=0.49, color=["#087F8C", "#7657A7"], zorder=3)
        right.set_yscale("log")
        right.set_ylim(1e-10, 1.9e-8)
        right.set_xlim(-0.6, 1.65)
        right.set_title(r"B   Qualified refinement: $\varepsilon=0.01$", loc="left", pad=18, weight="bold")
        right.set_xticks([0, 1], [r"$D_1$: $10^{-6}\to10^{-7}$", r"$D_2$: $10^{-7}\to10^{-8}$"])
        right.set_ylabel(r"Observed parameter difference $|\Delta a|$")
        right.yaxis.set_major_locator(LogLocator(base=10))
        right.yaxis.set_minor_locator(NullLocator())
        right.grid(True, axis="y", color="#E4E7EC", linewidth=0.8, zorder=0)
        ceiling = summary["refinement"]["maximum_finest_a_difference"]
        right.axhline(ceiling, color="#9A6B28", linestyle="--", linewidth=1.3, zorder=2)
        right.text(0.65, ceiling * 1.18, r"$D_2$ ceiling: $10^{-9}$", fontsize=9, color="#8B5F21")
        for position, value in enumerate(differences):
            right.text(position, value * 1.15, f"{value:.2e}", ha="center", va="bottom", weight="bold", fontsize=10, color="#344054")
        right.text(0.0, -0.31, f"D₂ / D₁ = {differences[1] / differences[0]:.3f}; both refinement gates pass.\nOnly this radius has three qualified tolerances.", transform=right.transAxes, va="top", fontsize=9.3, color="#667085", linespacing=1.6)
        fig.suptitle("EXP-476  |  Accuracy study stopped short of a complete grid", x=0.105, ha="left", fontsize=16, weight="bold", y=0.975)
        fig.text(0.105, 0.895, "5 passed · 1 failed · 3 skipped  |  Analytic controls passed  |  Endpoint comparisons unavailable", fontsize=10.5, color="#B33D2E")
        fig.text(0.105, 0.035, "Public compact summary only. Observed shifts are empirical sensitivity, not error bars or rigorous parameter bounds.", fontsize=9, color="#667085")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.output, dpi=args.dpi)
        plt.close(fig)
    receipt = {
        "schema": "butterfly.projected-homoclinic-grid-figure.v1",
        "experiment_id": "EXP-476",
        "source_commit": git_value("rev-parse", "HEAD"),
        "source_dirty": bool(git_value("status", "--porcelain")),
        "script_sha256": file_hash(__file__),
        "summary_sha256": file_hash(args.summary),
        "experiment_source_commit": summary["source_commit"],
        "experiment_raw_receipt_sha256": summary["raw_receipt_sha256"],
        "figure_sha256": file_hash(args.output),
        "dpi": args.dpi,
        "matplotlib_version": matplotlib.__version__,
        "inputs": [str(args.summary.relative_to(ROOT)) if args.summary.is_relative_to(ROOT) else str(args.summary)],
        "raw_artifact_required_to_regenerate_figure": False,
        "case_counts": summary["case_counts"],
        "qualified_radius": qualified["radius"],
        "qualified_D1": qualified["D1"],
        "qualified_D2": qualified["D2"],
        "failed_estimates_plotted_as_qualified": False,
        "endpoint_comparisons_qualified": False,
        "interpretation": "The frozen study failed and remains incomplete. Only the technically qualified radius 0.01 refinement is plotted; failed/skipped cases remain visible. Parameter shifts are observed sensitivity, not rigorous bounds or existence evidence.",
    }
    atomic_write(args.receipt, canonical_json(receipt))
    print(json.dumps({"figure": str(args.output), "sha256": receipt["figure_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

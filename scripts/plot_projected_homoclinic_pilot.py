#!/usr/bin/env python3
"""Plot EXP-475's analytic control and parameter sensitivity from public data.

Only the checked-in compact summary is needed; no orbit computation or private
raw artifact is required. Points are computed estimates, not error bars.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
import numpy as np

from butterfly.scan import atomic_write, canonical_json, git_value


ROOT = Path(__file__).resolve().parents[1]


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=ROOT / "docs/experiments/receipts/EXP-475.json")
    parser.add_argument("--output", type=Path, default=ROOT / "paper/figures/fig31-exp475-independent-homoclinic.png")
    parser.add_argument("--receipt", type=Path, default=ROOT / "paper/figures/fig31-exp475-independent-homoclinic.png.receipt.json")
    parser.add_argument("--dpi", type=int, default=240)
    args = parser.parse_args(argv)
    summary = json.loads(args.summary.read_bytes())
    if summary.get("schema") != "butterfly.projected-homoclinic-pilot-summary.v1" or not summary.get("passed"):
        raise SystemExit("a qualified EXP-475 compact summary is required")
    controls, cases = summary["controls"]["positive_controls"], summary["cases"]
    if len(controls) != 3 or len(cases) != 4 or not all(row["passed"] for row in controls + cases):
        raise SystemExit("the figure requires three passed controls and four passed target cases")
    radii = np.asarray([row["radius"] for row in controls])
    errors = np.asarray([row["maximum_analytic_state_error"] for row in controls])
    estimates = np.asarray([row["a"] for row in cases])
    reference = float(summary["reference"]["a"])
    if not np.all(np.isfinite(np.r_[radii, errors, estimates, reference])) or np.any(radii <= 0) or np.any(errors <= 0):
        raise SystemExit("figure values must be finite; log axes require positive data")
    offsets = (estimates - reference) / 1e-8
    mesh_delta = float(estimates[-1] - estimates[-2])
    if not np.isclose(abs(mesh_delta), summary["sensitivity"]["mesh_a_difference"], rtol=1e-10, atol=1e-16):
        raise SystemExit("summary mesh sensitivity disagrees with its case estimates")

    with plt.rc_context({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.titlesize": 13, "axes.labelsize": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#667085", "xtick.color": "#344054", "ytick.color": "#344054",
        "savefig.facecolor": "white",
    }):
        fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.9), gridspec_kw={"width_ratios": [1, 1.35]})
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.23, top=0.81, wspace=0.32)
        left, right = axes
        left.loglog(radii, errors, color="#087F8C", marker="o", markersize=8, linewidth=1.8)
        left.set_title("A   Analytic Duffing control", loc="left", pad=14, weight="bold")
        left.set_xlabel(r"Endpoint radius $\varepsilon$")
        left.set_ylabel("Maximum state error vs. analytic orbit")
        left.xaxis.set_major_locator(FixedLocator(radii))
        left.xaxis.set_major_formatter(FuncFormatter(lambda value, _position: f"{value:g}"))
        left.xaxis.set_minor_locator(NullLocator())
        left.set_xlim(0.021, 0.119)
        left.set_ylim(4e-7, 1.4e-4)
        left.grid(True, which="major", color="#E4E7EC", linewidth=0.8)
        left.text(0.04, 0.93, "About 8× less error per radius halving", transform=left.transAxes, va="top", fontsize=9.5)
        left.text(0.30, 0.05, r"Recovered $|\mu| < 8.2\times10^{-18}$" + "\nPositive-μ control rejected", transform=left.transAxes, fontsize=8.8, linespacing=1.7)

        positions = np.arange(4)
        right.axhline(0.0, color="#7A8494", linewidth=1.1, linestyle="--", zorder=0)
        right.plot(positions[:3], offsets[:3], color="#C35D36", marker="o", markersize=8, linewidth=1.8, label=r"Collocation tol. $10^{-5}$")
        right.plot(positions[2:], offsets[2:], color="#7657A7", linewidth=1.8)
        right.plot(positions[3], offsets[3], color="#7657A7", marker="D", markersize=8, linestyle="none", label=r"Collocation tol. $10^{-6}$")
        right.set_title("B   Rössler candidate: parameter sensitivity", loc="left", pad=14, weight="bold")
        right.set_ylabel(r"$(a-a_{\mathrm{EXP342}})\,/\,10^{-8}$")
        right.set_xticks(positions, ["0.01", "0.005", "0.0025", "0.0025\nrefined"])
        right.set_xlabel(r"Departure and arrival radius $\varepsilon$")
        right.set_xlim(-0.25, 3.25)
        right.set_ylim(-0.45, 6.1)
        right.grid(True, axis="y", color="#E4E7EC", linewidth=0.8)
        right.legend(loc="upper left", frameon=False, fontsize=9.5)
        right.annotate(
            "10× tighter tolerance\n" + r"$\Delta a=-4.06\times10^{-8}$",
            xy=(2.52, (offsets[2] + offsets[3]) / 2), xytext=(0.35, 1.18),
            textcoords="data", fontsize=9.5, color="#63438F",
            arrowprops={"arrowstyle": "->", "color": "#7657A7", "lw": 1.2},
        )
        right.text(-0.15, -0.2, "EXP-342 reference", color="#667085", fontsize=8.5, va="top")
        fig.suptitle("EXP-475  |  Independent endpoint-projection collocation", x=0.09, ha="left", fontsize=16, weight="bold", y=0.97)
        fig.text(0.09, 0.885, r"Analytic controls and a finite-radius Rössler candidate at $b=0.2,\ c=10.3084$", fontsize=11, color="#475467")
        fig.text(0.09, 0.035, "Source: checked-in EXP-475 summary. Parameter shifts are observed sensitivity, not error bars or rigorous bounds.", fontsize=9, color="#667085")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.output, dpi=args.dpi)
        plt.close(fig)

    receipt = {
        "schema": "butterfly.projected-homoclinic-pilot-figure.v1", "experiment_id": "EXP-475",
        "source_commit": git_value("rev-parse", "HEAD"),
        "source_dirty": bool(git_value("status", "--porcelain")),
        "script_sha256": file_hash(__file__), "summary_sha256": file_hash(args.summary),
        "experiment_source_commit": summary["source_commit"],
        "experiment_raw_receipt_sha256": summary["raw_receipt_sha256"],
        "figure_sha256": file_hash(args.output), "dpi": args.dpi,
        "matplotlib_version": matplotlib.__version__, "numpy_version": np.__version__,
        "inputs": [str(args.summary.relative_to(ROOT)) if args.summary.is_relative_to(ROOT) else str(args.summary)],
        "raw_artifact_required_to_regenerate_figure": False,
        "control_radii": radii.tolist(), "control_maximum_state_errors": errors.tolist(),
        "reference_a": reference, "target_a_offsets_in_units_of_1e_minus8": offsets.tolist(),
        "mesh_a_shift": mesh_delta,
        "interpretation": "Finite-radius analytic-control discrepancy and observed target-parameter sensitivity. No error bars, confidence intervals, existence proof, or later-turn qualification.",
    }
    atomic_write(args.receipt, canonical_json(receipt))
    print(json.dumps({"figure": str(args.output), "sha256": receipt["figure_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

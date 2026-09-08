#!/usr/bin/env python3
"""Plot the fixed EXP-483 descriptive result; no model fits or integrations."""
import argparse
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DIGEST = "bb14f469fb09a50ac2802a8af9dd28bb1d1570affa02da4553a7f0d2267cbddd"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    raw = args.receipt.read_bytes()
    if hashlib.sha256(raw).hexdigest() != DIGEST:
        raise ValueError("EXP-483 result anchor differs")
    if args.output.exists():
        raise FileExistsError("preserve existing figure")
    result = json.loads(raw)
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True, sharey=True)
    fig.subplots_adjust(left=.085, right=.98, top=.85, bottom=.23, hspace=.36, wspace=.08)
    styles = [("selected", "joint_original_cohort", "Four selected pairs", "#727c8e"),
              ("all", "joint_original_cohort", "All consecutive pairs, same seeds", "#087f8c"),
              ("all", "valid_before_detection", "All pairs before capture detection", "#c47d19")]
    for i, case in enumerate(("local-a025-c083", "local-a027-c083")):
        for w in (0, 1):
            ax = axes[i, w]
            for selector, population, label, color in styles:
                for profile, marker, line in (("rk4-00025", "o", "-"), ("rk4-000125", "x", "--")):
                    values = [next(row["coverage"] for row in result["rows"] if row["case"] == case
                        and row["window"] == w and row["bins"] == bins and row["selector"] == selector
                        and row["population"] == population and row["split"] == "calibration"
                        and row["profile"] == profile) for bins in (30, 40, 50)]
                    ax.plot([30, 40, 50], np.array(values)*100, color=color, marker=marker,
                        linestyle=line, alpha=.8, label=label if profile == "rk4-00025" else None)
            ax.axhline(70, color="#9ba4ae", lw=.7, ls=":")
            ax.set_title(f"a={.21575 if i==0 else .21577} | t={'80–140' if w==0 else '180–240'}")
            ax.set_xticks([30, 40, 50]); ax.set_ylim(40, 104)
            ax.grid(alpha=.15)
            ax.set_xlabel("Number of equal-width input bins")
            if w == 0:
                ax.set_ylabel("Calibration support (%)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(.5, .065), ncol=1, frameon=False)
    fig.suptitle("EXP-483: early support loss is strongly affected by pair selection\nLate-window concentration remains; no replacement map verdict", fontsize=14)
    fig.supxlabel("Support: bins with ≥8 distinct seeds. Solid/circle: RK4 .0025; dashed/cross: .00125. Original calibration bounds.\nThe before-detection population overlaps the original cohort; it is not an independent confirmation.", fontsize=9, y=.015)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Show every EXP-484 base state and its validated coordinate partial derivative."""
import argparse
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.receipt.read_bytes()
    if hashlib.sha256(raw).hexdigest() != "54c2b90a092e5fd1b97e6609f1e80dfb1f571924f31e5445c125bb0be5a0b97c":
        raise ValueError("audited geometry receipt differs")
    result = json.loads(raw)
    if args.output.exists():
        raise FileExistsError("preserve existing output")
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), layout="constrained")
    for i, (case, aval) in enumerate((("local-a025-c083", .21575), ("local-a027-c083", .21577))):
        points = [p for p in result["points"] if p["case"] == case]
        if len(points) != 40 or any(p["solvers"][m]["status"] != "returned" for p in points for m in ("DOP853", "Radau")):
            raise ValueError("figure requires this complete, returned fixed grid")
        states = np.array([p["initial_state"] for p in points])
        axes[i, 0].scatter(states[:, 0], states[:, 2], s=17, color="#727c8e")
        axes[i, 0].set_title(f"a={aval}: actual input section states")
        axes[i, 0].set_ylabel("z at input crossing")
        for method, marker, color in (("DOP853", "o", "#087f8c"), ("Radau", "+", "#d47845")):
            values = np.array([p["solvers"][method]["return_state"][0] for p in points])
            derivatives = np.array([p["solvers"][method]["return_jacobian"][0][0] for p in points])
            axes[i, 1].scatter(states[:, 0], values, s=20, marker=marker, color=color, label=method)
            axes[i, 2].scatter(states[:, 0], derivatives, s=20, marker=marker, color=color)
        axes[i, 1].set_title("Direct next-return observations")
        axes[i, 1].set_ylabel("x at next crossing")
        axes[i, 2].set_title("Coordinate partial, not curve derivative")
        axes[i, 2].set_ylabel(r"$\partial P_x/\partial x$ at fixed z")
        axes[i, 2].axhline(0, color="#9ba4ae", lw=.7)
        for ax in axes[i]:
            ax.set_xlabel("x at input crossing")
            ax.grid(alpha=.15)
    axes[0, 1].legend(frameon=False)
    fig.suptitle("EXP-484: all 80 points pass the direct first-return geometry checks", fontsize=16)
    fig.supxlabel("Two solvers overlap at plot resolution. 240 integrations; finite differences at 10 fixed points.\nPoints are selected observations, not a continued invariant curve. No C/D labels or chain arrows are assigned.", fontsize=10)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()

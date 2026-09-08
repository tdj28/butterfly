#!/usr/bin/env python3
"""Plot all audited EXP-485 points with vector/raster outputs and a receipt."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
from butterfly._paired_startup import sha256, write_json


def plot(source, expected_sha, output):
    if sha256(source) != expected_sha:
        raise ValueError("audited figure input anchor changed")
    result = json.loads(source.read_bytes())
    if result["status"] != "completed-audited" or not result["complete_grid_and_decision_replay"]:
        raise ValueError("only fully audited results may be plotted")
    cases = ("local-a025-c083", "local-a027-c083")
    if len(result["rows"]) != 80 or any(sorted(r["bin"] for r in result["rows"] if r["case"] == c) != list(range(40)) for c in cases):
        raise ValueError("complete two-case point grid required")
    output.mkdir(parents=True, exist_ok=False)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["svg.hashsalt"] = "EXP-485-transported-tangent"
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), layout="constrained")
    derived = []
    for i, case in enumerate(cases):
        rows = sorted([r for r in result["rows"] if r["case"] == case], key=lambda r: r["initial_state"][0])
        x = np.array([r["initial_state"][0] for r in rows])
        z = np.array([r["initial_state"][2] for r in rows])
        qualified = np.array([r["audit"]["qualified"] for r in rows])
        ax = axes[i, 0]
        ax.scatter(x[qualified], z[qualified], s=24, marker="o", facecolors="none", edgecolors="#087e8b", label="Consistent direction")
        ax.scatter(x[~qualified], z[~qualified], s=45, marker="x", color="#bd4d23", label="Unresolved direction")
        ax.set(ylabel="Observed section z", title=f"a = {0.21575 if i == 0 else 0.21577:.5f}: all 40 points")
        ax.legend(fontsize=8)
        partial, slope, angle = [], [], []
        for r in rows:
            audit = r["audit"]
            direction = audit["direction"]
            p = direction["projected"]["DOP853"] if direction else None
            partial.append(p["coordinate_partial"] if p else np.nan)
            slope.append(p["x_graph_derivative"] if p and p["graph_defined"] and audit["qualified"] else np.nan)
            angle.append(max(direction["history_angles"].values()) if direction else np.nan)
            derived.append(dict(case=case, bin=r["bin"], global_seed_id=r["global_seed_id"],
                x=r["initial_state"][0], z=r["initial_state"][2], qualified=audit["qualified"],
                coordinate_partial=p["coordinate_partial"] if p else None,
                graph_defined=p["graph_defined"] if p else False,
                displayed_curve_derivative=p["x_graph_derivative"] if p and p["graph_defined"] and audit["qualified"] else None,
                maximum_history_angle=angle[-1] if np.isfinite(angle[-1]) else None))
        ax = axes[i, 1]
        ax.axhline(0, color=".75", lw=.8)
        ax.scatter(x, partial, marker="x", color=".45", s=22, label="Fixed-z partial")
        ax.scatter(x, slope, marker="o", facecolors="none", edgecolors="#087e8b", s=32, label="Finite-history direction")
        undefined = int(np.count_nonzero(~np.isfinite(slope)))
        ax.set(ylabel="Projected x derivative", title=f"No curve interpolation; {undefined} unplotted slopes")
        ax.legend(fontsize=8)
        ax = axes[i, 2]
        floor = 1e-17
        ax.scatter(x, np.maximum(angle, floor), marker="+", color="#087e8b", s=36)
        ax.axhline(result["thresholds"]["maximum_angle"], color="#bd4d23", ls="--", label="Frozen agreement limit")
        ax.set(yscale="log", ylabel="Depth-4 vs depth-8 line angle (rad)", title="Zeros displayed at 1e-17 rad")
        ax.legend(fontsize=8)
        for ax in axes[i]:
            ax.set_xlabel("Observed section x")
            ax.grid(alpha=.15)
    fig.suptitle("Finite-history flow directions: a numerical ingredient, not verified symbolic chains", fontsize=14)
    outputs = {}
    for suffix in ("png", "svg"):
        path = output/f"EXP-485-transported-tangent.{suffix}"
        fig.savefig(path, dpi=300, metadata={"Date": None} if suffix == "svg" else None)
        if suffix == "svg":
            # Matplotlib emits trailing spaces in path data. Normalize only
            # line endings before hashing; geometry and displayed text stay intact.
            path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())+"\n")
        outputs[path.name] = dict(sha256=sha256(path), bytes=path.stat().st_size)
    plt.close(fig)
    write_json(output/"EXP-485-transported-tangent.receipt.json", dict(
        experiment_id="EXP-485", source_receipt_sha256=expected_sha,
        plotting_script_sha256=sha256(Path(__file__)), outputs=outputs, derived_values=derived,
        data_selection="All 80 audited points in both cases; DOP853 projected values; maximum history angle across both solvers. Unqualified or near-vertical x-graph slopes are not plotted and remain explicit in the receipt. No curve fits or connecting lines.",
        display_floor_radians=1e-17, raster_dpi=300,
        alt_text="Two rows show the two parameter cases. Each row displays all observed section states, compares fixed-z partials with finite-history directional x derivatives, and shows depth-refinement line angles against the frozen limit. These are discrete observations, not a certified return curve.",
        non_color_encodings="Open circles versus crosses distinguish derivative definitions; open circles versus crosses distinguish direction status; dashed threshold line. Panel titles report missing graph slopes.",
        claim_boundary=result["claim_boundary"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    plot(args.receipt, args.expected_sha256, args.output_dir)


if __name__ == "__main__":
    main()

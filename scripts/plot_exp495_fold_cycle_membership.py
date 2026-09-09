#!/usr/bin/env python3
"""Plot audited return pairs and complete case envelopes, without fitted branches."""
import argparse
import json
from pathlib import Path

import numpy as np

from scripts import analyze_exp495_fold_cycle_membership as run
from scripts import audit_exp495_fold_cycle_membership as audit

FIGURE = "EXP-495-fold-cycle-membership"


def derive(result):
    p, c, f, s = run.load_inputs()
    audit.check_result(result, c, f, s, p)
    rows = [dict(id=r["id"], case=r["case"], region=r["region"], family_id=r["family_id"],
                 status=r["status"], variants=r["variants"], envelope=r["envelope"]) for r in result["rows"]]
    return dict(rows=rows, cases=result["cases"], primary_radius=p["primary_radius"],
                scales=p["scales"], sensitivity_radii=p["sensitivity_radii"])


def plot(source, anchor, output):
    checked = audit.audit(source, anchor, public=True)
    result = json.loads(source.read_bytes())
    data = derive(result)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.size":10, "svg.hashsalt":FIGURE})
    output.mkdir(parents=True, exist_ok=False)
    fig, axes = plt.subplots(2, 2, figsize=(12, 9.6))
    fig.subplots_adjust(left=.10, right=.97, bottom=.23, top=.83, hspace=.52, wspace=.30)
    radius = data["primary_radius"]
    for column, case in enumerate(data["cases"]):
        all_rows = [r for r in data["rows"] if r["case"] == case["case"]]
        eligible = [r for r in all_rows if r["variants"]]
        if not eligible or not case["complete"]:
            raise ValueError("this two-case figure requires complete measured right-fold representation")
        ax, lower = axes[:, column]
        for row in eligible:
            for v in row["variants"]:
                marker = "D" if v["method"] == "DOP853" else "s"
                ax.scatter([v["fold_input"][0]], [v["fold_output"][0]], marker=marker,
                    s=55, facecolors="none", edgecolors="#c55916", linewidths=1.2, zorder=5)
        for v in eligible[0]["variants"]:
            events = np.asarray(v["cycle_events"])
            ax.scatter(events[:, 0], np.roll(events[:, 0], -1),
                marker="o" if v["method"] == "DOP853" else "s", s=28,
                facecolors="#0072b2" if v["method"] == "DOP853" else "none",
                edgecolors="#0072b2", linewidths=.8)
        events = np.asarray(eligible[0]["variants"][0]["cycle_events"])
        next_x = np.roll(events[:, 0], -1)
        # Group labels, not observations: all six exact points remain plotted.
        for j in range(3):
            x, y = np.mean(events[[j, j+3], 0]), np.mean(next_x[[j, j+3]])
            ax.annotate(f"{j}, {j+3}", (x, y), xytext=(7, 8), textcoords="offset points", fontsize=8)
        ax.margins(x=.09, y=.10)
        a = ".21575" if column == 0 else ".21577"
        ax.set(title=f"a = {a}  |  {len(eligible)}/{len(all_rows)} fold searches eligible",
               xlabel="Input x on historical section", ylabel="Next-return x")
        ax.text(.03, .04, "Discrete pairs only; no map fitted", transform=ax.transAxes, fontsize=8)
        e = case["envelope"]
        for values, shift, marker, color, label in (
            (e["pair_state_distance"], -.10, "o", "#0072b2", "Full state"),
            (e["pair_x_distance"], .10, "s", "#c55916", "x only")):
            scaled = np.asarray(values)/radius
            if not np.isfinite(scaled).all() or np.any(scaled <= 0):
                raise ValueError("log figure requires positive measured distances")
            lower.scatter(np.arange(6)+shift, scaled, marker=marker, s=35, color=color, label=label)
        lower.axhline(1., color="#253c53", lw=1.2)
        lower.axhline(10., color="#777777", lw=.8, ls="--")
        lower.set_yscale("log")
        lower.set(xlim=(-.5, 5.5), ylim=(.3, 20000), xticks=range(6),
                  xlabel="Cycle input event index j (successor j+1 wraps at 6)",
                  ylabel="Pair mismatch / primary radius",
                  title=f"Closest full-state mismatch: {e['minimum_state_distance']/radius:.2f} x radius")
        lower.text(.98, .19, "Solid: primary radius\nDashed: loosest sensitivity", ha="right",
                   va="bottom", transform=lower.transAxes, fontsize=8)
        for axis in (ax, lower):
            axis.grid(alpha=.17)
            axis.spines[["top", "right"]].set_visible(False)
    fig.suptitle("The nominated cycles miss the measured fold", fontsize=22, y=.98)
    fig.text(.5, .935, "EXP-495  |  Two primitive six-return cycles at b = 0.2, c = 7.212", ha="center", fontsize=12)
    fig.text(.5, .902, "All 26 fold candidates retained; 10 eligible, 16 parent-ineligible. No C/D labels assigned.", ha="center", fontsize=10)
    handles = [Line2D([], [], marker="o", color="#0072b2", ls="none", label="Periodic pair / full-state distance"),
        Line2D([], [], marker="D", markerfacecolor="none", color="#c55916", ls="none", label="Projected fold pair"),
        Line2D([], [], marker="s", color="#c55916", ls="none", label="x-only distance baseline")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .14), ncol=3, frameon=False, fontsize=9)
    fig.text(.08, .105, "Distance panels use the worst case across both solvers, both repeat windows and all eligible right-fold representatives.", fontsize=9)
    fig.text(.08, .080, "Both input and its correct next return must match at the same cycle index. Primary radius = 0.0001; scales = (15, 15, 0.01).", fontsize=9)
    fig.text(.08, .055, "Sixteen failed parent searches are not zero-distance observations. All four depth/direction families contribute in each case.", fontsize=9)
    fig.text(.08, .030, "Operational finite-resolution proximity, not exact critical membership, a complete partition, or a test of Jones's insertion arrows.", fontsize=9)
    outputs = {}
    for suffix in ("svg", "pdf", "png"):
        path = output/f"{FIGURE}.{suffix}"
        metadata = {"Date": None} if suffix == "svg" else ({"CreationDate": None, "ModDate": None} if suffix == "pdf" else None)
        fig.savefig(path, dpi=300, metadata=metadata)
        if suffix == "svg":
            path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())+"\n")
        outputs[path.name] = dict(bytes=path.stat().st_size, sha256=run.sha256(path))
    plt.close(fig)
    receipt = dict(figure_id=FIGURE, title="The nominated cycles miss the measured fold",
        description="Discrete projected return pairs and all-index full-state/x-only mismatch envelopes for both cases.",
        alt_text="Two top panels place six ordered periodic return pairs beside every qualified right-fold pair. Bottom log-scale panels show full-state circles and x-only squares at each of six cycle indices, all above the primary and loosest sensitivity thresholds. Sixteen ineligible parent searches are explicitly accounted for.",
        data_source=dict(path=source.resolve().relative_to(run.ROOT).as_posix(), sha256=anchor,
            fields=["rows.variants", "rows.status", "cases.envelope"],
            selection="All 26 candidates accounted for; geometry only for 10 parent-eligible paired searches.",
            exclusions="Sixteen parent-ineligible searches retain explicit status, not a distance or zero.",
            aggregation="Maximum across same-method comparisons, two repeat windows and all qualified right-fold representations.",
            transformation="Upper x projections; lower exact mismatch divided by fixed primary radius. No fits/interpolation."),
        provenance=dict(source_commit=result["binding"]["source_commit"], audit=checked,
            generator=Path(__file__).relative_to(run.ROOT).as_posix(), generator_sha256=run.sha256(Path(__file__)),
            matplotlib=matplotlib.__version__, outputs=outputs), derived_values=data,
        interval_semantics="Fixed-census maxima, not statistical confidence bounds; thresholds are operational.",
        accessibility="Shapes, labels, event indices, solid/dashed thresholds and explicit eligibility counts supplement color.",
        guards="Result SHA, frozen source/input hashes, separate complete scalar replay, positive finite log coordinates.",
        claim_scope="No exact criticality, C/D assignment, generating partition, insertion arrow or Jones refutation.")
    path = output/f"{FIGURE}.receipt.json"
    run.write(path, receipt)
    run.write(output/f"{FIGURE}.index.json", dict(receipts={path.name: dict(bytes=path.stat().st_size, sha256=run.sha256(path))}))


def verify(output):
    index = json.loads((output/f"{FIGURE}.index.json").read_bytes())
    name = f"{FIGURE}.receipt.json"
    if set(index["receipts"]) != {name}:
        raise ValueError("figure index differs")
    expected = index["receipts"][name]
    if run.sha256(output/name) != expected["sha256"] or (output/name).stat().st_size != expected["bytes"]:
        raise ValueError("figure receipt differs")
    r = json.loads((output/name).read_bytes())
    source = run.ROOT/r["data_source"]["path"]
    if run.sha256(source) != r["data_source"]["sha256"] or run.sha256(run.ROOT/r["provenance"]["generator"]) != r["provenance"]["generator_sha256"]:
        raise ValueError("source or generator drift")
    if derive(json.loads(source.read_bytes())) != r["derived_values"]:
        raise ValueError("plotted-data drift")
    for name, expected in r["provenance"]["outputs"].items():
        if run.sha256(output/name) != expected["sha256"] or (output/name).stat().st_size != expected["bytes"]:
            raise ValueError("figure output drift")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--sha256")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        verify(args.output_dir)
    else:
        plot(args.source, args.sha256, args.output_dir)


if __name__ == "__main__":
    main()

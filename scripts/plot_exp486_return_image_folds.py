#!/usr/bin/env python3
"""All-family EXP-486 curves and roots, with reproducible figure receipts."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
from butterfly._paired_startup import sha256, write_json

FIGURE = "EXP-486-continuous-return-curves"


def plot(source, expected_sha, output):
    if sha256(source) != expected_sha:
        raise ValueError("audited figure input anchor changed")
    result = json.loads(source.read_bytes())
    if result["status"] != "completed-audited" or not result["complete_grid_and_decision_replay"]:
        raise ValueError("fully audited result required")
    ids = {f"{c}--region-{r}--depth-{m}--direction-{d}" for c in
           ("local-a025-c083", "local-a027-c083") for r in (0, 1) for m in (4, 8) for d in (0, 1)}
    if (len(result["families"]) != 16 or len(result["rows"]) != 16
            or {f["id"] for f in result["families"]} != ids
            or {r["family_id"] for r in result["rows"]} != ids
            or any(len(r["analysis"]["grid_observations"]) != 17 for r in result["rows"])):
        raise ValueError("complete 16-family, 17-point grid required")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"svg.hashsalt": FIGURE, "font.size": 9})
    output.mkdir(parents=True, exist_ok=False)
    fig, axes = plt.subplots(4, 2, figsize=(12, 14), layout="constrained")
    styles = [("#0072b2", "-", "o"), ("#0072b2", "--", "s"),
              ("#d55e00", "-.", "^"), ("#d55e00", ":", "D")]
    derived = []
    for row_index, (case, region) in enumerate((c, r) for c in
            ("local-a025-c083", "local-a027-c083") for r in (0, 1)):
        members = sorted([f for f in result["families"] if f["case"] == case and f["region"] == region],
                         key=lambda f: (f["depth"], f["direction_id"]))
        ax, slope_ax = axes[row_index]
        a = members[0]["parameters"]["a"]
        interval = members[0]["old_x_interval"]
        ax.axvspan(*interval, color=".88", zorder=0)
        slope_ax.axhline(0., color=".6", lw=.7)
        missing = 0
        for family, (color, line, marker) in zip(members, styles, strict=True):
            analysis = next(r["analysis"] for r in result["rows"] if r["family_id"] == family["id"])
            observations = analysis["grid_observations"]
            x = [o["image_state"][0] if "image_state" in o else np.nan for o in observations]
            y = [o["next_state"][0] if "next_state" in o else np.nan for o in observations]
            slopes = [o["x_graph_slope"] if o["valid"] else np.nan for o in observations]
            invalid = [not o["valid"] for o in observations]
            missing += sum(invalid)
            label = f"m={family['depth']}, d{family['direction_id']}"
            ax.plot(x, y, color=color, ls=line, marker=marker, ms=3, lw=1.2, label=label)
            # Ordered u samples belong to this one flow curve, not different seeds.
            slope_ax.plot(np.asarray(family["grid"])/family["radius"], slopes,
                          color=color, ls=line, marker=marker, ms=3, lw=1.2)
            ax.scatter(np.asarray(x)[invalid], np.asarray(y)[invalid], marker="x", color="black", s=30, zorder=6)
            roots = []
            for root in analysis["roots"]:
                if "observations" not in root:
                    roots.append(dict(status=root["status"], original_u_bracket=root["original_u_bracket"]))
                    continue
                o = root["observations"]["DOP853"]
                qualified = root["status"] == "qualified" and root["in_region"]
                ax.scatter(o["image_state"][0], o["next_state"][0], marker="*", s=120,
                           edgecolors=color, facecolors=color if qualified else "none", zorder=7)
                slope_ax.scatter(root["u"]/family["radius"], o["x_graph_slope"], marker="*", s=100,
                                 edgecolors=color, facecolors=color if qualified else "none", zorder=7)
                roots.append(dict(u=root["u"], status=root["status"], in_region=root["in_region"],
                                  image_state=o["image_state"], next_state=o["next_state"],
                                  x_graph_slope=o["x_graph_slope"]))
            derived.append(dict(family_id=family["id"], qualified=analysis["qualified"],
                normalized_u=(np.asarray(family["grid"])/family["radius"]).tolist(),
                points=[dict(image_x=float(xx) if np.isfinite(xx) else None,
                             next_x=float(yy) if np.isfinite(yy) else None,
                             slope=float(ss) if np.isfinite(ss) else None, valid=not invalid[i])
                        for i, (xx, yy, ss) in enumerate(zip(x, y, slopes, strict=True))], roots=roots))
        outcome = next(r for r in result["regions"] if r["case"] == case and r["region"] == region)
        ax.set(title=f"a={a:.5f}, region {region+1}: {'consistent' if outcome['qualified'] else 'unresolved'}",
               xlabel="Image curve x after m returns", ylabel="Next-return x")
        slope_ax.set(title=f"Projected derivative; {missing}/68 grid slopes unavailable",
                     xlabel="Initial curve parameter u / frozen radius", ylabel="dx(next return) / dx(image curve)")
        ax.legend(fontsize=8, ncols=2)
        for panel in (ax, slope_ax):
            panel.grid(alpha=.15)
    fig.suptitle("Continuous flow-return curves: testing local fold geometry\nb = 0.2, c = 7.212; finite histories, not verified symbolic chains", fontsize=14)
    fig.legend(handles=[Line2D([], [], marker="*", color=".3", lw=0, markersize=11, label="Qualified in-region root"),
                        Line2D([], [], marker="*", color=".3", markerfacecolor="none", lw=0, markersize=11, label="Other evaluated root"),
                        Line2D([], [], marker="x", color="black", lw=0, label="Unavailable x-graph slope")],
               loc="outside lower center", ncols=3, fontsize=9)
    outputs = {}
    for suffix in ("png", "svg", "pdf"):
        path = output/f"{FIGURE}.{suffix}"
        metadata = {"Date": None} if suffix == "svg" else ({"CreationDate": None, "ModDate": None} if suffix == "pdf" else None)
        fig.savefig(path, dpi=300, metadata=metadata)
        if suffix == "svg":
            path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())+"\n")
        outputs[path.name] = dict(sha256=sha256(path), bytes=path.stat().st_size)
    plt.close(fig)
    receipt = dict(figure_id=FIGURE, experiment_id="EXP-486", title="Continuous finite-return curves and projected folds",
        description="All sixteen curve families, their ordered grid samples, projected slopes and retained root evaluations.",
        alt_text="Four rows show both candidate regions in two nearby parameter cases. Left panels show each continuous finite-history return curve; a gray band marks the prior candidate interval. Right panels show derivatives against the normalized starting-curve parameter. Line styles and markers distinguish both history lengths and both starting directions. Stars mark evaluated roots, and crosses or slope gaps retain invalid geometry.",
        source_receipt_sha256=expected_sha, source_fields=["families.id", "families.grid", "families.radius", "families.old_x_interval", "rows.analysis.grid_observations", "rows.analysis.roots", "regions.qualified"],
        data_selection="All 16 families and 17 grid points per family, all refined roots; no outcome filtering. Display DOP853 values only after the complete dual-solver audit; counterpart solver evidence remains in the source receipt. Unreturned states and invalid slopes are gaps, never filled.",
        interpolation="Straight display segments in the original u order between finite samples of each individual flow curve; not interpolation across trajectories or a rigorous continuum certificate.",
        interval_semantics="Gray band is the prior-outcome-informed observed x interval, not a confidence or error interval. No uncertainty bars are claimed.",
        generator=dict(path="scripts/plot_exp486_return_image_folds.py", sha256=sha256(Path(__file__)), python=sys.version, numpy=np.__version__, matplotlib=matplotlib.__version__),
        audit=dict(path="scripts/audit_exp486_return_image_folds.py", sha256=result["audit_script_sha256"]),
        outputs=outputs, derived_values=derived, raster_dpi=300,
        accessibility="Distinct line styles and point shapes in addition to color; filled/open stars distinguish root scope. Panel titles state missing slope counts and region status.",
        guards=["Exact input SHA-256", "completed-audited status", "complete 16-family/17-point grid", "all roots retained", "no scientific image generation"],
        claim_boundary=result["claim_boundary"])
    receipt_path = output/f"{FIGURE}.receipt.json"
    write_json(receipt_path, receipt)
    write_json(output/f"{FIGURE}.index.json", dict(schema="butterfly.figure-receipt-index.v1",
        receipts={receipt_path.name: dict(sha256=sha256(receipt_path), bytes=receipt_path.stat().st_size)}))


def verify(output):
    index = json.loads((output/f"{FIGURE}.index.json").read_bytes())
    if set(index["receipts"]) != {f"{FIGURE}.receipt.json"}:
        raise ValueError("receipt index membership changed")
    for name, anchor in index["receipts"].items():
        path = output/name
        if sha256(path) != anchor["sha256"] or path.stat().st_size != anchor["bytes"]:
            raise ValueError("figure receipt hash/size changed")
        receipt = json.loads(path.read_bytes())
        if set(receipt["outputs"]) != {f"{FIGURE}.{suffix}" for suffix in ("png", "svg", "pdf")}:
            raise ValueError("figure output set changed")
        for name, anchor in receipt["outputs"].items():
            path = output/name
            if sha256(path) != anchor["sha256"] or path.stat().st_size != anchor["bytes"]:
                raise ValueError("figure output hash/size changed")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        if args.receipt is None or args.expected_sha256 is None:
            parser.error("receipt and expected hash required for generation")
        plot(args.receipt, args.expected_sha256, args.output_dir)
    verify(args.output_dir)
    print("All figure receipt and SVG/PDF/PNG hashes verified")


if __name__ == "__main__":
    main()

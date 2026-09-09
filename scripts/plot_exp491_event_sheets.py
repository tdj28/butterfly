#!/usr/bin/env python3
"""All EXP-491 sampled return geometry, with no interpolation across gaps."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
import numpy as np
from butterfly._paired_startup import sha256,write_json
from butterfly.event_sheet_probe import interval,pair
from scripts import run_exp491_event_sheet_probe as run

FIGURE = "EXP-491-sampled-event-sheets"


def derive(result):
    plan = json.loads(run.PLAN.read_bytes())
    candidates,previous = run.load(plan)
    if result["experiment_id"] != "EXP-491" or result["status"] != "completed-audited" or result["target_trajectories"] != 156 or [r["id"] for r in result["candidates"]] != [c["id"] for c in candidates]:
        raise ValueError("complete audited candidate matrix required")
    rows = []
    for r,c,old in zip(result["candidates"],candidates,previous["candidates"],strict=True):
        if r["us"] != run.sample_values(c) or r["analysis"] != interval(r["points"],r["us"],plan) or r["prior_fold_qualified"] != old["qualified"]:
            raise ValueError("sample or decision replay differs")
        samples = []
        for i,point in enumerate(r["points"]):
            if [p["method"] for p in point["profiles"]] != plan["solvers"]:
                raise ValueError("both solvers required")
            if point != pair(point["profiles"],plan):
                raise ValueError("paired sample decision differs")
            for p in point["profiles"]:
                xy = None
                if p["status"] == "returned":
                    if len(p["events"]) != c["count"]:
                        raise ValueError("requested prefix differs")
                    xy = [p["events"][-2]["state"][0],p["events"][-1]["state"][0]]
                    if not np.isfinite(xy).all():
                        raise ValueError("nonfinite plotted coordinates")
                samples.append(dict(index=i,u=r["us"][i],method=p["method"],xy=xy,
                    numeric_qualified=point["numeric_qualified"],projection_qualified=point["projection_qualified"],
                    status=p["status"],reason=p["reason"]))
        rows.append(dict(id=c["id"],family_id=c["family_id"],case=c["case"],a=c["parameters"]["a"],region=c["region"],
            depth=c["count"]-1,direction=int(c["family_id"].split("--direction-")[-1]),
            ordinal=int(c["id"].split("--candidate-")[-1])+1,
            analysis=r["analysis"],prior_fold_qualified=r["prior_fold_qualified"],samples=samples))
    return rows


def plot(source,anchor,output):
    if sha256(source) != anchor:
        raise ValueError("source anchor differs")
    result = json.loads(source.read_bytes())
    data = derive(result)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"svg.hashsalt":FIGURE,"font.size":9,"axes.formatter.useoffset":False})
    output.mkdir(parents=True,exist_ok=False)
    fig,axes = plt.subplots(4,4,figsize=(14,13))
    fig.subplots_adjust(left=.075,right=.98,bottom=.18,top=.85,wspace=.37,hspace=.53)
    palette = ["#0072b2","#d55e00","#009e73","#8b519d"]
    markers = ["<","o",">"]
    families = []
    for ri,(depth,direction) in enumerate(((4,0),(4,1),(8,0),(8,1))):
        for ci,(case,region) in enumerate((("local-a025-c083",0),("local-a025-c083",1),("local-a027-c083",0),("local-a027-c083",1))):
            rows = [d for d in data if (d["case"],d["region"],d["depth"],d["direction"]) == (case,region,depth,direction)]
            if not rows:
                raise ValueError("missing family")
            ax = axes[ri,ci]
            missing = 0
            for d in rows:
                color = palette[d["ordinal"]-1]
                for s in d["samples"]:
                    if s["xy"] is None:
                        missing += 1
                        continue
                    x,y = s["xy"]
                    radau = s["method"] == "Radau"
                    ax.scatter([x],[y],s=64 if radau else 23,marker=markers[s["index"]],
                               facecolors="none" if radau else color,edgecolors=color,linewidths=.9,zorder=3)
                    if not s["numeric_qualified"]:
                        ax.scatter([x],[y],s=30,marker="x",color="black",linewidths=.8,zorder=4)
                    elif not s["projection_qualified"]:
                        ax.scatter([x],[y],s=30,marker="+",color="black",linewidths=.8,zorder=4)
            checks = {key:sum(not d["analysis"]["checks"][key] for d in rows) for key in ("point_numerics","point_projection","input_sign","time_coherence")}
            regular = sum(d["analysis"]["screened_regular"] for d in rows)
            label = "Left" if region == 0 else "Right"
            ax.set_title(f"a={rows[0]['a']:.5f} | {label}\nm={depth}, direction {direction}",fontsize=9.5,pad=21)
            ax.text(.5,1.025,f"Screen {regular}/{len(rows)}; cuts N/P/S/T: "+"/".join(str(v) for v in checks.values()),
                    transform=ax.transAxes,ha="center",fontsize=7.8)
            if missing:
                ax.text(.03,.04,f"{missing}/{6*len(rows)} unavailable",transform=ax.transAxes,fontsize=7,bbox=dict(facecolor="white",alpha=.85,edgecolor="none"))
            ax.grid(alpha=.18)
            ax.margins(.15)
            ax.tick_params(labelsize=7.5)
            ax.ticklabel_format(style="plain",axis="both",useOffset=False)
            for spine in ("top","right"):
                ax.spines[spine].set_visible(False)
            if ci == 0:
                ax.set_ylabel("Next section x",fontsize=9)
            if ri == 3:
                ax.set_xlabel("Input section x",fontsize=9)
            families.append(dict(family_id=rows[0]["family_id"],screened_regular=regular,candidates=len(rows),cuts=checks,unavailable_solver_points=missing))
    regular = sum(d["analysis"]["screened_regular"] for d in data)
    fig.suptitle("Where a sampled return curve can be trusted",fontsize=22,y=.97)
    fig.text(.5,.929,f"{regular}/26 intervals pass the three-point screen | 16 families | 156 solver trajectories",ha="center",fontsize=12)
    fig.text(.5,.902,"b=0.2, c=7.212. Every original interval retained. Points only: no fitted or certified continuous branches.",ha="center",fontsize=10)
    handles = [Line2D([],[],marker=markers[i],linestyle="none",color="#555555",label=label) for i,label in enumerate(("Left endpoint","Midpoint","Right endpoint"))]
    handles += [Line2D([],[],marker="o",linestyle="none",color="#555555",markerfacecolor="none" if i else "#555555",markersize=8 if i else 4,label=label) for i,label in enumerate(("DOP853 filled","Radau outline"))]
    fig.legend(handles=handles,loc="lower center",bbox_to_anchor=(.5,.111),ncol=5,frameon=False,fontsize=9)
    handles = [Line2D([],[],marker="o",linestyle="none",color=color,label=f"Candidate {i+1}") for i,color in enumerate(palette)]
    fig.legend(handles=handles,loc="lower center",bbox_to_anchor=(.5,.081),ncol=4,frameon=False,fontsize=9)
    fig.text(.075,.064,"Cuts: N numerical pair, P input projection, S input-tangent sign, T event-time coherence. Flags overlap; they are not diagnoses of a grazing root.",fontsize=8.4)
    fig.text(.075,.043,"Black x: numerical pair fails. Black +: numerics pass, input projection fails. Candidate numbers are local to each family; axes vary by panel.",fontsize=8.4)
    fig.text(.075,.022,"All coordinates use dimensionless model units. Passing three samples does not exclude hidden boundaries, establish an invariant partition or verify Jones's symbolic chains.",fontsize=8.4)
    outputs = {}
    for suffix in ("svg","pdf","png"):
        path = output/f"{FIGURE}.{suffix}"
        metadata = {"Date":None} if suffix == "svg" else ({"CreationDate":None,"ModDate":None} if suffix == "pdf" else None)
        fig.savefig(path,dpi=300,metadata=metadata)
        if suffix == "svg":
            path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())+"\n")
        outputs[path.name] = dict(sha256=sha256(path),bytes=path.stat().st_size)
    plt.close(fig)
    receipt = dict(figure_id=FIGURE,title="Where a sampled return curve can be trusted",
        alt_text="Sixteen scatter panels retain both parameter cases, both regions, two return depths and two initial directions. Three marker shapes identify interval endpoints and midpoint; filled and outlined marks retain both solvers. Failed numerical or input-projection points are overlaid, never removed. Panel counts retain all screened and cut intervals. No smooth curves are drawn.",
        source=dict(path=source.resolve().relative_to(ROOT).as_posix(),sha256=anchor,
            fields=["candidates.points.profiles.events","candidates.points.numeric_qualified","candidates.points.projection_qualified","candidates.analysis"],
            selection="All 26 frozen intervals, all 78 paired samples and both solvers, in all 16 families.",
            exclusions="Only unavailable requested returns have no coordinates; their counts are printed. Available failed points are retained.",
            aggregation="No coordinate averaging; solver points overlap when in agreement. Screen/cut counts summarize the frozen conjunction within each family.",
            transformation="Input x and next x are the penultimate and last selected event x. No interpolation, smoothing, fitted curves or error bars."),
        bindings=[dict(path=p,sha256=sha256(ROOT/p)) for p in ("scripts/plot_exp491_event_sheets.py","scripts/audit_exp491_event_sheet_probe.py","python/butterfly/event_sheet_probe.py",run.PLAN.relative_to(ROOT).as_posix(),"experiments/manifests/EXP-490-candidates.json")],
        runtime=dict(python=sys.version,matplotlib=matplotlib.__version__),derived_values=data,families=families,
        outputs=outputs,run_source_commit=result["source_commit"],completed_summary_sha256=result["summary_sha256"],
        units="Dimensionless model state coordinates; panel ranges differ and are not uncertainty intervals.",
        accessibility="Sample shapes and solver fill styles duplicate distinctions; textual cut counts and black overlays do not rely on color alone.",
        raster_dpi=300,claim_boundary=result["claim_boundary"])
    path = output/f"{FIGURE}.receipt.json"
    write_json(path,receipt)
    write_json(output/f"{FIGURE}.index.json",dict(receipts={path.name:dict(sha256=sha256(path),bytes=path.stat().st_size)}))


def verify(output):
    index = json.loads((output/f"{FIGURE}.index.json").read_bytes())
    if set(index["receipts"]) != {f"{FIGURE}.receipt.json"}:
        raise ValueError("receipt set differs")
    for name,item in index["receipts"].items():
        if sha256(output/name) != item["sha256"] or (output/name).stat().st_size != item["bytes"]:
            raise ValueError("receipt changed")
    r = json.loads((output/f"{FIGURE}.receipt.json").read_bytes())
    for item in [r["source"],*r["bindings"]]:
        path = (ROOT/item["path"]).resolve()
        path.relative_to(ROOT)
        if sha256(path) != item["sha256"]:
            raise ValueError("source/code changed")
    if r["derived_values"] != derive(json.loads((ROOT/r["source"]["path"]).read_bytes())):
        raise ValueError("derived values differ")
    if set(r["outputs"]) != {f"{FIGURE}.{s}" for s in ("svg","pdf","png")}:
        raise ValueError("output set differs")
    for name,item in r["outputs"].items():
        if sha256(output/name) != item["sha256"] or (output/name).stat().st_size != item["bytes"]:
            raise ValueError("output changed")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt",type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--verify-only",action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        plot(args.receipt,args.expected_sha256,args.output_dir)
    verify(args.output_dir)
    print("Complete sampled geometry and provenance hashes verified")

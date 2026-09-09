#!/usr/bin/env python3
"""All nominated event boundaries, with measured crossings and local theory."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
import numpy as np
from butterfly._paired_startup import sha256,write_json
from scripts import run_exp492_event_boundaries as run

FIGURE = "EXP-492-event-boundaries"


def derive(result):
    p = json.loads(run.PLAN.read_bytes())
    table,candidates = run.load(p)
    if result["experiment_id"] != "EXP-492" or result["status"] != "completed-audited" or not 32 <= result["target_integrations"] <= 384 or len(result["intervals"]) != 26:
        raise ValueError("complete audited matrix required")
    rows = []
    for r,c in zip(result["intervals"],table["intervals"],strict=True):
        if any(r[k] != c[k] for k in ("id","family_id","case","region")) or r["selection_status"] != c["status"]:
            raise ValueError("original interval identities differ")
        a = r["analysis"]
        if c["status"] != "nominated":
            if a is not None:
                raise ValueError("unselected interval acquired a result")
            continue
        samples,reference = [],None
        if not a["roots"]["eligible"]:
            if a["qualified"] or a["solvers"] or a["paired_sides"]:
                raise ValueError("failed root gate has side results")
        else:
            if [s["method"] for s in a["solvers"]] != p["solvers"] or len(a["paired_sides"]) != 4:
                raise ValueError("complete solver/side matrix required")
            reference = a["solvers"][0]["root"]
            for s in a["solvers"]:
                if [v["nominal_dose"] for v in s["sides"]] != c["doses"]:
                    raise ValueError("dose matrix differs")
                root = s["root"]
                for side_index,v in enumerate(s["sides"]):
                    u = a["roots"]["common_center_u"]+v["nominal_dose"]
                    dose = u-root["u"]
                    expected = 2 if root["jacobian"][0][0]*dose*root["jacobian"][1][1] < 0 else 0
                    local = v["local_roots"]
                    passed = (len(local) == expected and sum(e["accepted"] for e in local) == expected//2
                        and not v["uncertain_extrema"] and not v["prefix_uncertainty"]
                        and v["accepted_prefix_count"] == c["accepted_prefix"]
                        and all(abs(e["residual"]) <= p["side_residual"] and e["angle"] >= p["minimum_angle"] for e in local))
                    separation = local[1]["time"]-local[0]["time"] if len(local) == 2 else None
                    if v["u"] != u or v["dose"] != dose or v["expected_roots"] != expected or v["passed"] != passed or v["separation"] != separation:
                        raise ValueError("local event decision differs")
                    for e in local:
                        xy = [(u-reference["u"])/max(abs(d) for d in c["doses"]),e["time"]-reference["time"]]
                        if not np.isfinite(xy).all():
                            raise ValueError("nonfinite figure coordinate")
                        paired_passed = a["paired_sides"][side_index]["passed"]
                        samples.append(dict(method=s["method"],nominal_dose=v["nominal_dose"],xy=xy,accepted=e["accepted"],
                            local_passed=v["passed"],paired_passed=paired_passed,side_passed=bool(v["passed"] and paired_passed)))
                pairs = sorted([v for v in s["sides"] if v["expected_roots"] == 2],key=lambda v:abs(v["nominal_dose"]))
                ratio = pairs[1]["separation"]/pairs[0]["separation"] if len(pairs) == 2 and all(v["separation"] is not None and v["separation"] > 0 for v in pairs) else None
                passed = all(v["passed"] for v in s["sides"]) and ratio is not None and abs(ratio/np.sqrt(10)-1) <= p["square_root_ratio_relative_error"]
                if s["square_root_ratio"] != ratio or s["passed"] != passed:
                    raise ValueError("scaling decision differs")
            for pair,dose in zip(a["paired_sides"],c["doses"],strict=True):
                counts = pair["counts"]
                if len(counts) != 2 or pair["dose"] != dose or len(pair["errors"]) != (counts[0] if counts[0] == counts[1] else 0):
                    raise ValueError("paired event sequence differs")
                passed = counts[0] == counts[1] and all(e["time"] <= p["side_solver_time"] and e["scaled_state"] <= p["side_solver_scaled_state"] for e in pair["errors"])
                if pair["passed"] != passed:
                    raise ValueError("paired event decision differs")
            if a["qualified"] != (all(s["passed"] for s in a["solvers"]) and all(s["passed"] for s in a["paired_sides"])):
                raise ValueError("qualification differs")
        rows.append(dict(id=c["id"],family_id=c["family_id"],a=c["parameters"]["a"],region=c["region"],
            depth=int(c["family_id"].split("--depth-")[1].split("--")[0]),
            direction=int(c["family_id"].split("--direction-")[-1]),ordinal=int(c["id"].split("--candidate-")[-1])+1,
            prefix=c["accepted_prefix"],wide_dose=max(abs(d) for d in c["doses"]),reference=reference,
            qualified=a["qualified"],root_gate=a["roots"]["eligible"],analysis=a,samples=samples))
    if len(rows) != 16 or len({r["family_id"] for r in rows}) != 10:
        raise ValueError("all sixteen nominations in ten families required")
    return rows


def plot(source,anchor,output):
    if sha256(source) != anchor:
        raise ValueError("source anchor differs")
    result = json.loads(source.read_bytes())
    rows = derive(result)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MaxNLocator
    plt.rcParams.update({"svg.hashsalt":FIGURE,"font.size":9})
    output.mkdir(parents=True,exist_ok=False)
    fig,axes = plt.subplots(4,4,figsize=(14,13))
    fig.subplots_adjust(left=.08,right=.985,bottom=.18,top=.86,wspace=.35,hspace=.55)
    colors = {"DOP853":"#0072b2","Radau":"#d55e00"}
    for i,(ax,r) in enumerate(zip(axes.flat,rows,strict=True)):
        root = r["reference"]
        if root is not None:
            hu,htt = root["jacobian"][0][0],root["jacobian"][1][1]
            sign = -np.sign(hu*htt)
            x = sign*np.linspace(0.,1.05,150)
            dt = np.sqrt(np.maximum(0.,-2*hu*x*r["wide_dose"]/htt))
            for polarity in (-1,1):
                ax.plot(x,polarity*dt,color="#777777",ls="--",lw=1,zorder=1)
            ax.scatter([0],[0],marker="D",color="black",s=19,zorder=4)
            for s in r["samples"]:
                ax.scatter(*s["xy"],marker="o" if s["accepted"] else "s",s=53 if s["method"] == "Radau" else 20,
                    facecolors="none" if s["method"] == "Radau" else colors[s["method"]],edgecolors=colors[s["method"]],linewidths=1,zorder=3)
                if not s["side_passed"]:
                    ax.scatter(*s["xy"],marker="x",s=25,color="black",zorder=5)
            # Explicit zero-root conditions remain visible, not silently absent.
            counts = "\n".join(f"{m}: "+"/".join(str(len(v["local_roots"])) for v in s["sides"])
                for m,s in zip(("D","R"),r["analysis"]["solvers"],strict=True))
            text_x = .04 if sign > 0 else .57
            ax.text(text_x,.05,counts,transform=ax.transAxes,fontsize=7,
                bbox=dict(facecolor="white",alpha=.9,edgecolor="none"))
            ax.text(text_x,.23,f"Paired: {sum(v['passed'] for v in r['analysis']['paired_sides'])}/4",
                transform=ax.transAxes,fontsize=7,bbox=dict(facecolor="white",alpha=.9,edgecolor="none"))
        else:
            ax.text(.5,.5,"Root/box gate failed\nAll side arms skipped",ha="center",va="center",transform=ax.transAxes)
        ax.axvline(0,color="#cccccc",lw=.6,zorder=0)
        ax.axhline(0,color="#cccccc",lw=.6,zorder=0)
        ax.set_xlim(-1.2,1.2)
        ax.set_xticks([-1.,0.,1.])
        ax.yaxis.set_major_locator(MaxNLocator(3))
        ax.ticklabel_format(style="plain",axis="y",useOffset=False)
        ax.tick_params(labelsize=8)
        ax.grid(alpha=.15)
        label = "L" if r["region"] == 0 else "R"
        ax.set_title(f"a={r['a']:.5f} {label} | m={r['depth']} d={r['direction']} c={r['ordinal']}\n"
            f"{'Qualified' if r['qualified'] else 'Unqualified'} | {r['prefix']} prior negative returns",fontsize=9,pad=9)
        for spine in ("top","right"):
            ax.spines[spine].set_visible(False)
        if i%4 == 0:
            ax.set_ylabel("Time from grazing",fontsize=9)
        if i//4 == 3:
            ax.set_xlabel("Initial displacement / wide dose",fontsize=9)
    qualified = sum(r["qualified"] for r in rows)
    fig.suptitle("Where a section intersection is born or lost",fontsize=21,y=.975)
    fig.text(.5,.937,f"{qualified}/16 nominated intervals qualify | both solvers and all prescribed side arms retained",ha="center",fontsize=12)
    fig.text(.5,.908,"Fixed b=0.2, c=7.212; varying initial conditions, not parameters. Ten screened-regular intervals were not selected.",ha="center",fontsize=10)
    handles = [Line2D([],[],marker="o",linestyle="none",color=colors["DOP853"],markersize=5,label="DOP853 filled"),
        Line2D([],[],marker="o",linestyle="none",color=colors["Radau"],markerfacecolor="none",markersize=8,label="Radau outline"),
        Line2D([],[],marker="o",linestyle="none",color="black",label="Accepted negative crossing"),
        Line2D([],[],marker="s",linestyle="none",color="black",label="Other crossing")]
    fig.legend(handles=handles,loc="lower center",bbox_to_anchor=(.5,.109),ncol=4,frameon=False,fontsize=9)
    fig.legend(handles=[Line2D([],[],marker="D",linestyle="none",color="black",label="Located tangency"),
        Line2D([],[],ls="--",color="#777777",label="Local quadratic prediction (not a fit)"),
        Line2D([],[],marker="x",linestyle="none",color="black",label="Failed side arm retained")],
        loc="lower center",bbox_to_anchor=(.5,.079),ncol=3,frameon=False,fontsize=9)
    fig.text(.08,.061,"Panel labels: m return depth, d initial direction, c candidate number (local to each family). D/R counts follow doses -1, -0.1, +0.1, +1.",fontsize=8.5)
    fig.text(.08,.040,"Coordinates use the DOP853 root as the common plotting origin; the wide dose is the frozen half-interval width / 1000. Panel time scales differ.",fontsize=8.5)
    fig.text(.08,.019,"Time is in dimensionless model units. Crossing-pair birth/death is not proof of a new periodic window, an inner return, or a Jones symbolic-chain arrow.",fontsize=8.5)
    outputs = {}
    for suffix in ("svg","pdf","png"):
        path = output/f"{FIGURE}.{suffix}"
        metadata = {"Date":None} if suffix == "svg" else ({"CreationDate":None,"ModDate":None} if suffix == "pdf" else None)
        fig.savefig(path,dpi=300,metadata=metadata)
        if suffix == "svg":
            path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())+"\n")
        outputs[path.name] = dict(bytes=path.stat().st_size,sha256=sha256(path))
    plt.close(fig)
    bindings = tuple(dict.fromkeys(("scripts/plot_exp492_event_boundaries.py",run.PLAN.relative_to(ROOT).as_posix(),
        "experiments/manifests/EXP-492-event-boundary-inputs.json",*run.SOURCES)))
    receipt = dict(figure_id=FIGURE,title="Where a section intersection is born or lost",
        alt_text="Sixteen panels show every nominated boundary. Measured crossings are circles for accepted negative crossings and squares for the other orientation. Filled blue and outlined orange retain both solvers. Dashed curves show the local quadratic prediction. Zero-root conditions and failed or skipped conditions are labeled.",
        source=dict(path=source.resolve().relative_to(ROOT).as_posix(),sha256=anchor,
            fields=["intervals.analysis.solvers.root","intervals.analysis.solvers.sides.local_roots","intervals.analysis.paired_sides"],
            selection="All sixteen nominated intervals in ten families; the ten previously screened-regular intervals explicitly remain unselected.",
            exclusions="No nominated candidate or side outcome removed. Skipped side matrices have labeled panels; zero roots are explicit counts.",
            transformation="Horizontal (u-u_DOP)/wide_dose; vertical t-t_DOP. No averaging or fitting. Dashed theory uses DOP root h_u and h_tt in the local quadratic expansion.",
            aggregation="None for coordinates. Header counts the frozen qualification conjunction; panel counts retain all four side arms per solver."),
        bindings=[dict(path=s,sha256=sha256(ROOT/s)) for s in bindings],derived_values=rows,
        outputs=outputs,run_source_commit=result["source_commit"],completed_summary_sha256=result["summary_sha256"],
        runtime=dict(python=sys.version,matplotlib=matplotlib.__version__),raster_dpi=300,
        accessibility="Shape identifies crossing orientation, fill style identifies solver, textual labels retain failures and zero-root conditions.",
        units="Dimensionless model time and normalized initial-curve coordinate; axis ranges are not confidence intervals.",claim_boundary=result["claim_boundary"])
    path = output/f"{FIGURE}.receipt.json"
    write_json(path,receipt)
    write_json(output/f"{FIGURE}.index.json",dict(receipts={path.name:dict(sha256=sha256(path),bytes=path.stat().st_size)}))


def verify(output):
    index = json.loads((output/f"{FIGURE}.index.json").read_bytes())
    if set(index["receipts"]) != {f"{FIGURE}.receipt.json"}:
        raise ValueError("receipt matrix differs")
    for name,v in index["receipts"].items():
        if sha256(output/name) != v["sha256"] or (output/name).stat().st_size != v["bytes"]:
            raise ValueError("receipt changed")
    r = json.loads((output/f"{FIGURE}.receipt.json").read_bytes())
    for item in [r["source"],*r["bindings"]]:
        path = (ROOT/item["path"]).resolve()
        path.relative_to(ROOT)
        if sha256(path) != item["sha256"]:
            raise ValueError("source/code changed")
    if derive(json.loads((ROOT/r["source"]["path"]).read_bytes())) != r["derived_values"]:
        raise ValueError("derived geometry differs")
    if set(r["outputs"]) != {f"{FIGURE}.{s}" for s in ("svg","pdf","png")}:
        raise ValueError("output matrix differs")
    for name,v in r["outputs"].items():
        if sha256(output/name) != v["sha256"] or (output/name).stat().st_size != v["bytes"]:
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
    print("All boundary geometry and provenance hashes verified")

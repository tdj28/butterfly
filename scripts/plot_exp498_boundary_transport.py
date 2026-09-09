#!/usr/bin/env python3
"""Receipt-bound section geometry; connectors indicate event order, not flow."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from butterfly._paired_startup import sha256,write_json
from butterfly.event_boundary_shooting import assess
from scripts import run_exp498_boundary_transport as run
from scripts import audit_exp498_boundary_transport as audit

STEM = "EXP-498-boundary-transport"
SOURCE = "511ff1c1593ced21a91496d7fb1270eca9b9878d"
COLORS = ["#007f86","#007f86","#4477aa","#4477aa","#a65d27","#a65d27","#8b559b","#8b559b"]
MARKERS = ["o","s","^","v","D","P","X","h"]


def validate(result):
    p,anchor = run.load()
    if (result.get("experiment_id") != "EXP-498" or result.get("passed") is not True
            or result.get("source_commit") != SOURCE
            or result.get("audit_source_sha256") != sha256(Path(audit.__file__))
            or result.get("ledger") != p["ledger"]
            or [r["id"] for r in result.get("rows",[])] != [c["id"] for c in p["candidates"]]):
        raise ValueError("complete audited fixed-source result required")
    for r,c in zip(result["rows"],p["candidates"],strict=True):
        if r["parent_id"] != c["parent_id"] or r["parent_qualified"] != c["parent_qualified"]:
            raise ValueError("historical failure/identity differs")
        b = r["boundary"]
        if not run.polygon_audit.same_numeric(assess(b["roots"],b["sides"],c,p["boundary"]),b["analysis"]):
            raise ValueError("boundary decision differs")
        g = r["geometry"]
        expected = run.winding.compare(g["sides"],c,p["winding"],b["analysis"]["qualified"]) if g["sides"] else None
        if not run.polygon_audit.same_numeric(expected,g["analysis"]): raise ValueError("winding decision differs")
        if not run.polygon_audit.same_numeric(audit.scalar_predecessors(c,b,anchor,p),r["predecessors"]):
            raise ValueError("saved predecessor arithmetic differs")
    if not run.polygon_audit.same_numeric(audit.scalar_diagnostic(result["rows"],anchor,p),result["diagnostic"]):
        raise ValueError("all-index diagnostic differs")
    return p,anchor


def plot_rows(result):
    rows = []
    for row in result["rows"]:
        records = [v for v in row["predecessors"] if v["eligible"]]
        passed = bool(row["geometry"]["analysis"] and row["geometry"]["analysis"]["qualified"])
        distances = np.max(np.array([w["state_distances"] for v in records for w in v["windows"]]),axis=0).tolist() if records else None
        rows.append(dict(id=row["id"],qualified=passed,states=[v["event"]["state"] for v in records],worst_distances=distances))
    return rows


def build(path,expected_sha,output):
    if sha256(path) != expected_sha: raise ValueError("audited input anchor differs")
    result = json.loads(path.read_bytes())
    p,anchor = validate(result)
    output.mkdir(parents=True,exist_ok=False)
    plt.rcParams.update({"svg.hashsalt":STEM,"font.size":10})
    fig,(left,right) = plt.subplots(1,2,figsize=(13,7))
    fig.subplots_adjust(left=.08,right=.97,top=.80,bottom=.35,wspace=.32)
    complete = result["diagnostic"]["complete_qualified_matrix"]
    title = "The extra-return boundary at the primitive-cycle point" if complete else "The extra-return boundary is not yet matched to the cycle"
    fig.suptitle(title,fontsize=19,y=.97)
    qualified = sum(bool(r["geometry"]["analysis"] and r["geometry"]["analysis"]["qualified"]) for r in result["rows"])
    fig.text(.5,.91,f"EXP-498 | a = {p['anchor_parameters']['a']:.10f}, b = 0.2, c = 7.212 | {qualified}/8 boundary/turn matrices qualify",ha="center")
    cycles = anchor["result"]["cycle"]["profiles"]
    q = np.asarray(cycles[0]["metric"]["windows"][0]["event_states"]["historical"])
    for i in range(6):
        left.annotate("",xy=q[(i+1)%6,[0,2]],xytext=q[i,[0,2]],arrowprops=dict(arrowstyle="->",color="#aaaaaa",lw=.8))
        offset = [(-12,-14),(12,16),(8,8),(10,-4),(-10,8),(-10,-12)][i]
        left.annotate(str(i),q[i,[0,2]],xytext=offset,textcoords="offset points",fontsize=8,
                      arrowprops=dict(arrowstyle="-",lw=.5,color="#777777"))
    all_cycles = np.array([q for profile in cycles for w in profile["metric"]["windows"] for q in w["event_states"]["historical"]])
    left.scatter(all_cycles[:,0],all_cycles[:,2],c="#222222",s=35,marker="*",zorder=4)
    fold = np.array([v["fold_input"] for r in anchor["result"]["contact"]["rows"] for v in r["variants"]])
    left.scatter(fold[:,0],fold[:,2],facecolors="none",edgecolors="#138455",s=100,marker="D",lw=1.4,zorder=5)
    handles,plotted,missing = [],plot_rows(result),[]
    for i,(row,c) in enumerate(zip(result["rows"],p["candidates"],strict=True)):
        passed = bool(row["geometry"]["analysis"] and row["geometry"]["analysis"]["qualified"])
        label = c["parent_id"].split("--region-0--")[1].replace("depth-","h").replace("direction-","d").replace("candidate-","n").replace("--"," / ")
        if not passed: label += " (unqualified)"
        if row["parent_qualified"] is False: label += " [prior fail]"
        handles.append(Line2D([],[],color=COLORS[i],marker=MARKERS[i],ls="none",label=label,
            markerfacecolor=COLORS[i] if passed else "none"))
        records = [v for v in row["predecessors"] if v["eligible"]]
        if not records:
            missing.append(label)
            continue
        states = np.array([v["event"]["state"] for v in records])
        distances = np.max(np.array([w["state_distances"] for v in records for w in v["windows"]]),axis=0)
        left.scatter(states[:,0],states[:,2],edgecolors=COLORS[i],facecolors=COLORS[i] if passed else "none",marker=MARKERS[i],s=38,alpha=.7,zorder=3)
        if not np.all(distances > 0): raise ValueError("positive distance required for log display")
        right.plot(range(6),distances,color=COLORS[i],marker=MARKERS[i],ms=5,lw=.8,alpha=.7,
                   markerfacecolor=COLORS[i] if passed else "none")
    right.axhline(1e-4,color="#555555",ls="--",lw=1)
    right.set_yscale("log")
    left.set(xlabel="Historical section x",ylabel="Historical section z",title="Pre-grazing inputs and the six-return cycle")
    right.set(xlabel="Cycle event index (fixed common phase)",ylabel="Worst scaled full-state input distance",
              title="All cycle events; no nearest-event selection",xticks=list(range(6)))
    if missing: right.text(.02,.03,"No predecessor data: "+"; ".join(missing),transform=right.transAxes,fontsize=7,wrap=True)
    for ax in (left,right):
        ax.grid(alpha=.15)
        ax.spines[["top","right"]].set_visible(False)
    handles += [Line2D([],[],color="#222222",marker="*",ls="none",label="EXP-497 cycle hits"),
                Line2D([],[],color="#138455",marker="D",markerfacecolor="none",ls="none",label="EXP-497 measured fold input")]
    fig.legend(handles=handles,loc="lower center",bbox_to_anchor=(.5,.155),ncol=4,frameon=False,fontsize=8)
    fig.text(.07,.115,"h: history depth; d: initial direction; n: parent nomination. All realized doses and solvers contribute; failures remain visible.",fontsize=9)
    fig.text(.07,.078,"Grey arrows encode successive section hits, not spatial flow paths. Dashed line: the unchanged 1e−4 proximity reference.",fontsize=9)
    fig.text(.07,.04,"Finite-dose pre-grazing inputs are not exact critical coordinates. No C/D assignment, second smooth critical point or Jones arrow is verified.",fontsize=9)
    outputs = {}
    for extension in ("svg","png"):
        f = output/f"{STEM}.{extension}"
        fig.savefig(f,dpi=300,metadata={"Date":None} if extension == "svg" else None)
        if extension == "svg": f.write_text("\n".join(line.rstrip() for line in f.read_text().splitlines())+"\n")
        outputs[f.name] = dict(bytes=f.stat().st_size,sha256=sha256(f))
    plt.close(fig)
    receipt = output/f"{STEM}.receipt.json"
    write_json(receipt,dict(figure_id=STEM,title=title,description="Measured boundary predecessor inputs relative to the qualified cycle and right-fold input.",
        alt_text="Left: all realized pre-grazing section points, six cycle hits with next-hit connectors, and right-fold inputs. Right: each nomination's worst distance across realized methods, doses and windows to all six cycle indices; incomplete nominations stay labeled.",
        source_data_path=path.resolve().relative_to(run.ROOT).as_posix(),source_data_sha256=expected_sha,
        generator_sha256=sha256(Path(__file__)),audit_source_sha256=sha256(Path(audit.__file__)),
        source_commit=result["source_commit"],summary_sha256=result["summary_sha256"],derived_rows=plotted,
        outputs=outputs,matplotlib=matplotlib.__version__,symbolic_chains_verified=False,
        interval_semantics="Fixed finite-dose census, not confidence intervals or a rigorous flow enclosure.",
        accessibility="Distinct markers as well as colors; unqualified rows use open markers and labels."))
    write_json(output/f"{STEM}.index.json",dict(receipts={receipt.name:dict(bytes=receipt.stat().st_size,sha256=sha256(receipt))}))


def verify(output):
    name = f"{STEM}.receipt.json"
    index = json.loads((output/f"{STEM}.index.json").read_bytes())["receipts"]
    if set(index) != {name} or sha256(output/name) != index[name]["sha256"] or (output/name).stat().st_size != index[name]["bytes"]:
        raise ValueError("figure receipt differs")
    receipt = json.loads((output/name).read_bytes())
    if receipt["figure_id"] != STEM or set(receipt["outputs"]) != {f"{STEM}.svg",f"{STEM}.png"}:
        raise ValueError("complete figure output set required")
    source = run.ROOT/receipt["source_data_path"]
    if sha256(source) != receipt["source_data_sha256"] or sha256(Path(__file__)) != receipt["generator_sha256"]:
        raise ValueError("figure source differs")
    result = json.loads(source.read_bytes())
    validate(result)
    if (not run.polygon_audit.same_numeric(plot_rows(result),receipt["derived_rows"])
            or receipt["source_commit"] != result["source_commit"]
            or receipt["summary_sha256"] != result["summary_sha256"]
            or receipt["audit_source_sha256"] != result["audit_source_sha256"]
            or receipt["symbolic_chains_verified"] is not False):
        raise ValueError("plotted data or source identity differs")
    for name,binding in receipt["outputs"].items():
        if sha256(output/name) != binding["sha256"] or (output/name).stat().st_size != binding["bytes"]:
            raise ValueError("figure bytes differ")
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--result",type=Path)
    p.add_argument("--expected-sha256")
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--verify-only",action="store_true")
    a = p.parse_args()
    if a.verify_only: print(json.dumps(dict(verified=verify(a.output_dir))))
    else:
        if not a.result or not a.expected_sha256: p.error("result and SHA required")
        build(a.result,a.expected_sha256,a.output_dir)


if __name__ == "__main__": main()

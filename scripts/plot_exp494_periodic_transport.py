#!/usr/bin/env python3
"""All planned periodic-transport nodes, without hiding stopped arms."""
import argparse
import gzip
import json
from pathlib import Path

import numpy as np

from scripts import run_exp494_periodic_winding_transport as run
from scripts.audit_exp494_periodic_winding_transport import numeric_equal

FIGURE = "EXP-494-periodic-winding-transport"


def derive(saved):
    p = run.load_plan()
    if (saved["experiment_id"] != "EXP-494" or saved["source_commit"] != "4e5054955e8ddeb9db94e4702fe78d6232eda303"
            or [r["spec"] for r in saved["rows"]] != run.grid(p) or len(saved["saved_profiles"]) != 8
            or saved["symbolic_chains_verified"] is not False):
        raise ValueError("complete fixed periodic-transport study required")
    rows = []
    for r in saved["rows"]:
        if r["status"] not in ("qualified", "unqualified", "not-run", "interrupted"):
            raise ValueError("unknown node status")
        if r["pair"] is not None:
            if not numeric_equal(run.compare_profiles(r["profiles"],p),r["pair"]) or (r["status"] == "qualified") != r["pair"]["passed"]:
                raise ValueError("paired status differs")
        profiles = []
        for v in r["profiles"]:
            metric = v.get("metric")
            w = metric["windows"][0] if metric else None
            profiles.append(dict(method=v["method"], qualified=v["qualified"],
                period=v["correction"]["period_time"] if v.get("correction_gate",{}).get("passed") else None,
                winding=w["geometry"]["midpoint_enriched"]["cut_index"] if w else None,
                counts=w["counts"] if w else None,
                minimal_period=w["conditional_minimal_period"] if w else None))
        rows.append(dict(spec=r["spec"],status=r["status"],profiles=profiles))
    return rows


def plot(source, anchor, output):
    if run.sha256(source) != anchor:
        raise ValueError("source archive anchor differs")
    saved = json.loads(gzip.decompress(source.read_bytes()))
    rows = derive(saved)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Rectangle
    plt.rcParams.update({"font.size":10, "svg.hashsalt":FIGURE})
    output.mkdir(parents=True,exist_ok=False)
    fig = plt.figure(figsize=(12,10))
    gs = fig.add_gridspec(2,2,height_ratios=[1,1.45],left=.16,right=.97,top=.82,bottom=.16,hspace=.43,wspace=.25)
    colors = {"local-a025-c083":"#0072b2","local-a027-c083":"#a45190"}
    for ax,axis in zip([fig.add_subplot(gs[0,0]),fig.add_subplot(gs[0,1])],("a","c"),strict=True):
        for r in rows:
            if r["spec"]["arm"] != "base" and not r["spec"]["arm"].startswith(axis):
                continue
            for v in r["profiles"]:
                if v["period"] is None:
                    continue
                x,y = r["spec"]["parameters"][axis],v["period"]
                ax.scatter([x],[y],s=21 if v["method"] == "DOP853" else 44,
                    marker="o" if v["method"] == "DOP853" else "s",
                    facecolors=colors[r["spec"]["case"]] if v["method"] == "DOP853" else "none",
                    edgecolors=colors[r["spec"]["case"]],linewidths=.85,zorder=3)
                if r["status"] != "qualified":
                    ax.scatter([x],[y],s=30,marker="x",color="black",zorder=5)
        ax.set(xlabel=f"Parameter {axis}",ylabel="Candidate flow period T",
               title="Vary a at c = 7.212" if axis == "a" else "Vary c at fixed starting a")
        ax.ticklabel_format(style="plain",useOffset=False)
        ax.grid(alpha=.18)
        ax.spines[["top","right"]].set_visible(False)
    ax = fig.add_subplot(gs[1,:])
    new = [r for r in rows if r["spec"]["step"] > 0]
    arms = [(case,arm) for case in run.load_plan()["cases"] for arm in ("a-","a+","c-","c+")]
    labels = []
    for i,(case,arm) in enumerate(arms):
        labels.append(f"a0={'.21575' if case == arms[0][0] else '.21577'}  {arm}")
        for r in [r for r in new if r["spec"]["case"] == case and r["spec"]["arm"] == arm]:
            step = r["spec"]["step"]
            color = {"qualified":"#e1f0ec","unqualified":"#fbe1d8","not-run":"#f0f1f3","interrupted":"#faedc8"}[r["status"]]
            ax.add_patch(Rectangle((step-.47,i-.44),.94,.88,facecolor=color,edgecolor="white"))
            text = "/".join(str(v["winding"]) if v["winding"] is not None else "?" for v in r["profiles"])
            if r["status"] == "not-run":
                text = "not run"
            elif r["status"] != "qualified":
                text = "FAIL\n"+(text or "interrupted")
            ax.text(step,i,text,ha="center",va="center",fontsize=8,color="#253c53")
    ax.set(xlim=(.5,8.5),ylim=(7.55,-.55),xticks=range(1,9),yticks=range(8),yticklabels=labels,
        xlabel="Fixed step index  |  |delta a| = 0.0001 per step; |delta c| = 0.002 per step",
        title="Every planned parameter node: DOP853 / Radau projected winding")
    ax.tick_params(length=0,pad=8)
    ax.spines[:].set_visible(False)
    qualified = sum(r["status"] == "qualified" for r in new)
    attempted = sum(r["status"] != "not-run" for r in new)
    base = [r for r in rows if r["spec"]["step"] == 0]
    fig.suptitle("Following the corrected periodic orbits",fontsize=22,y=.98)
    fig.text(.5,.94,f"EXP-494  |  {qualified}/64 new nodes qualify; {attempted}/64 attempted  |  all eight arms retained",ha="center",fontsize=12)
    fig.text(.5,.908,f"Base pairs: {sum(r['status'] == 'qualified' for r in base)}/2 qualify. b = 0.2 throughout. No symbolic letters are assigned.",ha="center",fontsize=10)
    handles = [Line2D([],[],color=c,lw=3,label=f"Starting a = {'.21575' if i == 0 else '.21577'}") for i,c in enumerate(colors.values())]
    handles += [Line2D([],[],color="black",marker="o",ls="none",label="DOP853"),
        Line2D([],[],color="black",marker="s",markerfacecolor="none",ls="none",label="Radau"),
        Line2D([],[],color="black",marker="x",ls="none",label="Complete pair unqualified")]
    fig.legend(handles=handles,loc="lower center",bbox_to_anchor=(.5,.087),ncol=3,frameon=False,fontsize=9)
    fig.text(.08,.058,"Period panels include only corrected candidates passing their correction gate; the grid retains every failed/unrun node.",fontsize=9)
    fig.text(.08,.037,"Numbers are projected winding, not C/D words. Counts may change between nodes; no interpolated connection is claimed.",fontsize=9)
    fig.text(.08,.016,"A stopped arm does not establish absence of a periodic family. Numerical minimal-period checks are conditional, not proofs.",fontsize=9)
    outputs = {}
    for suffix in ("svg","pdf","png"):
        path = output/f"{FIGURE}.{suffix}"
        metadata = {"Date":None} if suffix == "svg" else ({"CreationDate":None,"ModDate":None} if suffix == "pdf" else None)
        fig.savefig(path,dpi=300,metadata=metadata)
        outputs[path.name] = dict(bytes=path.stat().st_size,sha256=run.sha256(path))
    plt.close(fig)
    receipt = dict(figure_id=FIGURE,title="Following the corrected periodic orbits",
        description="Candidate periods and the full continuation ledger, including failures and unrun successors.",
        alt_text="Two upper scatter panels compare candidate flow periods under a and c changes for both starting cycles and both solvers. The lower eight-by-eight grid lists each paired projected winding, explicitly marking failed and unrun nodes.",
        data_source=dict(path=source.resolve().relative_to(run.ROOT).as_posix(),sha256=anchor,
            fields=["rows.spec","rows.status","rows.profiles.correction","rows.profiles.metric.windows"],
            selection="All 66 nodes, including two bases; all 64 new parameter nodes appear in the grid.",
            exclusions="Uncorrected candidates have no period point, but remain explicitly present in the status grid.",
            transformation="Raw parameter and period coordinates; first-window integer winding; no fit or connecting lines.",aggregation="Counts only; no averaging of solvers."),
        derived_values=rows,interval_semantics="Discrete exploratory samples; no interval certificate or statistical uncertainty band.",
        provenance=dict(source_commit=saved["source_commit"],generator=Path(__file__).relative_to(run.ROOT).as_posix(),
            generator_sha256=run.sha256(Path(__file__)),matplotlib=matplotlib.__version__,outputs=outputs),
        accessibility="Solver shapes/fill, explicit FAIL/not-run text and labels supplement colors.",
        guards="Fixed complete grid, source identity, paired verdict replay and artifact hash verified before plotting.",
        claim_scope="No generating partition, word, insertion arrow, homoclinic proof or full-plane coverage.")
    path = output/f"{FIGURE}.receipt.json"
    run.write_json(path,receipt)
    run.write_json(output/f"{FIGURE}.index.json",dict(receipts={path.name:dict(bytes=path.stat().st_size,sha256=run.sha256(path))}))


def verify(output):
    index = json.loads((output/f"{FIGURE}.index.json").read_bytes())
    if set(index["receipts"]) != {f"{FIGURE}.receipt.json"}:
        raise ValueError("figure receipt set differs")
    for name, row in index["receipts"].items():
        if run.sha256(output/name) != row["sha256"] or (output/name).stat().st_size != row["bytes"]:
            raise ValueError("figure receipt changed")
    r = json.loads((output/f"{FIGURE}.receipt.json").read_bytes())
    source = run.ROOT/r["data_source"]["path"]
    if run.sha256(source) != r["data_source"]["sha256"] or run.sha256(run.ROOT/r["provenance"]["generator"]) != r["provenance"]["generator_sha256"]:
        raise ValueError("figure source/generator changed")
    if derive(json.loads(gzip.decompress(source.read_bytes()))) != r["derived_values"]:
        raise ValueError("plotted data differ")
    for name,v in r["provenance"]["outputs"].items():
        if run.sha256(output/name) != v["sha256"] or (output/name).stat().st_size != v["bytes"]:
            raise ValueError("figure output changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path)
    parser.add_argument("--sha256")
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--verify-only",action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        verify(args.output_dir)
    else:
        plot(args.source,args.sha256,args.output_dir)


if __name__ == "__main__":
    main()

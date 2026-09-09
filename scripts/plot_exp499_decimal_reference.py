#!/usr/bin/env python3
"""Complete-input accuracy figure derived only from an audited compact table."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
from butterfly._paired_startup import sha256, write_json
from scripts import run_exp499_decimal_reference as run
from scripts import audit_exp499_decimal_reference as audit

STEM = "EXP-499-decimal-event-reference"
SOURCE = "cef7b57ee1102b5bb6fa7350e22be2ae05de9240"


def validate(result):
    p,old = run.load()
    if (result.get("experiment_id") != "EXP-499" or result.get("passed") is not True
            or result.get("source_commit") != SOURCE or result.get("audit_source_sha256") != sha256(Path(audit.__file__))
            or result.get("ledger") != p["ledger"] or result.get("target_ivps") != 64
            or result.get("root_evaluations") != 480 or result.get("repairs_exp498") is not False
            or result.get("symbolic_chains_verified") is not False
            or [r["id"] for r in result.get("rows",[])] != [r["id"] for r in p["trials"]]):
        raise ValueError("complete audited fixed-source result required")
    for trial,row in zip(p["trials"],result["rows"],strict=True):
        if ([v["configuration"] for v in row["profiles"]] != [c["name"] for c in p["configurations"]]
                or any(len(v["events"]) != len(trial["boxes"]) for v in row["profiles"])
                or not audit.agree(audit.scalar_comparison(trial,row["profiles"],old,p),row["analysis"])):
            raise ValueError("saved complete reference comparison differs")
    if result["reference_qualified"] != all(r["analysis"]["reference_qualified"] for r in result["rows"]):
        raise ValueError("complete reference decision differs")
    return p,old


def values(result,p,old):
    table = []
    for trial,row in zip(p["trials"],result["rows"],strict=True):
        events = row["analysis"]["events"]
        parent = next(r for r in old["rows"] if r["id"] == trial["candidate_id"])
        methods = []
        for name in ("DOP853","Radau"):
            cells = [c for e in events for c in e["original_comparisons"] if c["method"] == name]
            methods.append(dict(name=name,state=max(c["state"] for c in cells),time=max(c["time"] for c in cells),
                within_original_thresholds=all(c["within_original_thresholds"] for c in cells)))
        table.append(dict(id=trial["id"],candidate_id=trial["candidate_id"],dose=trial["dose"],
            original_pair_passed=parent["boundary"]["analysis"]["paired_sides"][trial["side_index"]]["passed"],
            reference_qualified=row["analysis"]["reference_qualified"],
            reference_state=max(e["reference_error"]["state"] for e in events),
            reference_time=max(e["reference_error"]["time"] for e in events),methods=methods))
    return table


def build(path,expected_sha,output):
    if sha256(path) != expected_sha: raise ValueError("input hash differs")
    result = json.loads(path.read_bytes())
    p,old = validate(result)
    table = values(result,p,old)
    output.mkdir(parents=True,exist_ok=False)
    plt.rcParams.update({"svg.hashsalt":STEM,"font.size":10})
    fig,ax = plt.subplots(figsize=(13,7))
    fig.subplots_adjust(left=.10,right=.97,bottom=.29,top=.78)
    title = "Higher precision checks every nominated section crossing"
    fig.suptitle(title,fontsize=19,y=.97)
    fig.text(.5,.91,"EXP-499 | 32 realized inputs | 64 decimal trajectories | 480 root evaluations",ha="center")
    all_values = [r["reference_state"] for r in table]+[v["state"] for r in table for v in r["methods"]]
    if not all(np.isfinite(v) and v >= 0 for v in all_values): raise ValueError("finite nonnegative errors required")
    positive = [v for v in all_values if v > 0]
    floor = min(positive+[1e-9])/10
    series = [("DOP853 vs both references","#4477aa","o",[r["methods"][0]["state"] for r in table],
               [r["methods"][0]["within_original_thresholds"] for r in table]),
              ("Radau vs both references","#aa6633","^",[r["methods"][1]["state"] for r in table],
               [r["methods"][1]["within_original_thresholds"] for r in table]),
              ("40-digit vs 50-digit reference","#008477","D",[r["reference_state"] for r in table],
               [r["reference_qualified"] for r in table])]
    handles = []
    for name,color,marker,ys,qualified in series:
        displayed = [v if v > 0 else floor for v in ys]
        ax.plot(range(32),displayed,color=color,lw=.8,alpha=.6)
        for i,(v,passed) in enumerate(zip(displayed,qualified,strict=True)):
            ax.scatter(i,v,marker=marker,s=30,edgecolors=color,facecolors=color if passed else "none",zorder=4)
            if ys[i] == 0: ax.annotate("0",(i,v),xytext=(0,-10),textcoords="offset points",ha="center",fontsize=7)
        handles.append(Line2D([],[],color=color,marker=marker,lw=.8,label=name))
    for i,row in enumerate(table):
        if not row["original_pair_passed"]: ax.axvspan(i-.35,i+.35,color="#e6c293",alpha=.35,zorder=0)
    ax.axhline(1e-6,color="#333333",ls="--",lw=1)
    ax.axhline(1e-9,color="#777777",ls=":",lw=1)
    for i in range(8):
        if i: ax.axvline(i*4-.5,color="#aaaaaa",lw=.6,alpha=.5)
        ident = p["trials"][4*i]["candidate_id"]
        parts = ident.split("--")
        h,d,n = [next(v.split("-")[-1] for v in parts if v.startswith(key)) for key in ("depth-","direction-","candidate-")]
        ax.text(4*i+1.5,-.12,f"h{h} d{d} n{n}",transform=ax.get_xaxis_transform(),ha="center",fontsize=9)
    ax.set(yscale="log",xlim=(-.7,31.7),xticks=range(32),xticklabels=["-L","-S","+S","+L"]*8,
        ylabel="Worst scaled section-state disagreement")
    ax.tick_params(axis="x",labelsize=8)
    ax.set_xlabel("All four original displacements for each history / direction / nomination",labelpad=31)
    ax.grid(axis="y",alpha=.15)
    ax.spines[["top","right"]].set_visible(False)
    handles += [Patch(facecolor="#e6c293",alpha=.5,label="Original EXP-498 pair failed"),
        Line2D([],[],color="#333333",ls="--",label="Original state threshold: 1e-6"),
        Line2D([],[],color="#777777",ls=":",label="Reference state threshold: 1e-9")]
    fig.legend(handles=handles,loc="upper center",bbox_to_anchor=(.53,.875),ncol=3,frameon=False,fontsize=9)
    fig.text(.07,.13,"Each point is the maximum over every nominated event (and both references for the original solvers).",fontsize=9)
    fig.text(.07,.095,"Hollow markers fail a time or state comparison. L/S denote the larger/smaller dose; lines only guide the eye.",fontsize=9)
    fig.text(.07,.060,"Root boxes stop at 1e-25 time width: tiny paired differences are not absolute accuracy or a rigorous error bound.",fontsize=9)
    fig.text(.07,.025,"EXP-498 verdicts stay unchanged. No C/D assignment or Jones arrow is established."+(" Zero errors are labeled at the axis baseline." if any(v == 0 for v in all_values) else ""),fontsize=9)
    outputs = {}
    for extension in ("svg","pdf","png"):
        file = output/f"{STEM}.{extension}"
        metadata = {"Date":None} if extension == "svg" else ({"CreationDate":None,"ModDate":None} if extension == "pdf" else None)
        fig.savefig(file,dpi=300,metadata=metadata)
        if extension == "svg": file.write_text("\n".join(s.rstrip() for s in file.read_text().splitlines())+"\n")
        outputs[file.name] = dict(bytes=file.stat().st_size,sha256=sha256(file))
    plt.close(fig)
    receipt = output/f"{STEM}.receipt.json"
    write_json(receipt,dict(figure_id=STEM,title=title,description="All-input numerical accuracy comparison with both original failures retained.",
        alt_text="All 32 side inputs in eight groups: DOP853 and Radau disagreement from both decimal references, and disagreement between the 40- and 50-digit configurations. Original failed pairs are shaded; hollow markers retain failed criteria.",
        source_data_path=path.resolve().relative_to(run.ROOT).as_posix(),source_data_sha256=expected_sha,
        generator_sha256=sha256(Path(__file__)),audit_source_sha256=sha256(Path(audit.__file__)),
        source_commit=result["source_commit"],summary_sha256=result["summary_sha256"],derived_rows=table,outputs=outputs,
        interval_semantics="Complete fixed-input worst discrepancies, not confidence intervals or rigorous error enclosures.",
        zero_display="Exact zeros, if present, are labeled at min(positive errors,1e-9)/10; receipt values remain zero.",
        accessibility="Separate marker shapes and colors; hollow failed markers and labeled inherited-failure shading.",
        matplotlib=matplotlib.__version__,repairs_exp498=False,symbolic_chains_verified=False))
    write_json(output/f"{STEM}.index.json",dict(receipts={receipt.name:dict(bytes=receipt.stat().st_size,sha256=sha256(receipt))}))


def verify(output):
    name = f"{STEM}.receipt.json"
    index = json.loads((output/f"{STEM}.index.json").read_bytes())["receipts"]
    if set(index) != {name} or sha256(output/name) != index[name]["sha256"] or (output/name).stat().st_size != index[name]["bytes"]:
        raise ValueError("figure receipt differs")
    receipt = json.loads((output/name).read_bytes())
    path = run.ROOT/receipt["source_data_path"]
    if receipt["figure_id"] != STEM or sha256(path) != receipt["source_data_sha256"] or sha256(Path(__file__)) != receipt["generator_sha256"]:
        raise ValueError("figure source differs")
    result = json.loads(path.read_bytes())
    p,old = validate(result)
    if (not audit.agree(values(result,p,old),receipt["derived_rows"]) or receipt["source_commit"] != result["source_commit"]
            or receipt["summary_sha256"] != result["summary_sha256"] or receipt["audit_source_sha256"] != result["audit_source_sha256"]
            or receipt["repairs_exp498"] is not False or receipt["symbolic_chains_verified"] is not False
            or set(receipt["outputs"]) != {f"{STEM}.{e}" for e in ("svg","pdf","png")}):
        raise ValueError("complete plotted data/source differs")
    for name,binding in receipt["outputs"].items():
        if sha256(output/name) != binding["sha256"] or (output/name).stat().st_size != binding["bytes"]:
            raise ValueError("figure output differs")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result",type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--verify-only",action="store_true")
    args = parser.parse_args()
    if args.verify_only: print(json.dumps(dict(verified=verify(args.output_dir))))
    else:
        if not args.result or not args.expected_sha256: parser.error("result and hash required")
        build(args.result,args.expected_sha256,args.output_dir)


if __name__ == "__main__": main()

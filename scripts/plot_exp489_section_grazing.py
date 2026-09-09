#!/usr/bin/env python3
"""Receipt-derived section-grazing unfolding, including every side and solver."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
import numpy as np
from butterfly._paired_startup import sha256,write_json

FIGURE = "EXP-489-section-grazing"


def derive(result):
    if result["experiment_id"] != "EXP-489" or result["status"] != "completed-audited" or [c["case"] for c in result["cases"]] != ["local-a025-c083","local-a027-c083"]:
        raise ValueError("complete audited two-case result required")
    data = []
    for case in result["cases"]:
        if [s["method"] for s in case["solvers"]] != ["DOP853","Radau"]:
            raise ValueError("solver matrix incomplete")
        for s in case["solvers"]:
            entry = dict(case=case["case"],case_passed=case["passed"],method=s["method"],passed=s["passed"],
                         root=s.get("root"),square_root_ratio=s["square_root_ratio"],sides=[])
            if "root" in s:
                if [v["dose"] for v in s["sides"]] != [-1e-6,-1e-7,1e-7,1e-6]:
                    raise ValueError("four-side matrix incomplete")
                for v in s["sides"]:
                    entry["sides"].append(dict(dose=v["dose"],dose_micro=v["dose"]*1e6,passed=v["passed"],
                        expected_roots=v["expected_roots"],observed_roots=len(v["local_roots"]),
                        crossing_offsets_milliunits=[(e["time"]-s["root"]["time"])*1000 for e in v["local_roots"]],
                        accepted=[e["accepted"] for e in v["local_roots"]],
                        accepted_prefix_count=v["accepted_prefix_count"],
                        separation_milliunits=None if v["separation"] is None else 1000*v["separation"],
                        next_accepted_time=None if v["next_accepted"] is None else v["next_accepted"]["time"]))
            elif s["passed"]:
                raise ValueError("passing solver missing root")
            data.append(entry)
    return data


def plot(source,anchor,output):
    if sha256(source) != anchor:
        raise ValueError("source receipt changed")
    result = json.loads(source.read_bytes())
    data = derive(result)
    parameter_path = ROOT/"docs/experiments/receipts/EXP-487-section-census-result.json"
    parameter_source = dict(path=parameter_path.relative_to(ROOT).as_posix(),sha256="eb7f1c9765fe42a1c9fd06d9096e9cdfbf68084dde77969c48a866cd94005938")
    if sha256(parameter_path) != parameter_source["sha256"]:
        raise ValueError("parameter source changed")
    parameters = {s["case"]:s["parameters"] for s in json.loads(parameter_path.read_bytes())["selection"]}
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"svg.hashsalt":FIGURE,"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
    output.mkdir(parents=True,exist_ok=False)
    fig,axes = plt.subplots(1,2,figsize=(11.5,6.7))
    fig.subplots_adjust(left=.08,right=.98,bottom=.33,top=.74,wspace=.3)
    predictions = []
    for ax,case in zip(axes,result["cases"],strict=True):
        members = [d for d in data if d["case"] == case["case"]]
        ax.axhline(0,color=".82",lw=.7)
        ax.axvline(0,color=".65",lw=.8)
        for entry,color,marker,ls in zip(members,["#0072b2","#d55e00"],["o","s"],["--",":"],strict=True):
            if entry["root"] is None:
                ax.text(.03,.85 if entry["method"]=="DOP853" else .75,entry["method"]+": no qualified root",transform=ax.transAxes,color=color)
                continue
            j = np.asarray(entry["root"]["jacobian"])
            sign = -np.sign(j[0,0]*j[1,1])
            dose = sign*np.linspace(0,1.06e-6,161)
            offsets = np.sqrt(np.maximum(0,-2*j[0,0]*dose/j[1,1]))*1000
            for branch in (-1,1):
                ax.plot(dose*1e6,branch*offsets,color=color,ls=ls,lw=1,alpha=.8)
            predictions.append(dict(case=entry["case"],method=entry["method"],dose=dose.tolist(),positive_time_offset_milliunits=offsets.tolist()))
            for side in entry["sides"]:
                for t,accepted in zip(side["crossing_offsets_milliunits"],side["accepted"],strict=True):
                    ax.scatter(side["dose_micro"],t,color=color,marker=marker,s=48,
                               facecolors=color if accepted else "none",zorder=5)
                if not side["observed_roots"]:
                    # Vertical placement is an annotation, not a time observation.
                    ax.plot(side["dose_micro"],.91 if entry["method"]=="DOP853" else .84,marker="x",color=color,
                            transform=ax.get_xaxis_transform(),ms=7,linestyle="none")
            ax.scatter(0,0,marker="*",s=75,color="black",zorder=6)
        ratios = "; ".join(d["method"]+": "+("unresolved" if d["square_root_ratio"] is None else f"{d['square_root_ratio']:.5f}") for d in members)
        ax.set(title=f"a = {parameters[case['case']]['a']:.5f}"+"\n"+("Grazing checks pass" if case["passed"] else "Unresolved: retain failures"),
               xlabel=r"Displacement from each solver's tangency, $\epsilon$ ($10^{-6}$)",
               ylabel=r"Crossing-time offset ($10^{-3}$ model-time units)",xlim=(-1.12,1.12))
        ax.grid(alpha=.14)
        ax.text(.5,-.29,"10x displacement: separation ratio\n"+ratios+"\nSquare-root prediction: 3.16228",transform=ax.transAxes,ha="center",va="top",fontsize=8.5)
    fig.suptitle("Why the selected fifth return can jump",fontsize=19,y=.97)
    fig.text(.5,.89,"Two local tangency witnesses: crossing-pair birth/death, not a new symbolic-chain verification",ha="center",fontsize=10)
    fig.text(.5,.84,"b = 0.2, c = 7.212. Star: tangency, not an accepted transverse return.",ha="center",fontsize=9)
    handles=[Line2D([],[],marker="o",color="#0072b2",lw=0,label="DOP853"),
             Line2D([],[],marker="s",color="#d55e00",lw=0,label="Radau"),
             Line2D([],[],marker="o",color=".25",lw=0,label="Filled: accepted crossing"),
             Line2D([],[],marker="o",markerfacecolor="none",color=".25",lw=0,label="Open: other orientation"),
             Line2D([],[],marker="x",color=".25",lw=0,label="Top x: no local crossing"),
             Line2D([],[],color=".25",ls="--",lw=1,label="Local quadratic prediction")]
    fig.legend(handles=handles,loc="lower center",ncol=3,fontsize=8.5,frameon=False,bbox_to_anchor=(.5,.005))
    outputs = {}
    for suffix in ("svg","pdf","png"):
        path = output/f"{FIGURE}.{suffix}"
        metadata = {"Date":None} if suffix=="svg" else ({"CreationDate":None,"ModDate":None} if suffix=="pdf" else None)
        fig.savefig(path,dpi=300,metadata=metadata)
        if suffix == "svg":
            path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())+"\n")
        outputs[path.name] = dict(sha256=sha256(path),bytes=path.stat().st_size)
    plt.close(fig)
    generator = dict(path="scripts/plot_exp489_section_grazing.py",sha256=sha256(Path(__file__)),
                     python=sys.version,numpy=np.__version__,matplotlib=matplotlib.__version__)
    source_meta = dict(artifact=source.resolve().relative_to(ROOT).as_posix(),sha256=anchor,
        fields=["cases.passed","cases.solvers.root","cases.solvers.sides","cases.solvers.square_root_ratio"],
        selection="Both cases, both solvers, all four signed displacements; all local roots and explicit no-root sides.",
        exclusions="None. Failed/no-root shootings remain explicitly labeled, not dropped.",aggregation="No averages or pooling.",
        transformation="Displacement times 1e6; dimensionless model-time offset from that solver's own tangency times 1000, not physical milliseconds. Root agreement remains separately reported in source. Dashed curves use +/-sqrt(-2*h_delta*epsilon/h_tt), not interpolated observations.")
    audit = dict(path="scripts/run_exp489_section_grazing.py",sha256=sha256(ROOT/"scripts/run_exp489_section_grazing.py"))
    receipt = dict(figure_id=FIGURE,title="Why the selected fifth return can jump",
        description="Measured crossing pairs unfold from two numerical section tangencies; both sides and both solvers retained.",
        alt_text="Two panels plot time offsets of both plane crossings against signed displacement from a numerical tangency. Filled circles and squares mark the accepted negative-oriented crossing, open shapes the other crossing. Top crosses indicate tested displacements with no crossing, not time observations. The two cases can unfold on opposite displacement sides. Dashed curves are local quadratic predictions; stars denote tangencies that are not accepted transverse returns. Titles retain qualification status and text reports each solver's pair-separation ratio.",
        data_source=source_meta,parameter_source=parameter_source,provenance=dict(study_id="EXP-489",run_source_commit=result["source_commit"],
            completed_summary_sha256=result["summary_sha256"],audit=audit,generator=generator,outputs=outputs),
        generator=generator,audit=audit,outputs=outputs,derived_values=data,quadratic_predictions=predictions,
        interval_semantics="No error bars, confidence intervals or rigorous bounds. Curves are local Taylor predictions, not certified return-map branches.",
        accessibility="Solver shapes plus color; fill distinguishes crossing orientation; separate annotation row for absent events.",
        raster_dpi=300,guards=["Source SHA-256","audited status","complete cases/solvers/doses","no outcome filtering","source/code/output hash index"],
        claim_boundary=result["claim_boundary"])
    path = output/f"{FIGURE}.receipt.json"
    write_json(path,receipt)
    write_json(output/f"{FIGURE}.index.json",dict(receipts={path.name:dict(sha256=sha256(path),bytes=path.stat().st_size)}))


def verify(output):
    index = json.loads((output/f"{FIGURE}.index.json").read_bytes())
    if set(index["receipts"]) != {f"{FIGURE}.receipt.json"}:
        raise ValueError("receipt index differs")
    name,anchor = next(iter(index["receipts"].items()))
    if sha256(output/name) != anchor["sha256"] or (output/name).stat().st_size != anchor["bytes"]:
        raise ValueError("receipt bytes differ")
    r = json.loads((output/name).read_bytes())
    for item in (dict(path=r["data_source"]["artifact"],sha256=r["data_source"]["sha256"]),r["parameter_source"],r["generator"],r["audit"]):
        path = (ROOT/item["path"]).resolve()
        path.relative_to(ROOT)
        if sha256(path) != item["sha256"]:
            raise ValueError("source/code changed")
    if derive(json.loads((ROOT/r["data_source"]["artifact"]).read_bytes())) != r["derived_values"]:
        raise ValueError("derived observations differ")
    if set(r["outputs"]) != {f"{FIGURE}.{s}" for s in ("svg","pdf","png")}:
        raise ValueError("output set differs")
    for name,anchor in r["outputs"].items():
        if sha256(output/name) != anchor["sha256"] or (output/name).stat().st_size != anchor["bytes"]:
            raise ValueError("output bytes differ")
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--receipt",type=Path)
    p.add_argument("--expected-sha256")
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--verify-only",action="store_true")
    args = p.parse_args()
    if not args.verify_only:
        plot(args.receipt,args.expected_sha256,args.output_dir)
    verify(args.output_dir)
    print("Figure source, derived values, code, receipt and SVG/PDF/PNG hashes verified")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Audited dependent localization points; no interpolation or symbolic labels."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from butterfly._paired_startup import sha256,write_json
from scripts import run_exp497_contact_localization as run
from scripts import audit_exp497_contact_localization as audit

STEM = "EXP-497-contact-localization"
COLORS = ["#007f86","#4698cc","#ad593d","#93649c"]


def validate(result):
    p,source = run.load()
    if (not result["passed"] or result["experiment_id"] != "EXP-497"
            or result["parent_ledger"] != source["data"]["ledger"]
            or result["audit_source_sha256"] != sha256(Path(audit.__file__))):
        raise ValueError("audited source and full ledger required")
    def saved(spec,candidates,seed):
        rows = [r for r in result["rows"] if r["case"] == spec["case"] and r["level"] == spec["level"]]
        if len(rows) != 1 or rows[0]["spec"] != spec or rows[0]["candidates"] != candidates or rows[0]["seed"] != seed:
            raise ValueError("adaptive data/phase seed differs")
        r = rows[0]["result"]
        if r["contact"] is not None and not audit.periodic_audit.numeric_equal(
                audit.scalar_contact(r["folds"],r["cycle"]),r["contact"]):
            raise ValueError("independent scalar figure data differ")
        return r
    if run.campaign(p,source,saved) != result["rows"]:
        raise ValueError("complete adaptive/blocked figure ledger differs")
    return p,source


def build(path,anchor,output):
    if sha256(path) != anchor: raise ValueError("figure input anchor differs")
    result = json.loads(path.read_bytes())
    p,source = validate(result)
    rows = [r for r in result["rows"] if r["case"] == p["cases"][0]]
    output.mkdir(parents=True,exist_ok=False)
    plt.rcParams.update({"svg.hashsalt":STEM,"font.size":10})
    fig,(left,right) = plt.subplots(1,2,figsize=(12,6))
    fig.subplots_adjust(left=.08,right=.97,top=.79,bottom=.28,wspace=.31)
    success = any(r["status"] == "proximate" for r in rows)
    title = "A primitive cycle reaches measured fold proximity" if success else "Bounded contact localization remains unresolved"
    fig.suptitle(title,fontsize=19,y=.97)
    fig.text(.5,.90,"EXP-497 | b = 0.2, c = 7.212 | first case only; second case retains its failed endpoint gate",ha="center",fontsize=10)
    ends = run.initial_endpoints(p["cases"][0],source)
    for e in ends:
        left.scatter([e["a"]],[e["mean_residual"]],color="#777777",marker="s",s=45,zorder=5)
    left.axhline(0,color="#555555",lw=1)
    ratios = []
    for row in rows:
        level = row["level"]
        if "result" not in row or row["result"]["contact"] is None:
            right.text(level,.07,row["status"].replace("-","\n"),transform=right.get_xaxis_transform(),
                       ha="center",va="bottom",fontsize=8,color="#777777")
            continue
        contact = row["result"]["contact"]
        a = row["spec"]["parameters"]["a"]
        for i,curve in enumerate(contact["rows"]):
            for v in curve["variants"]:
                marker = "o" if v["method"] == "DOP853" else "s"
                left.scatter([a],[v["signed_residual"]],color=COLORS[i],marker=marker,s=30,alpha=.8)
                value = v["pair_state_distance"][3]/1e-4
                if value <= 0: raise ValueError("positive distance required for log display")
                ratios.append(value)
                right.scatter([level+(i-1.5)*.07],[value],color=COLORS[i],marker=marker,s=28,alpha=.8)
            if not curve["variants"]:
                right.text(level+(i-1.5)*.07,.07,"unresolved fold",rotation=90,fontsize=7,
                           transform=right.get_xaxis_transform(),color=COLORS[i])
        left.annotate(str(level),(a,contact["mean_residual"] or 0),xytext=(5,7),textcoords="offset points",fontsize=9)
    left.set(xlabel="a (computed parameter values only)",ylabel="Signed event-3 input-x residual / 15",
             title="Endpoint lead and new localization points")
    left.ticklabel_format(axis="x",style="plain",useOffset=False)
    left.tick_params(axis="x",labelrotation=20)
    right.axhline(1,color="#333333",ls="--",lw=1.2)
    right.set_yscale("log")
    right.set(xlim=(.5,3.5),xticks=[1,2,3],xlabel="Prospective refinement level",
              ylabel="Full-state event-3 pair mismatch / 1e−4",
              title="All four representations, solvers and windows")
    if ratios: right.set_ylim(min(.2,min(ratios)*.7),max(2,max(ratios)*1.5))
    for ax in (left,right):
        ax.grid(alpha=.16)
        ax.spines[["top","right"]].set_visible(False)
    from matplotlib.lines import Line2D
    handles = [Line2D([],[],color=COLORS[i],marker="o",ls="none",label=f"depth {4 if i<2 else 8} / direction {i%2}") for i in range(4)]
    fig.legend(handles=handles,loc="lower center",bbox_to_anchor=(.5,.145),ncol=4,frameon=False,fontsize=9)
    fig.text(.07,.11,"Grey squares: inherited endpoint means. New points are dependent refinements, not independent replications.",fontsize=9)
    fig.text(.07,.075,"Dashed line: the unchanged full-state proximity limit. Both input and its correct next return must match at event 3.",fontsize=9)
    fig.text(.07,.04,"All six case/level ledger entries are retained. Proximity is not exact criticality, C/D, a second critical point or a Jones arrow.",fontsize=9)
    outputs = {}
    for extension in ("svg","png"):
        file = output/f"{STEM}.{extension}"
        fig.savefig(file,dpi=300,metadata={"Date":None} if extension == "svg" else None)
        if extension == "svg": file.write_text("\n".join(s.rstrip() for s in file.read_text().splitlines())+"\n")
        outputs[file.name] = dict(bytes=file.stat().st_size,sha256=sha256(file))
    plt.close(fig)
    receipt = output/f"{STEM}.receipt.json"
    write_json(receipt,dict(experiment_id="EXP-497",title=title,source_data_path=path.resolve().relative_to(run.ROOT).as_posix(),
        source_data_sha256=anchor,generator_sha256=sha256(Path(__file__)),audit_source_sha256=sha256(Path(audit.__file__)),
        derived_rows=result["rows"],source_commit=result["source_commit"],summary_sha256=result["summary_sha256"],
        primary_event=3,primary_radius=1e-4,outputs=outputs,matplotlib=matplotlib.__version__,
        interval_semantics="All measured solver/window observations, not confidence intervals; no connecting parameter curve.",
        alt_text="Left: inherited endpoint means and all measured signed residuals at each new parameter. Right: all four representations, both solvers and windows relative to the full-state threshold, with unrun or unresolved levels labeled.",
        symbolic_chains_verified=False,exact_contact_verified=False))
    write_json(output/f"{STEM}.index.json",dict(receipts={receipt.name:dict(bytes=receipt.stat().st_size,sha256=sha256(receipt))}))


def verify(output):
    name = f"{STEM}.receipt.json"
    expected = json.loads((output/f"{STEM}.index.json").read_bytes())["receipts"]
    if set(expected) != {name} or sha256(output/name) != expected[name]["sha256"] or (output/name).stat().st_size != expected[name]["bytes"]:
        raise ValueError("figure receipt differs")
    r = json.loads((output/name).read_bytes())
    source = run.ROOT/r["source_data_path"]
    if sha256(source) != r["source_data_sha256"] or sha256(Path(__file__)) != r["generator_sha256"]:
        raise ValueError("figure source differs")
    result = json.loads(source.read_bytes())
    validate(result)
    if result["rows"] != r["derived_rows"]: raise ValueError("plotted data drift")
    for name,expected in r["outputs"].items():
        if sha256(output/name) != expected["sha256"] or (output/name).stat().st_size != expected["bytes"]:
            raise ValueError("figure bytes differ")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result",type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--verify-only",action="store_true")
    a = parser.parse_args()
    if a.verify_only: print(json.dumps(dict(verified=verify(a.output_dir))))
    else:
        if not a.result or not a.expected_sha256: parser.error("build needs result and SHA")
        build(a.result,a.expected_sha256,a.output_dir)


if __name__ == "__main__":
    main()

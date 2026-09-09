#!/usr/bin/env python3
"""Complete receipt-derived EXP-490 outcome matrix, with no outcome filtering."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from butterfly._paired_startup import sha256,write_json

FIGURE = "EXP-490-direct-folds"
TABLE = ROOT/"experiments/manifests/EXP-490-candidates.json"
TABLE_SHA = "f7ef9d69bad22cd0ce8ca3c112e4c4d2c420ac247c0d3187359a33cc71329fea"


def derive(result):
    if result["experiment_id"] != "EXP-490" or result["status"] != "completed-audited" or sha256(TABLE) != TABLE_SHA:
        raise ValueError("audited result and frozen complete input table required")
    candidates = json.loads(TABLE.read_bytes())
    if [r["id"] for r in result["candidates"]] != [c["id"] for c in candidates]:
        raise ValueError("complete candidate matrix required")
    data = []
    for row,c in zip(result["candidates"],candidates,strict=True):
        if [s["method"] for s in row["solvers"]] != ["DOP853","Radau"]:
            raise ValueError("both solvers required")
        statuses = []
        for s in row["solvers"]:
            if s["qualified"]:
                code = "Q"
            elif "checks" in s:
                code = "F"
            elif "observations" in s:
                code = "E"
            else:
                code = "N"
            statuses.append(dict(method=s["method"],code=code,reason=s.get("reason"),checks=s.get("checks")))
        if row["qualified"] and any(s["code"] != "Q" for s in statuses):
            raise ValueError("paired qualification conflicts with solver outcomes")
        data.append(dict(id=c["id"],case=c["case"],a=c["parameters"]["a"],region=c["region"],
            depth=c["count"]-1,direction=int(c["family_id"].split("--direction-")[-1]),
            ordinal=int(c["id"].split("--candidate-")[-1])+1,solvers=statuses,
            paired="Q" if row["qualified"] else "U",in_region=row["qualified_in_region"],
            input_x=[s["observations"][1]["image_state"][0] for s in row["solvers"]] if row["qualified"] else None))
    return data


def plot(source,anchor,output):
    if sha256(source) != anchor:
        raise ValueError("source changed")
    result = json.loads(source.read_bytes())
    data = derive(result)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    plt.rcParams.update({"svg.hashsalt":FIGURE,"font.size":10})
    output.mkdir(parents=True,exist_ok=False)
    fig,axes = plt.subplots(1,2,figsize=(12,9))
    fig.subplots_adjust(left=.025,right=.975,top=.79,bottom=.19,wspace=.08)
    colors = dict(Q="#0072b2",N="#737373",E="#d55e00",F="#8b519d",U="#eeeeee")
    for ax,case in zip(axes,("local-a025-c083","local-a027-c083"),strict=True):
        rows = [d for d in data if d["case"] == case]
        ax.set(xlim=(0,10),ylim=(14.8,-1.8))
        ax.axis("off")
        ax.text(5,-1.3,f"a = {rows[0]['a']:.5f}",ha="center",weight="bold",fontsize=13)
        for x,label in ((.1,"Region / depth / direction / candidate"),(5.7,"DOP"),(6.7,"Radau"),(7.7,"Both"),(9.,"Fold input x")):
            ax.text(x,-.5,label,ha="left" if x==.1 else "center",fontsize=8)
        for i,d in enumerate(rows):
            if i%2==0:
                ax.add_patch(Rectangle((0,i-.4),10,.85,facecolor="#f3f6f8",edgecolor="none"))
            name = f"{'Left' if d['region']==0 else 'Right'} / {d['depth']} / {d['direction']} / {d['ordinal']}"
            ax.text(.1,i,name,va="center",fontsize=9.5)
            for x,code in zip((5.7,6.7,7.7),[s["code"] for s in d["solvers"]]+[d["paired"]],strict=True):
                ax.add_patch(Rectangle((x-.3,i-.3),.6,.6,facecolor=colors[code],edgecolor="white",linewidth=.5))
                ax.text(x,i,code,ha="center",va="center",color="black" if code=="U" else "white",weight="bold",fontsize=9)
            value = "--" if d["input_x"] is None else f"{d['input_x'][0]:.6f}"+("*" if not d["in_region"] else "")
            ax.text(9.,i,value,ha="center",va="center",fontsize=8.5)
        count = sum(d["paired"]=="Q" for d in rows)
        ax.text(5,14.5,f"{count}/{len(rows)} candidates qualify in both solvers",ha="center",fontsize=10)
    total = sum(d["paired"]=="Q" for d in data)
    fig.suptitle("Direct fold test: all 26 candidate intervals",fontsize=20,y=.965)
    fig.text(.5,.913,f"{total}/26 pass all paired checks. All 16 finite-return curve families retained.",ha="center",fontsize=12)
    fig.text(.5,.865,"b = 0.2, c = 7.212 | Unresolved does not mean absent | No symbolic letters assigned",ha="center",fontsize=10)
    fig.text(.055,.135,"Q  Qualified     N  No qualified shooting/census     E  Event or input projection invalid",fontsize=10)
    fig.text(.055,.103,"F  A fold check failed     U  Paired result unresolved     *  Outside the prior observed x region",fontsize=10)
    fig.text(.055,.059,"Input x is the DOP853 value only when both solvers qualify; both unrounded values are retained in the receipt.\nDepth is the number of prior returns; directions 0 and 1 are the two frozen initial tangents. Candidate numbers are local to each family.",fontsize=8.5,linespacing=1.5)
    outputs = {}
    for suffix in ("svg","pdf","png"):
        path = output/f"{FIGURE}.{suffix}"
        metadata = {"Date":None} if suffix=="svg" else ({"CreationDate":None,"ModDate":None} if suffix=="pdf" else None)
        fig.savefig(path,dpi=300,metadata=metadata)
        if suffix == "svg":
            path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())+"\n")
        outputs[path.name] = dict(sha256=sha256(path),bytes=path.stat().st_size)
    plt.close(fig)
    generator = dict(path="scripts/plot_exp490_direct_folds.py",sha256=sha256(Path(__file__)),python=sys.version,matplotlib=matplotlib.__version__)
    receipt = dict(figure_id=FIGURE,title="Direct fold test: all 26 candidate intervals",
        alt_text="Two panels retain every candidate at each of two parameter values. Each row shows the DOP853, Radau and paired verdict, with letters as well as colors. Unresolved candidates remain visible. Input x is printed only for paired-qualified folds; this is an outcome table, not a reconstructed curve or proof that unresolved intervals lack folds.",
        source=dict(path=source.resolve().relative_to(ROOT).as_posix(),sha256=anchor,fields=["candidates.id","candidates.solvers","candidates.qualified","candidates.qualified_in_region"],selection="All 26 candidates, all 16 families and both solvers in frozen order.",exclusions="None; unavailable qualified locations are explicitly --.",aggregation="No pooling; paired verdict is the frozen conjunction, not a vote.",transformation="Categorical solver verdicts Q/N/E/F and paired Q/U. Successful input x printed to six decimals from DOP853; both exact solver values retained."),
        input_table=dict(path=TABLE.relative_to(ROOT).as_posix(),sha256=TABLE_SHA),
        audit=dict(path="scripts/audit_exp490_direct_folds.py",sha256=sha256(ROOT/"scripts/audit_exp490_direct_folds.py")),
        generator=generator,outputs=outputs,derived_values=data,run_source_commit=result["source_commit"],completed_summary_sha256=result["summary_sha256"],
        interval_semantics="Candidate intervals are original search boxes, not confidence intervals. No error bars or rigorous bounds.",accessibility="Letters duplicate color; explicit text for unavailable locations.",raster_dpi=300,claim_boundary=result["claim_boundary"])
    path = output/f"{FIGURE}.receipt.json"
    write_json(path,receipt)
    write_json(output/f"{FIGURE}.index.json",dict(receipts={path.name:dict(sha256=sha256(path),bytes=path.stat().st_size)}))


def verify(output):
    index = json.loads((output/f"{FIGURE}.index.json").read_bytes())
    if set(index["receipts"]) != {f"{FIGURE}.receipt.json"}:
        raise ValueError("receipt set differs")
    for name,anchor in index["receipts"].items():
        if sha256(output/name) != anchor["sha256"] or (output/name).stat().st_size != anchor["bytes"]:
            raise ValueError("receipt changed")
    r = json.loads((output/f"{FIGURE}.receipt.json").read_bytes())
    for item in (r["source"],r["input_table"],r["audit"],r["generator"]):
        path = (ROOT/item["path"]).resolve()
        path.relative_to(ROOT)
        if sha256(path) != item["sha256"]:
            raise ValueError("source/code changed")
    if derive(json.loads((ROOT/r["source"]["path"]).read_bytes())) != r["derived_values"]:
        raise ValueError("derived values differ")
    if set(r["outputs"]) != {f"{FIGURE}.{s}" for s in ("svg","pdf","png")}:
        raise ValueError("output set differs")
    for name,anchor in r["outputs"].items():
        if sha256(output/name) != anchor["sha256"] or (output/name).stat().st_size != anchor["bytes"]:
            raise ValueError("output changed")
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--receipt",type=Path)
    p.add_argument("--expected-sha256")
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--verify-only",action="store_true")
    a = p.parse_args()
    if not a.verify_only:
        plot(a.receipt,a.expected_sha256,a.output_dir)
    verify(a.output_dir)
    print("Complete outcome matrix, source/code/receipt/output hashes verified")


if __name__ == "__main__":
    main()

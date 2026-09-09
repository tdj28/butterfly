#!/usr/bin/env python3
"""Audited two-contact residuals, with a full target view and a measured-point zoom."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
from butterfly._paired_startup import sha256,write_json
from scripts import verify_exp503_public_contact as public

ROOT = Path(__file__).resolve().parents[1]
FIGURE = "EXP-503-joint-contact-residuals"
TITLE = "Testing both contacts together"


def derive(result):
    p = public.run.load()
    points = [dict(id="anchor",axis="anchor",scale=1.,sign=0,qualified=True,vectors=p["base_vectors"],parameters=p["anchor"])]
    for row in result["rows"]+([result["proposal"]] if result["proposal"] is not None else []):
        s = row["spec"]
        points.append(dict(id=s["id"],axis=s.get("axis","proposal"),scale=s.get("scale",1.),
            sign=s.get("sign",0),qualified=row["qualified"],vectors=row["vectors"],parameters=s["parameters"]))
    output = []
    for point in points:
        vectors = point.pop("vectors")
        complete = len(vectors) == 256 and len({tuple(v["key"]) for v in vectors}) == 256
        values = np.asarray([r["value"] for r in vectors]) if complete else None
        if complete and (values.shape != (256,2) or not np.isfinite(values).all()):
            raise ValueError("finite complete two-residual matrix required")
        output.append(dict(point,plotted=complete,variants=len(vectors),
            mean=None if values is None else np.mean(values,axis=0).tolist(),
            minimum=None if values is None else np.min(values,axis=0).tolist(),
            maximum=None if values is None else np.max(values,axis=0).tolist()))
    if len(output) != 9+int(result["proposal"] is not None):
        raise ValueError("anchor and complete target ledger required")
    return output


def draw(data,title,subtitle):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Rectangle
    plt.rcParams.update({"svg.hashsalt":FIGURE,"font.size":10,"axes.formatter.useoffset":False})
    fig,axes = plt.subplots(1,2,figsize=(11,6.8))
    fig.subplots_adjust(left=.08,right=.98,bottom=.32,top=.80,wspace=.30)
    styles = dict(a=("#0072b2","D"),c=("#d55e00","s"),anchor=("#222222","*"),proposal=("#00805a","P"))
    plotted = [r for r in data if r["plotted"]]
    cloud = np.array([np.array(r[k])*1000 for r in plotted for k in ("minimum","maximum")])
    for index,ax in enumerate(axes):
        for row in plotted:
            x,y = np.array(row["mean"])*1000
            low,high = [np.array(row[k])*1000 for k in ("minimum","maximum")]
            color,marker = styles[row["axis"]]
            ax.errorbar(x,y,xerr=[[max(0.,x-low[0])],[max(0.,high[0]-x)]],
                yerr=[[max(0.,y-low[1])],[max(0.,high[1]-y)]],fmt="none",color=color,lw=.9,capsize=2,zorder=2)
            ax.scatter([x],[y],marker=marker,s=130 if row["axis"] in ("anchor","proposal") else 55,
                facecolors=color if row["scale"] == 1 else "white",edgecolors=color,linewidths=1.1,
                zorder=6 if row["axis"] == "anchor" else 3)
            if not row["qualified"]:
                ax.scatter([x],[y],marker="x",s=65,color="black",linewidths=1.3,zorder=4)
            if index == 1 and row["axis"] in ("a","c"):
                label = row["axis"]+("+" if row["sign"] == 1 else "-")+("/2" if row["scale"] == .5 else "")
                offset = (6 if row["sign"] > 0 else -6,10 if row["axis"] == "a" else -18)
                if row["axis"] == "c":
                    offset = ((32,-28 if row["scale"] == 1 else -8) if row["sign"] > 0
                              else (-32,24 if row["scale"] == 1 else 4))
                ax.annotate(label,(x,y),xytext=offset,textcoords="offset points",
                    ha="left" if row["sign"] > 0 else "right",fontsize=9,color=color,
                    arrowprops=dict(arrowstyle="-",color=color,lw=.6) if row["axis"] == "c" else None)
        extent = cloud if index else np.vstack((cloud,[-.1,-.1],[.1,.1]))
        low,high = np.min(extent,axis=0),np.max(extent,axis=0)
        span = np.maximum(high-low,[.25,.25])
        pad = .23 if index else .13
        ax.set_xlim(low[0]-pad*span[0],high[0]+pad*span[0])
        ax.set_ylim(low[1]-pad*span[1],high[1]+pad*span[1])
        if index == 0:
            ax.add_patch(Rectangle((-.1,-.1),.2,.2,facecolor="#e9e9e9",edgecolor="#555555",lw=.7,zorder=1))
            ax.scatter([0],[0],marker="+",s=55,color="#555555",zorder=3)
            ax.annotate("two-coordinate target",(0,0),xytext=(8,8),textcoords="offset points",fontsize=9)
        ax.set_title("Target and measured points" if index == 0 else "Zoom into the measured responses",fontsize=12,pad=12)
        ax.set_xlabel("Right-fold signed x residual / 15  (x 1000)",labelpad=8)
        ax.set_ylabel("Boundary signed x residual / 15  (x 1000)",labelpad=8)
        ax.ticklabel_format(style="plain",useOffset=False)
        ax.grid(alpha=.18)
        for spine in ("top","right"):
            ax.spines[spine].set_visible(False)
    fig.suptitle(title,fontsize=19,y=.98)
    fig.text(.5,.905,subtitle,ha="center",fontsize=11)
    handles = [Line2D([],[],marker="*",color="#222222",ls="none",markersize=11,label="EXP-497/501 anchor")]
    for axis in ("a","c"):
        color,marker = styles[axis]
        for scale in (1.,.5):
            handles.append(Line2D([],[],marker=marker,color=color,markerfacecolor=color if scale == 1 else "white",
                ls="none",markersize=6,label=axis+(" full step" if scale == 1 else " half step")))
    if any(r["axis"] == "proposal" for r in data):
        handles.append(Line2D([],[],marker="P",color=styles["proposal"][0],ls="none",markersize=9,label="Measured joint proposal"))
    if any(not r["qualified"] for r in data):
        handles.append(Line2D([],[],marker="x",color="black",ls="none",label="Unqualified: diagnostic only"))
    fig.legend(handles=handles,loc="lower center",bbox_to_anchor=(.5,.14),ncol=3,frameon=False,fontsize=9)
    fig.text(.08,.097,"Means and complete ranges of 256 correlated representations; ranges are not confidence intervals.",fontsize=9)
    fig.text(.08,.066,"The coordinate target is necessary, not sufficient: full-state, primitive-period and representation checks still apply.",fontsize=9)
    missing = [r["id"] for r in data if not r["plotted"]]
    fig.text(.08,.035,"No fitted curves. Full and half steps refer to the frozen a,c increments."
             if not missing else "No complete matrix to plot for: "+", ".join(missing),fontsize=9)
    return fig


def plot(source,expected_sha,output):
    checked = public.verify(source,expected_sha)
    result = json.loads(source.read_bytes())
    data = derive(result)
    subtitles = {"unresolved-response-matrix":"The response checks did not authorize a joint step",
        "failed-proposal-qualification":"The proposed point failed numerical qualification",
        "qualified-joint-proximity":"Both numerical proximity tests met; symbolic chains remain unverified",
        "qualified-proposal-without-joint-proximity":"The tested correction did not achieve both contacts"}
    fig = draw(data,TITLE,subtitles[result["analysis"]["status"]])
    output.mkdir(parents=True,exist_ok=False)
    outputs = {}
    for suffix in ("svg","pdf","png"):
        path = output/(FIGURE+"."+suffix)
        metadata = {"Date":None} if suffix == "svg" else ({"CreationDate":None,"ModDate":None} if suffix == "pdf" else None)
        fig.savefig(path,dpi=300,metadata=metadata)
        outputs[path.name] = dict(sha256=sha256(path),bytes=path.stat().st_size)
    import matplotlib
    from matplotlib import pyplot as plt
    plt.close(fig)
    receipt = dict(figure_id=FIGURE,title=TITLE,
        description="The same two contact residuals are shown against their coordinate target and at a closer scale; neither panel is a parameter-plane atlas.",
        alt_text="Two scatter panels show the old anchor, all complete two-residual stencil matrices, and the measured joint proposal when available. Diamonds distinguish a changes, squares c changes, and outlines half steps. Black crosses flag unqualified points. The left panel includes the coordinate target at zero; the right zooms into measured responses. Missing complete matrices are explicitly listed.",
        data_source=dict(path=source.resolve().relative_to(ROOT).as_posix(),sha256=expected_sha,
            fields=["rows.vectors","rows.qualified","proposal","analysis","EXP-502.base_vectors"],
            selection="All eight fixed points, the old anchor and the sole measured proposal if present.",
            exclusions="Only points lacking all 256 distinct residual vectors have no plotted coordinate; all are retained in the derived table and named on the figure.",
            aggregation="Arithmetic means and componentwise full ranges over all correlated variants; not independent samples.",
            transformation="Both residual coordinates multiplied by 1000 for display. No interpolation or fitted curves."),
        provenance=dict(experiment_id="EXP-503",audit_receipt_sha256=expected_sha,source_commit=result["source_commit"],
            generator_path=Path(__file__).resolve().relative_to(ROOT).as_posix(),generator_sha256=sha256(Path(__file__)),
            python=sys.version,matplotlib=matplotlib.__version__,outputs=outputs),
        bindings={n:sha256(ROOT/n) for n in ("scripts/verify_exp503_public_contact.py","scripts/exp502_response.py",
            "experiments/manifests/EXP-502-joint-contact-search.json","experiments/manifests/EXP-503-joint-contact-continuation.json")},
        derived_values=data,interval_semantics="Descriptive fixed-census numerical-representation ranges, not inferential uncertainty or absolute error bounds.",
        claim_exclusions=["No exact flow contact proof","No C/D identification","No verified symbolic chain","Not a global parameter-plane explanation"],
        accessibility=dict(non_color_channels="Marker shape, open/filled markers, signed text labels and black failure crosses",png_dpi=300),
        hard_guards=checked)
    receipt_path = output/(FIGURE+".receipt.json")
    write_json(receipt_path,receipt)
    write_json(output/(FIGURE+".index.json"),dict(figures=[dict(path=receipt_path.name,sha256=sha256(receipt_path))]))
    return receipt


def verify(output):
    path = output/(FIGURE+".receipt.json")
    index = json.loads((output/(FIGURE+".index.json")).read_bytes())
    if index != dict(figures=[dict(path=path.name,sha256=sha256(path))]):
        raise ValueError("figure receipt index differs")
    r = json.loads(path.read_bytes())
    if (sha256(Path(__file__)) != r["provenance"]["generator_sha256"]
            or any(sha256(ROOT/n) != h for n,h in r["bindings"].items())
            or public.verify(ROOT/r["data_source"]["path"],r["data_source"]["sha256"]) != r["hard_guards"]
            or derive(json.loads((ROOT/r["data_source"]["path"]).read_bytes())) != r["derived_values"]
            or any(sha256(output/n) != v["sha256"] or (output/n).stat().st_size != v["bytes"]
                   for n,v in r["provenance"]["outputs"].items())):
        raise ValueError("figure source/code/data/output drift")
    return dict(passed=True,figure_id=FIGURE,source_sha256=r["data_source"]["sha256"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt",type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--verify-only",action="store_true")
    a = parser.parse_args()
    if a.verify_only:
        print(json.dumps(verify(a.output_dir)))
    else:
        if not a.receipt or not a.expected_sha256:
            parser.error("audited receipt and expected hash required")
        plot(a.receipt,a.expected_sha256,a.output_dir)
        print(json.dumps(verify(a.output_dir)))


if __name__ == "__main__":
    main()

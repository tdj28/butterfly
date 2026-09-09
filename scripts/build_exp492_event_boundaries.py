#!/usr/bin/env python3
"""Derive EXP-492 inputs only from immutable, completed EXP-491 records."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
import numpy as np
from butterfly._paired_startup import sha256,write_json
from scripts import run_exp491_event_sheet_probe as parent

RECEIPT = ROOT/"docs/experiments/receipts/EXP-491-event-sheet-result.json"
RECEIPT_SHA = "d96454454290ed83d5503fce91f9b86ccce516b40b50a84b9d35ab512f6fc879"
SUMMARY_SHA = "a47959ab1041aac772908524a45e1ae4451fcdf88fc903107333c6f5c826a69f"


def digest(value):
    return hashlib.sha256((json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()).hexdigest()


def inputs():
    if sha256(RECEIPT) != RECEIPT_SHA:
        raise ValueError("EXP-491 public result changed")
    candidates,_ = parent.load(json.loads(parent.PLAN.read_bytes()))
    result = json.loads(RECEIPT.read_bytes())
    if [c["id"] for c in candidates] != [c["id"] for c in result["candidates"]]:
        raise ValueError("parent identity matrix differs")
    return candidates,result


def derive(c,r,evidence):
    if r["analysis"]["screened_regular"]:
        if evidence:
            raise ValueError("unselected interval has unexpected endpoint inputs")
        return dict(id=c["id"],family_id=c["family_id"],case=c["case"],region=c["region"],
                    status="not-selected-screened-regular",evidence=[])
    halves = [[h for h in (0,1) if any(v["half"] == h and abs(v["time_change"]) > 1.
               for v in s["time_comparisons"])] for s in r["analysis"]["solvers"]]
    if len(halves[0]) != 1 or halves[0] != halves[1]:
        raise ValueError("unique paired flagged half required")
    half = halves[0][0]
    labels = [(i,m) for i in (half,half+1) for m in ("DOP853","Radau")]
    if [(e["sample_index"],e["method"]) for e in evidence] != labels:
        raise ValueError("complete endpoint evidence required")
    reports = []
    for e,(i,method) in zip(evidence,labels,strict=True):
        p = e["raw"]["report"]
        if p["method"] != method or p["initial_state"] != (np.asarray(c["initial_state"])+r["us"][i]*np.asarray(c["initial_tangent"])).tolist() or p["initial_tangent"] != c["initial_tangent"] or e["raw"]["profile"] != r["points"][i]["profiles"][0 if method == "DOP853" else 1]:
            raise ValueError("endpoint identity or prior derived profile differs")
        reports.append(p)
    if len({len(p["extrema"]) for p in reports}) != 1:
        raise ValueError("extremum ordinal alignment unavailable")
    flips = [[i for i,(a,b) in enumerate(zip(reports[j]["extrema"],reports[j+2]["extrema"],strict=True))
              if a["plane_value"]*b["plane_value"] < 0] for j in (0,1)]
    if len(flips[0]) != 1 or flips[0] != flips[1]:
        raise ValueError("unique paired extremum sign change required")
    index = flips[0][0]
    extrema = [p["extrema"][index] for p in reports]
    prefixes = [sum(e["accepted"] and e["time"] < g["time"]-.5 for e in p["reconstructed"])
                for p,g in zip(reports,extrema,strict=True)]
    if len(set(prefixes)) != 1:
        raise ValueError("preceding accepted count differs")
    left,right = r["us"][half:half+2]
    width = right-left
    seed_time = sum(e["time"] for e in extrema)/4.
    return dict(id=c["id"],family_id=c["family_id"],case=c["case"],region=c["region"],status="nominated",
        half=half,extremum_index=index,accepted_prefix=prefixes[0],parameters=c["parameters"],
        initial_state=c["initial_state"],initial_tangent=c["initial_tangent"],horizon=c["horizon"],
        u_box=[left,right],seed_u=(left+right)/2.,seed_time=seed_time,time_box=[seed_time-.25,seed_time+.25],
        doses=[-width/1000.,-width/10000.,width/10000.,width/1000.],evidence=evidence)


def validate(table):
    candidates,result = inputs()
    if table["experiment_id"] != "EXP-492" or table["parent_receipt_sha256"] != RECEIPT_SHA or table["parent_summary_sha256"] != SUMMARY_SHA:
        raise ValueError("historical anchors differ")
    metadata = table["parent_summary_metadata"]
    if "candidates" in metadata or digest(dict(metadata,candidates=result["candidates"])) != SUMMARY_SHA:
        raise ValueError("complete historical summary reconstruction differs")
    if [r["id"] for r in table["intervals"]] != [c["id"] for c in candidates]:
        raise ValueError("all 26 original intervals required")
    names = set()
    for c,r,row in zip(candidates,result["candidates"],table["intervals"],strict=True):
        for e in row["evidence"]:
            name = f"{c['id']}--sample-{e['sample_index']}--{e['method']}.json"
            raw = (json.dumps(e["raw"],sort_keys=True,indent=2,allow_nan=False)+"\n").encode()
            if e["path"] != name or e["sha256"] != metadata["files"][name]["sha256"] or hashlib.sha256(raw).hexdigest() != e["sha256"] or len(raw) != metadata["files"][name]["bytes"] or name in names:
                raise ValueError("immutable endpoint report differs")
            names.add(name)
        if derive(c,r,row["evidence"]) != row:
            raise ValueError("candidate derivation differs")
    nominated = [r for r in table["intervals"] if r["status"] == "nominated"]
    if len(nominated) != 16 or len(names) != 64 or len({r["family_id"] for r in nominated}) != 10:
        raise ValueError("complete boundary matrix differs")
    return nominated


def build(directory):
    if sha256(directory/"summary.json") != SUMMARY_SHA:
        raise ValueError("completed raw summary anchor differs")
    saved = json.loads((directory/"summary.json").read_bytes())
    candidates,result = inputs()
    rows = []
    for c,r in zip(candidates,result["candidates"],strict=True):
        evidence = []
        if not r["analysis"]["screened_regular"]:
            half = next(h for h in (0,1) if any(v["half"] == h and abs(v["time_change"]) > 1 for v in r["analysis"]["solvers"][0]["time_comparisons"]))
            for i in (half,half+1):
                for method in ("DOP853","Radau"):
                    name = f"{c['id']}--sample-{i}--{method}.json"
                    if sha256(directory/name) != saved["files"][name]["sha256"]:
                        raise ValueError("raw endpoint changed")
                    evidence.append(dict(path=name,sample_index=i,method=method,sha256=sha256(directory/name),raw=json.loads((directory/name).read_bytes())))
        rows.append(derive(c,r,evidence))
    table = dict(experiment_id="EXP-492",parent_receipt_sha256=RECEIPT_SHA,parent_summary_sha256=SUMMARY_SHA,
                 parent_summary_metadata={k:v for k,v in saved.items() if k != "candidates"},intervals=rows)
    validate(table)
    return table


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a = p.parse_args()
    table = build(a.run)
    write_json(a.output,table)
    print(json.dumps(dict(intervals=len(table["intervals"]),nominations=len(validate(table)),bytes=a.output.stat().st_size,sha256=sha256(a.output))))

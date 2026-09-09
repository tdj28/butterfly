#!/usr/bin/env python3
"""Bounded grazing transport at the independently corrected EXP-497 anchor."""
import argparse
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

import numpy as np
import scipy
from butterfly._paired_startup import inventory, sha256, write_json
from butterfly.models import RosslerParameters, rossler_rhs, rossler_jacobian
from butterfly.poincare import legacy_rossler_section
from scripts import run_exp492_event_boundaries as boundary
from scripts import audit_exp492_event_boundaries as boundary_audit
from scripts import analyze_exp493_projected_inner_turn as winding
from scripts import export_exp493_projected_inner_turn as polygon_audit
from scripts import run_exp497_contact_localization as contact

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/"experiments/manifests/EXP-498-boundary-transport.json"
ANCHOR = ROOT/"docs/experiments/receipts/EXP-497-contact-localization-result.json"
ANCHOR_SHA = "ed229b4a772ef19d227272006401d19090ee5e28a357791f25400cafa3271cff"
EXPLICIT = ["scripts/run_exp498_boundary_transport.py", "scripts/audit_exp498_boundary_transport.py",
    "tests/test_exp498_boundary_transport.py", "docs/experiments/EXP-498-boundary-transport.md",
    "experiments/manifests/EXP-498-boundary-transport.json", "experiments/manifests/EXP-492-event-boundaries.json",
    "experiments/manifests/EXP-493-projected-inner-turn.json", "scripts/export_exp493_projected_inner_turn.py",
    "pyproject.toml", "uv.lock"]


def inputs():
    p492 = json.loads(boundary.PLAN.read_bytes())
    table, _ = boundary.load(p492)
    p493 = winding.load_plan()
    receipt = ROOT/p493["parent_receipt_path"]
    if sha256(receipt) != p493["parent_receipt_sha256"] or sha256(ANCHOR) != ANCHOR_SHA:
        raise ValueError("audited parent or primitive-cycle anchor changed")
    old = json.loads(receipt.read_bytes())
    saved = json.loads(ANCHOR.read_bytes())
    p497, _ = contact.load()
    points = [r for r in saved["rows"] if r["status"] == "proximate"]
    if (not saved["passed"] or len(points) != 1 or len(saved["rows"]) != 6
            or points[0]["case"] != "local-a025-c083" or points[0]["level"] != 3
            or points[0]["spec"]["parameters"] != dict(a=.21558015990653545,b=.2,c=7.212)
            or points[0]["result"]["cycle"]["status"] != "qualified"):
        raise ValueError("unique qualified fixed anchor required")
    return p492,p493,p497,table,old,points[0]


def derive(table,old,anchor):
    if [r["id"] for r in table["intervals"]] != [r["id"] for r in old["intervals"]]:
        raise ValueError("complete parent identities required")
    ledger,candidates = [],[]
    for c,r in zip(table["intervals"],old["intervals"],strict=True):
        selected = c["status"] == "nominated" and c["case"] == anchor["case"]
        previous = r["analysis"]["qualified"] if r["analysis"] is not None else None
        ledger.append(dict(id=c["id"],family_id=c["family_id"],case=c["case"],region=c["region"],
            parent_selection=c["status"],parent_qualified=previous,
            status="selected" if selected else ("not-run-no-anchor" if c["status"] == "nominated" else "not-run-parent-unselected")))
        if not selected: continue
        if not r["analysis"]["roots"]["eligible"] or c["region"] != 0:
            raise ValueError("all first-case old paired roots must be eligible")
        roots = [s["root"] for s in r["analysis"]["solvers"]]
        u,t = [float(np.mean([v[k] for v in roots])) for k in ("u","time")]
        new = {k:deepcopy(v) for k,v in c.items() if k != "evidence"}
        new.update(id=c["id"]+"--anchor",parent_id=c["id"],parent_qualified=previous,
            parameters=deepcopy(anchor["spec"]["parameters"]),seed_u=u,seed_time=t,
            u_box=[u-.02,u+.02],time_box=[t-1,t+1])
        new["initial_state"][1] = legacy_rossler_section(RosslerParameters(**new["parameters"])).offset
        candidates.append(new)
    if len(ledger) != 26 or len(candidates) != 8 or sum(c["parent_qualified"] is False for c in candidates) != 1:
        raise ValueError("complete eight-candidate matrix including old failure required")
    return ledger,candidates


def expected():
    p492,p493,p497,table,old,anchor = inputs()
    ledger,candidates = derive(table,old,anchor)
    return dict(experiment_id="EXP-498",boundary=p492,winding=p493,ledger=ledger,candidates=candidates,
        anchor_parameters=anchor["spec"]["parameters"],scales=[15.,15.,.01],ordering_gap=1e-4,
        radii=[1e-6,1e-5,1e-4,1e-3],limits=dict(target_ivps=192,wall_seconds=3600,output_bytes=2*1024**3,
            initial_free_bytes=12*1024**3,minimum_free_bytes=8*1024**3),
        inputs={**p497["inputs"],str(ANCHOR.relative_to(ROOT)):ANCHOR_SHA,
            str(boundary.PLAN.relative_to(ROOT)):sha256(boundary.PLAN),
            p492["inputs_path"]:p492["inputs_sha256"],p493["parent_receipt_path"]:p493["parent_receipt_sha256"]},
        required_sources=sorted(set(EXPLICIT)|set(p497["source_paths"])|set(boundary.SOURCES)|set(winding.SOURCES)),
        paid_review="not_run-human-approval-policy")


def load():
    p = json.loads(PLAN.read_bytes())
    e = expected()
    if ({k:v for k,v in p.items() if k != "source_paths"} != e
            or not set(e["required_sources"]) <= set(p["source_paths"])
            or any(sha256(ROOT/s) != h for s,h in p["inputs"].items())):
        raise ValueError("frozen plan/source/input contract differs")
    return p,inputs()[-1]


def geometry(output,c,result,p):
    sides = []
    for side in result["sides"]:
        profiles = []
        for j,(report,name) in enumerate(zip(side["reports"],side["raw_files"],strict=True)):
            with np.load(output/name,allow_pickle=False) as f:
                raw = {k:f[k] for k in f.files}
            root = result["roots"][j]["shooting"]["trace"][-1]
            profiles.append(winding.profile(raw,report,c,root["time"],p))
        sides.append(dict(dose=side["dose"],u=side["u"],profiles=profiles))
    verdict = winding.compare(sides,c,p,result["analysis"]["qualified"]) if sides else None
    return dict(sides=sides,analysis=verdict)


def predecessors(c,result,anchor,p):
    rows = []
    cycle = anchor["result"]["cycle"]
    for side in result["sides"]:
        for j,report in enumerate(side["reports"]):
            root = result["roots"][j]["shooting"]["trace"][-1]
            before = [e for e in report["reconstructed"] if e["accepted"] and e["time"] <= root["time"]-p["boundary"]["window"]]
            eligible = len(before) == c["accepted_prefix"] and bool(before)
            row = dict(method=report["method"],dose=side["dose"],u=side["u"],prefix_count=len(before),
                eligible=eligible,event=before[-1] if eligible else None,windows=[])
            if eligible:
                profile = next(v for v in cycle["profiles"] if v["method"] == report["method"])
                for w in profile["metric"]["windows"]:
                    distance = np.max(np.abs((np.asarray(w["event_states"]["historical"])-before[-1]["state"])/p["scales"]),axis=1)
                    row["windows"].append(dict(phase=w["phase"],state_distances=distance.tolist()))
            rows.append(row)
    return rows


def diagnostic(rows,anchor,p):
    records = [v for r in rows for v in r["predecessors"] if v["eligible"]]
    complete = len(rows) == 8 and len(records) == 64 and all(r["geometry"]["analysis"] and r["geometry"]["analysis"]["qualified"] for r in rows)
    states = np.array([v["event"]["state"] for v in records])
    folds = [v["fold_input"] for r in anchor["result"]["contact"]["rows"] for v in r["variants"]]
    result = dict(complete_qualified_matrix=bool(complete),predecessors=len(records),
        comparison_cells=sum(len(w["state_distances"]) for r in records for w in r["windows"]),
        state_envelope=None,max_pairwise_scaled_spread=None,worst_cycle_distances=None,
        sensitivity=[],fold_input_x_range=[min(v[0] for v in folds),max(v[0] for v in folds)],
        predecessor_minus_fold_x_scaled_range=None,ordering="unresolved",symbolic_chains_verified=False)
    if not records: return result
    worst = np.max(np.array([w["state_distances"] for r in records for w in r["windows"]]),axis=0)
    gaps = (states[:,0,None]-np.array(folds)[None,:,0])/15.
    result.update(state_envelope=[np.min(states,axis=0).tolist(),np.max(states,axis=0).tolist()],
        max_pairwise_scaled_spread=float(np.max(np.ptp(states,axis=0)/p["scales"])),
        worst_cycle_distances=worst.tolist(),
        sensitivity=[dict(radius=r,all_realized_predecessors_proximate=(worst<=r).tolist()) for r in p["radii"]],
        predecessor_minus_fold_x_scaled_range=[float(np.min(gaps)),float(np.max(gaps))])
    if complete:
        result["ordering"] = "left" if np.max(gaps) < -p["ordering_gap"] else ("right" if np.min(gaps) > p["ordering_gap"] else "overlap-or-unresolved-gap")
    return result


def controls(p):
    a = boundary.controls(p["boundary"])
    boundary_audit.check_controls(a,p["boundary"])
    b = winding.controls(p["winding"])
    if not b["passed"]: raise ValueError("analytic winding controls failed")
    return dict(boundary=a,winding=b)


def execute(output,source,remote):
    from scripts import audit_exp498_boundary_transport  # noqa: F401
    p,anchor = load()
    def git(*args): return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()
    if (git("rev-parse","HEAD") != source or git("status","--porcelain")
            or git("ls-remote","origin",remote).split() != [source,remote]
            or not contact.parent.imported_sources() <= set(p["source_paths"])):
        raise ValueError("clean live pushed source/import closure required")
    output = output.resolve()
    marker = ROOT/"artifacts/EXP-498/target-once.json"
    if ROOT/"artifacts/EXP-498" not in output.parents or marker.exists():
        raise ValueError("fresh EXP-498 output and unconsumed attempt required")
    if shutil.disk_usage(ROOT).free < p["limits"]["initial_free_bytes"]: raise ValueError("initial disk reserve")
    output.mkdir(parents=True,exist_ok=False)
    b = dict(source_commit=source,remote_ref=remote,started_utc=boundary.utc(),plan_sha256=sha256(PLAN),
        inputs=p["inputs"],sources={s:sha256(ROOT/s) for s in p["source_paths"]},
        runtime=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__),paid_review=p["paid_review"])
    write_json(output/"binding.json",b)
    calls = 0
    start = time.monotonic()
    def budget():
        if (calls >= p["limits"]["target_ivps"] or shutil.disk_usage(ROOT).free < p["limits"]["minimum_free_bytes"]
                or sum(f.stat().st_size for f in output.iterdir()) > p["limits"]["output_bytes"]-64*1024**2):
            raise RuntimeError("EXP-498 target/storage reserve reached")
    def retain(name,raw):
        nonlocal calls
        budget()
        with (output/name).open("xb") as f: np.savez_compressed(f,**raw)
        calls += 1
    def begin(label,metadata):
        budget()
        write_json(output/(label+"-started.json"),dict(metadata,started_utc=boundary.utc()))
    def timeout(*_): raise TimeoutError("EXP-498 whole-run deadline")
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p["limits"]["wall_seconds"])
    try:
        write_json(output/"controls.json",controls(p))
        write_json(marker,b)
        rows = []
        for c in p["candidates"]:
            par = RosslerParameters(**c["parameters"])
            rhs,jac = lambda t,q:rossler_rhs(t,q,par),lambda t,q:rossler_jacobian(q,par)
            section = replace(legacy_rossler_section(par),direction=-1)
            result = boundary.run_candidate(c,p["boundary"],rhs,jac,section,retain,begin,budget)
            row = dict(id=c["id"],parent_id=c["parent_id"],parent_qualified=c["parent_qualified"],boundary=result,
                geometry=geometry(output,c,result,p["winding"]),predecessors=predecessors(c,result,anchor,p))
            write_json(output/(c["id"]+".json"),row)
            rows.append(row)
            print(c["id"]+": completed",flush=True)
        write_json(output/"summary.json",dict(experiment_id="EXP-498",status="completed",binding=b,
            ledger=p["ledger"],rows=rows,diagnostic=diagnostic(rows,anchor,p),target_ivps=calls,
            elapsed_seconds=time.monotonic()-start,completed_utc=boundary.utc(),files=inventory(output),
            marker_sha256=sha256(marker),symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True,target_ivps=calls,summary_sha256=sha256(output/"summary.json"))))
    except BaseException as exc:
        write_json(output/"failure.json",dict(error_type=type(exc).__name__,message=str(exc),target_ivps=calls,
            utc=boundary.utc(),files=inventory(output)))
        raise
    finally: signal.alarm(0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare",action="store_true")
    parser.add_argument("--controls-only",action="store_true")
    parser.add_argument("--execute",action="store_true")
    parser.add_argument("--output-dir",type=Path)
    parser.add_argument("--source-commit")
    parser.add_argument("--remote-ref")
    a = parser.parse_args()
    if sum((a.prepare,a.controls_only,a.execute)) > 1: parser.error("separate modes required")
    if a.prepare:
        from scripts import audit_exp498_boundary_transport  # noqa: F401
        p = expected()
        p["source_paths"] = sorted(set(p["required_sources"])|contact.parent.imported_sources())
        write_json(PLAN,p)
    elif a.controls_only:
        if not a.output_dir: parser.error("controls need fresh output")
        p,_ = load()
        a.output_dir.mkdir(parents=True,exist_ok=False)
        write_json(a.output_dir/"controls.json",controls(p))
        print(json.dumps(dict(controls_passed=True,new_target_ivps=0)))
    elif a.execute:
        if not all((a.output_dir,a.source_commit,a.remote_ref)): parser.error("execution needs output/source/ref")
        execute(a.output_dir,a.source_commit,a.remote_ref)
    else:
        p,_ = load()
        print(json.dumps(dict(preflight=True,candidates=len(p["candidates"]),new_target_ivps=0)))


if __name__ == "__main__": main()

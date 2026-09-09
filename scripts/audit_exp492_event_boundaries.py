#!/usr/bin/env python3
"""Read-only complete-matrix audit of EXP-492 roots and side censuses."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
import numpy as np
from butterfly._paired_startup import inventory,sha256,write_json
from butterfly.models import RosslerParameters
from butterfly.poincare import legacy_rossler_section
from butterfly.event_boundary_shooting import assess
from scripts import run_exp492_event_boundaries as run
from scripts.run_exp488_event_accuracy import validate_geometry


def check_controls(rows,p):
    if [r["spec"] for r in rows] != run.control_specs() or not all(r["passed"] for r in rows):
        raise ValueError("complete five-condition analytic control matrix required")
    for row in rows:
        c,r = row["spec"],row["result"]
        if assess(r["roots"],r["sides"],c,p) != r["analysis"]:
            raise ValueError("control decision replay differs")
        calls = sum(len(v["shooting"]["raw_files"]) for v in r["roots"])+sum(len(s["raw_files"]) for s in r["sides"])
        if calls != row["control_integrations"] or calls > 24:
            raise ValueError("control workload differs")
        if c["kind"] != "grazing":
            reason = "singular Newton matrix" if c["kind"] == "transverse" else "prospective search box exceeded"
            if r["sides"] or r["analysis"]["qualified"] or any(v["shooting"]["converged"] or v["shooting"]["reason"] != reason for v in r["roots"]):
                raise ValueError("analytic negative did not fail for its expected reason")
            continue
        prefix = c["accepted_prefix"]
        target = 2*prefix+1.
        if not r["analysis"]["qualified"]:
            raise ValueError("analytic positive failed")
        for v in r["roots"]:
            root = v["shooting"]["trace"][-1]
            if abs(root["u"]+1e-5) > 1e-9 or abs(root["time"]-target) > 1e-8:
                raise ValueError("known analytic grazing root differs")
        for side in r["sides"]:
            x = 2e-5+2*side["u"]
            exact = list(np.arange(1,2*prefix,2,dtype=float))
            if x < 0:
                exact.append(target-np.sqrt(-x))
            for report in side["reports"]:
                actual = [e["time"] for e in report["reconstructed"] if e["accepted"]]
                if len(actual) != len(exact) or not np.allclose(actual,exact,rtol=0,atol=1e-7):
                    raise ValueError("known complete analytic event sequence differs")


def check_shooting(output,row,c,p,method):
    shooting = row["shooting"]
    if row["method"] != method or not 1 <= len(shooting["trace"]) <= 8 or len(shooting["trace"]) != len(shooting["raw_files"]):
        raise ValueError("shooting identity/trace matrix differs")
    par = RosslerParameters(**c["parameters"])
    section = legacy_rossler_section(par)
    u,end = c["seed_u"],c["seed_time"]
    expected = set()
    for i,(v,name) in enumerate(zip(shooting["trace"],shooting["raw_files"],strict=True)):
        if name != f"{c['id']}--{method}--newton-{i}.npz" or v["iteration"] != i or v["u"] != u or v["time"] != end:
            raise ValueError("Newton sequence differs")
        expected.add(name)
        with np.load(output/name,allow_pickle=False) as raw:
            times,states = raw["integration_times"],raw["integration_augmented_states"]
            initial = np.r_[np.asarray(c["initial_state"])+u*np.asarray(c["initial_tangent"]),c["initial_tangent"]]
            if states.shape != (len(times),6) or not np.isfinite(states).all() or not np.isfinite(times).all() or not np.all(np.diff(times)>0) or times[0] != 0. or times[-1] != v["reached_time"] or not np.array_equal(states[0],initial) or not np.array_equal(states[-1],np.r_[v["state"],v["raw_tangent"]]):
                raise ValueError("raw fixed-time trajectory differs")
        if not v["solver_success"]:
            if i != len(shooting["trace"])-1 or shooting["converged"] or shooting["reason"] != "integration failed":
                raise ValueError("failed IVP not retained as a failed root")
            continue
        if v["reached_time"] != end or not c["u_box"][0] <= u <= c["u_box"][1] or not c["time_box"][0] <= end <= c["time_box"][1]:
            raise ValueError("fixed-time endpoint outside contract")
        x,y,z = v["state"]
        vx,vy,vz = v["raw_tangent"]
        fx,fy = -y-z,x+par.a*y
        residual = np.array([y-section.offset,fy])
        matrix = np.array([[vy,fy],[vx+par.a*vy,fx+par.a*fy]])
        if not np.allclose(residual,v["residual"],rtol=0,atol=1e-13) or not np.allclose(matrix,v["jacobian"],rtol=1e-14,atol=1e-12):
            raise ValueError("independent Rössler grazing algebra differs")
        converged = abs(residual[0]) <= p["root_plane"] and abs(residual[1]) <= p["root_velocity"]
        if converged:
            if i != len(shooting["trace"])-1 or not shooting["converged"] or shooting["reason"] != "residual tolerances":
                raise ValueError("Newton convergence decision differs")
        elif "newton_step" in v:
            step = np.linalg.solve(matrix,residual)
            if not np.allclose(step,v["newton_step"],rtol=1e-12,atol=1e-15):
                raise ValueError("Newton correction differs")
            u,end = float(u-v["newton_step"][0]),float(end-v["newton_step"][1])
            outside = not c["u_box"][0] <= u <= c["u_box"][1] or not c["time_box"][0] <= end <= c["time_box"][1] or end <= 0
            if i == len(shooting["trace"])-1 and (shooting["converged"] or shooting["reason"] != ("prospective search box exceeded" if outside else "iteration limit") or (not outside and i != 7)):
                raise ValueError("Newton termination differs")
        else:
            try:
                np.linalg.solve(matrix,residual)
            except np.linalg.LinAlgError:
                if i == len(shooting["trace"])-1 and not shooting["converged"] and shooting["reason"] == "singular Newton matrix":
                    continue
            raise ValueError("unexplained missing Newton correction")
    return expected


def audit(output,anchor):
    if sha256(output/"summary.json") != anchor:
        raise ValueError("completed summary anchor differs")
    saved = json.loads((output/"summary.json").read_bytes())
    p = json.loads(run.PLAN.read_bytes())
    table,candidates = run.load(p)
    b = json.loads((output/"binding.json").read_bytes())
    if saved["status"] != "completed" or saved["binding"] != b or b["sources"] != {s:sha256(ROOT/s) for s in run.SOURCES} or b["plan_sha256"] != sha256(run.PLAN) or b["inputs_sha256"] != p["inputs_sha256"] or inventory(output,omit=("summary.json",)) != saved["files"]:
        raise ValueError("source/input/output binding differs")
    check_controls(json.loads((output/"controls.json").read_bytes()),p)
    expected,results = {"binding.json","controls.json"},[]
    calls = 0
    for c in candidates:
        name = c["id"]+".json"
        expected.add(name)
        row = json.loads((output/name).read_bytes())
        if row["id"] != c["id"] or [r["method"] for r in row["roots"]] != p["solvers"]:
            raise ValueError("candidate/root solver identity differs")
        starts = []
        for method,r in zip(p["solvers"],row["roots"],strict=True):
            files = check_shooting(output,r,c,p,method)
            expected.update(files)
            calls += len(files)
            starts.append((c["id"]+"--"+method+"-started.json",dict(candidate_id=c["id"],method=method,phase="shooting")))
        decision = assess(row["roots"],row["sides"],c,p)
        if decision != row["analysis"] or row["skipped_doses"] != ([] if decision["roots"]["eligible"] else c["doses"]):
            raise ValueError("root/side decision replay differs")
        for i,side in enumerate(row["sides"]):
            names = [f"{c['id']}--side-{i}--{method}.npz" for method in p["solvers"]]
            if side["raw_files"] != names:
                raise ValueError("side raw identity differs")
            for method,report,name in zip(p["solvers"],side["reports"],names,strict=True):
                expected.add(name)
                calls += 1
                starts.append((name.removesuffix(".npz")+"-started.json",dict(candidate_id=c["id"],method=method,phase="side",dose=side["dose"],u=side["u"])))
                if report["method"] != method or report["horizon"] != c["horizon"] or any(report[k] != p[k] for k in ("rtol","atol","max_step","guard")):
                    raise ValueError("side numerical contract differs")
                initial = (np.asarray(c["initial_state"])+side["u"]*np.asarray(c["initial_tangent"])).tolist()
                validate_geometry(report,output/name,dict(c,initial_state=initial),dict(p,horizon=c["horizon"]))
        for name,metadata in starts:
            expected.add(name)
            start = json.loads((output/name).read_bytes())
            if {k:v for k,v in start.items() if k != "started_utc"} != metadata or not b["started_utc"] <= start["started_utc"] <= saved["completed_utc"]:
                raise ValueError("profile start identity/time differs")
        results.append(row)
    marker = ROOT/"artifacts/EXP-492/target-once.json"
    if results != saved["candidates"] or set(saved["files"]) != expected or calls != saved["target_integrations"] or calls > 384 or sha256(marker) != saved["marker_sha256"] or json.loads(marker.read_bytes()) != b:
        raise ValueError("complete matrix/inventory/attempt differs")
    by_id = {r["id"]:r for r in results}
    intervals = [dict(id=c["id"],family_id=c["family_id"],case=c["case"],region=c["region"],selection_status=c["status"],
        analysis=by_id[c["id"]]["analysis"] if c["id"] in by_id else None) for c in table["intervals"]]
    return dict(experiment_id="EXP-492",status="completed-audited",source_commit=b["source_commit"],summary_sha256=anchor,
        target_integrations=calls,intervals=intervals,elapsed_seconds=saved["elapsed_seconds"],same_agent_local_audit=True,
        paid_review="not_run",claim_boundary=p["claim_boundary"])


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run",type=Path,required=True)
    p.add_argument("--expected-summary-sha256",required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a = p.parse_args()
    result = audit(a.run,a.expected_summary_sha256)
    a.output_dir.mkdir(parents=True,exist_ok=False)
    write_json(a.output_dir/"summary.json",result)
    print(json.dumps(dict(intervals=len(result["intervals"]),qualified=sum(bool(r["analysis"] and r["analysis"]["qualified"]) for r in result["intervals"]))))

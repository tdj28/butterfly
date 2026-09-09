#!/usr/bin/env python3
"""Direct fixed-time section-grazing witness and two-sided unfolding test."""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import numpy as np
import scipy
from butterfly._paired_startup import sha256, write_json, inventory
from butterfly.models import RosslerParameters, rossler_rhs, rossler_jacobian
from butterfly.poincare import legacy_rossler_section, PoincareSection
from butterfly.section_census import collect
from butterfly.section_grazing import shoot, side_verdict
from scripts.run_exp488_event_accuracy import utc, validate_geometry

PLAN = ROOT/"experiments/manifests/EXP-489-section-grazing.json"
SOURCES = ("scripts/run_exp489_section_grazing.py", "python/butterfly/section_grazing.py",
           "python/butterfly/section_census.py", "python/butterfly/models.py",
           "python/butterfly/poincare.py", "python/butterfly/_paired_startup.py",
           "scripts/run_exp488_event_accuracy.py")
CASES = ["local-a025-c083", "local-a027-c083"]
DOSES = [-1e-6, -1e-7, 1e-7, 1e-6]


def validate_plan(p):
    if sorted(p["witness_reports"]) != CASES or p["solvers"] != ["DOP853", "Radau"] or p["doses"] != DOSES or p["newton_iterations"] != 8 or p["accepted_prefix"] != 4 or p["limits"]["max_target_integrations"] != 48:
        raise ValueError("complete frozen matrix differs")
    if [p[k] for k in ("rtol", "atol", "max_step", "root_plane", "root_velocity", "delta_bound", "time_bound", "window")] != [1e-13, 1e-15, .001, 1e-10, 1e-9, 1e-4, .1, .05]:
        raise ValueError("frozen numerical settings differ")


def selection_for(p):
    if sha256(ROOT/p["parent_receipt"]) != p["parent_receipt_sha256"]:
        raise ValueError("parent changed")
    selection = json.loads((ROOT/p["parent_receipt"]).read_bytes())["selection"]
    if [s["case"] for s in selection] != CASES:
        raise ValueError("witness selection differs")
    result = []
    for s in selection:
        ref = p["witness_reports"][s["case"]]
        if sha256(ROOT/ref["path"]) != ref["sha256"]:
            raise ValueError("extremum seed source changed")
        r = json.loads((ROOT/ref["path"]).read_bytes())
        fifth = [e for e in r["reconstructed"] if e["accepted"]][4]
        extremum = min(r["extrema"], key=lambda e: abs(e["time"]-fifth["time"]))
        result.append(dict(**s, seed_time=extremum["time"], seed_extremum=extremum))
    return result


def evaluate_root(result, sides, p):
    if not result["converged"]:
        return dict(passed=False, reason=result["reason"], sides=[], square_root_ratio=None)
    root = result["trace"][-1]
    j = np.asarray(root["jacobian"])
    if len(sides) != 4 or [r["dose"] for r in sides] != DOSES:
        raise ValueError("complete side matrix differs")
    verdicts = [side_verdict(r["report"], root, r["dose"], p) for r in sides]
    pair = [v for v in verdicts if v["expected_roots"] == 2]
    ratio = None
    if len(pair) == 2 and all(v["separation"] is not None and v["separation"] > 0 for v in pair):
        pair.sort(key=lambda v:abs(v["dose"]))
        ratio = pair[1]["separation"]/pair[0]["separation"]
    passed = abs(j[0,0]) >= p["minimum_unfolding"] and abs(j[1,1]) >= p["minimum_curvature"] and all(v["passed"] for v in verdicts) and ratio is not None and abs(ratio/np.sqrt(10)-1) <= p["square_root_ratio_relative_error"]
    return dict(passed=bool(passed), root=root, sides=verdicts, square_root_ratio=ratio)


def compare_case(case, rows, p):
    if len(rows) != 2 or [r["method"] for r in rows] != p["solvers"]:
        raise ValueError("solver matrix differs")
    verdicts = [dict(method=r["method"], **evaluate_root(r["shooting"], r["sides"], p)) for r in rows]
    agreement = None
    if all(r["shooting"]["converged"] for r in rows):
        a,b = [r["shooting"]["trace"][-1] for r in rows]
        agreement = dict(delta=abs(a["delta"]-b["delta"]), time=abs(a["time"]-b["time"]),
                         scaled_state=float(np.max(np.abs((np.asarray(a["state"])-b["state"])/p["scales"]))))
    passed = all(v["passed"] for v in verdicts) and agreement is not None and all(agreement[k] <= p["solver_"+k] for k in agreement)
    return dict(case=case, passed=bool(passed), solver_agreement=agreement, solvers=verdicts)


def controls(p):
    p = dict(p, accepted_prefix=0)
    rhs = lambda t,q:np.array([1.,2*q[0],0.])
    jac = lambda t,q:np.array([[0.,0.,0.],[2.,0.,0.],[0.,0.,0.]])
    section = PoincareSection((0.,1.,0.),0.,-1)
    rows = []
    for method in p["solvers"]:
        root = shoot(rhs,jac,[-.5,.25001,0.],[0.,1.,0.],section,.498,method=method,plan=p,retain=lambda *_:None)
        sides = []
        if root["converged"]:
            final = root["trace"][-1]
            for dose in DOSES:
                report,_ = collect(rhs,jac,[-.5,.25001+final["delta"]+dose,0.],[0.,1.,0.],section,
                    method=method,horizon=1.,**{k:p[k] for k in ("max_step", "rtol", "atol", "guard", "extremum_margin")})
                sides.append(dict(dose=dose,report=report))
        verdict = evaluate_root(root,sides,p)
        exact = root["converged"] and abs(root["trace"][-1]["delta"]+1e-5) <= 1e-10 and abs(root["trace"][-1]["time"]-.5) <= 1e-9
        rows.append(dict(method=method,shooting=root,sides=sides,verdict=verdict,passed=bool(exact and verdict["passed"])))
    return rows


def audit(output, anchor):
    p = json.loads(PLAN.read_bytes())
    validate_plan(p)
    if sha256(output/"summary.json") != anchor:
        raise ValueError("summary changed")
    saved = json.loads((output/"summary.json").read_bytes())
    b = json.loads((output/"binding.json").read_bytes())
    if saved["status"] != "completed" or saved["binding"] != b or b["sources"] != {s:sha256(ROOT/s) for s in SOURCES} or b["plan_sha256"] != sha256(PLAN) or inventory(output,omit=("summary.json",)) != saved["files"]:
        raise ValueError("source/inventory differs")
    selection = selection_for(p)
    if json.loads((output/"selection.json").read_bytes()) != selection:
        raise ValueError("selection differs")
    cs = json.loads((output/"controls.json").read_bytes())
    if [c["method"] for c in cs] != p["solvers"] or not all(c["passed"] for c in cs):
        raise ValueError("controls incomplete")
    for c in cs:
        r = c["shooting"]["trace"][-1]
        if evaluate_root(c["shooting"],c["sides"],dict(p,accepted_prefix=0)) != c["verdict"] or not c["verdict"]["passed"] or abs(r["delta"]+1e-5) > 1e-10 or abs(r["time"]-.5) > 1e-9:
            raise ValueError("control decisions differ")
    expected = {"binding.json", "selection.json", "controls.json"}
    cases, calls = [], 0
    for s in selection:
        rows = []
        par = RosslerParameters(**s["parameters"])
        section = replace(legacy_rossler_section(par),direction=-1)
        for method in p["solvers"]:
            label = s["case"]+"--"+method
            expected.update((label+".json",label+"-started.json"))
            row = json.loads((output/(label+".json")).read_bytes())
            if row["method"] != method:
                raise ValueError("method identity differs")
            shooting = row["shooting"]
            if len(shooting["raw_files"]) != len(shooting["trace"]) or not 1 <= len(shooting["trace"]) <= 8:
                raise ValueError("shooting trace incomplete")
            delta, end = 0., s["seed_time"]
            for i, (v, name) in enumerate(zip(shooting["trace"], shooting["raw_files"],strict=True)):
                if name != f"{label}--newton-{i}.npz" or v["delta"] != delta or v["time"] != end:
                    raise ValueError("Newton sequence differs")
                expected.add(name)
                calls += 1
                with np.load(output/name,allow_pickle=False) as raw:
                    t,q = raw["integration_times"],raw["integration_augmented_states"]
                    initial = np.r_[np.asarray(s["initial_state"])+delta*np.asarray(s["initial_tangent"]),s["initial_tangent"]]
                    if q.shape != (len(t),6) or not np.isfinite(q).all() or not np.all(np.diff(t)>0) or t[0] != 0 or t[-1] != end or not np.array_equal(q[0],initial) or not np.array_equal(q[-1],np.r_[v["state"],v["raw_tangent"]]):
                        raise ValueError("raw fixed-time endpoint differs")
                x,y,z = v["state"]
                f = np.array([-y-z,x+par.a*y,par.b+z*(x-par.c)])
                w = np.asarray(v["raw_tangent"])
                residual = [y-section.offset,f[1]]
                matrix = np.array([[w[1],f[1]],[w[0]+par.a*w[1],f[0]+par.a*f[1]]])
                if not np.allclose(v["residual"],residual,rtol=0,atol=1e-13) or not np.allclose(v["jacobian"],matrix,rtol=1e-14,atol=1e-12):
                    raise ValueError("separate grazing algebra differs")
                if "newton_step" in v:
                    step = np.linalg.solve(matrix,residual)
                    if not np.allclose(step,v["newton_step"],rtol=1e-12,atol=1e-15):
                        raise ValueError("Newton correction differs")
                    delta,end = float(delta-v["newton_step"][0]),float(end-v["newton_step"][1])
            if shooting["converged"]:
                r = shooting["trace"][-1]
                if abs(r["residual"][0]) > p["root_plane"] or abs(r["residual"][1]) > p["root_velocity"] or abs(r["delta"]) > p["delta_bound"] or abs(r["time"]-s["seed_time"]) > p["time_bound"]:
                    raise ValueError("root qualification differs")
                for i, side in enumerate(row["sides"]):
                    name = f"{label}--side-{i}.npz"
                    expected.add(name)
                    calls += 1
                    shifted = dict(s, initial_state=(np.asarray(s["initial_state"])+(r["delta"]+side["dose"])*np.asarray(s["initial_tangent"])).tolist())
                    report = side["report"]
                    if report["method"] != method or any(report[k] != p[k] for k in ("rtol","atol","max_step","horizon","guard")):
                        raise ValueError("side configuration differs")
                    validate_geometry(report,output/name,shifted,p)
            elif row["sides"] or row["skipped_doses"] != DOSES:
                raise ValueError("failed root sides not marked skipped")
            rows.append(row)
        cases.append(compare_case(s["case"],rows,p))
    marker = ROOT/"artifacts/EXP-489/target-once.json"
    if cases != saved["cases"] or set(saved["files"]) != expected or calls != saved["target_integrations"] or calls > 48 or sha256(marker) != saved["marker_sha256"] or json.loads(marker.read_bytes()) != b:
        raise ValueError("matrix/decision/marker differs")
    return dict(experiment_id="EXP-489",status="completed-audited",source_commit=b["source_commit"],summary_sha256=anchor,
                target_integrations=calls,cases=cases,elapsed_seconds=saved["elapsed_seconds"],paid_review="not_run",
                same_agent_local_audit=True,claim_boundary=p["claim_boundary"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--audit-run",type=Path)
    parser.add_argument("--expected-summary-sha256")
    args = parser.parse_args()
    if args.audit_run:
        result = audit(args.audit_run,args.expected_summary_sha256)
        args.output_dir.mkdir(parents=True,exist_ok=False)
        write_json(args.output_dir/"summary.json",result)
        print(json.dumps([dict(case=c["case"],passed=c["passed"]) for c in result["cases"]]))
        return
    output = args.output_dir.resolve()
    if ROOT/"artifacts/EXP-489" not in output.parents:
        parser.error("fresh EXP-489 output required")
    if subprocess.check_output(["git","status","--porcelain"],text=True).strip():
        parser.error("clean source required")
    source = subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    if source != subprocess.check_output(["git","rev-parse","@{upstream}"],text=True).strip():
        parser.error("push exact source first")
    p = json.loads(PLAN.read_bytes())
    validate_plan(p)
    output.mkdir(parents=True,exist_ok=False)
    binding = dict(source_commit=source,plan_sha256=sha256(PLAN),sources={s:sha256(ROOT/s) for s in SOURCES},
                   started_utc=utc(),runtime=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__))
    write_json(output/"binding.json",binding)
    started = time.monotonic()
    calls = 0
    def timeout(*_):
        raise TimeoutError("EXP-489 wall limit")
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p["limits"]["wall_seconds"])
    def retain(name,raw):
        nonlocal calls
        if calls >= 48 or sum(f.stat().st_size for f in output.iterdir() if f.is_file()) > p["limits"]["output_bytes"]-16777216:
            raise RuntimeError("target integration/output cap")
        with (output/name).open("xb") as stream:
            np.savez_compressed(stream,**raw)
        calls += 1
    try:
        selection = selection_for(p)
        write_json(output/"selection.json",selection)
        c = controls(p)
        write_json(output/"controls.json",c)
        if not all(v["passed"] for v in c):
            raise ValueError("controls failed; no targets")
        marker = ROOT/"artifacts/EXP-489/target-once.json"
        write_json(marker,binding)
        cases = []
        for s in selection:
            par = RosslerParameters(**s["parameters"])
            section = replace(legacy_rossler_section(par),direction=-1)
            rhs,jac = lambda t,q:rossler_rhs(t,q,par), lambda t,q:rossler_jacobian(q,par)
            rows = []
            for method in p["solvers"]:
                label = s["case"]+"--"+method
                write_json(output/(label+"-started.json"),dict(case=s["case"],method=method,started_utc=utc()))
                names = []
                def keep(i,raw):
                    name = f"{label}--newton-{i}.npz"
                    retain(name,raw)
                    names.append(name)
                root = shoot(rhs,jac,s["initial_state"],s["initial_tangent"],section,s["seed_time"],method=method,plan=p,retain=keep)
                root["raw_files"] = names
                sides = []
                if root["converged"]:
                    for i,dose in enumerate(DOSES):
                        initial = np.asarray(s["initial_state"])+(root["trace"][-1]["delta"]+dose)*np.asarray(s["initial_tangent"])
                        report,raw = collect(rhs,jac,initial,s["initial_tangent"],section,method=method,
                            **{k:p[k] for k in ("rtol","atol","max_step","horizon","guard","extremum_margin")})
                        retain(f"{label}--side-{i}.npz",raw)
                        sides.append(dict(dose=dose,report=report))
                row = dict(method=method,shooting=root,sides=sides,skipped_doses=[] if root["converged"] else DOSES)
                write_json(output/(label+".json"),row)
                rows.append(row)
                print(label+": completed",flush=True)
            cases.append(compare_case(s["case"],rows,p))
        write_json(output/"summary.json",dict(status="completed",binding=binding,cases=cases,target_integrations=calls,
            elapsed_seconds=time.monotonic()-started,completed_utc=utc(),files=inventory(output),marker_sha256=sha256(marker)))
        print(json.dumps([dict(case=c["case"],passed=c["passed"]) for c in cases]))
    except (Exception,KeyboardInterrupt) as e:
        write_json(output/"failure.json",dict(error_type=type(e).__name__,message=str(e),utc=utc(),target_integrations=calls))
        raise
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()

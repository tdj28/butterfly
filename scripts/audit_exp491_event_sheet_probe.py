#!/usr/bin/env python3
"""Read-only complete-matrix/raw-geometry audit of EXP-491."""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
import numpy as np
from butterfly._paired_startup import inventory,sha256,write_json
from butterfly.models import RosslerParameters,rossler_rhs
from butterfly.poincare import PoincareSection,legacy_rossler_section
from butterfly.event_sheet_probe import profile,pair,interval
from scripts import run_exp491_event_sheet_probe as run
from scripts.run_exp486_return_image_folds import control_field
from scripts.run_exp488_event_accuracy import validate_geometry


def independent_derivatives(derived,report,rhs):
    if derived["status"] != "returned":
        return
    raw = [e for e in report["reconstructed"] if e["accepted"]][:len(derived["events"])]
    for i,(event,e) in enumerate(zip(derived["events"],raw,strict=True)):
        vx,vy,vz = e["raw_tangent"]
        fx,fy,fz = rhs(e["time"],np.asarray(e["state"]))
        tau = -vy/fy
        corrected = [vx+fx*tau,vy+fy*tau,vz+fz*tau]
        if event["time"] != e["time"] or event["state"] != e["state"] or not np.allclose(event["tangent"],corrected,rtol=1e-12,atol=1e-10) or abs(derived["time_gradients"][i]-tau) > 1e-12*max(1.,abs(tau)):
            raise ValueError("independent event sensitivity arithmetic differs")


def check_controls(rows,plan):
    if [r["spec"] for r in rows] != run.control_specs() or not all(r["passed"] for r in rows):
        raise ValueError("complete analytic control matrix required")
    count = 0
    section = PoincareSection((0.,1.,0.),0.,-1)
    for row in rows:
        s = row["spec"]
        rhs,_ = run.grazing_field() if s["kind"].startswith("grazing") else control_field(0. if s["kind"] == "regular-no-fold" else 1e4)
        points = []
        for u,reports in zip(s["us"],row["reports"],strict=True):
            if len(reports) != 2 or [r["method"] for r in reports] != ["DOP853","Radau"]:
                raise ValueError("control solver matrix differs")
            profiles = []
            for report in reports:
                count += 1
                initial = (np.asarray(s["initial_state"])+u*np.asarray(s["initial_tangent"])).tolist()
                if report["initial_state"] != initial or report["initial_tangent"] != s["initial_tangent"] or report["guard"] != s["guard"] or report["horizon"] != s["horizon"] or any(report[k] != plan[k] for k in ("rtol","atol","max_step")):
                    raise ValueError("control numerical contract differs")
                selected = [e for e in report["reconstructed"] if e["accepted"]]
                expected_times = ([1.,3-np.sqrt(-u),4.] if u < 0 else [1.,4.]) if s["kind"].startswith("grazing") else [2*np.pi*(i+1) for i in range(s["count"])]
                # At exact tangency the numerical count is uncertain, never certified.
                checked = [e for e in selected if not (s["kind"] == "grazing-tangency" and u == 0 and abs(e["time"]-3.) < 1e-4)]
                if len(checked) != len(expected_times) or not np.allclose([e["time"] for e in checked],expected_times,rtol=0,atol=1e-7):
                    raise ValueError("analytic event times differ")
                derived = profile(report,s,rhs,section,plan)
                independent_derivatives(derived,report,rhs)
                if derived["status"] == "returned":
                    if s["kind"].startswith("grazing"):
                        expected_gradient = [0.,1/(2*np.sqrt(-u))] if u < 0 else [0.,0.]
                    else:
                        expected_gradient = [0.]*s["count"]
                    if not np.allclose(derived["time_gradients"],expected_gradient,rtol=1e-7,atol=1e-7):
                        raise ValueError("analytic return-time derivative differs")
                profiles.append(derived)
            points.append(pair(profiles,plan))
        analysis = interval(points,s["us"],plan)
        if points != row["points"] or analysis != row["analysis"] or not run.control_expectation(s,points,analysis,row["reports"]):
            raise ValueError("control decision replay differs")
    if count != 48:
        raise ValueError("48 analytic control profiles required")


def audit(output,anchor):
    if sha256(output/"summary.json") != anchor:
        raise ValueError("completed summary anchor differs")
    saved = json.loads((output/"summary.json").read_bytes())
    plan = json.loads(run.PLAN.read_bytes())
    candidates,previous = run.load(plan)
    b = json.loads((output/"binding.json").read_bytes())
    if saved["status"] != "completed" or saved["binding"] != b or b["sources"] != {s:sha256(ROOT/s) for s in run.SOURCES} or b["plan_sha256"] != sha256(run.PLAN) or b["candidates_sha256"] != plan["candidates_sha256"] or b["parent_receipt_sha256"] != plan["parent_receipt_sha256"] or inventory(output,omit=("summary.json",)) != saved["files"]:
        raise ValueError("source/input/output binding differs")
    check_controls(json.loads((output/"controls.json").read_bytes()),plan)
    expected = {"binding.json","controls.json"}
    results = []
    calls = 0
    for c,old in zip(candidates,previous["candidates"],strict=True):
        par = RosslerParameters(**c["parameters"])
        rhs = lambda t,q:rossler_rhs(t,q,par)
        section = replace(legacy_rossler_section(par),direction=-1)
        points = []
        us = run.sample_values(c)
        for i,u in enumerate(us):
            profiles = []
            for method in plan["solvers"]:
                label = f"{c['id']}--sample-{i}--{method}"
                expected.update(label+s for s in ("-started.json",".json",".npz"))
                row = json.loads((output/(label+".json")).read_bytes())
                start = json.loads((output/(label+"-started.json")).read_bytes())
                if {k:start[k] for k in ("candidate_id","sample_index","method","u")} != dict(candidate_id=c["id"],sample_index=i,method=method,u=u) or not b["started_utc"] <= start["started_utc"] <= saved["completed_utc"]:
                    raise ValueError("profile identity/start differs")
                report = row["report"]
                if report["method"] != method or report["horizon"] != c["horizon"] or any(report[k] != plan[k] for k in ("rtol","atol","max_step","guard")):
                    raise ValueError("target numerical settings differ")
                initial = (np.asarray(c["initial_state"])+u*np.asarray(c["initial_tangent"])).tolist()
                validate_geometry(report,output/(label+".npz"),dict(c,initial_state=initial),dict(plan,horizon=c["horizon"]))
                derived = profile(report,c,rhs,section,plan)
                independent_derivatives(derived,report,rhs)
                if derived != row["profile"]:
                    raise ValueError("profile derivation differs")
                profiles.append(derived)
                calls += 1
            points.append(pair(profiles,plan))
        results.append(dict(id=c["id"],family_id=c["family_id"],case=c["case"],region=c["region"],us=us,
                            prior_fold_qualified=old["qualified"],points=points,analysis=interval(points,us,plan)))
    marker = ROOT/"artifacts/EXP-491/target-once.json"
    if calls != 156 or saved["target_trajectories"] != calls or results != saved["candidates"] or set(saved["files"]) != expected or sha256(marker) != saved["marker_sha256"] or json.loads(marker.read_bytes()) != b:
        raise ValueError("complete matrix, primary decisions or marker differs")
    return dict(experiment_id="EXP-491",status="completed-audited",source_commit=b["source_commit"],summary_sha256=anchor,
                candidates=results,target_trajectories=calls,elapsed_seconds=saved["elapsed_seconds"],
                same_agent_local_audit=True,paid_review="not_run",claim_boundary=plan["claim_boundary"])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run",type=Path,required=True)
    p.add_argument("--expected-summary-sha256",required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a = p.parse_args()
    result = audit(a.run,a.expected_summary_sha256)
    a.output_dir.mkdir(parents=True,exist_ok=False)
    write_json(a.output_dir/"summary.json",result)
    print(json.dumps(dict(candidates=len(result["candidates"]),screened_regular=sum(r["analysis"]["screened_regular"] for r in result["candidates"]))))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Read-only EXP-490 inventory, independent fold algebra and decision replay."""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
import numpy as np
from butterfly._paired_startup import sha256,inventory,write_json
from butterfly.models import RosslerParameters,rossler_rhs
from butterfly.poincare import legacy_rossler_section,PoincareSection
from butterfly.projected_fold_qualification import qualify,compare
from scripts import run_exp490_direct_folds as run
from scripts.run_exp486_return_image_folds import control_field
from scripts.run_exp488_event_accuracy import validate_geometry


def separate_algebra(row,parameters,offset):
    x,y,z = row["state"]
    vx,vy,vz = row["first"]
    wx,wy,_ = row["second"]
    a,b,c = parameters.a,parameters.b,parameters.c
    fx,fy,fz = -y-z,x+a*y,b+z*(x-c)
    jvx,jvy = -vy-vz,vx+a*vy
    jfx,jfy = -fy-fz,fx+a*fy
    g = fy*vx-fx*vy
    gu = jvy*vx+fy*wx-jvx*vy-fx*wy
    gt = jfy*vx+fy*jvx-jfx*vy-fx*jvy
    scale = max(1.,float(np.linalg.norm([fx,fy,fz])*np.linalg.norm([vx,vy,vz])))
    return np.array([y-offset,g]),np.array([[vy,fy],[gu,gt]]),scale


def check_trace(shooting,c,method,p,output,label,par,section):
    trace = shooting["trace"]
    expected = [f"newton-{i}" for i in range(len(trace))]
    if not 1 <= len(trace) <= 8 or shooting["retained_labels"] != expected:
        raise ValueError("incomplete Newton trajectory inventory")
    u,t = c["seed_u"],c["seed_time"]
    names = []
    for i,r in enumerate(trace):
        if r["iteration"] != i or r["u"] != u or r["time"] != t or not c["u_box"][0] <= u <= c["u_box"][1] or not c["time_box"][0] <= t <= c["time_box"][1]:
            raise ValueError("Newton iterate differs from fixed update/box")
        name = f"{label}--newton-{i}.npz"
        names.append(name)
        with np.load(output/name,allow_pickle=False) as raw:
            times,states = raw["integration_times"],raw["integration_augmented_states"]
            initial = np.r_[np.asarray(c["initial_state"])+u*np.asarray(c["initial_tangent"]),c["initial_tangent"],np.zeros(3)]
            if r.get("integration_failed"):
                if i != len(trace)-1 or shooting["converged"] or shooting["reason"] != "integration failed" or states.shape != (len(times),9) or not np.isfinite(times).all() or not np.all(np.diff(times)>0) or times[0] != 0 or times[-1] != r["observed_last_time"] or times[-1] > t or np.isfinite(states).all() != r["finite_states"] or not np.array_equal(states[0],initial):
                    raise ValueError("incomplete integration failure evidence")
                return names
            if states.shape != (len(times),9) or not np.isfinite(states).all() or not np.isfinite(times).all() or not np.all(np.diff(times)>0) or times[0] != 0 or times[-1] != t or not np.array_equal(states[0],initial) or not np.array_equal(states[-1],np.r_[r["state"],r["first"],r["second"]]):
                raise ValueError("retained 9D endpoint identity differs")
        residual,matrix,scale = separate_algebra(r,par,section.offset)
        if not np.allclose(residual,r["residual"],rtol=1e-12,atol=1e-12) or not np.allclose(matrix,r["jacobian"],rtol=1e-12,atol=1e-10) or abs(r["determinant_scale"]-scale) > 1e-12*scale:
            raise ValueError("independent fold algebra differs")
        field = rossler_rhs(t,np.asarray(r["state"]),par)
        angle = abs(field[1])/np.linalg.norm(field)
        if abs(r["angle"]-angle) > 1e-12:
            raise ValueError("root angle differs")
        if "event_second_derivative" in r:
            first = np.asarray(r["first"])
            tau = -first[1]/field[1]
            moving = first+field*tau
            dvelocity = moving[0]+par.a*moving[1]
            curvature = (matrix[1,0]+matrix[1,1]*tau)/field[1]-residual[1]*dvelocity/field[1]**2
            if abs(curvature-r["event_second_derivative"]) > 1e-10*max(1.,abs(curvature)):
                raise ValueError("event curvature algebra differs")
        if "newton_step" in r:
            step = np.linalg.solve(matrix,residual)
            if not np.allclose(r["newton_step"],step,rtol=1e-10,atol=1e-12):
                raise ValueError("Newton arithmetic differs")
            u,t = float(u-r["newton_step"][0]),float(t-r["newton_step"][1])
    final = trace[-1]
    converged = abs(final["residual"][0]) <= p["root_plane"] and abs(final["residual"][1])/final["determinant_scale"] <= p["root_determinant"]
    if shooting["converged"] != converged:
        raise ValueError("Newton convergence label differs")
    if not converged:
        if shooting["reason"] == "fixed search box exceeded" and c["u_box"][0] <= u <= c["u_box"][1] and c["time_box"][0] <= t <= c["time_box"][1]:
            raise ValueError("unfounded search-box failure")
        if shooting["reason"] == "iteration limit" and len(trace) != p["iterations"]:
            raise ValueError("premature iteration stop")
    return names


def check_controls(controls,p):
    expected = [(count,kind,method) for count in (2,3) for kind in ("fold","no-fold","projection-degenerate") for method in ("DOP853","Radau")]
    if [(c["count"],c["kind"],c["method"]) for c in controls] != expected or not all(c["passed"] for c in controls):
        raise ValueError("analytic control matrix differs")
    section = PoincareSection((0.,1.,0.),0.,-1)
    for control in controls:
        count,kind = control["count"],control["kind"]
        total = 2*np.pi*count
        exact = 1/(2*(1-np.exp(-.06*total)))-.5
        candidate = dict(count=count,epsilon=1e-6,old_x_interval=[-100.,100.])
        result = control["result"]
        rhs,_ = control_field(1e4 if kind == "fold" else 0.)
        q = qualify(result["shooting"],result["censuses"],candidate,rhs,section,p)
        if q != result["qualification"] or q["qualified"] != (kind == "fold"):
            raise ValueError("control qualification replay differs")
        if kind == "fold":
            r = result["shooting"]["trace"][-1]
            if abs(r["u"]-exact) > 1e-8 or abs(r["time"]-total) > 1e-7 or abs(r["event_second_derivative"]+2*(1-np.exp(-.06*total))) > 1e-8:
                raise ValueError("analytic fold/curvature value differs")


def audit(output,anchor):
    if sha256(output/"summary.json") != anchor:
        raise ValueError("completed summary anchor changed")
    saved = json.loads((output/"summary.json").read_bytes())
    p = json.loads(run.PLAN.read_bytes())
    candidates = json.loads((ROOT/p["candidates_path"]).read_bytes())
    run.validate_candidates(candidates,p)
    b = json.loads((output/"binding.json").read_bytes())
    if saved["status"] != "completed" or saved["binding"] != b or b["sources"] != {s:sha256(ROOT/s) for s in run.SOURCES} or b["plan_sha256"] != sha256(run.PLAN) or b["candidates_sha256"] != sha256(ROOT/p["candidates_path"]) or inventory(output,omit=("summary.json",)) != saved["files"]:
        raise ValueError("source/input/output binding differs")
    check_controls(json.loads((output/"controls.json").read_bytes()),p)
    expected = {"binding.json","controls.json"}
    results,calls = [],0
    for c in candidates:
        rows = []
        par = RosslerParameters(**c["parameters"])
        section = replace(legacy_rossler_section(par),direction=-1)
        rhs = lambda t,q:rossler_rhs(t,q,par)
        for method in p["solvers"]:
            label = c["id"]+"--"+method
            expected.update((label+".json",label+"-started.json"))
            row = json.loads((output/(label+".json")).read_bytes())
            start = json.loads((output/(label+"-started.json")).read_bytes())
            if row["method"] != method or start["method"] != method or start["candidate_id"] != c["id"] or not b["started_utc"] <= start["started_utc"] <= saved["completed_utc"]:
                raise ValueError("profile/start identity differs")
            names = check_trace(row["shooting"],c,method,p,output,label,par,section)
            expected.update(names)
            calls += len(names)
            if row["shooting"]["converged"]:
                u = row["shooting"]["trace"][-1]["u"]
                eligible = c["u_box"][0] <= u-c["epsilon"] < u+c["epsilon"] <= c["u_box"][1]
                if eligible and len(row["censuses"]) != 3 or not eligible and row["censuses"]:
                    raise ValueError("prescribed census eligibility differs")
            elif row["censuses"]:
                raise ValueError("unconverged shooting acquired censuses")
            for i,census in enumerate(row["censuses"]):
                name = f"{label}--census-{i}.npz"
                expected.add(name)
                calls += 1
                report = census["report"]
                initial = np.asarray(c["initial_state"])+(u+census["offset"])*np.asarray(c["initial_tangent"])
                shifted = dict(c,initial_state=initial.tolist())
                if report["method"] != method or any(report[k] != p[k] for k in ("rtol","atol","max_step","guard")) or report["horizon"] != c["horizon"]:
                    raise ValueError("census configuration differs")
                validate_geometry(report,output/name,shifted,dict(p,horizon=c["horizon"]))
            qualification = qualify(row["shooting"],row["censuses"],c,rhs,section,p)
            if qualification != row["qualification"]:
                raise ValueError("qualification replay differs")
            rows.append(row)
        results.append(compare(c,rows,p))
    marker = ROOT/"artifacts/EXP-490/target-once.json"
    if results != saved["candidates"] or calls != saved["target_trajectories"] or calls > 572 or set(saved["files"]) != expected or sha256(marker) != saved["marker_sha256"] or json.loads(marker.read_bytes()) != b:
        raise ValueError("complete matrix/decisions/marker differs")
    families = [dict(family_id=f,qualified=sum(r["qualified"] for r in results if r["family_id"]==f),
                     in_region=sum(r["qualified_in_region"] for r in results if r["family_id"]==f),
                     unresolved=sum(not r["qualified"] for r in results if r["family_id"]==f)) for f in dict.fromkeys(c["family_id"] for c in candidates)]
    return dict(experiment_id="EXP-490",status="completed-audited",source_commit=b["source_commit"],
        summary_sha256=anchor,candidates=results,families=families,target_trajectories=calls,
        elapsed_seconds=saved["elapsed_seconds"],same_agent_local_audit=True,paid_review="not_run",claim_boundary=p["claim_boundary"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path,required=True)
    parser.add_argument("--expected-summary-sha256",required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    a = parser.parse_args()
    result = audit(a.run,a.expected_summary_sha256)
    a.output_dir.mkdir(parents=True,exist_ok=False)
    write_json(a.output_dir/"summary.json",result)
    print(json.dumps(result["families"]))


if __name__ == "__main__":
    main()

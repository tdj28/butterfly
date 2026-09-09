#!/usr/bin/env python3
"""All-candidate direct projected-fold pilot; no paid services or old retries."""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
import numpy as np
import scipy
from butterfly._paired_startup import write_json,sha256,inventory
from butterfly.models import RosslerParameters,rossler_rhs,rossler_jacobian
from butterfly.poincare import PoincareSection,legacy_rossler_section
from butterfly.section_census import collect
from butterfly.projected_fold_shooting import shoot
from butterfly.projected_fold_qualification import qualify,compare
from scripts.run_exp486_return_image_folds import control_field
from scripts.run_exp488_event_accuracy import utc,validate_geometry
from scripts import audit_exp486_return_image_folds as parent

PLAN = ROOT/"experiments/manifests/EXP-490-direct-folds.json"
SOURCES = ("scripts/run_exp490_direct_folds.py","scripts/audit_exp490_direct_folds.py",
           "python/butterfly/projected_fold_shooting.py","python/butterfly/projected_fold_qualification.py",
           "python/butterfly/section_census.py","python/butterfly/return_geometry.py",
           "python/butterfly/return_image_curve.py","python/butterfly/models.py","python/butterfly/poincare.py",
           "python/butterfly/_paired_startup.py","scripts/run_exp486_return_image_folds.py",
           "scripts/run_exp488_event_accuracy.py")


def load_parent(p):
    if sha256(ROOT/p["parent_receipt"]) != p["parent_receipt_sha256"]:
        raise ValueError("parent receipt changed")
    return json.loads((ROOT/p["parent_receipt"]).read_bytes())


def build_candidates(p):
    d = load_parent(p)
    audited = parent.audit(ROOT/p["parent_run"],p["parent_summary_sha256"],d["source_commit"])
    if audited != d:
        raise ValueError("parent replay differs")
    candidates = []
    for family in d["families"]:
        row = next(r for r in d["rows"] if r["family_id"] == family["id"])
        for ordinal,indices in enumerate(row["analysis"]["candidate_intervals"]):
            endpoints = []
            for i in indices:
                for m in p["solvers"]:
                    path = ROOT/p["parent_run"]/"trials"/f"{family['id']}--eval-{i:04d}--{m}.json"
                    raw = json.loads(path.read_bytes())
                    endpoints.append(dict(grid_index=i,method=m,time=raw["events"][-1]["time"],
                                          path=path.relative_to(ROOT).as_posix(),sha256=sha256(path)))
            box = [family["grid"][i] for i in indices]
            times = [e["time"] for e in endpoints]
            time_box = [min(times)-.5,max(times)+.5]
            candidates.append(dict(id=f"{family['id']}--candidate-{ordinal}",family_id=family["id"],
                case=family["case"],region=family["region"],count=family["depth"]+1,
                initial_state=family["initial_state"],initial_tangent=family["initial_tangent"],
                parameters=family["parameters"],old_x_interval=family["old_x_interval"],
                indices=indices,u_box=box,seed_u=float(np.mean(box)),seed_time=float(np.mean(times)),
                time_box=time_box,horizon=time_box[1]+2.,epsilon=min(1e-6,(box[1]-box[0])/100),
                historical_endpoints=endpoints))
    validate_candidates(candidates,p)
    return candidates


def validate_candidates(candidates,p):
    expected_settings = dict(solvers=["DOP853","Radau"],rtol=1e-13,atol=1e-15,max_step=.001,
        iterations=8,root_plane=1e-10,root_determinant=1e-10,guard=1e-8,extremum_margin=1e-10,
        scales=[15.,15.,.01],controls=dict(counts=[2,3],kinds=["fold","no-fold","projection-degenerate"]),
        thresholds=dict(angle=1e-7,plane=1e-8,time=1e-7,state=1e-6,minimum_gain=1e-4,
            minimum_x_component=.001,root_derivative=1e-7,curvature_relative_error=.001,
            minimum_scaled_curvature=1e-6,solver_u=1e-9))
    if any(p[k] != v for k,v in expected_settings.items()):
        raise ValueError("frozen numerical settings differ")
    d = load_parent(p)
    expected = []
    for f in d["families"]:
        r = next(r for r in d["rows"] if r["family_id"] == f["id"])
        expected += [(f,i,indices) for i,indices in enumerate(r["analysis"]["candidate_intervals"])]
    if len(candidates) != 26 or len(expected) != 26 or len({c["family_id"] for c in candidates}) != 16:
        raise ValueError("26-candidate/16-family matrix differs")
    for c,(f,i,indices) in zip(candidates,expected,strict=True):
        fixed = dict(id=f"{f['id']}--candidate-{i}",family_id=f["id"],case=f["case"],region=f["region"],
                     count=f["depth"]+1,initial_state=f["initial_state"],initial_tangent=f["initial_tangent"],
                     parameters=f["parameters"],old_x_interval=f["old_x_interval"],indices=indices,
                     u_box=[f["grid"][j] for j in indices])
        if any(c[k] != v for k,v in fixed.items()):
            raise ValueError("historical candidate identity differs")
        if [(e["grid_index"],e["method"]) for e in c["historical_endpoints"]] != [(j,m) for j in indices for m in ("DOP853","Radau")]:
            raise ValueError("historical endpoint matrix differs")
        times = [e["time"] for e in c["historical_endpoints"]]
        if not np.isfinite(times).all() or c["seed_u"] != float(np.mean(c["u_box"])) or c["seed_time"] != float(np.mean(times)) or c["time_box"] != [min(times)-.5,max(times)+.5] or c["horizon"] != max(times)+2.5 or c["epsilon"] != min(1e-6,np.ptp(c["u_box"])/100):
            raise ValueError("deterministic search settings differ")
    if p["solvers"] != ["DOP853","Radau"] or p["limits"]["shootings"] != 52 or p["limits"]["max_target_trajectories"] != 572:
        raise ValueError("complete solver matrix differs")


def run_candidate(c,method,p,rhs,jac,hvv,section,retain):
    names = []
    def keep(i,raw):
        label = f"newton-{i}"
        retain(label,raw)
        names.append(label)
    shooting = shoot(rhs,jac,hvv,c,section,method,p,keep)
    shooting["retained_labels"] = names
    censuses,skip = [],None
    if shooting["converged"]:
        u = shooting["trace"][-1]["u"]
        if not c["u_box"][0] <= u-c["epsilon"] < u+c["epsilon"] <= c["u_box"][1]:
            skip = "fixed finite-difference perturbation outside original bracket"
        else:
            for i,offset in enumerate((-c["epsilon"],0.,c["epsilon"])):
                initial = np.asarray(c["initial_state"])+(u+offset)*np.asarray(c["initial_tangent"])
                report,raw = collect(rhs,jac,initial,c["initial_tangent"],section,method=method,horizon=c["horizon"],
                    **{k:p[k] for k in ("rtol","atol","max_step","guard","extremum_margin")})
                retain(f"census-{i}",raw)
                censuses.append(dict(offset=offset,report=report))
    else:
        skip = shooting["reason"]
    return dict(method=method,shooting=shooting,censuses=censuses,census_skip_reason=skip,
                qualification=qualify(shooting,censuses,c,rhs,section,p))


def controls(p):
    rows = []
    section = PoincareSection((0.,1.,0.),0.,-1)
    for count in p["controls"]["counts"]:
        total = 2*np.pi*count
        exact = 1/(2*(1-np.exp(-.06*total)))-.5
        for kind in p["controls"]["kinds"]:
            # Affine-rescale the analytic z coordinate into the target metric.
            k = 1e4 if kind == "fold" else 0.
            tangent = [0.,0.,.01] if kind == "projection-degenerate" else [1.,0.,.01]
            c = dict(id="control",family_id="control",case="control",region=0,count=count,
                initial_state=[-4.,0.,.005],initial_tangent=tangent,old_x_interval=[-100.,100.],
                u_box=[exact-.04,exact+.02],seed_u=exact-.01,seed_time=total if kind == "projection-degenerate" else total+.01,
                time_box=[total-.5,total+.5],horizon=total+2.5,epsilon=1e-6)
            for method in p["solvers"]:
                rhs,jac = control_field(k)
                hvv = lambda t,q,v:np.array([-4*k*.03*v[2]**2,-2*k*v[2]**2,0.])
                result = run_candidate(c,method,p,rhs,jac,hvv,section,lambda *_:None)
                passed = result["qualification"]["qualified"] == (kind == "fold")
                if kind == "fold":
                    passed &= result["shooting"]["converged"] and abs(result["shooting"]["trace"][-1]["u"]-exact) <= 1e-8
                rows.append(dict(kind=kind,count=count,method=method,passed=bool(passed),result=result))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--prepare",action="store_true")
    args = parser.parse_args()
    p = json.loads(PLAN.read_bytes())
    if args.prepare:
        args.output_dir.mkdir(parents=True,exist_ok=False)
        write_json(args.output_dir/"candidates.json",build_candidates(p))
        return
    output = args.output_dir.resolve()
    if ROOT/"artifacts/EXP-490" not in output.parents:
        parser.error("fresh EXP-490 output required")
    if subprocess.check_output(["git","status","--porcelain"],text=True).strip():
        parser.error("clean source required")
    source = subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    if source != subprocess.check_output(["git","rev-parse","@{upstream}"],text=True).strip():
        parser.error("push source first")
    if shutil.disk_usage(ROOT).free < p["limits"]["initial_free_bytes"]:
        parser.error("initial free-space reserve insufficient")
    candidates = json.loads((ROOT/p["candidates_path"]).read_bytes())
    validate_candidates(candidates,p)
    output.mkdir(parents=True,exist_ok=False)
    binding = dict(source_commit=source,started_utc=utc(),plan_sha256=sha256(PLAN),
        candidates_sha256=sha256(ROOT/p["candidates_path"]),sources={s:sha256(ROOT/s) for s in SOURCES},
        runtime=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__))
    write_json(output/"binding.json",binding)
    started = time.monotonic()
    calls,bytes_written = 0,0
    def timeout(*_):
        raise TimeoutError("EXP-490 wall limit")
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p["limits"]["wall_seconds"])
    try:
        c = controls(p)
        write_json(output/"controls.json",c)
        if not all(r["passed"] for r in c):
            raise ValueError("analytic controls failed; no targets")
        marker = ROOT/"artifacts/EXP-490/target-once.json"
        write_json(marker,binding)
        results = []
        for candidate in candidates:
            par = RosslerParameters(**candidate["parameters"])
            rhs,jac = lambda t,q:rossler_rhs(t,q,par),lambda t,q:rossler_jacobian(q,par)
            hvv = lambda t,q,v:np.array([0.,0.,2*v[0]*v[2]])
            section = replace(legacy_rossler_section(par),direction=-1)
            rows = []
            for method in p["solvers"]:
                label = candidate["id"]+"--"+method
                write_json(output/(label+"-started.json"),dict(candidate_id=candidate["id"],method=method,started_utc=utc()))
                def retain(suffix,raw):
                    nonlocal calls,bytes_written
                    if calls >= 572 or bytes_written > p["limits"]["output_bytes"]-33554432 or shutil.disk_usage(ROOT).free < p["limits"]["minimum_free_bytes"]:
                        raise RuntimeError("trajectory/storage reserve reached")
                    path = output/f"{label}--{suffix}.npz"
                    with path.open("xb") as stream:
                        np.savez_compressed(stream,**raw)
                    calls += 1
                    bytes_written += path.stat().st_size
                row = run_candidate(candidate,method,p,rhs,jac,hvv,section,retain)
                write_json(output/(label+".json"),row)
                bytes_written += (output/(label+".json")).stat().st_size
                rows.append(row)
                print(label+": completed",flush=True)
            results.append(compare(candidate,rows,p))
        write_json(output/"summary.json",dict(status="completed",binding=binding,candidates=results,
            target_trajectories=calls,elapsed_seconds=time.monotonic()-started,completed_utc=utc(),
            files=inventory(output),marker_sha256=sha256(marker)))
        print(json.dumps(dict(completed_candidates=len(results),qualified=sum(r["qualified"] for r in results),target_trajectories=calls)))
    except (Exception,KeyboardInterrupt) as e:
        write_json(output/"failure.json",dict(error_type=type(e).__name__,message=str(e),utc=utc(),target_trajectories=calls))
        raise
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()

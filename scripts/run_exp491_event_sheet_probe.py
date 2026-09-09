#!/usr/bin/env python3
"""Fixed three-point census at every EXP-490 candidate; no target root retries."""
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
from butterfly._paired_startup import inventory,sha256,write_json
from butterfly.models import RosslerParameters,rossler_rhs,rossler_jacobian
from butterfly.poincare import PoincareSection,legacy_rossler_section
from butterfly.section_census import collect
from butterfly.event_sheet_probe import profile,pair,interval
from scripts.run_exp486_return_image_folds import control_field
from scripts.run_exp488_event_accuracy import utc
from scripts import run_exp490_direct_folds as parent

PLAN = ROOT/"experiments/manifests/EXP-491-event-sheet-probe.json"
SOURCES = ("scripts/run_exp491_event_sheet_probe.py","scripts/audit_exp491_event_sheet_probe.py",
    "python/butterfly/event_sheet_probe.py","python/butterfly/projected_fold_qualification.py",
    "python/butterfly/section_census.py","python/butterfly/return_geometry.py","python/butterfly/return_image_curve.py",
    "python/butterfly/models.py","python/butterfly/poincare.py","python/butterfly/_paired_startup.py",
    "scripts/run_exp486_return_image_folds.py","scripts/run_exp488_event_accuracy.py","scripts/run_exp490_direct_folds.py",
    "experiments/manifests/EXP-490-direct-folds.json","tests/test_event_sheet_probe.py",
    "docs/experiments/EXP-491-event-sheet-probe.md","pyproject.toml","uv.lock")


def load(plan):
    expected = dict(solvers=["DOP853","Radau"],fractions=[0.,.5,1.],rtol=1e-13,atol=1e-15,max_step=.001,
        guard=1e-8,extremum_margin=1e-10,scales=[15.,15.,.01],
        thresholds=dict(angle=1e-7,plane=1e-8,state=1e-6,time=1e-7,tangent_relative=1e-5,time_gradient_relative=1e-5,
                        minimum_gain=1e-4,minimum_x_component=.001,adjacent_time=1.,time_prediction=.25),
        limits=dict(candidates=26,families=16,samples=78,target_trajectories=156,control_profiles=48,wall_seconds=7200,
                    output_bytes=8589934592,initial_free_bytes=17179869184,minimum_free_bytes=8589934592))
    if any(plan[k] != v for k,v in expected.items()):
        raise ValueError("frozen numerical/matrix/resource settings differ")
    anchors = dict(candidates=("experiments/manifests/EXP-490-candidates.json","f7ef9d69bad22cd0ce8ca3c112e4c4d2c420ac247c0d3187359a33cc71329fea"),
                   parent=("docs/experiments/receipts/EXP-490-direct-fold-result.json","ec74b11f2e9784ab990d142e3df36e7c500f3235faeefc92afdca50778e88b66"))
    for role,(path,anchor) in anchors.items():
        path_key = "candidates_path" if role == "candidates" else "parent_receipt"
        hash_key = "candidates_sha256" if role == "candidates" else "parent_receipt_sha256"
        if plan[path_key] != path or plan[hash_key] != anchor or sha256(ROOT/path) != anchor:
            raise ValueError("historical input anchor differs")
    candidates = json.loads((ROOT/plan["candidates_path"]).read_bytes())
    parent.validate_candidates(candidates,json.loads(parent.PLAN.read_bytes()))
    previous = json.loads((ROOT/plan["parent_receipt"]).read_bytes())
    if [r["id"] for r in previous["candidates"]] != [c["id"] for c in candidates]:
        raise ValueError("parent decision matrix differs")
    return candidates,previous


def sample_values(candidate):
    left,right = candidate["u_box"]
    return [left,(left+right)/2.,right]


def grazing_field():
    def terms(z):
        return z**4-12*z**3+49*z*z-78*z+40,4*z**3-36*z*z+98*z-78,12*z*z-72*z+98
    def rhs(t,q):
        x,_,z = q
        b,bp,_ = terms(z)
        return np.array([0.,bp*((z-3)**2+x)+2*b*(z-3),1.])
    def jac(t,q):
        x,_,z = q
        b,bp,bpp = terms(z)
        return np.array([[0.,0.,0.],[bp,0.,bpp*((z-3)**2+x)+4*bp*(z-3)+2*b],[0.,0.,0.]])
    return rhs,jac


def control_specs():
    specs = []
    for count in (2,3):
        for kind in ("output-fold","regular-no-fold","input-turn"):
            total = 2*np.pi*(count-1 if kind == "input-turn" else count)
            center = 0. if kind == "regular-no-fold" else 1/(2*(1-np.exp(-.06*total)))-.5
            specs.append(dict(kind=kind,count=count,us=[center-.02,center,center+.02],
                              initial_state=[-4.,0.,.005],initial_tangent=[1.,0.,.01],horizon=2*np.pi*count+2.5,guard=1e-8))
    for kind,us in (("grazing-jump",[-1e-4,2e-4,5e-4]),("grazing-tangency",[-1e-4,0.,1e-4])):
        specs.append(dict(kind=kind,count=2,us=us,initial_state=[0.,360.,0.],initial_tangent=[1.,40.,0.],horizon=5.5,guard=0.))
    return specs


def control_expectation(spec,points,analysis,reports):
    checks = analysis["checks"]
    if spec["kind"] == "output-fold":
        return analysis["screened_regular"] and analysis["sampled_output_turn"]
    if spec["kind"] == "regular-no-fold":
        return analysis["screened_regular"] and not analysis["sampled_output_turn"]
    if spec["kind"] == "input-turn":
        return not analysis["screened_regular"] and checks["point_numerics"] and not checks["point_projection"] and not checks["input_sign"] and checks["time_coherence"]
    counts = [[sum(e["accepted"] for e in r["reconstructed"]) for r in sample] for sample in reports]
    if counts[0] != [3,3] or counts[2] != [2,2]:
        return False
    if spec["kind"] == "grazing-jump":
        return counts[1] == [2,2] and checks["point_projection"] and checks["input_sign"] and not checks["time_coherence"] and not analysis["screened_regular"]
    return not points[1]["numeric_qualified"] and all(r["uncertain_extrema"] for r in reports[1]) and not analysis["screened_regular"]


def controls(plan):
    rows = []
    section = PoincareSection((0.,1.,0.),0.,-1)
    for spec in control_specs():
        rhs,jac = grazing_field() if spec["kind"].startswith("grazing") else control_field(0. if spec["kind"] == "regular-no-fold" else 1e4)
        points,reports = [],[]
        for u in spec["us"]:
            profiles,raw_reports = [],[]
            for method in plan["solvers"]:
                initial = np.asarray(spec["initial_state"])+u*np.asarray(spec["initial_tangent"])
                report,_ = collect(rhs,jac,initial,spec["initial_tangent"],section,method=method,horizon=spec["horizon"],guard=spec["guard"],
                                   **{k:plan[k] for k in ("rtol","atol","max_step","extremum_margin")})
                profiles.append(profile(report,spec,rhs,section,plan))
                raw_reports.append(report)
            points.append(pair(profiles,plan))
            reports.append(raw_reports)
        analysis = interval(points,spec["us"],plan)
        rows.append(dict(spec=spec,points=points,reports=reports,analysis=analysis,
                         passed=bool(control_expectation(spec,points,analysis,reports))))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--controls-only",action="store_true")
    args = parser.parse_args()
    plan = json.loads(PLAN.read_bytes())
    candidates,previous = load(plan)
    if args.controls_only:
        args.output_dir.mkdir(parents=True,exist_ok=False)
        rows = controls(plan)
        write_json(args.output_dir/"controls.json",rows)
        print(json.dumps([dict(kind=r["spec"]["kind"],count=r["spec"]["count"],passed=r["passed"]) for r in rows]))
        return
    output = args.output_dir.resolve()
    if ROOT/"artifacts/EXP-491" not in output.parents or subprocess.check_output(["git","status","--porcelain"],text=True).strip():
        parser.error("fresh EXP-491 output and clean source required")
    source = subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    if source != subprocess.check_output(["git","rev-parse","@{upstream}"],text=True).strip():
        parser.error("push source before execution")
    if shutil.disk_usage(ROOT).free < plan["limits"]["initial_free_bytes"]:
        parser.error("initial free-space reserve insufficient")
    output.mkdir(parents=True,exist_ok=False)
    binding = dict(source_commit=source,started_utc=utc(),plan_sha256=sha256(PLAN),sources={s:sha256(ROOT/s) for s in SOURCES},
                   runtime=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__),
                   candidates_sha256=plan["candidates_sha256"],parent_receipt_sha256=plan["parent_receipt_sha256"])
    write_json(output/"binding.json",binding)
    started = time.monotonic()
    calls,bytes_written = 0,0
    def deadline(*_):
        raise TimeoutError("EXP-491 whole-run deadline")
    signal.signal(signal.SIGALRM,deadline)
    signal.alarm(plan["limits"]["wall_seconds"])
    try:
        control_rows = controls(plan)
        write_json(output/"controls.json",control_rows)
        bytes_written += (output/"controls.json").stat().st_size
        if not all(r["passed"] for r in control_rows):
            raise ValueError("analytic controls failed; no target access")
        marker = ROOT/"artifacts/EXP-491/target-once.json"
        write_json(marker,binding)
        results = []
        for c,old in zip(candidates,previous["candidates"],strict=True):
            par = RosslerParameters(**c["parameters"])
            rhs,jac = lambda t,q:rossler_rhs(t,q,par),lambda t,q:rossler_jacobian(q,par)
            section = replace(legacy_rossler_section(par),direction=-1)
            points = []
            us = sample_values(c)
            for i,u in enumerate(us):
                profiles = []
                for method in plan["solvers"]:
                    if calls >= 156 or bytes_written+33554432 > plan["limits"]["output_bytes"] or shutil.disk_usage(ROOT).free-33554432 < plan["limits"]["minimum_free_bytes"]:
                        raise RuntimeError("pre-integration trajectory/storage reserve reached")
                    label = f"{c['id']}--sample-{i}--{method}"
                    write_json(output/(label+"-started.json"),dict(candidate_id=c["id"],sample_index=i,method=method,u=u,started_utc=utc()))
                    initial = np.asarray(c["initial_state"])+u*np.asarray(c["initial_tangent"])
                    report,raw = collect(rhs,jac,initial,c["initial_tangent"],section,method=method,horizon=c["horizon"],
                                         **{k:plan[k] for k in ("rtol","atol","max_step","guard","extremum_margin")})
                    raw_bytes = sum(v.nbytes for v in raw.values())
                    if calls >= 156 or bytes_written+raw_bytes+33554432 > plan["limits"]["output_bytes"] or shutil.disk_usage(ROOT).free-raw_bytes < plan["limits"]["minimum_free_bytes"]:
                        raise RuntimeError("trajectory/storage reserve reached")
                    path = output/(label+".npz")
                    with path.open("xb") as stream:
                        np.savez_compressed(stream,**raw)
                    calls += 1
                    bytes_written += path.stat().st_size
                    derived = profile(report,c,rhs,section,plan)
                    write_json(output/(label+".json"),dict(report=report,profile=derived))
                    bytes_written += (output/(label+".json")).stat().st_size
                    profiles.append(derived)
                    print(label+": completed",flush=True)
                points.append(pair(profiles,plan))
            results.append(dict(id=c["id"],family_id=c["family_id"],case=c["case"],region=c["region"],us=us,
                                prior_fold_qualified=old["qualified"],points=points,analysis=interval(points,us,plan)))
        write_json(output/"summary.json",dict(status="completed",binding=binding,candidates=results,target_trajectories=calls,
            elapsed_seconds=time.monotonic()-started,completed_utc=utc(),files=inventory(output),marker_sha256=sha256(marker)))
        print(json.dumps(dict(completed_candidates=len(results),target_trajectories=calls)))
    except (Exception,KeyboardInterrupt) as e:
        write_json(output/"failure.json",dict(error_type=type(e).__name__,message=str(e),utc=utc(),retained_target_trajectories=calls))
        raise
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""One bounded local execution of all sixteen nominated grazing boundaries."""
import argparse
from dataclasses import replace
import json
import math
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
from butterfly.event_boundary_shooting import shoot,root_pair,assess
from scripts import build_exp492_event_boundaries as builder
from scripts.run_exp488_event_accuracy import utc

PLAN = ROOT/"experiments/manifests/EXP-492-event-boundaries.json"
SOURCES = tuple(dict.fromkeys((*builder.parent.SOURCES,
    "experiments/manifests/EXP-491-event-sheet-probe.json","scripts/run_exp491_event_sheet_probe.py",
    "scripts/build_exp492_event_boundaries.py","scripts/run_exp492_event_boundaries.py",
    "scripts/audit_exp492_event_boundaries.py","python/butterfly/event_boundary_shooting.py",
    "python/butterfly/section_grazing.py","docs/experiments/EXP-492-event-boundaries.md","tests/test_event_boundary_shooting.py")))


def load(p):
    expected = dict(experiment_id="EXP-492",inputs_path="experiments/manifests/EXP-492-event-boundary-inputs.json",
        inputs_sha256="9377b422f1321d1b811f59a2b477bf72bee5e58bb4272decb60e040746cf86da",
        solvers=["DOP853","Radau"],rtol=1e-13,atol=1e-15,max_step=.001,newton_iterations=8,
        root_plane=1e-10,root_velocity=1e-9,minimum_unfolding=1.,minimum_curvature=1.,
        solver_u=1e-9,solver_time=1e-8,solver_scaled_state=1e-7,scales=[15.,15.,.01],
        window=.05,side_residual=1e-8,minimum_angle=1e-7,square_root_ratio_relative_error=.05,
        side_solver_time=1e-7,side_solver_scaled_state=1e-6,guard=1e-8,extremum_margin=1e-10,
        limits=dict(intervals=26,candidates=16,families=10,max_target_integrations=384,wall_seconds=7200,
                    output_bytes=8589934592,initial_free_bytes=17179869184,minimum_free_bytes=8589934592))
    if any(p[k] != v for k,v in expected.items()) or sha256(ROOT/p["inputs_path"]) != p["inputs_sha256"]:
        raise ValueError("frozen numerical/input/resource settings differ")
    table = json.loads((ROOT/p["inputs_path"]).read_bytes())
    return table,builder.validate(table)


def polynomial_field(prefix):
    denominator = math.factorial(2*prefix)
    target = 2*prefix+1.
    def terms(z):
        b,bp,bpp = 1.,0.,0.
        for r in range(1,2*prefix+1):
            b,bp,bpp = b*(z-r),bp*(z-r)+b,bpp*(z-r)+2*bp
        return b/denominator,bp/denominator,bpp/denominator
    def rhs(t,q):
        x,_,z = q
        b,bp,_ = terms(z)
        return np.array([0.,bp*((z-target)**2+x)+2*b*(z-target),1.])
    def jac(t,q):
        x,_,z = q
        b,bp,bpp = terms(z)
        return np.array([[0.,0.,0.],[bp,0.,bpp*((z-target)**2+x)+4*bp*(z-target)+2*b],[0.,0.,0.]])
    return rhs,jac


def control_specs():
    rows = []
    for prefix in (0,1,8):
        target = 2*prefix+1.
        rows.append(dict(id=f"analytic-prefix-{prefix}",kind="grazing",accepted_prefix=prefix,
            initial_state=[2e-5,target*target+2e-5,0.],initial_tangent=[2.,2.,0.],horizon=target+1.5,
            u_box=[-.001,.001],seed_u=0.,seed_time=target+.002,time_box=[target-.1,target+.1],
            doses=[-2e-6,-2e-7,2e-7,2e-6]))
    rows.append(dict(rows[0],id="analytic-no-root-in-box",kind="no-root-in-box",initial_state=[.1,1.1,0.]))
    rows.append(dict(rows[0],id="analytic-transverse",kind="transverse",initial_state=[0.,.5,0.],initial_tangent=[1.,0.,0.],seed_time=.5,time_box=[.4,.6]))
    return rows


def fields_for_control(c):
    if c["kind"] == "transverse":
        return lambda t,q:np.array([0.,-1.,1.]),lambda t,q:np.zeros((3,3))
    return polynomial_field(c["accepted_prefix"])


def run_candidate(c,p,rhs,jac,section,retain,started,before_integrate=None):
    rows = []
    for method in p["solvers"]:
        label = c["id"]+"--"+method
        started(label,dict(candidate_id=c["id"],method=method,phase="shooting"))
        names = []
        def keep(i,raw):
            name = label+f"--newton-{i}.npz"
            retain(name,raw)
            names.append(name)
        root = shoot(rhs,jac,section,c,p,method,keep,before_integrate)
        root["raw_files"] = names
        rows.append(dict(method=method,shooting=root))
    joint = root_pair(rows,c,p)
    sides = []
    if joint["eligible"]:
        for i,dose in enumerate(c["doses"]):
            u = joint["common_center_u"]+dose
            reports,names = [],[]
            for method in p["solvers"]:
                label = c["id"]+f"--side-{i}--{method}"
                started(label,dict(candidate_id=c["id"],method=method,phase="side",dose=dose,u=u))
                if before_integrate is not None:
                    before_integrate()
                report,raw = collect(rhs,jac,np.asarray(c["initial_state"])+u*np.asarray(c["initial_tangent"]),c["initial_tangent"],section,
                    method=method,horizon=c["horizon"],**{k:p[k] for k in ("rtol","atol","max_step","guard","extremum_margin")})
                retain(label+".npz",raw)
                reports.append(report)
                names.append(label+".npz")
            sides.append(dict(dose=dose,u=u,reports=reports,raw_files=names))
    return dict(id=c["id"],roots=rows,sides=sides,skipped_doses=[] if joint["eligible"] else c["doses"],analysis=assess(rows,sides,c,p))


def controls(p):
    rows = []
    for c in control_specs():
        calls = 0
        def retain(_name,_raw):
            nonlocal calls
            calls += 1
        rhs,jac = fields_for_control(c)
        result = run_candidate(c,p,rhs,jac,PoincareSection((0.,1.,0.),0.,-1),retain,lambda *_:None)
        exact = all(r["shooting"]["converged"] and abs(r["shooting"]["trace"][-1]["u"]+1e-5) <= 1e-9
                    and abs(r["shooting"]["trace"][-1]["time"]-(2*c["accepted_prefix"]+1)) <= 1e-8 for r in result["roots"])
        passed = result["analysis"]["qualified"] and exact if c["kind"] == "grazing" else not result["analysis"]["qualified"] and not result["sides"]
        rows.append(dict(spec=c,result=result,control_integrations=calls,passed=bool(passed)))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--controls-only",action="store_true")
    args = parser.parse_args()
    p = json.loads(PLAN.read_bytes())
    table,candidates = load(p)
    if args.controls_only:
        args.output_dir.mkdir(parents=True,exist_ok=False)
        rows = controls(p)
        write_json(args.output_dir/"controls.json",rows)
        print(json.dumps([dict(id=r["spec"]["id"],passed=r["passed"],integrations=r["control_integrations"]) for r in rows]))
        return
    output = args.output_dir.resolve()
    if ROOT/"artifacts/EXP-492" not in output.parents or subprocess.check_output(["git","status","--porcelain"],text=True).strip():
        parser.error("fresh EXP-492 output and clean source required")
    source = subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    if source != subprocess.check_output(["git","rev-parse","@{upstream}"],text=True).strip() or shutil.disk_usage(ROOT).free < p["limits"]["initial_free_bytes"]:
        parser.error("pushed source and initial space reserve required")
    output.mkdir(parents=True,exist_ok=False)
    b = dict(source_commit=source,started_utc=utc(),plan_sha256=sha256(PLAN),inputs_sha256=p["inputs_sha256"],
        sources={s:sha256(ROOT/s) for s in SOURCES},runtime=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__))
    write_json(output/"binding.json",b)
    start = time.monotonic()
    calls,used = 0,0
    def check(reserve):
        if calls >= 384 or used+reserve > p["limits"]["output_bytes"] or shutil.disk_usage(ROOT).free-reserve < p["limits"]["minimum_free_bytes"]:
            raise RuntimeError("target/storage reserve reached")
    def begin(label,metadata):
        check(33554432)
        write_json(output/(label+"-started.json"),dict(metadata,started_utc=utc()))
    def retain(name,raw):
        nonlocal calls,used
        check(sum(a.nbytes for a in raw.values())+33554432)
        with (output/name).open("xb") as stream:
            np.savez_compressed(stream,**raw)
        calls += 1
        used += (output/name).stat().st_size
    def deadline(*_):
        raise TimeoutError("EXP-492 whole-run deadline")
    signal.signal(signal.SIGALRM,deadline)
    signal.alarm(p["limits"]["wall_seconds"])
    try:
        cs = controls(p)
        write_json(output/"controls.json",cs)
        used += (output/"controls.json").stat().st_size
        if not all(c["passed"] for c in cs):
            raise ValueError("analytic controls failed; no targets")
        marker = ROOT/"artifacts/EXP-492/target-once.json"
        write_json(marker,b)
        results = []
        for c in candidates:
            par = RosslerParameters(**c["parameters"])
            rhs,jac = lambda t,q:rossler_rhs(t,q,par),lambda t,q:rossler_jacobian(q,par)
            section = replace(legacy_rossler_section(par),direction=-1)
            row = run_candidate(c,p,rhs,jac,section,retain,begin,lambda:check(33554432))
            write_json(output/(c["id"]+".json"),row)
            used += (output/(c["id"]+".json")).stat().st_size
            results.append(row)
            print(c["id"]+": completed",flush=True)
        write_json(output/"summary.json",dict(status="completed",binding=b,candidates=results,target_integrations=calls,
            elapsed_seconds=time.monotonic()-start,completed_utc=utc(),files=inventory(output),marker_sha256=sha256(marker)))
        print(json.dumps(dict(completed_candidates=len(results),target_integrations=calls)))
    except (Exception,KeyboardInterrupt) as e:
        write_json(output/"failure.json",dict(error_type=type(e).__name__,message=str(e),utc=utc(),retained_target_integrations=calls))
        raise
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()

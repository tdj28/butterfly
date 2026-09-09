#!/usr/bin/env python3
"""Frozen, bounded joint-parameter contact search with full target retention."""
import argparse
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal as D, localcontext
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

import numpy as np
import scipy
from butterfly import decimal_grazing as numeric
from butterfly import projected_fold_shooting, section_census
from butterfly._paired_startup import inventory, sha256, write_json
from butterfly.models import RosslerParameters, rossler_rhs, rossler_jacobian
from butterfly.poincare import legacy_rossler_section
from butterfly.projected_fold_qualification import compare
from scripts import run_exp497_contact_localization as previous
from scripts import run_exp501_limiting_contact as limiting
from scripts import exp501_contact_analysis as boundary_analysis
from scripts import exp500_census_analysis as census
from scripts import exp502_response as response

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/"experiments/manifests/EXP-502-joint-contact-search.json"
INPUTS = {
    "experiments/manifests/EXP-497-contact-localization.json": "2e3cc27a66bc99e4b2f76fa9ad7bb9b61da233bcf1a080463980f30c51678cfe",
    "docs/experiments/receipts/EXP-497-contact-localization-result.json": "ed229b4a772ef19d227272006401d19090ee5e28a357791f25400cafa3271cff",
    "experiments/manifests/EXP-501-limiting-grazing-contact.json": "d9ef2516e08a7014c3c5b1917be4d17884e0146d93ddd5492bd4b1520896b5cd",
    "docs/experiments/receipts/EXP-501-limiting-grazing-contact-result.json": "c97b64e4770e1b53a66802c9bf6791fe4dbbf22e84d6d12281ccda9ae451b485"}
EXPLICIT = ["scripts/run_exp502_joint_contact.py", "scripts/audit_exp502_joint_contact.py",
    "scripts/exp502_response.py", "tests/test_exp502_joint_contact.py",
    "docs/experiments/EXP-502-joint-contact-search.md", "docs/experiments/EXP-502-local-design-audit.md",
    "experiments/manifests/EXP-502-joint-contact-search.json", "pyproject.toml", "uv.lock"]


def utc():
    return datetime.now(timezone.utc).isoformat()


def expected():
    if any(sha256(ROOT/n) != h for n, h in INPUTS.items()):
        raise ValueError("authenticated public input changed")
    p497, old497, p501, old501 = [json.loads((ROOT/n).read_bytes()) for n in INPUTS]
    eligible = [r for r in old497["rows"] if r["status"] == "proximate"]
    if len(eligible) != 1 or eligible[0]["level"] != 3 or not old501["passed"]:
        raise ValueError("unique audited primitive anchor required")
    old = eligible[0]
    folds = deepcopy(old["candidates"])
    for c, row in zip(folds, old["result"]["folds"], strict=True):
        if c["id"] != row["id"]:
            raise ValueError("fold representation identity")
        u, t = [float(np.mean([r["root"][k] for r in row["solvers"]])) for k in ("u", "time")]
        c.update(seed_u=u, seed_time=t, u_box=[u-.02, u+.02], time_box=[t-1, t+1], horizon=t+3, epsilon=1e-6)
    boundaries = deepcopy(p501["candidates"])
    with localcontext() as ctx:
        ctx.prec = 70
        for c, row in zip(boundaries, old501["rows"], strict=True):
            if c["id"] != row["id"] or not row["comparison"]["qualified"]:
                raise ValueError("boundary representation identity")
            u, t = [sum(D(r["shooting"]["trace"][-1][k]) for r in row["profiles"])/2 for k in ("u", "time")]
            c.update(seed_u=str(u), seed_time=str(t), u_box=[str(u-D('.02')), str(u+D('.02'))],
                     time_box=[str(t-1), str(t+1)])
    anchor = old["spec"]["parameters"]
    base = response.vectors(old["result"]["contact"], old501["rows"])
    if len(folds) != 4 or len(boundaries) != 8 or len(base) != 256 or len(old501["ledger"]) != 26:
        raise ValueError("complete representation/parent ledger required")
    return dict(experiment_id="EXP-502", status="prospective-outcome-informed-pilot", inputs=INPUTS,
        anchor=anchor, stencil=response.stencil(anchor), fold_candidates=folds, boundary_candidates=boundaries,
        cycle_seed=old["result"]["cycle"]["profiles"][0]["correction"], reference_cycle=old["result"]["cycle"],
        base_vectors=base, ledger=old501["ledger"], fold=p497["fold"], periodic=p497["periodic"],
        primary_radius=1e-4, sign_floor=1e-6, sensitivity_radii=[1e-6, 1e-5, 1e-4, 1e-3],
        configurations=numeric.CONFIGS, limits=dict(target_ivps=2048, wall_seconds=7200,
            output_bytes=8*1024**3, initial_free_bytes=17*1024**3, minimum_free_bytes=8*1024**3),
        paid_review="not-requested-human-approval-policy", symbolic_chains_verified=False)


def imported():
    return {Path(m.__file__).resolve().relative_to(ROOT).as_posix() for m in list(sys.modules.values())
            if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to(ROOT)
            and Path(m.__file__).suffix == ".py" and not Path(m.__file__).resolve().is_relative_to(ROOT/".venv")}


def load():
    p = json.loads(PLAN.read_bytes())
    if {k:v for k,v in p.items() if k != "source_paths"} != expected() or not set(EXPLICIT) <= set(p["source_paths"]):
        raise ValueError("frozen joint-contact plan differs")
    return p


def point_inputs(p, spec):
    parameters = spec["parameters"]
    section = replace(legacy_rossler_section(RosslerParameters(**parameters)), direction=-1)
    folds, boundaries = deepcopy(p["fold_candidates"]), deepcopy(p["boundary_candidates"])
    for c in folds:
        c["parameters"] = parameters
    for c in folds+boundaries:
        c["initial_state"][1] = section.offset
    a, b, c = [parameters[k] for k in ("a", "b", "c")]
    field = numeric.augment(dict(constant=[0, 0, b],
        linear=[[0, 1, -1], [0, 2, -1], [1, 0, 1], [1, 1, a], [2, 2, -c]], quadratic=[[2, 0, 2, 1]]))
    return folds, boundaries, field, dict(offset=section.offset, gate_upper=section.gate_upper)


def retain_npz(path, raw):
    with path.open("xb") as stream:
        np.savez_compressed(stream, **raw)


def fold_profile(output, c, method, p, budget):
    """Count before every solve; preserve otherwise omitted guard meshes."""
    par = RosslerParameters(**c["parameters"])
    label = c["id"]+"--"+method
    write_json(output/(label+"-started.json"), dict(candidate_id=c["id"], method=method, started_utc=utc()))
    shooting_solve, census_solve = projected_fold_shooting.solve_ivp, section_census.solve_ivp
    guard_count = 0
    def shooting(*args, **kwargs):
        budget(True)
        return shooting_solve(*args, **kwargs)
    def collect(*args, **kwargs):
        nonlocal guard_count
        budget(True)
        sol = census_solve(*args, **kwargs)
        if args[1][0] == 0. and args[1][1] == p["guard"]:
            retain_npz(output/(label+f"--guard-{guard_count}.npz"),
                dict(times=sol.t, augmented_states=sol.y.T, success=np.array(sol.success), nfev=np.array(sol.nfev)))
            guard_count += 1
        return sol
    with patch.object(projected_fold_shooting, "solve_ivp", shooting), patch.object(section_census, "solve_ivp", collect):
        row = previous.folds_run.run_candidate(c, method, p,
            lambda t,q: rossler_rhs(t,q,par), lambda t,q: rossler_jacobian(q,par),
            lambda t,q,v: np.array([0.,0.,2*v[0]*v[2]]),
            replace(legacy_rossler_section(par), direction=-1),
            lambda suffix,raw: retain_npz(output/(label+"--"+suffix+".npz"), raw))
    write_json(output/(label+".json"), row)
    return row


def summarize(p, cycle, folds, boundaries):
    transport = response.correspondence(cycle, p["reference_cycle"])
    contact = previous.measure(folds, cycle, p) if cycle["status"] == "qualified" else None
    aggregate = boundary_analysis.aggregate(boundaries)
    vectors = response.vectors(contact, boundaries)
    qualified = bool(transport["passed"] and all(f["qualified_in_region"] for f in folds)
                     and aggregate["complete"] and len(vectors) == 256)
    proximity = bool(qualified and contact["envelope"]["pair_state_distance"][3] <= 1e-4
                     and aggregate["cycle_indices"][1]["all_proximate"])
    return dict(correspondence=transport, contact=contact, boundary_analysis=aggregate,
                qualified=qualified, vectors=vectors, joint_proximity=proximity)


def evaluate(p, spec, output, budget):
    output.mkdir()
    folds_in, boundaries_in, field, section = point_inputs(p, spec)
    write_json(output/"inputs.json", dict(spec=spec, folds=folds_in, boundaries=boundaries_in, field=field, section=section))
    profiles = []
    for method in p["periodic"]["methods"]:
        profile = previous.cycles_run.run_profile(spec, method, p["cycle_seed"], p["periodic"], output, budget)
        if "error" in profile:
            raise RuntimeError("periodic exception retained: "+profile["error"])
        profiles.append(profile)
    pair = previous.cycles_run.compare_profiles(profiles, p["periodic"])
    cycle = dict(spec=spec, profiles=profiles, pair=pair, status="qualified" if pair["passed"] else "unqualified")
    if pair["passed"] and not all(w["counts"] == dict(historical=6, barrio=8) for v in profiles for w in v["metric"]["windows"]):
        cycle.update(status="unqualified", count_failure=True)
    folds = []
    for c in folds_in:
        rows = [fold_profile(output,c,method,p["fold"],budget) for method in p["fold"]["solvers"]]
        folds.append(dict(compare(c,rows,p["fold"]), parent_id=c["parent_id"]))
    cycles = [dict(method=v["method"],phase=w["phase"],states=w["event_states"]["historical"])
              for v in profiles for w in v.get("metric", {}).get("windows", [])] if cycle["status"] == "qualified" else []
    boundaries = []
    for c in boundaries_in:
        profiles = []
        for config in numeric.CONFIGS:
            label = c["id"]+"--"+config["name"]
            write_json(output/(label+"-started.json"), dict(id=c["id"], configuration=config["name"], started_utc=utc()))
            def integrate(iteration,initial,end,f,configuration):
                budget(True)
                name = label+f"--iteration-{iteration}.json.gz"
                return numeric.run_profile(output/name,initial,f,end,configuration,lambda:budget(False)),name
            shooting, raw = numeric.shooting(c,field,section["offset"],config,integrate)
            result = dict(configuration=config["name"], shooting=shooting, census=None)
            if shooting["status"] == "qualified":
                with localcontext() as ctx:
                    ctx.prec = config["digits"]
                    end = D(shooting["trace"][-1]["time"])-D('.05')
                result["census"], certificates = census.profile(numeric.prefix_state(raw,end),section,before_segment=lambda:budget(False))
                write_json(output/(label+"-certificates.json"),certificates)
            write_json(output/(label+"-result.json"),result)
            profiles.append(result)
        row = dict(id=c["id"],profiles=profiles,comparison=boundary_analysis.compare(profiles,c,cycles))
        write_json(output/(c["id"]+".json"),row)
        boundaries.append(row)
        print(json.dumps(dict(point=spec["id"], boundary_profiles=len(boundaries)*2)),flush=True)
    result = dict(spec=spec, cycle=cycle, folds=folds, boundaries=boundaries,
                  **summarize(p,cycle,folds,boundaries))
    write_json(output/"point.json",result)
    return result


def startup(p):
    """Fresh copied source, isolated interpreter; no target integrations."""
    target = Path(tempfile.mkdtemp(prefix="exp502-startup-")).resolve()
    names = set(p["source_paths"]) | set(INPUTS)
    for name in names:
        destination = target/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/name, destination)
    command = [sys.executable, "-I", "-B", "-c",
        f"import sys;from pathlib import Path;root=Path({str(target)!r});"
        f"sys.path[:0]={[str(target),str(target/'python')]!r};from scripts.run_exp502_joint_contact import main;main();"
        "assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() "
        "if n.startswith(('scripts.','butterfly')) and getattr(m,'__file__',None))"]
    child = subprocess.run(command,cwd=target,capture_output=True,text=True,check=True,timeout=60)
    if any(sha256(ROOT/n) != sha256(target/n) for n in names):
        raise ValueError("copied source identity differs")
    return dict(passed=True, stdout=child.stdout, stderr=child.stderr,
                sources={n:sha256(target/n) for n in sorted(names)}, isolated=True, target_integrations=0)


def run_controls(p,output):
    from scripts import audit_exp502_joint_contact as audit
    from scripts import exp501_analytic_controls as controls
    fold_controls = previous.folds_run.controls(p["fold"])
    audit.old.fold_audit.check_controls(fold_controls,p["fold"])
    write_json(output/"fold-controls.json",fold_controls)
    previous.cycles_run.controls(output)
    audit.old.check_periodic_controls(output)
    analytic = controls.run(output/"decimal-controls")
    audit.decimal_audit.check_controls(output/"decimal-controls",analytic)
    write_json(output/"decimal-controls.json",analytic)
    write_json(output/"response-controls.json",audit.response_controls())
    return dict(passed=True,fold_profiles=12,periodic_profiles=4,decimal_profiles=4,response_cases=6,target_integrations=0)


def execute(output, source, remote):
    from scripts import audit_exp502_joint_contact as audit
    from scripts import exp501_analytic_controls as controls
    p = load()
    def git(*args):
        return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()
    if (git("rev-parse","HEAD") != source or git("status","--porcelain")
            or git("ls-remote","origin",remote).split() != [source,remote]
            or not imported() <= set(p["source_paths"])):
        raise ValueError("clean live public source/import closure required")
    output = output.resolve()
    marker = ROOT/"artifacts/EXP-502/target-once.json"
    if ROOT/"artifacts/EXP-502" not in output.parents or output.exists() or marker.exists():
        raise ValueError("fresh output and unconsumed attempt required")
    if shutil.disk_usage(ROOT).free < p["limits"]["initial_free_bytes"]:
        raise ValueError("initial disk reserve")
    output.mkdir(parents=True)
    binding = dict(source_commit=source,remote_ref=remote,started_utc=utc(),plan_sha256=sha256(PLAN),inputs=INPUTS,
        sources={n:sha256(ROOT/n) for n in p["source_paths"]},paid_review=p["paid_review"],
        runtime=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__))
    write_json(output/"binding.json",binding)
    started, calls, checks = time.monotonic(), 0, 0
    slots = [dict(spec=s,status="not-run") for s in p["stencil"]]+[dict(spec=None,status="not-run",role="proposal")]
    def budget(integrating=False):
        nonlocal calls, checks
        checks += 1
        if integrating:
            if calls >= p["limits"]["target_ivps"]:
                raise previous.cycles_run.BudgetStop("target IVP cap")
            calls += 1
        if integrating or checks % 1024 == 1:
            if (time.monotonic()-started > p["limits"]["wall_seconds"]
                    or shutil.disk_usage(ROOT).free < p["limits"]["minimum_free_bytes"]
                    or sum(f.stat().st_size for f in output.rglob('*') if f.is_file()) > p["limits"]["output_bytes"]-32*1024**2):
                raise previous.cycles_run.BudgetStop("time/storage cap")
    def timeout(*_):
        raise previous.cycles_run.BudgetStop("wall deadline")
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p["limits"]["wall_seconds"])
    try:
        write_json(output/"startup.json",startup(p))
        run_controls(p,output)
        budget(False)
        write_json(marker,binding)
        rows = []
        for index,spec in enumerate(p["stencil"]):
            slots[index]["status"] = "started"
            rows.append(evaluate(p,spec,output/spec["id"],budget))
            slots[index]["status"] = "completed"
            print(json.dumps(dict(completed_stencil_points=len(rows),target_ivps=calls)),flush=True)
        matrix = response.response(rows,p["base_vectors"],p["anchor"])
        audit.check_scalar(matrix,p["base_vectors"],p["anchor"])
        write_json(output/"response.json",matrix)
        proposal = None
        if matrix["qualified"]:
            slots[-1].update(spec=matrix["proposal"],status="started")
            proposal = evaluate(p,matrix["proposal"],output/"joint-proposal",budget)
            slots[-1]["status"] = "completed"
        else:
            slots[-1]["reason"] = matrix["reason"]
        budget(False)
        target_files = [n for n in inventory(output) if n.split('/')[0] in {s["id"] for s in p["stencil"]}|{"joint-proposal"}]
        inherited_products = sum(n.endswith((".npz", ".json.gz")) and "--guard-" not in n for n in target_files)
        write_json(output/"summary.json",dict(experiment_id="EXP-502",status="completed",binding=binding,
            rows=rows,proposal=proposal,response=matrix,analysis=response.verdict(matrix,proposal,p["base_vectors"]),
            slots=slots,ledger=p["ledger"],target_ivps=calls,inherited_archive_products=inherited_products,
            elapsed_seconds=time.monotonic()-started,
            files=inventory(output),completed_utc=utc(),marker_sha256=sha256(marker),symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True,target_ivps=calls,summary_sha256=sha256(output/"summary.json"))),flush=True)
    except BaseException as exc:
        signal.alarm(0)
        write_json(output/"failure.json",dict(error_type=type(exc).__name__,message=str(exc),utc=utc(),
            target_ivps=calls,slots=slots,files=inventory(output)))
        raise
    finally:
        signal.alarm(0)


def main():
    from scripts import audit_exp502_joint_contact  # noqa: F401
    from scripts import exp501_analytic_controls  # noqa: F401
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prepare",action="store_true")
    mode.add_argument("--execute",action="store_true")
    mode.add_argument("--startup",action="store_true")
    mode.add_argument("--controls",action="store_true")
    parser.add_argument("--output-dir",type=Path)
    parser.add_argument("--source-commit")
    parser.add_argument("--remote-ref")
    a = parser.parse_args()
    if a.prepare:
        p = expected()
        p["source_paths"] = sorted(imported()|set(EXPLICIT))
        write_json(PLAN,p)
    elif a.execute:
        if not all((a.output_dir,a.source_commit,a.remote_ref)):
            parser.error("execution requires output/source/ref")
        execute(a.output_dir,a.source_commit,a.remote_ref)
    elif a.controls:
        if a.output_dir is None:
            parser.error("fresh output directory required")
        a.output_dir.mkdir(parents=True,exist_ok=False)
        print(json.dumps(run_controls(load(),a.output_dir)))
    else:
        p = load()
        if not imported() <= set(p["source_paths"]):
            raise ValueError("import closure differs")
        print(json.dumps(startup(p) if a.startup else dict(valid=True,target_integrations=0,stencil_points=8)))


if __name__ == "__main__":
    main()

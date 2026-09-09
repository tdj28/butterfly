#!/usr/bin/env python3
"""Three-point, all-representation contact refinement on one eligible family."""
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
from butterfly.projected_fold_qualification import compare
from scripts import run_exp490_direct_folds as folds_run
from scripts import run_exp494_periodic_winding_transport as cycles_run
from scripts import run_exp496_contact_endpoint as parent
from scripts import analyze_exp495_fold_cycle_membership as distances

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/"experiments/manifests/EXP-497-contact-localization.json"
PARENT_RESULT = ROOT/"docs/experiments/receipts/EXP-496-contact-endpoint-result.json"
PARENT_SHA = "c6ad2dca38df1e0628550b5f697252ce81e62cb47db9ae1dec9736d8c5ab3e6b"
EXPLICIT = ["scripts/run_exp497_contact_localization.py", "scripts/audit_exp497_contact_localization.py",
    "tests/test_exp497_contact_localization.py", "docs/experiments/EXP-497-contact-localization.md",
    "experiments/manifests/EXP-497-contact-localization.json", "experiments/manifests/EXP-494-periodic-winding-transport.json",
    *parent.EXPLICIT_SOURCES, *cycles_run.SOURCES]


def inputs():
    p496, data, old_folds, cycles = parent.load_inputs()
    if sha256(PARENT_RESULT) != PARENT_SHA:
        raise ValueError("parent audited outcome changed")
    result = json.loads(PARENT_RESULT.read_bytes())
    from scripts.audit_exp496_contact_endpoint import reconstruct_contact
    if (not result["passed"] or result["ledger"] != data["ledger"]
            or reconstruct_contact(result["candidates"], data, old_folds, cycles, p496) != result["contact"]):
        raise ValueError("parent endpoint replay differs")
    return p496, data, old_folds, cycles, result


def prepare():
    from scripts import audit_exp497_contact_localization  # noqa: F401
    p496, *_ = inputs()
    periodic_plan = cycles_run.load_plan()
    p = dict(experiment_id="EXP-497", levels=3, cases=["local-a025-c083", "local-a027-c083"],
        primary_event=3, primary_radius=1e-4, sign_floor=1e-6,
        sensitivity_radii=[1e-6, 1e-5, 1e-4, 1e-3],
        fold={k:p496[k] for k in parent.NUMERIC_KEYS}, periodic=periodic_plan,
        limits=dict(wall_seconds=3600, max_target_ivps=512, output_bytes=2*1024**3,
                    initial_free_bytes=12*1024**3, minimum_free_bytes=8*1024**3),
        inputs={**p496["inputs"], str(PARENT_RESULT.relative_to(ROOT)):PARENT_SHA,
                str(parent.PLAN.relative_to(ROOT)):sha256(parent.PLAN),
                str(parent.INPUT.relative_to(ROOT)):sha256(parent.INPUT)},
        source_paths=sorted(set(EXPLICIT) | set(p496["source_paths"]) | parent.imported_sources()),
        paid_review="not-run-human-approval-policy")
    write_json(PLAN, p)
    print(json.dumps(dict(prepared=True, new_target_ivps=0)))


def load():
    p = json.loads(PLAN.read_bytes())
    p496, data, old_folds, cycles, result = inputs()
    if (p["experiment_id"] != "EXP-497" or p["levels"] != 3
            or p["cases"] != ["local-a025-c083", "local-a027-c083"]
            or p["primary_event"] != 3 or p["primary_radius"] != 1e-4 or p["sign_floor"] != 1e-6
            or p["sensitivity_radii"] != [1e-6, 1e-5, 1e-4, 1e-3]
            or p["fold"] != {k:p496[k] for k in parent.NUMERIC_KEYS}
            or p["periodic"] != cycles_run.load_plan()
            or p["limits"] != dict(wall_seconds=3600, max_target_ivps=512, output_bytes=2*1024**3,
                                   initial_free_bytes=12*1024**3, minimum_free_bytes=8*1024**3)
            or not set(EXPLICIT) <= set(p["source_paths"])
            or p["inputs"] != {**p496["inputs"],str(PARENT_RESULT.relative_to(ROOT)):PARENT_SHA,
                str(parent.PLAN.relative_to(ROOT)):sha256(parent.PLAN),str(parent.INPUT.relative_to(ROOT)):sha256(parent.INPUT)}
            or any(sha256(ROOT/s) != h for s,h in p["inputs"].items())
            or p["inputs"].get(str(PARENT_RESULT.relative_to(ROOT))) != PARENT_SHA):
        raise ValueError("frozen localization settings/input/source differ")
    return p, dict(data=data, old_folds=old_folds, cycles=cycles, result=result)


def initial_endpoints(case, source):
    contact = [r for r in source["result"]["contact"]["rows"] if r["case"] == case]
    endpoints = []
    for lower in (True, False):
        cycle = parent.cycle_node(source["cycles"], case, lower)
        collection = source["result"]["candidates"] if lower else source["old_folds"]["candidates"]
        ids = [r["id"] for r in contact]
        folds = [next(f for f in collection if f["id"] == i) for i in ids]
        key = "lower_signed_residual" if lower else "upper_signed_residual"
        values = [v[key] for r in contact for v in r["variants"]]
        if len(values) != 16 or not all(f["qualified_in_region"] for f in folds):
            raise ValueError("complete qualified endpoint required")
        endpoints.append(dict(a=cycle["spec"]["parameters"]["a"], mean_residual=float(np.mean(values)),
                              folds=folds, cycle=cycle))
    return endpoints


def propose(left, right):
    lo, hi, a, b = left["a"], right["a"], left["mean_residual"], right["mean_residual"]
    if not (np.isfinite([lo, hi, a, b]).all() and lo < hi and a < 0 < b):
        raise ValueError("ordered sign-resolved endpoint pair required")
    value = lo-a*(hi-lo)/(b-a)
    if not np.isfinite(value) or not lo < value < hi:
        raise ValueError("false position is not strictly interior")
    return float(value)


def candidates_at(case, level, a, left, right, source):
    fraction = (a-left["a"])/(right["a"]-left["a"])
    output = []
    for c in source["data"]["candidates"]:
        if c["case"] != case:
            continue
        new = deepcopy(c)
        new.update(id=c["id"]+f"--contact-{level:02d}", parent_id=c["id"])
        new["parameters"] = dict(a=a, b=.2, c=7.212)
        new["initial_state"][1] = legacy_rossler_section(RosslerParameters(**new["parameters"])).offset
        roots = []
        for endpoint in (left, right):
            f = next(f for f in endpoint["folds"] if f.get("parent_id", f["id"]) == c["id"])
            roots.append([float(np.mean([s["root"][k] for s in f["solvers"]])) for k in ("u", "time")])
        u, t = [roots[0][k]+fraction*(roots[1][k]-roots[0][k]) for k in range(2)]
        new.update(seed_u=u, seed_time=t, u_box=[u-.02,u+.02], time_box=[t-1,t+1], horizon=t+3, epsilon=1e-6)
        output.append(new)
    return output


def measure(folds, cycle, p):
    rows, variants = [], []
    if len(folds) != 4:
        raise ValueError("four measured fold representations required")
    for f in folds:
        row = dict(id=f["id"], family_id=f["family_id"], variants=[], envelope=None)
        if f["qualified_in_region"]:
            for method in p["fold"]["solvers"]:
                o = next(s for s in f["solvers"] if s["method"] == method)["observations"][1]
                profile = next(s for s in cycle["profiles"] if s["method"] == method)
                for w in profile["metric"]["windows"]:
                    events = w["event_states"]["historical"]
                    v = dict(method=method, phase=w["phase"], fold_input=o["image_state"],
                        fold_output=o["next_state"], cycle_events=events,
                        signed_residual=(events[3][0]-o["image_state"][0])/15.,
                        **distances.pair_distances(o["image_state"],o["next_state"],events,[15.,15.,.01]))
                    row["variants"].append(v)
                    variants.append(v)
            row["envelope"] = distances.envelope(row["variants"],p["sensitivity_radii"])
        rows.append(row)
    mean, env = None, None
    status = "fold-unqualified"
    if len(variants) == 16:
        env = distances.envelope(variants,p["sensitivity_radii"])
        residuals = [v["signed_residual"] for v in variants]
        mean = float(np.mean(residuals))
        if env["pair_state_distance"][3] <= p["primary_radius"]:
            status = "proximate"
        elif all(v >= p["sign_floor"] for v in residuals):
            status = "replace-high"
        elif all(v <= -p["sign_floor"] for v in residuals):
            status = "replace-low"
        else:
            status = "sign-unresolved"
    return dict(status=status, rows=rows, envelope=env, mean_residual=mean,
                exact_contact_verified=False, symbolic_chains_verified=False)


def campaign(p, source, evaluate):
    rows = []
    for case in p["cases"]:
        eligible = next(c for c in source["result"]["contact"]["cases"] if c["case"] == case)["status"] == "opposite-sign-endpoints"
        stop = None if eligible else "parent endpoint representation matrix unqualified"
        if eligible:
            left, right = initial_endpoints(case, source)
            seed = deepcopy(parent.cycle_node(source["cycles"],case,False)["profiles"][0]["correction"])
        for level in range(1,4):
            row = dict(case=case,level=level,status="not-run",reason=stop)
            if stop is None:
                try:
                    a = propose(left,right)
                except ValueError as exc:
                    row.update(status="interpolation-unresolved", reason=str(exc))
                    stop = row["reason"]
                else:
                    candidates = candidates_at(case,level,a,left,right,source)
                    spec = dict(id=case+f"--contact-{level:02d}",case=case,level=level,parameters=dict(a=a,b=.2,c=7.212))
                    result = evaluate(spec,candidates,seed)
                    row.update(spec=spec,candidates=candidates,seed=seed,result=result,
                        bracket_before=[dict(a=e["a"],mean_residual=e["mean_residual"]) for e in (left,right)])
                    if result["cycle"]["status"] != "qualified":
                        row["status"] = "cycle-unqualified"
                    else:
                        row["status"] = result["contact"]["status"]
                    if row["status"] in ("replace-low","replace-high"):
                        endpoint = dict(a=a,mean_residual=result["contact"]["mean_residual"],
                                        folds=result["folds"],cycle=result["cycle"])
                        if row["status"] == "replace-low": left = endpoint
                        else: right = endpoint
                    else:
                        stop = "proximity criterion met" if row["status"] == "proximate" else row["status"]
            rows.append(row)
    return rows


def execute(output, source_commit, remote_ref):
    from scripts import audit_exp497_contact_localization  # noqa: F401
    p, source = load()
    def git(*args):
        return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()
    if (git("rev-parse","HEAD") != source_commit or git("status","--porcelain")
            or git("ls-remote","origin",remote_ref).split() != [source_commit,remote_ref]
            or not parent.imported_sources() <= set(p["source_paths"])):
        raise ValueError("clean exact pushed source/import closure required")
    output = output.resolve()
    marker = ROOT/"artifacts/EXP-497/target-once.json"
    if ROOT/"artifacts/EXP-497" not in output.parents or marker.exists():
        raise ValueError("fresh output and unconsumed target attempt required")
    if shutil.disk_usage(ROOT).free < p["limits"]["initial_free_bytes"]:
        raise ValueError("initial free-space reserve insufficient")
    output.mkdir(parents=True,exist_ok=False)
    binding = dict(source_commit=source_commit,remote_ref=remote_ref,started_utc=distances.utc(),
        plan_sha256=sha256(PLAN),inputs=p["inputs"],sources={s:sha256(ROOT/s) for s in p["source_paths"]},
        runtime=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__),paid_review=p["paid_review"])
    write_json(output/"binding.json",binding)
    started = time.monotonic()
    calls = 0
    def timeout(*_):
        raise cycles_run.BudgetStop("EXP-497 wall limit")
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p["limits"]["wall_seconds"])
    def budget(new_ivp):
        nonlocal calls
        if (shutil.disk_usage(ROOT).free < p["limits"]["minimum_free_bytes"]
                or sum(f.stat().st_size for f in output.iterdir()) > p["limits"]["output_bytes"]-33554432
                or (new_ivp and calls >= p["limits"]["max_target_ivps"])):
            raise cycles_run.BudgetStop("target IVP/storage limit reached")
        if new_ivp: calls += 1
    try:
        fold_controls = folds_run.controls(p["fold"])
        write_json(output/"fold-controls.json",fold_controls)
        if not all(r["passed"] for r in fold_controls):
            raise ValueError("fold controls failed; no targets")
        cycles_run.controls(output)
        audit_exp497_contact_localization.check_periodic_controls(output)
        write_json(marker,binding)
        def evaluate(spec,candidates,seed):
            profiles = []
            for method in p["fold"]["solvers"]:
                profile = cycles_run.run_profile(spec,method,seed,p["periodic"],output,budget)
                if "error" in profile:
                    raise RuntimeError("periodic profile exception; retained prefix: "+profile["error"])
                profiles.append(profile)
            pair = cycles_run.compare_profiles(profiles,p["periodic"])
            cycle = dict(spec=spec,profiles=profiles,pair=pair,status="qualified" if pair["passed"] else "unqualified")
            # Explicitly keep six/eight cardinalities in addition to primitive-period checks.
            if pair["passed"] and not all(w["counts"] == dict(historical=6,barrio=8)
                    for profile in profiles for w in profile["metric"]["windows"]):
                cycle["status"] = "unqualified"
                cycle["count_failure"] = True
            results = []
            if cycle["status"] == "qualified":
                for c in candidates:
                    par = RosslerParameters(**c["parameters"])
                    rhs = lambda t,q:rossler_rhs(t,q,par)
                    jac = lambda t,q:rossler_jacobian(q,par)
                    hvv = lambda t,q,v:np.array([0.,0.,2*v[0]*v[2]])
                    section = replace(legacy_rossler_section(par),direction=-1)
                    rows = []
                    for method in p["fold"]["solvers"]:
                        label = c["id"]+"--"+method
                        write_json(output/(label+"-started.json"),dict(candidate_id=c["id"],method=method,started_utc=distances.utc()))
                        def retain(suffix,raw):
                            budget(True)
                            with (output/f"{label}--{suffix}.npz").open("xb") as stream:
                                np.savez_compressed(stream,**raw)
                        row = folds_run.run_candidate(c,method,p["fold"],rhs,jac,hvv,section,retain)
                        write_json(output/(label+".json"),row)
                        rows.append(row)
                        print(label+": completed",flush=True)
                    results.append(dict(compare(c,rows,p["fold"]),parent_id=c["parent_id"]))
            contact = measure(results,cycle,p) if cycle["status"] == "qualified" else None
            result = dict(cycle=cycle,folds=results,contact=contact)
            write_json(output/(spec["id"]+"--point.json"),result)
            print(spec["id"]+": complete point",flush=True)
            return result
        rows = campaign(p,source,evaluate)
        write_json(output/"summary.json",dict(experiment_id="EXP-497",status="completed",binding=binding,
            rows=rows,parent_ledger=source["data"]["ledger"],target_ivps=calls,
            elapsed_seconds=time.monotonic()-started,completed_utc=distances.utc(),
            files=inventory(output),marker_sha256=sha256(marker),symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True,target_ivps=calls,summary_sha256=sha256(output/"summary.json"))))
    except BaseException as exc:
        write_json(output/"failure.json",dict(error_type=type(exc).__name__,message=str(exc),
            target_ivps=calls,utc=distances.utc(),files=inventory(output)))
        raise
    finally:
        signal.alarm(0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare",action="store_true")
    parser.add_argument("--execute",action="store_true")
    parser.add_argument("--output-dir",type=Path)
    parser.add_argument("--source-commit")
    parser.add_argument("--remote-ref")
    a = parser.parse_args()
    if a.prepare and a.execute: parser.error("prepare and execute are separate")
    if a.prepare: prepare()
    elif a.execute:
        if not all((a.output_dir,a.source_commit,a.remote_ref)): parser.error("execution requires output/source/ref")
        execute(a.output_dir,a.source_commit,a.remote_ref)
    else:
        load()
        print(json.dumps(dict(preflight=True,new_target_ivps=0)))


if __name__ == "__main__":
    main()

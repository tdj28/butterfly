#!/usr/bin/env python3
"""Frozen complete-census analysis of EXP-499 archives, with zero integrations."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

from butterfly._paired_startup import inventory,sha256,write_json
from butterfly import decimal_taylor as taylor
from scripts import plot_exp499_decimal_reference as parent
from scripts import exp500_census_analysis as analysis

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/"experiments/manifests/EXP-500-complete-polynomial-census.json"
PARENT = ROOT/"docs/experiments/receipts/EXP-499-decimal-event-reference-result.json"
PARENT_SHA = "d8e01f7cf572f5a77a0319fc59aa465f6e5f2ce9c590d613c7ebbd7cfd29c8d5"
RAW = ROOT/"artifacts/EXP-499/target-cef7b57"
RAW_SHA = "340617c9dfde4240a468b04574f87dc01c2cc3f13a6e488d933050adef1deab3"
EXPLICIT = ["scripts/run_exp500_polynomial_census.py","scripts/audit_exp500_polynomial_census.py",
    "scripts/exp500_census_analysis.py","python/butterfly/polynomial_census.py",
    "scripts/plot_exp499_decimal_reference.py","scripts/verify_quadratic_symbolic_control.py",
    "tests/test_polynomial_census.py","tests/test_exp500_polynomial_census.py",
    "docs/experiments/EXP-500-complete-polynomial-census.md",
    "experiments/manifests/EXP-500-complete-polynomial-census.json","pyproject.toml","uv.lock"]


def utc(): return datetime.now(timezone.utc).isoformat()


def expected():
    if sha256(PARENT) != PARENT_SHA: raise ValueError("audited parent hash differs")
    old = json.loads(PARENT.read_bytes())
    p,_ = parent.validate(old)
    trials = [dict(id=t["id"],candidate_id=t["candidate_id"],side_index=t["side_index"],
        initial=t["initial"],horizon=t["horizon"],profiles=[dict(configuration=v["configuration"],raw_path=v["raw_path"])
        for v in r["profiles"]]) for t,r in zip(p["trials"],old["rows"],strict=True)]
    return dict(experiment_id="EXP-500",status="prospective-outcome-informed-saved-polynomial-census",
        trials=trials,ledger=old["ledger"],section=p["section"],scales=p["scales"],
        limits=dict(wall_seconds=7200,output_bytes=512*1024**2,initial_free_bytes=9*1024**3,
                    minimum_free_bytes=8*1024**3,segments=1_000_000),
        isolation=dict(time_width="1e-25",maximum_depth=160,maximum_nodes=2048,maximum_refinements=256),
        comparison=dict(time="1e-12",scaled_state="1e-9",angle="1e-7",initial_time_cutoff="1e-8",join_jump="1e-20"),
        raw_summary_sha256=RAW_SHA,parent_sha256=PARENT_SHA,new_integrations=0,
        inputs={**p["inputs"],str(parent.run.PLAN.relative_to(ROOT)):sha256(parent.run.PLAN),
                str(PARENT.relative_to(ROOT)):PARENT_SHA},
        source_paths=sorted(set(p["source_paths"])|set(EXPLICIT)),
        paid_review="not_run-human-approval-policy",repairs_exp498=False,symbolic_chains_verified=False)


def load():
    p = json.loads(PLAN.read_bytes())
    if p != expected() or any(sha256(ROOT/n) != h for n,h in p["inputs"].items()):
        raise ValueError("EXP-500 frozen contract differs")
    return p,json.loads(PARENT.read_bytes())


def authenticate_raw(p):
    if sha256(RAW/"summary.json") != RAW_SHA: raise ValueError("raw summary anchor differs")
    raw = json.loads((RAW/"summary.json").read_bytes())
    if (raw["files"] != inventory(RAW,omit=("summary.json",)) or raw["binding"]["source_commit"] != parent.SOURCE
            or raw["ledger"] != p["ledger"] or raw["target_ivps"] != 64 or raw["status"] != "completed"
            or raw["binding"]["sources"] != {s:sha256(ROOT/s) for s in parent.run.load()[0]["source_paths"]}):
        raise ValueError("complete original raw/source inventory differs")
    return raw


def fixture_controls():
    cases = [([1,0,1],0),([-1,2],1),([3,-16,16],2),([0,-1,1],2),([1,-4,4],1)]
    from butterfly import polynomial_census as c
    for power,count in cases:
        result = c.verify(power,1,c.isolate(power,1))
        if not result["complete"] or len(result["roots"]) != count: raise ValueError("exact fixture control failed")
    return dict(passed=True,cases=len(cases),new_integrations=0)


def saved_controls(output):
    output.mkdir(parents=True,exist_ok=False)
    fixture_controls()
    rows = []
    known = json.loads((RAW/"controls.json").read_bytes())["profiles"]
    for config in parent.run.CONFIGS:
        for kind in ("rotation","near-tangent","polynomial"):
            name = config["name"]+"--"+kind+".json.gz"
            _,raw = taylor.load_stream(RAW/"controls"/name)
            section = dict(offset="0.99999999" if kind == "near-tangent" else (2 if kind == "polynomial" else 0),gate_upper=10)
            result,proof = analysis.profile(raw,section)
            replay,_ = analysis.profile(raw,section,certificate=proof)
            wanted = 1 if kind == "polynomial" else 2
            if result != replay or not result["complete"] or len(result["events"]) != wanted:
                raise ValueError("complete stored analytic census control failed")
            baseline = next(v for v in known if v["config"] == config["name"] and v["kind"] == kind)["events"]
            if kind == "rotation": baseline = [dict(time="0",state=raw["initial"])]+baseline
            identity = analysis.compare_events(result["events"],baseline,raw["scales"])
            if not identity["passed"]: raise ValueError("stored analytic root identities differ")
            write_json(output/(name+".json"),dict(result=result,certificates=proof,raw_sha256=sha256(RAW/"controls"/name)))
            rows.append(dict(configuration=config["name"],kind=kind,roots=len(result["events"]),identity=identity,passed=True))
    return dict(passed=True,profiles=rows,new_integrations=0)


def execute(output,source,remote):
    from scripts import audit_exp500_polynomial_census  # noqa: F401
    p,old = load()
    def git(*args): return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()
    if (git("rev-parse","HEAD") != source or git("status","--porcelain")
            or git("ls-remote","origin",remote).split() != [source,remote]):
        raise ValueError("clean live-pushed execution source required")
    imported = parent.run.parent_plot.run.contact.parent.imported_sources()
    if not imported <= set(p["source_paths"]): raise ValueError("imported source closure differs")
    marker = ROOT/"artifacts/EXP-500/analysis-once.json"
    output = output.resolve()
    if ROOT/"artifacts/EXP-500" not in output.parents or marker.exists():
        raise ValueError("fresh analysis namespace and marker required")
    if shutil.disk_usage(ROOT).free < p["limits"]["initial_free_bytes"]: raise ValueError("initial disk reserve")
    authenticate_raw(p)
    def forbidden(*args,**kwargs): raise RuntimeError("EXP-500 must not integrate")
    taylor.integrate = forbidden
    output.mkdir(parents=True,exist_ok=False)
    binding = dict(source_commit=source,remote_ref=remote,started_utc=utc(),plan_sha256=sha256(PLAN),
        sources={s:sha256(ROOT/s) for s in p["source_paths"]},inputs=p["inputs"],raw_summary_sha256=RAW_SHA,
        runtime=dict(python=sys.version),new_integrations=0,paid_review=p["paid_review"])
    write_json(output/"binding.json",binding)
    count,segments,start = 0,0,time.monotonic()
    def budget():
        nonlocal segments
        segments += 1
        if segments > p["limits"]["segments"]: raise RuntimeError("segment budget")
        if segments % 1024 == 1 and (shutil.disk_usage(ROOT).free < p["limits"]["minimum_free_bytes"]
                or sum(f.stat().st_size for f in output.rglob("*") if f.is_file()) > p["limits"]["output_bytes"]-16*1024**2):
            raise RuntimeError("storage budget")
    def timeout(*_): raise TimeoutError("EXP-500 phase deadline")
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p["limits"]["wall_seconds"])
    try:
        write_json(output/"controls.json",saved_controls(output/"controls"))
        write_json(marker,binding)
        rows = []
        for trial,old_row in zip(p["trials"],old["rows"],strict=True):
            profiles = []
            for item in trial["profiles"]:
                label = trial["id"]+"--"+item["configuration"]
                write_json(output/(label+"-started.json"),dict(id=trial["id"],configuration=item["configuration"],started_utc=utc()))
                header,raw = taylor.load_stream(RAW/item["raw_path"])
                if (header["initial"] != trial["initial"] or header["horizon"] != trial["horizon"]
                        or header["config"]["name"] != item["configuration"]): raise ValueError("raw trial identity")
                result,proof = analysis.profile(raw,p["section"],before_segment=budget)
                write_json(output/(label+"-certificates.json"),proof)
                profile = dict(configuration=item["configuration"],raw_path=item["raw_path"],
                    raw_sha256=sha256(RAW/item["raw_path"]),analysis=result)
                write_json(output/(label+"-result.json"),profile)
                profiles.append(profile)
                count += 1
                print(json.dumps(dict(completed_profiles=count,segments=segments)),flush=True)
            row = dict(id=trial["id"],profiles=profiles,comparison=analysis.compare(profiles,old_row,p["scales"]))
            write_json(output/(trial["id"]+".json"),row)
            rows.append(row)
        write_json(output/"summary.json",dict(experiment_id="EXP-500",status="completed",binding=binding,
            ledger=p["ledger"],rows=rows,profiles=count,segments=segments,new_integrations=0,
            elapsed_seconds=time.monotonic()-start,completed_utc=utc(),files=inventory(output),
            marker_sha256=sha256(marker),repairs_exp498=False,symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True,summary_sha256=sha256(output/"summary.json"))))
    except BaseException as exc:
        signal.alarm(0)
        write_json(output/"failure.json",dict(error_type=type(exc).__name__,message=str(exc),utc=utc(),
            completed_profiles=count,segments=segments,files=inventory(output),new_integrations=0))
        raise
    finally: signal.alarm(0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    for name in ("prepare","fixture-controls","saved-controls","execute"): mode.add_argument("--"+name,action="store_true")
    parser.add_argument("--output-dir",type=Path)
    parser.add_argument("--source-commit")
    parser.add_argument("--remote-ref")
    args = parser.parse_args()
    if args.prepare: write_json(PLAN,expected())
    elif args.fixture_controls: print(json.dumps(fixture_controls()))
    elif args.saved_controls:
        if not args.output_dir: parser.error("fresh controls directory required")
        result = saved_controls(args.output_dir)
        write_json(args.output_dir/"controls.json",result)
        print(json.dumps(result))
    elif args.execute:
        if not all((args.output_dir,args.source_commit,args.remote_ref)): parser.error("output/source/ref required")
        execute(args.output_dir,args.source_commit,args.remote_ref)
    else:
        p,_ = load()
        print(json.dumps(dict(valid=True,trials=len(p["trials"]),new_integrations=0)))


if __name__ == "__main__": main()

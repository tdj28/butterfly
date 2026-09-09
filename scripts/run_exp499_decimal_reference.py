#!/usr/bin/env python3
"""All-input decimal reference; frozen local CPU accuracy pilot."""
import argparse
from decimal import Decimal as D, localcontext
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

from butterfly import decimal_taylor as taylor
from butterfly._paired_startup import inventory, sha256, write_json
from butterfly.models import RosslerParameters
from butterfly.poincare import legacy_rossler_section
from scripts import plot_exp498_boundary_transport as parent_plot
from scripts.exp499_reference_controls import CONFIGS, SCALES, controls

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/"experiments/manifests/EXP-499-decimal-event-reference.json"
PARENT = ROOT/"docs/experiments/receipts/EXP-498-boundary-transport-result.json"
PARENT_SHA = "f327a6acb9bb72cd0286ff41090f38e12e3b10a0ff9f476b0a6b2f705e176344"
TRANSITIVE_INPUTS = {
    "docs/experiments/receipts/EXP-486-return-image-fold-result.json": "74fd97ef7c32e56a8c29d32113ab7cfa2531f9a48caf543906beb8cb2b5762d4",
    "docs/experiments/receipts/EXP-491-event-sheet-result.json": "d96454454290ed83d5503fce91f9b86ccce516b40b50a84b9d35ab512f6fc879",
}
EXPLICIT = ["scripts/run_exp499_decimal_reference.py", "scripts/audit_exp499_decimal_reference.py",
    "scripts/exp499_reference_controls.py", "python/butterfly/decimal_taylor.py",
    "tests/test_decimal_taylor.py", "tests/test_exp499_decimal_reference.py",
    "docs/experiments/EXP-499-decimal-event-reference.md",
    "experiments/manifests/EXP-499-decimal-event-reference.json", "pyproject.toml", "uv.lock"]


def parent():
    if sha256(PARENT) != PARENT_SHA:
        raise ValueError("parent receipt changed")
    result = json.loads(PARENT.read_bytes())
    plan, _ = parent_plot.validate(result)
    return plan, result


def derive(old_plan, old):
    rows = []
    for candidate in old["rows"]:
        for index, side in enumerate(candidate["boundary"]["sides"]):
            reports = side["reports"]
            if reports[0]["initial_state"] != reports[1]["initial_state"] or reports[0]["horizon"] != reports[1]["horizon"]:
                raise ValueError("same realized input required")
            events = [[e for e in report["reconstructed"] if e["accepted"]] for report in reports]
            if len(events[0]) != len(events[1]):
                raise ValueError("paired parent event count differs")
            boxes = []
            with localcontext() as ctx:
                ctx.prec = 70
                for a,b in zip(*events, strict=True):
                    middle = (D.from_float(a["time"])+D.from_float(b["time"]))/2
                    boxes.append([str(middle-D("1e-5")),str(middle+D("1e-5"))])
            rows.append(dict(id=candidate["id"]+f"--side-{index}", candidate_id=candidate["id"],
                side_index=index, dose=side["dose"], initial=reports[0]["initial_state"],
                horizon=reports[0]["horizon"], boxes=boxes,
                original_candidate_qualified=candidate["geometry"]["analysis"]["qualified"],
                historical_parent_qualified=candidate["parent_qualified"]))
    if len(rows) != 32 or sum(len(row["boxes"]) for row in rows) != 240:
        raise ValueError("complete input/event matrix required")
    return rows


def expected():
    p, old = parent()
    parameters = p["anchor_parameters"]
    section = legacy_rossler_section(RosslerParameters(**parameters))
    return dict(experiment_id="EXP-499",status="prospective-exploratory-accuracy-reference",
        configurations=CONFIGS, scales=SCALES, ledger=old["ledger"], trials=derive(p, old),
        field=dict(constant=[0,0,parameters["b"]],
            linear=[[0,1,-1],[0,2,-1],[1,0,1],[1,1,parameters["a"]],[2,2,-parameters["c"]]],
            quadratic=[[2,0,2,1]]), section=dict(offset=section.offset,gate_upper=section.gate_upper),
        reference_time=1e-12, reference_state=1e-9, original_time=p["boundary"]["side_solver_time"],
        original_state=p["boundary"]["side_solver_scaled_state"],
        limits=dict(target_ivps=64,wall_seconds=7200,output_bytes=2*1024**3,
            initial_free_bytes=11*1024**3,minimum_free_bytes=8*1024**3),
        inputs={**p["inputs"],**TRANSITIVE_INPUTS,str(PARENT.relative_to(ROOT)):PARENT_SHA,
            str(parent_plot.run.PLAN.relative_to(ROOT)):sha256(parent_plot.run.PLAN)},
        required_sources=sorted(set(EXPLICIT)|set(p["source_paths"])|{"scripts/plot_exp498_boundary_transport.py"}),
        paid_review="not_run-human-approval-policy", symbolic_chains_verified=False)


def load():
    plan = json.loads(PLAN.read_bytes())
    exp = expected()
    if ({k:v for k,v in plan.items() if k != "source_paths"} != exp
            or not set(exp["required_sources"]) <= set(plan["source_paths"])
            or any(sha256(ROOT/path) != value for path,value in plan["inputs"].items())):
        raise ValueError("frozen EXP-499 contract differs")
    return plan, parent()[1]


def distance(a, b, scales):
    with localcontext() as ctx:
        ctx.prec = 65
        values = [abs(taylor.exact(x)-taylor.exact(y))/taylor.exact(s) for x,y,s in zip(a["state"],b["state"],scales,strict=True)]
        return dict(time=float(abs(taylor.exact(a["time"])-taylor.exact(b["time"]))), state=float(max(values)))


def compare(trial, profiles, old, plan):
    source = next(r for r in old["rows"] if r["id"] == trial["candidate_id"])["boundary"]["sides"][trial["side_index"]]
    original = [[e for e in report["reconstructed"] if e["accepted"]] for report in source["reports"]]
    if ([r["configuration"] for r in profiles] != [c["name"] for c in CONFIGS]
            or not trial["boxes"] or any(len(r["events"]) != len(trial["boxes"]) for r in profiles)):
        raise ValueError("complete ordered configuration pair required")
    rows = []
    for index in range(len(trial["boxes"])):
        a,b = [profile["events"][index] for profile in profiles]
        error = distance(a,b,plan["scales"])
        qualified = error["time"] <= plan["reference_time"] and error["state"] <= plan["reference_state"]
        comparisons = []
        for j, method in enumerate(("DOP853","Radau")):
            for profile in profiles:
                d = distance(original[j][index],profile["events"][index],plan["scales"])
                comparisons.append(dict(method=method,configuration=profile["configuration"],**d,
                    within_original_thresholds=bool(d["time"] <= plan["original_time"] and d["state"] <= plan["original_state"])))
        rows.append(dict(index=index,reference_error=error,reference_qualified=qualified,original_comparisons=comparisons))
    return dict(reference_qualified=all(row["reference_qualified"] for row in rows),events=rows,
        repairs_exp498=False,symbolic_chains_verified=False)


def execute(output, source, remote):
    from scripts import audit_exp499_decimal_reference  # noqa: F401
    p, old = load()
    def git(*args): return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()
    if (git("rev-parse","HEAD") != source or git("status","--porcelain")
            or git("ls-remote","origin",remote).split() != [source,remote]
            or not parent_plot.run.contact.parent.imported_sources() <= set(p["source_paths"])):
        raise ValueError("clean live-pushed source/import inventory required")
    marker = ROOT/"artifacts/EXP-499/target-once.json"
    output = output.resolve()
    if ROOT/"artifacts/EXP-499" not in output.parents or marker.exists():
        raise ValueError("fresh target namespace and unconsumed attempt required")
    if shutil.disk_usage(ROOT).free < p["limits"]["initial_free_bytes"]:
        raise ValueError("initial disk reserve")
    output.mkdir(parents=True,exist_ok=False)
    b = dict(source_commit=source,remote_ref=remote,started_utc=parent_plot.run.boundary.utc(),
        plan_sha256=sha256(PLAN),sources={s:sha256(ROOT/s) for s in p["source_paths"]},inputs=p["inputs"],
        runtime=dict(python=sys.version,decimal_library=__import__("decimal").__libmpdec_version__),paid_review=p["paid_review"])
    write_json(output/"binding.json",b)
    start, calls, steps = time.monotonic(), 0, 0
    def budget():
        nonlocal steps
        steps += 1
        if steps % 128 == 1 and (shutil.disk_usage(ROOT).free < p["limits"]["minimum_free_bytes"]
                or sum(f.stat().st_size for f in output.rglob("*") if f.is_file()) > p["limits"]["output_bytes"]-64*1024**2):
            raise RuntimeError("EXP-499 storage reserve")
    def timeout(*_): raise TimeoutError("EXP-499 whole-run deadline")
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p["limits"]["wall_seconds"])
    try:
        write_json(output/"controls.json",controls(output/"controls"))
        write_json(marker,b)
        rows = []
        for trial in p["trials"]:
            profiles = []
            for config in p["configurations"]:
                if calls >= p["limits"]["target_ivps"]:
                    raise RuntimeError("target integration cap")
                label = trial["id"]+"--"+config["name"]
                write_json(output/(label+"-started.json"),dict(id=trial["id"],configuration=config["name"],started_utc=parent_plot.run.boundary.utc()))
                calls += 1
                name = label+".json.gz"
                raw = taylor.run_profile(output/name,label,trial["initial"],p["field"],trial["horizon"],config,p["scales"],before_step=budget)
                curve = taylor.Curve(raw)
                events = [taylor.root(curve,box,p["section"]["offset"],gate_upper=p["section"]["gate_upper"]) for box in trial["boxes"]]
                profile = dict(configuration=config["name"],raw_path=name,events=events,steps=len(raw["steps"]),maximum_tail=raw["maximum_tail"])
                write_json(output/(label+"-events.json"),profile)
                profiles.append(profile)
                print(label+": completed",flush=True)
            result = dict(id=trial["id"],profiles=profiles,analysis=compare(trial,profiles,old,p))
            write_json(output/(trial["id"]+".json"),result)
            rows.append(result)
        write_json(output/"summary.json",dict(experiment_id="EXP-499",status="completed",binding=b,ledger=p["ledger"],
            rows=rows,target_ivps=calls,elapsed_seconds=time.monotonic()-start,completed_utc=parent_plot.run.boundary.utc(),
            marker_sha256=sha256(marker),files=inventory(output),repairs_exp498=False,symbolic_chains_verified=False))
        print(json.dumps(dict(completed=True,target_ivps=calls,summary_sha256=sha256(output/"summary.json"))))
    except BaseException as exc:
        signal.alarm(0)
        write_json(output/"failure.json",dict(error_type=type(exc).__name__,message=str(exc),target_ivps=calls,
            utc=parent_plot.run.boundary.utc(),files=inventory(output)))
        raise
    finally:
        signal.alarm(0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare",action="store_true")
    parser.add_argument("--controls-only",action="store_true")
    parser.add_argument("--execute",action="store_true")
    parser.add_argument("--output-dir",type=Path)
    parser.add_argument("--source-commit")
    parser.add_argument("--remote-ref")
    args = parser.parse_args()
    if sum((args.prepare,args.controls_only,args.execute)) > 1:
        parser.error("separate modes required")
    if args.prepare:
        from scripts import audit_exp499_decimal_reference  # noqa: F401
        p = expected()
        p["source_paths"] = sorted(set(p["required_sources"])|parent_plot.run.contact.parent.imported_sources())
        write_json(PLAN,p)
    elif args.controls_only:
        if not args.output_dir: parser.error("fresh control output required")
        result = controls(args.output_dir)
        write_json(args.output_dir/"controls.json",result)
        print(json.dumps(dict(controls_passed=True,new_target_integrations=0)))
    elif args.execute:
        if not all((args.output_dir,args.source_commit,args.remote_ref)): parser.error("output/source/ref required")
        execute(args.output_dir,args.source_commit,args.remote_ref)
    else:
        p,_ = load()
        print(json.dumps(dict(valid=True,trials=len(p["trials"]),target_ivps=64,new_integrations=0)))


if __name__ == "__main__": main()

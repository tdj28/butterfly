#!/usr/bin/env python3
"""Prospective local limiting-grazing contact pilot, with durable full traces."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal as D, localcontext
import decimal
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

from butterfly import decimal_grazing as numeric
from butterfly.decimal_taylor import exact, load_stream
from butterfly._paired_startup import inventory, sha256, write_json
from scripts import exp500_census_analysis as census
from scripts import exp501_contact_analysis as analysis

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/"experiments/manifests/EXP-501-limiting-grazing-contact.json"
INPUTS = {
    "experiments/manifests/EXP-498-boundary-transport.json":"495e61145346fb6b2e13cd726b4d00367072eb91d5b53a31cb84e247a9fafc6a",
    "experiments/manifests/EXP-499-decimal-event-reference.json":"bf876d4d95f67eaa9ff79532519ecf344dcf8763b7b466e0afe026daa7bce256",
    "docs/experiments/receipts/EXP-498-boundary-transport-result.json":"f327a6acb9bb72cd0286ff41090f38e12e3b10a0ff9f476b0a6b2f705e176344",
    "docs/experiments/receipts/EXP-497-contact-localization-result.json":"ed229b4a772ef19d227272006401d19090ee5e28a357791f25400cafa3271cff"}
EXPLICIT = ["scripts/run_exp501_limiting_contact.py", "scripts/audit_exp501_limiting_contact.py",
    "scripts/exp501_contact_analysis.py", "scripts/exp501_analytic_controls.py", "scripts/exp500_census_analysis.py",
    "python/butterfly/decimal_grazing.py", "python/butterfly/decimal_taylor.py", "python/butterfly/polynomial_census.py",
    "tests/test_exp501_limiting_contact.py", "tests/test_decimal_grazing.py",
    "docs/experiments/EXP-501-limiting-grazing-contact.md", "experiments/manifests/EXP-501-limiting-grazing-contact.json",
    "pyproject.toml", "uv.lock"]


def utc():
    return datetime.now(timezone.utc).isoformat()


def imported():
    return {Path(m.__file__).resolve().relative_to(ROOT).as_posix() for m in list(sys.modules.values())
            if getattr(m,"__file__",None) and Path(m.__file__).resolve().is_relative_to(ROOT)
            and Path(m.__file__).suffix == ".py" and not Path(m.__file__).resolve().is_relative_to(ROOT/".venv")}


def expected():
    for name, digest in INPUTS.items():
        if sha256(ROOT/name) != digest:
            raise ValueError("public input hash differs")
    p498, p499, old, anchor = [json.loads((ROOT/name).read_bytes()) for name in INPUTS]
    selected = [r for r in anchor["rows"] if r["status"] == "proximate"]
    if len(selected) != 1 or selected[0]["level"] != 3 or selected[0]["result"]["cycle"]["status"] != "qualified":
        raise ValueError("unique audited primitive anchor required")
    cycle = selected[0]["result"]["cycle"]
    cycles = [dict(method=v["method"],phase=w["phase"],states=w["event_states"]["historical"])
              for v in cycle["profiles"] for w in v["metric"]["windows"]]
    if len(cycles) != 4 or any(len(c["states"]) != 6 for c in cycles):
        raise ValueError("complete 2-method/2-window/6-event anchor required")
    candidates = []
    with localcontext() as ctx:
        ctx.prec = 70
        for candidate, row in zip(p498["candidates"],old["rows"],strict=True):
            if candidate["id"] != row["id"]:
                raise ValueError("candidate order differs")
            roots = [v["root"] for v in row["boundary"]["analysis"]["solvers"]]
            c = {k:candidate[k] for k in ("id","initial_state","initial_tangent","u_box","time_box","accepted_prefix","parent_qualified")}
            c.update(seed_u=str(sum(exact(r["u"]) for r in roots)/2),
                     seed_time=str(sum(exact(r["time"]) for r in roots)/2),
                     original_exp498_qualified=row["geometry"]["analysis"]["qualified"])
            candidates.append(c)
    if len(candidates) != 8 or len(old["ledger"]) != 26:
        raise ValueError("complete candidate ledger required")
    return dict(experiment_id="EXP-501",status="prospective-outcome-informed-limiting-contact-pilot",
        candidates=candidates,cycles=cycles,ledger=old["ledger"],field=numeric.augment(p499["field"]),
        section=p499["section"],configurations=numeric.CONFIGS,inputs=INPUTS,
        limits=dict(target_ivps=128,wall_seconds=7200,output_bytes=4*1024**3,
                    initial_free_bytes=9*1024**3,minimum_free_bytes=8*1024**3),
        thresholds=dict(root_residual="1e-24",root_u="1e-12",root_time="1e-12",root_state="1e-9",
                        prefix_time="1e-12",prefix_state="1e-9",contact="1e-4",prefix_cut="0.05"),
        paid_review="not_requested-human-approval-policy",symbolic_chains_verified=False)


def load():
    p = json.loads(PLAN.read_bytes())
    if ({k:v for k,v in p.items() if k != "source_paths"} != expected()
            or not set(EXPLICIT) <= set(p["source_paths"])):
        raise ValueError("EXP-501 frozen plan differs")
    return p


def execute(output,source,remote):
    from scripts import audit_exp501_limiting_contact as auditor
    from scripts import exp501_analytic_controls as controls
    p = load()
    def git(*args):
        return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()
    if (git("rev-parse","HEAD") != source or git("status","--porcelain")
            or git("ls-remote","origin",remote).split() != [source,remote]):
        raise ValueError("clean live-pushed source required")
    if not imported() <= set(p["source_paths"]):
        raise ValueError("import closure differs")
    output = output.resolve()
    marker = ROOT/"artifacts/EXP-501/target-once.json"
    if ROOT/"artifacts/EXP-501" not in output.parents or output.exists() or marker.exists():
        raise ValueError("fresh output and unconsumed attempt required")
    if shutil.disk_usage(ROOT).free < p["limits"]["initial_free_bytes"]:
        raise ValueError("initial disk reserve")
    output.mkdir(parents=True)
    binding = dict(source_commit=source,remote_ref=remote,started_utc=utc(),plan_sha256=sha256(PLAN),
        sources={s:sha256(ROOT/s) for s in p["source_paths"]},inputs=INPUTS,
        runtime=dict(python=sys.version,decimal=decimal.__libmpdec_version__),paid_review=p["paid_review"])
    write_json(output/"binding.json",binding)
    start, ivps, steps = time.monotonic(), 0, 0
    def budget():
        nonlocal steps
        steps += 1
        if steps % 1024 == 1 and (shutil.disk_usage(ROOT).free < p["limits"]["minimum_free_bytes"]
                or sum(f.stat().st_size for f in output.rglob("*") if f.is_file()) > p["limits"]["output_bytes"]-32*1024**2):
            raise RuntimeError("storage budget")
    def timeout(*_):
        raise TimeoutError("EXP-501 phase deadline")
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p["limits"]["wall_seconds"])
    try:
        control_receipt = controls.run(output/"controls")
        auditor.check_controls(output/"controls",control_receipt)
        write_json(output/"controls.json",control_receipt)
        write_json(marker,binding)
        rows = []
        for candidate in p["candidates"]:
            profiles = []
            for config in numeric.CONFIGS:
                label = candidate["id"]+"--"+config["name"]
                write_json(output/(label+"-started.json"),dict(id=candidate["id"],configuration=config["name"],started_utc=utc()))
                def integrate_step(iteration,initial,end,field,configuration):
                    nonlocal ivps
                    if ivps >= p["limits"]["target_ivps"]:
                        raise RuntimeError("target IVP budget")
                    name = label+f"--iteration-{iteration}.json.gz"
                    ivps += 1
                    raw = numeric.run_profile(output/name,initial,field,end,configuration,budget)
                    return raw,name
                shooting, raw = numeric.shooting(candidate,p["field"],p["section"]["offset"],config,integrate_step)
                result = dict(configuration=config["name"],shooting=shooting,census=None)
                if shooting["status"] == "qualified":
                    with localcontext() as ctx:
                        ctx.prec = config["digits"]
                        end = D(shooting["trace"][-1]["time"])-D("0.05")
                    prefix = numeric.prefix_state(raw,end)
                    result["census"], certificates = census.profile(prefix,p["section"],before_segment=budget)
                    write_json(output/(label+"-certificates.json"),certificates)
                write_json(output/(label+"-result.json"),result)
                profiles.append(result)
                print(json.dumps(dict(completed_profiles=len(rows)*2+len(profiles),target_ivps=ivps)),flush=True)
            row = dict(id=candidate["id"],profiles=profiles,comparison=analysis.compare(profiles,candidate,p["cycles"]))
            write_json(output/(candidate["id"]+".json"),row)
            rows.append(row)
        write_json(output/"summary.json",dict(experiment_id="EXP-501",status="completed",binding=binding,
            ledger=p["ledger"],rows=rows,analysis=analysis.aggregate(rows),target_ivps=ivps,
            elapsed_seconds=time.monotonic()-start,completed_utc=utc(),files=inventory(output),marker_sha256=sha256(marker)))
        print(json.dumps(dict(completed=True,summary_sha256=sha256(output/"summary.json"))))
    except BaseException as exc:
        signal.alarm(0)
        write_json(output/"failure.json",dict(error_type=type(exc).__name__,message=str(exc),utc=utc(),
            target_ivps=ivps,files=inventory(output)))
        raise
    finally:
        signal.alarm(0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    for name in ("prepare","controls","execute"):
        mode.add_argument("--"+name,action="store_true")
    parser.add_argument("--output-dir",type=Path)
    parser.add_argument("--source-commit")
    parser.add_argument("--remote-ref")
    args = parser.parse_args()
    from scripts import exp501_analytic_controls as controls
    from scripts import audit_exp501_limiting_contact as auditor
    if args.prepare:
        p = expected()
        p["source_paths"] = sorted(imported()|set(EXPLICIT))
        write_json(PLAN,p)
    elif args.controls:
        if not args.output_dir:
            parser.error("fresh controls directory required")
        result = controls.run(args.output_dir)
        auditor.check_controls(args.output_dir,result)
        write_json(args.output_dir/"controls.json",result)
        print(json.dumps(dict(passed=True,profiles=len(result["profiles"]))))
    elif args.execute:
        if not all((args.output_dir,args.source_commit,args.remote_ref)):
            parser.error("output/source/ref required")
        execute(args.output_dir,args.source_commit,args.remote_ref)
    else:
        p = load()
        print(json.dumps(dict(valid=True,candidates=len(p["candidates"]),target_integrations=0,
                              import_closure=imported() <= set(p["source_paths"]))))


if __name__ == "__main__":
    main()

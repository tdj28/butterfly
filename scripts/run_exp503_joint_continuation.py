#!/usr/bin/env python3
"""Resource-only checkpoint continuation; never resets the EXP-502 attempt."""
import argparse
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from butterfly._paired_startup import inventory,sha256,write_json
from scripts import run_exp502_joint_contact as base
from scripts import audit_exp502_joint_contact as prior_audit

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/"experiments/manifests/EXP-503-joint-contact-continuation.json"
BASE_SHA = "20c9fc885f2eeaf8df6225e487f67ee5d531b64ccaa4e0fe2e7e32bb28091038"
BASE_SOURCE = "69efcd337ea1601256ed60779f1ca6a73712c9cd"
EXPLICIT = ["scripts/run_exp503_joint_continuation.py","scripts/audit_exp503_joint_continuation.py",
    "tests/test_exp503_joint_continuation.py","docs/experiments/EXP-503-joint-contact-resource-continuation.md",
    "experiments/manifests/EXP-503-joint-contact-continuation.json"]


def prefix(slots,specs):
    if (len(slots) != 9 or [s["spec"] for s in slots[:8]] != specs
            or slots[-1].get("role") != "proposal"
            or any(s["status"] not in ("completed","started","not-run") for s in slots)):
        raise ValueError("exact original slot ledger required")
    count = 0
    while count < 8 and slots[count]["status"] == "completed":
        count += 1
    if any(s["status"] == "completed" for s in slots[count:8]) or count < 6:
        raise ValueError("all of a contiguous prefix of at least six points required")
    if count < 8 and any(s["status"] != "not-run" for s in slots[count+1:]):
        raise ValueError("later slot cannot precede interrupted point")
    return count


def original_metadata(original):
    p = base.load()
    if sha256(base.PLAN) != BASE_SHA:
        raise ValueError("original numerical plan changed")
    original = original.resolve()
    failed = json.loads((original/"failure.json").read_bytes())
    b = json.loads((original/"binding.json").read_bytes())
    if (failed["error_type"] != "BudgetStop" or failed["message"] not in ("time/storage cap","wall deadline","target IVP cap")
            or type(failed["target_ivps"]) is not int or not 0 <= failed["target_ivps"] <= p["limits"]["target_ivps"]
            or (original/"summary.json").exists()
            or b["source_commit"] != BASE_SOURCE or b["plan_sha256"] != BASE_SHA
            or b["inputs"] != base.INPUTS or b["sources"] != {n:sha256(ROOT/n) for n in p["source_paths"]}
            or inventory(original,omit=("failure.json",)) != failed["files"]
            or json.loads((original.parent/"target-once.json").read_bytes()) != b):
        raise ValueError("immutable original resource failure/source/raw binding required")
    count = prefix(failed["slots"],p["stencil"])
    for spec in p["stencil"][:count]:
        if json.loads((original/spec["id"]/"point.json").read_bytes())["spec"] != spec:
            raise ValueError("completed checkpoint identity")
    return dict(failure_sha256=sha256(original/"failure.json"),binding=b,files=failed["files"],
        marker_sha256=sha256(original.parent/"target-once.json"),reserved_ivps=failed["target_ivps"],
        slots=failed["slots"],completed_prefix=count)


def expected(original):
    return dict(experiment_id="EXP-503",status="outcome-informed-resource-continuation",
        base_plan_sha256=BASE_SHA,original=original_metadata(original),
        limits=dict(cumulative_reserved_ivps=4096,wall_seconds=7200,output_bytes=4*1024**3,
                    initial_free_bytes=13*1024**3,minimum_free_bytes=8*1024**3),
        paid_review="not-requested-human-approval-policy",scientific_settings_changed=False,
        original_attempt_reset=False,symbolic_chains_verified=False)


def load(original):
    p = json.loads(PLAN.read_bytes())
    if ({k:v for k,v in p.items() if k != "source_paths"} != expected(original)
            or not set(EXPLICIT)|set(base.load()["source_paths"]) <= set(p["source_paths"])):
        raise ValueError("frozen resource continuation differs")
    return p


def startup(p,original):
    target = Path(tempfile.mkdtemp(prefix="exp503-startup-")).resolve()
    names = set(p["source_paths"])|set(base.INPUTS)
    for name in names:
        destination = target/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,destination)
    code = (f"import sys;from pathlib import Path;root=Path({str(target)!r});sys.path[:0]={[str(target),str(target/'python')]!r};"
        "from scripts.run_exp503_joint_continuation import main;main();"
        "assert all(Path(m.__file__).resolve().is_relative_to(root) for n,m in sys.modules.items() "
        "if n.startswith(('scripts.','butterfly')) and getattr(m,'__file__',None))")
    child = subprocess.run([sys.executable,"-I","-B","-c",code,"--original-run",str(original.resolve())],
        cwd=target,capture_output=True,text=True,check=True,timeout=120)
    if any(sha256(ROOT/n) != sha256(target/n) for n in names):
        raise ValueError("copied continuation source identity")
    return dict(passed=True,stdout=child.stdout,stderr=child.stderr,isolated=True,new_integrations=0,
                sources={n:sha256(target/n) for n in sorted(names)})


def replay_controls(original,p):
    startup = json.loads((original/"startup.json").read_bytes())
    if (not startup["passed"] or not startup["isolated"] or startup["target_integrations"] != 0
            or startup["sources"] != {n:sha256(ROOT/n) for n in set(p["source_paths"])|set(base.INPUTS)}
            or json.loads(startup["stdout"]) != dict(valid=True,target_integrations=0,stencil_points=8)):
        raise ValueError("original copied-source startup differs")
    prior_audit.old.fold_audit.check_controls(json.loads((original/"fold-controls.json").read_bytes()),p["fold"])
    prior_audit.old.check_periodic_controls(original)
    prior_audit.decimal_audit.check_controls(original/"decimal-controls",json.loads((original/"decimal-controls.json").read_bytes()))
    if json.loads((original/"response-controls.json").read_bytes()) != prior_audit.response_controls():
        raise ValueError("original response controls differ")
    return dict(passed=True,reused_original_controls=True,new_integrations=0)


def remaining(p,numerical,fetch,measure,progress,completed=lambda *_:None,response_ready=lambda *_:None):
    """Complete the fixed matrix; checkpoint reuse never depends on outcomes."""
    rows = []
    for index,spec in enumerate(numerical["stencil"]):
        reused = index < p["original"]["completed_prefix"]
        progress[index]["status"] = "started"
        rows.append(fetch(spec) if reused else measure(spec))
        progress[index]["status"] = "completed"
        completed(len(rows),reused)
    matrix = base.response.response(rows,numerical["base_vectors"],numerical["anchor"])
    prior_audit.check_scalar(matrix,numerical["base_vectors"],numerical["anchor"])
    response_ready(matrix)
    proposal = None
    previous = p["original"]["slots"][-1]
    if matrix["qualified"]:
        if previous["spec"] is not None and previous["spec"] != matrix["proposal"]:
            raise ValueError("original proposal value cannot change")
        reused = previous["status"] == "completed"
        progress[-1].update(spec=matrix["proposal"],provenance="original" if reused else "continuation",status="started")
        proposal = fetch(matrix["proposal"]) if reused else measure(matrix["proposal"])
        progress[-1]["status"] = "completed"
    else:
        if previous["status"] != "not-run":
            raise ValueError("original proposal conflicts with reconstructed response")
        progress[-1]["reason"] = matrix["reason"]
    return rows,matrix,proposal


def execute(output,original,source,remote):
    p = load(original)
    numerical = base.load()
    def git(*args):
        return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()
    if (git("rev-parse","HEAD") != source or git("status","--porcelain")
            or git("ls-remote","origin",remote).split() != [source,remote]
            or not base.imported() <= set(p["source_paths"])):
        raise ValueError("clean live-pushed continuation/source closure required")
    output,original = output.resolve(),original.resolve()
    marker = ROOT/"artifacts/EXP-503/target-once.json"
    if ROOT/"artifacts/EXP-503" not in output.parents or output.exists() or marker.exists():
        raise ValueError("fresh continuation output and unconsumed new marker required")
    if shutil.disk_usage(ROOT).free < p["limits"]["initial_free_bytes"]:
        raise ValueError("continuation initial reserve")
    output.mkdir(parents=True)
    binding = dict(source_commit=source,remote_ref=remote,started_utc=base.utc(),plan_sha256=sha256(PLAN),
        sources={n:sha256(ROOT/n) for n in p["source_paths"]},original_failure_sha256=p["original"]["failure_sha256"],
        runtime=dict(python=sys.version,numpy=base.np.__version__,scipy=base.scipy.__version__),paid_review=p["paid_review"])
    write_json(output/"binding.json",binding)
    start,calls,checks = time.monotonic(),0,0
    progress = [dict(spec=s,provenance="original" if i < p["original"]["completed_prefix"] else "continuation",status="not-run")
                for i,s in enumerate(numerical["stencil"])]+[dict(spec=None,provenance=None,status="not-run",role="proposal")]
    def budget(integrating=False):
        nonlocal calls,checks
        checks += 1
        if integrating or checks % 1024 == 1:
            if (time.monotonic()-start > p["limits"]["wall_seconds"]
                    or shutil.disk_usage(ROOT).free < p["limits"]["minimum_free_bytes"]
                    or sum(f.stat().st_size for f in output.rglob('*') if f.is_file()) > p["limits"]["output_bytes"]-32*1024**2):
                raise base.previous.cycles_run.BudgetStop("continuation time/storage cap")
        if integrating:
            if calls+p["original"]["reserved_ivps"] >= p["limits"]["cumulative_reserved_ivps"]:
                raise base.previous.cycles_run.BudgetStop("cumulative reserved IVP cap")
            calls += 1
    def timeout(*_):
        raise base.previous.cycles_run.BudgetStop("continuation wall deadline")
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(p["limits"]["wall_seconds"])
    try:
        write_json(output/"startup.json",startup(p,original))
        write_json(output/"control-replay.json",replay_controls(original,numerical))
        budget(False)
        write_json(marker,binding)
        rows,matrix,proposal = remaining(p,numerical,
            lambda spec:json.loads((original/spec["id"]/"point.json").read_bytes()),
            lambda spec:base.evaluate(numerical,spec,output/spec["id"],budget),progress,
            lambda count,reused:print(json.dumps(dict(completed_stencil_points=count,reused=reused,new_target_ivps=calls)),flush=True),
            lambda matrix:write_json(output/"response.json",matrix))
        budget(False)
        write_json(output/"summary.json",dict(experiment_id="EXP-503",status="completed",binding=binding,
            original_failure_sha256=p["original"]["failure_sha256"],rows=rows,proposal=proposal,response=matrix,
            analysis=base.response.verdict(matrix,proposal,numerical["base_vectors"]),progress=progress,
            ledger=numerical["ledger"],new_target_ivps=calls,original_reserved_ivps=p["original"]["reserved_ivps"],
            elapsed_seconds=time.monotonic()-start,completed_utc=base.utc(),files=inventory(output),
            marker_sha256=sha256(marker),symbolic_chains_verified=False,original_attempt_reset=False))
        print(json.dumps(dict(completed=True,new_target_ivps=calls,summary_sha256=sha256(output/"summary.json"))),flush=True)
    except BaseException as exc:
        signal.alarm(0)
        write_json(output/"failure.json",dict(error_type=type(exc).__name__,message=str(exc),utc=base.utc(),
            new_target_ivps=calls,progress=progress,files=inventory(output)))
        raise
    finally:
        signal.alarm(0)


def main():
    from scripts import audit_exp503_joint_continuation  # noqa: F401
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prepare",action="store_true")
    mode.add_argument("--startup",action="store_true")
    mode.add_argument("--execute",action="store_true")
    parser.add_argument("--original-run",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path)
    parser.add_argument("--source-commit")
    parser.add_argument("--remote-ref")
    a = parser.parse_args()
    if a.prepare:
        p = expected(a.original_run)
        p["source_paths"] = sorted(set(EXPLICIT)|set(base.load()["source_paths"])|base.imported())
        write_json(PLAN,p)
    elif a.execute:
        if not all((a.output_dir,a.source_commit,a.remote_ref)):
            parser.error("fresh output/source/ref required")
        execute(a.output_dir,a.original_run,a.source_commit,a.remote_ref)
    else:
        p = load(a.original_run)
        if not base.imported() <= set(p["source_paths"]):
            raise ValueError("continuation import closure differs")
        print(json.dumps(startup(p,a.original_run) if a.startup else dict(valid=True,new_integrations=0,
            reused_stencil_points=p["original"]["completed_prefix"])))


if __name__ == "__main__":
    main()

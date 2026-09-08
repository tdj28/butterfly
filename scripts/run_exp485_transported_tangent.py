#!/usr/bin/env python3
"""One-shot finite-history tangent pilot using authenticated observed returns."""
import argparse
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import scipy
from butterfly._paired_startup import inventory, sha256, write_json
from butterfly.models import RosslerParameters, rossler_rhs, rossler_jacobian
from butterfly.poincare import legacy_rossler_section
from butterfly.return_geometry import first_return_geometry
from butterfly.transported_tangent import dominant_history, assess_direction
from butterfly.paired_input_package import load_package
from butterfly.paired_inputs import load_references
from butterfly.paired_phases import from_reference_audit, _expectation
from butterfly.paired_replay import read_batch
from butterfly.paired_sampling import SECTIONS
from scripts import run_exp484_return_geometry as old
from scripts import audit_exp484_return_geometry as prior
from scripts import summarize_exp482_maps as source

PLAN = ROOT/"experiments/manifests/EXP-485-transported-tangent-pilot.json"
SOURCE_FILES = ("python/butterfly/return_geometry.py", "python/butterfly/transported_tangent.py",
                "scripts/run_exp485_transported_tangent.py", "scripts/run_exp484_return_geometry.py",
                "scripts/audit_exp484_return_geometry.py")


def extract_history(events, point, depth):
    """Exact same-seed predecessor chain, including explicit raw event indices."""
    indices = np.flatnonzero(np.asarray(events["global_seed_ids"]) == point["global_seed_id"])
    times, states = np.asarray(events["times"]), np.asarray(events["states"])
    if (not len(indices) or np.any(np.diff(times[indices]) <= 0)
            or not np.isfinite(times[indices]).all() or not np.isfinite(states[indices]).all()
            or np.any(np.asarray(events["gate_unresolved"])[indices])
            or np.any(np.asarray(events["orientation_unresolved"])[indices])):
        raise ValueError("absent, ambiguous, nonfinite or unordered seed history")
    indices = indices[np.asarray(events["accepted"], bool)[indices]]
    matches = np.flatnonzero(times[indices] == point["saved_pair_times"][0])
    if len(matches) != 1 or matches[0] < depth:
        raise ValueError("missing unique endpoint or insufficient predecessor history")
    position = int(matches[0])
    if not np.array_equal(states[indices[position]], point["initial_state"]):
        raise ValueError("predecessor endpoint differs from EXP-484 state")
    chain = indices[position-depth:position+1]
    return dict(raw_indices=chain.tolist(), times=times[chain].tolist(), states=states[chain].tolist())


def prepare(plan):
    if (sha256(prior.TARGET/"summary.json") != plan["exp484_summary_sha256"]
            or sha256(ROOT/"docs/experiments/receipts/EXP-484-return-geometry-result.json") != plan["exp484_audit_sha256"]):
        raise ValueError("EXP-484 immutable input anchor changed")
    completed = json.loads((prior.TARGET/"summary.json").read_bytes())
    if inventory(prior.TARGET, omit=("summary.json",)) != completed["files"]:
        raise ValueError("EXP-484 output inventory changed")
    selections = old.prepare(json.loads(old.PLAN.read_bytes()))
    if selections != json.loads((prior.TARGET/"selection.json").read_bytes()):
        raise ValueError("EXP-484 exact point selection changed")
    pre_path = source.RUN/"preflight/receipt.json"
    if sha256(pre_path) != plan["preflight482_sha256"]:
        raise ValueError("EXP-482 preflight anchor changed")
    pre = json.loads(pre_path.read_bytes())
    package = load_package(source.RUN/"preflight/inputs", pre["inputs"]["sha256"])
    design, _ = from_reference_audit(package, load_references(package, source.RUN/"preflight/inputs"),
                                   source_commit=source.SOURCE, plan_sha256=pre["plan_sha256"])
    receipt = json.loads((source.RUN/"campaign/receipt.json").read_bytes())
    for selection in selections:
        selection["raw_sources"] = {}
        found = set()
        for trial in design.validate():
            if trial.stage != "collection" or trial.candidate_id != selection["case"] or trial.profile != "rk4-000125":
                continue
            points = [p for p in selection["points"] if p["global_seed_id"] in trial.global_seed_ids]
            if not points:
                continue
            relative = f"collection/phase/receipts/{trial.trial_id}.json"
            path = source.RUN/"campaign"/relative
            if sha256(path) != receipt["files"][relative]["sha256"]:
                raise ValueError("source batch receipt anchor changed")
            recorded = json.loads(path.read_bytes())
            if recorded["status"] != "completed" or recorded["binding"] != design.binding(trial):
                raise ValueError("source batch differs from expected design")
            raw = read_batch(source.RUN/"campaign/collection/phase/trials"/trial.trial_id,
                             _expectation(design, trial, recorded))
            selection["raw_sources"][trial.trial_id] = dict(receipt_sha256=sha256(path), source=raw["source"])
            for point in points:
                if point["bin"] in found:
                    raise ValueError("duplicate point source")
                found.add(point["bin"])
                point["history"] = extract_history(raw["events"][SECTIONS[0]], point, max(plan["depths"]))
                point["history"]["batch_id"] = trial.trial_id
        if found != set(range(40)):
            raise ValueError("incomplete fixed point grid")
    if sum(len(s["points"]) for s in selections)*max(plan["depths"])*len(plan["solvers"]) != plan["limits"]["maximum_target_integrations"]:
        raise ValueError("integration matrix differs from prospective cap")
    return selections


def controls(plan):
    flow = old.controls(plan)
    diagonal = dominant_history([np.diag([2., .1])]*8, depths=plan["depths"])
    isotropic = dominant_history([np.eye(2)]*8, depths=plan["depths"])
    def assess(h):
        return assess_direction({m: h for m in plan["solvers"]},
                                {m: np.eye(2) for m in plan["solvers"]})
    positive, negative = assess(diagonal), assess(isotropic)
    if not positive["direction_consistent"] or negative["direction_consistent"]:
        raise ValueError("transported-direction positive/negative control failed")
    return dict(flow=flow, tangent_positive=positive, tangent_negative=negative)


def analyze(point, segments, endpoints, plan):
    scales = np.asarray(plan["section_coordinate_scales"])
    geometry = []
    for i, base in enumerate(segments):
        pair = dict(saved_next_state=point["history"]["states"][i+1],
                    saved_pair_times=point["history"]["times"][i:i+2])
        # Check both solvers against the saved chain, not only the first solver.
        forward = old.analyze_point(pair, base, {}, plan)
        swapped_plan = dict(plan, solvers=list(reversed(plan["solvers"])))
        reverse = old.analyze_point(pair, base, {}, swapped_plan)
        geometry.append(dict(passed=forward["passed"] and reverse["passed"],
                             forward=forward, reverse=reverse))
    if any(r["status"] != "returned" for base in segments for r in base.values()):
        return dict(qualified=False, geometry=geometry, direction=None, reason="missing predecessor return")
    histories = {method: dominant_history([old.scaled_jacobian(s[method]["return_jacobian"], scales)
                                           for s in segments], depths=plan["depths"])
                 for method in plan["solvers"]}
    current = {m: old.scaled_jacobian(endpoints[m]["return_jacobian"], scales) for m in plan["solvers"]}
    direction = assess_direction(histories, current,
        **{k: plan["thresholds"][k] for k in ("maximum_ratio", "maximum_angle", "minimum_x_component")})
    return dict(qualified=all(r["passed"] for r in geometry) and direction["direction_consistent"],
                geometry=geometry, histories=histories, direction=direction)


def execute(plan, selections, output):
    rows, count = [], 0
    for selection in selections:
        parameters = RosslerParameters(**selection["parameters"])
        section = replace(legacy_rossler_section(parameters), direction=-1)
        rhs = lambda t, q: rossler_rhs(t, q, parameters)
        jac = lambda t, q: rossler_jacobian(q, parameters)
        for point in selection["points"]:
            label = f"{selection['case']}--bin-{point['bin']:02d}"
            segments = []
            for i, state in enumerate(point["history"]["states"][:-1]):
                base = {}
                for method in plan["solvers"]:
                    if count >= plan["limits"]["maximum_target_integrations"] or sum(p.stat().st_size for p in output.rglob("*") if p.is_file()) >= plan["limits"]["maximum_output_bytes"]-4194304:
                        raise ValueError("target count/output cap reached")
                    stem = f"{label}--past-{i:02d}--{method}"
                    write_json(output/"trials"/(stem+"-started.json"), dict(label=stem, initial_state=state, method=method))
                    count += 1
                    result = first_return_geometry(rhs, jac, state, section, method=method,
                        **{k: plan[k] for k in ("rtol", "atol", "max_step", "horizon", "minimum_angle", "initial_root_guard")})
                    write_json(output/"trials"/(stem+".json"), old.serial(result))
                    base[method] = result
                segments.append(base)
            endpoints = {m: prior.restore(json.loads((prior.TARGET/"trials"/(label+"--"+m+".json")).read_bytes()))
                         for m in plan["solvers"]}
            result = old.serial(analyze(point, segments, endpoints, plan))
            row = dict(case=selection["case"], bin=point["bin"], global_seed_id=point["global_seed_id"],
                       initial_state=point["initial_state"], audit=result)
            rows.append(row)
            write_json(output/"comparisons"/(label+".json"), row)
            print(f"{label}: {'qualified' if result['qualified'] else 'unresolved'} ({count} integrations)", flush=True)
    if count != plan["limits"]["maximum_target_integrations"]:
        raise ValueError("realized target matrix differs")
    return dict(experiment_id="EXP-485", status="completed", rows=rows, target_integrations=count,
                qualified_points=sum(r["audit"]["qualified"] for r in rows),
                historical_symbols_verified=False, paid_review="not_run", claim_boundary=plan["claim_boundary"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if ROOT/"artifacts/EXP-485" not in output.parents:
        parser.error("fresh output must be beneath artifacts/EXP-485")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
        parser.error("clean committed source required")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if commit != subprocess.check_output(["git", "rev-parse", "@{upstream}"], cwd=ROOT, text=True).strip():
        parser.error("push this exact source freeze first")
    plan = json.loads(PLAN.read_bytes())
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    binding = dict(source_commit=commit, plan_sha256=sha256(PLAN),
        source_files={p: sha256(ROOT/p) for p in SOURCE_FILES},
        runtime=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__),
        started_at_utc=datetime.now(timezone.utc).isoformat(), execution_mode="local-audited-no-paid-review")
    write_json(output/"binding.json", binding)
    start = time.monotonic()
    def timeout(*_):
        raise TimeoutError("EXP-485 wall bound reached")
    previous = signal.signal(signal.SIGALRM, timeout)
    signal.alarm(plan["limits"]["wall_seconds"])
    try:
        selections = prepare(plan)
        write_json(output/"selection.json", selections)
        write_json(output/"controls.json", controls(plan))
        if not args.execute:
            print("All 80 predecessor chains and analytic controls passed; zero target integrations")
            return
        marker = ROOT/"artifacts/EXP-485/target-once.json"
        with marker.open("x") as handle:
            json.dump(binding, handle, sort_keys=True, allow_nan=False)
        (output/"trials").mkdir()
        (output/"comparisons").mkdir()
        result = execute(plan, selections, output)
        result.update(binding=binding, target_slot_sha256=sha256(marker), elapsed_seconds=time.monotonic()-start,
                      files=inventory(output))
        if sum(row["bytes"] for row in result["files"].values()) + len((json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+"\n").encode()) > plan["limits"]["maximum_output_bytes"]-131072:
            raise ValueError("terminal result exceeds reserved output bound")
        write_json(output/"summary.json", result)
        print(json.dumps({k: result[k] for k in ("status", "target_integrations", "qualified_points", "elapsed_seconds")}))
    except (Exception, KeyboardInterrupt) as error:
        write_json(output/"failure.json", dict(binding=binding, status="failed", error_type=type(error).__name__,
                   message=str(error), elapsed_seconds=time.monotonic()-start))
        raise
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


if __name__ == "__main__":
    main()

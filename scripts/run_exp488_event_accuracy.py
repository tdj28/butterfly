#!/usr/bin/env python3
"""Prospective two-witness tolerance study; old failed verdicts are immutable."""
import argparse
from dataclasses import replace
from datetime import datetime, timezone
from itertools import combinations
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
from butterfly.poincare import legacy_rossler_section, PoincareSection
from butterfly.section_census import collect
from scripts import run_exp487_section_census as parent
from scripts.run_exp486_return_image_folds import control_field

PLAN = ROOT / "experiments/manifests/EXP-488-event-accuracy.json"
SOURCES = ("scripts/run_exp488_event_accuracy.py", "python/butterfly/section_census.py",
           "python/butterfly/models.py", "python/butterfly/poincare.py",
           "python/butterfly/_paired_startup.py", "scripts/run_exp487_section_census.py",
           "scripts/run_exp486_return_image_folds.py")


def utc():
    return datetime.now(timezone.utc).isoformat()


def validate_plan(plan):
    # Reconstruct intended scientific matrix, not merely its self-reported size.
    expected = dict(cases=["local-a025-c083", "local-a027-c083"],
                    solvers=["DOP853", "Radau"],
                    tolerances=[[1e-10, 1e-12], [1e-12, 1e-14], [1e-13, 1e-15]],
                    max_step=.001, horizon=50., guard=1e-8, extremum_margin=1e-10,
                    scales=[15., 15., .01],
                    thresholds=dict(fine_scaled_state=1e-7, fine_time=1e-9,
                                    minimum_angle=1e-7, section_residual=1e-8),
                    control=dict(horizon=13., state_error=1e-8, time_error=1e-9))
    if any(plan[k] != v for k, v in expected.items()) or plan["limits"] != dict(
            wall_seconds=1800, output_bytes=268435456, target_integrations=12):
        raise ValueError("frozen plan/matrix differs")


def profiles(plan):
    return [(m, i, r, a) for m in plan["solvers"] for i, (r, a) in enumerate(plan["tolerances"])]


def accepted(row):
    return [r for r in row["reconstructed"] if r["accepted"]]


def errors(a, b, scales):
    return [dict(state=float(np.max(np.abs((np.asarray(x["state"])-y["state"])/scales))),
                 time=abs(x["time"]-y["time"])) for x, y in zip(a, b)]


def compare(rows, selection, plan):
    expected = {(m, r, a) for m, _, r, a in profiles(plan)}
    if len(rows) != 6 or {(r["method"], r["rtol"], r["atol"]) for r in rows} != expected:
        raise ValueError("six-profile matrix differs")
    reference = accepted(next(r for r in rows if r["method"] == "Radau" and r["rtol"] == 1e-13))
    fine = [r for r in rows if r["rtol"] < 1e-10]
    details = []
    for row in rows:
        values = accepted(row)
        finite = all(np.isfinite([v["time"], *v["state"], v["angle"], v["residual"]]).all() for v in values)
        valid = finite and len(values) == len(reference) and len(values) >= 5 and not row["uncertain_extrema"] and all(
            v["angle"] >= plan["thresholds"]["minimum_angle"] and abs(v["residual"]) <= plan["thresholds"]["section_residual"] for v in values)
        ordinary = accepted(dict(reconstructed=row["ordinary"]))
        details.append(dict(method=row["method"], rtol=row["rtol"], atol=row["atol"],
            valid_census=bool(valid), accepted_count=len(values), ordinary_accepted_count=len(ordinary),
            missing_ordinary_indices=[i for i, v in enumerate(values) if not any(abs(v["time"]-o["time"]) <= 1e-7 for o in ordinary)],
            reference_errors=errors(values, reference, plan["scales"]),
            old_radau_fifth_error=errors(values[4:5], [selection["prior_fifth"]["Radau"]], plan["scales"]),
            uncertain_extrema=len(row["uncertain_extrema"])))
    pairs = []
    for a, b in combinations(fine, 2):
        es = errors(accepted(a), accepted(b), plan["scales"])
        pairs.append(dict(profiles=[[r["method"], r["rtol"]] for r in (a, b)], errors=es,
            passed=bool(len(accepted(a)) == len(accepted(b)) >= 5 and all(
                e["state"] <= plan["thresholds"]["fine_scaled_state"] and e["time"] <= plan["thresholds"]["fine_time"] for e in es))))
    return dict(case=selection["case"], passed=all(d["valid_census"] for d in details) and all(p["passed"] for p in pairs),
                profiles=details, fine_pairs=pairs, reference_accepted=reference)


def control_verdict(row, plan):
    values = accepted(row)
    expected = [dict(time=float(t), state=[-4-.25*(1-np.exp(-.06*t)), 0., .5*np.exp(-.03*t)]) for t in 2*np.pi*np.arange(1, 3)]
    es = errors(values, expected, [1., 1., 1.])
    return dict(passed=bool(len(values) == 2 and not row["uncertain_extrema"] and all(
        e["state"] <= plan["control"]["state_error"] and e["time"] <= plan["control"]["time_error"] for e in es)), errors=es)


def controls(plan):
    hidden = parent.controls()
    rotation = []
    for m, _, r, a in profiles(plan):
        row, _ = collect(*control_field(), [-4., 0., .5], [1., 0., 1.],
            PoincareSection((0., 1., 0.), 0., -1), method=m, max_step=plan["max_step"],
            horizon=plan["control"]["horizon"], guard=plan["guard"], rtol=r, atol=a)
        rotation.append(dict(report=row, **control_verdict(row, plan)))
    return dict(hidden=hidden, rotation=rotation,
                passed=all(r["passed"] for r in hidden+rotation))


def selection_for(plan, *, replay_parent=False):
    if sha256(ROOT/plan["parent_receipt"]) != plan["parent_receipt_sha256"]:
        raise ValueError("parent receipt changed")
    receipt = json.loads((ROOT/plan["parent_receipt"]).read_bytes())
    if replay_parent and parent.audit(ROOT/plan["parent_run"], plan["parent_summary_sha256"]) != receipt:
        raise ValueError("parent replay differs")
    if [r["case"] for r in receipt["selection"]] != plan["cases"]:
        raise ValueError("witness matrix changed")
    return receipt["selection"]


def validate_geometry(row, raw_path, selection, plan):
    p = RosslerParameters(**selection["parameters"])
    section = replace(legacy_rossler_section(p), direction=-1)
    if row["initial_state"] != selection["initial_state"] or row["initial_tangent"] != selection["initial_tangent"]:
        raise ValueError("initial data differ")
    knots = [plan["guard"], *[v["time"] for v in row["extrema"]], plan["horizon"]]
    if row["knots"] != knots or len(row["knot_values"]) != len(knots) or not np.all(np.diff(knots) > 0):
        raise ValueError("extremum partition differs")
    brackets = [[a, b] for a, b, x, y in zip(knots[:-1], knots[1:], row["knot_values"][:-1], row["knot_values"][1:], strict=True) if x*y < 0]
    if [r["bracket"] for r in row["reconstructed"]] != brackets:
        raise ValueError("complete bracket set differs")
    for event in row["ordinary"]+row["reconstructed"]+row["extrema"]:
        x, y, z = event["state"]
        field = np.array([-y-z, x+p.a*y, p.b+z*(x-p.c)])
        angle = abs(field[1])/np.linalg.norm(field)
        if not np.isfinite([event["time"], *event["state"], *event["raw_tangent"], event["angle"], event["residual"]]).all():
            raise ValueError("nonfinite event")
        if abs(event["normal_velocity"]-field[1]) > 1e-12 or abs(event["angle"]-angle) > 1e-12 or event["accepted"] != bool(x < section.gate_upper and field[1] < 0) or abs(event["residual"]-section.value(event["state"])) > 1e-12:
            raise ValueError("independent event algebra differs")
    for event in row["reconstructed"]:
        if not event["bracket"][0] < event["time"] < event["bracket"][1] or abs(event["residual"]) > 1e-8:
            raise ValueError("root outside bracket/section")
    uncertain = [dict(time=v["time"], plane_value=v["plane_value"], state=v["state"]) for v in row["extrema"] if abs(v["plane_value"]) <= plan["extremum_margin"]]
    if uncertain != row["uncertain_extrema"]:
        raise ValueError("uncertain extremum erased")
    with np.load(raw_path, allow_pickle=False) as raw:
        times, states = raw["integration_times"], raw["integration_augmented_states"]
        if states.shape != (len(times), 6) or not np.isfinite(states).all() or not np.isfinite(times).all() or not np.all(np.diff(times) > 0) or times[0] != plan["guard"] or times[-1] != plan["horizon"]:
            raise ValueError("raw trajectory malformed")
        if not np.allclose([row["knot_values"][0], row["knot_values"][-1]], [section.value(states[i, :3]) for i in (0, -1)], rtol=0, atol=1e-12):
            raise ValueError("endpoint values differ")


def audit(output, anchor):
    if sha256(output/"summary.json") != anchor:
        raise ValueError("summary anchor changed")
    saved = json.loads((output/"summary.json").read_bytes())
    plan = json.loads(PLAN.read_bytes())
    validate_plan(plan)
    if saved["status"] != "completed" or inventory(output, omit=("summary.json",)) != saved["files"]:
        raise ValueError("inventory changed")
    binding = json.loads((output/"binding.json").read_bytes())
    if saved["binding"] != binding or binding["plan_sha256"] != sha256(PLAN) or binding["sources"] != {p: sha256(ROOT/p) for p in SOURCES}:
        raise ValueError("source binding changed")
    selection = selection_for(plan)
    if json.loads((output/"selection.json").read_bytes()) != selection:
        raise ValueError("selection changed")
    c = json.loads((output/"controls.json").read_bytes())
    if not c["passed"] or len(c["hidden"]) != 6 or not all(r["passed"] for r in c["hidden"]):
        raise ValueError("hidden controls failed")
    if len(c["rotation"]) != 6 or {(v["report"]["method"], v["report"]["rtol"], v["report"]["atol"]) for v in c["rotation"]} != {(m,r,a) for m,_,r,a in profiles(plan)}:
        raise ValueError("control matrix changed")
    for r in c["rotation"]:
        if control_verdict(r["report"], plan) != {k:r[k] for k in ("passed", "errors")} or not r["passed"]:
            raise ValueError("analytic accuracy control failed")
    cases, expected = [], {"binding.json", "selection.json", "controls.json"}
    for s in selection:
        rows = []
        for m, i, r, a in profiles(plan):
            label = f"{s['case']}--{m}--tol{i}"
            expected.update((label+".json", label+".npz", label+"-started.json"))
            row = json.loads((output/(label+".json")).read_bytes())
            if row["method"] != m or row["rtol"] != r or row["atol"] != a or any(row[k] != plan[k] for k in ("max_step", "horizon", "guard")):
                raise ValueError("profile configuration differs")
            start = json.loads((output/(label+"-started.json")).read_bytes())
            if {k:start[k] for k in ("case", "method", "rtol", "atol")} != dict(case=s["case"], method=m, rtol=r, atol=a):
                raise ValueError("start identity differs")
            if not binding["started_utc"] <= start["started_utc"] <= saved["completed_utc"]:
                raise ValueError("start timestamp differs")
            validate_geometry(row, output/(label+".npz"), s, plan)
            rows.append(row)
        cases.append(compare(rows, s, plan))
    marker = ROOT/"artifacts/EXP-488/target-once.json"
    if set(saved["files"]) != expected or saved["target_integrations"] != 12 or saved["cases"] != cases or sha256(marker) != saved["marker_sha256"] or json.loads(marker.read_bytes()) != binding:
        raise ValueError("matrix/decision/marker differs")
    return dict(experiment_id="EXP-488", status="completed-audited", source_commit=binding["source_commit"],
        summary_sha256=anchor, cases=cases, target_integrations=12, elapsed_seconds=saved["elapsed_seconds"],
        started_utc=binding["started_utc"], completed_utc=saved["completed_utc"],
        controls_passed=True, same_agent_local_audit=True, paid_review="not_run", claim_boundary=plan["claim_boundary"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--audit-run", type=Path)
    parser.add_argument("--expected-summary-sha256")
    args = parser.parse_args()
    if args.audit_run:
        result = audit(args.audit_run, args.expected_summary_sha256)
        args.output_dir.mkdir(parents=True, exist_ok=False)
        write_json(args.output_dir/"summary.json", result)
        print(json.dumps({"cases": [{"case":c["case"], "passed":c["passed"]} for c in result["cases"]]}))
        return
    output = args.output_dir.resolve()
    if ROOT/"artifacts/EXP-488" not in output.parents:
        parser.error("fresh EXP-488 output required")
    if subprocess.check_output(["git", "status", "--porcelain"], text=True).strip():
        parser.error("clean source required")
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if source != subprocess.check_output(["git", "rev-parse", "@{upstream}"], text=True).strip():
        parser.error("push source first")
    plan = json.loads(PLAN.read_bytes())
    validate_plan(plan)
    output.mkdir(parents=True, exist_ok=False)
    binding = dict(source_commit=source, plan_sha256=sha256(PLAN), sources={p:sha256(ROOT/p) for p in SOURCES},
                   started_utc=utc(), runtime=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__))
    write_json(output/"binding.json", binding)
    started = time.monotonic()
    def timeout(*_):
        raise TimeoutError("EXP-488 wall limit")
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(plan["limits"]["wall_seconds"])
    try:
        selection = selection_for(plan, replay_parent=True)
        write_json(output/"selection.json", selection)
        control = controls(plan)
        write_json(output/"controls.json", control)
        if not control["passed"]:
            raise ValueError("controls failed; targets not started")
        marker = ROOT/"artifacts/EXP-488/target-once.json"
        write_json(marker, binding)
        cases = []
        for s in selection:
            rows = []
            p = RosslerParameters(**s["parameters"])
            section = replace(legacy_rossler_section(p), direction=-1)
            for m, i, r, a in profiles(plan):
                if sum(f.stat().st_size for f in output.iterdir() if f.is_file()) > plan["limits"]["output_bytes"]-16777216:
                    raise RuntimeError("output byte cap")
                label = f"{s['case']}--{m}--tol{i}"
                write_json(output/(label+"-started.json"), dict(case=s["case"], method=m, rtol=r, atol=a, started_utc=utc()))
                row, raw = collect(lambda t,q:rossler_rhs(t,q,p), lambda t,q:rossler_jacobian(q,p),
                    s["initial_state"], s["initial_tangent"], section, method=m, rtol=r, atol=a,
                    **{k:plan[k] for k in ("max_step", "horizon", "guard", "extremum_margin")})
                with (output/(label+".npz")).open("xb") as stream:
                    np.savez_compressed(stream, **raw)
                write_json(output/(label+".json"), row)
                rows.append(row)
                print(label+": completed", flush=True)
            cases.append(compare(rows, s, plan))
        write_json(output/"summary.json", dict(experiment_id="EXP-488", status="completed", binding=binding,
            target_integrations=12, cases=cases, files=inventory(output), marker_sha256=sha256(marker),
            elapsed_seconds=time.monotonic()-started, completed_utc=utc()))
        print(json.dumps({"cases":[dict(case=c["case"], passed=c["passed"]) for c in cases]}))
    except (Exception, KeyboardInterrupt) as e:
        write_json(output/"failure.json", dict(error_type=type(e).__name__, message=str(e), utc=utc()))
        raise
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()

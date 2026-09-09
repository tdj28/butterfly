#!/usr/bin/env python3
"""Frozen two-witness extremum-refined event census; no paid services."""
import argparse
from dataclasses import replace
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
from scripts import audit_exp486_return_image_folds as parent

PLAN = ROOT/"experiments/manifests/EXP-487-section-census-witness.json"
SOURCES = ("scripts/run_exp487_section_census.py", "python/butterfly/section_census.py",
           "python/butterfly/models.py", "python/butterfly/poincare.py")


def controls():
    rows = []
    for method in ("DOP853", "Radau"):
        for offset in (-.0001, .0001, 0.):
            report, raw = collect(lambda t, q: np.array([1., 2*(t-.5), 0.]),
                lambda t, q: np.zeros((3, 3)), [0., .25+offset, 0.], [1., 0., 0.],
                PoincareSection((0., 1., 0.), 0., -1), method=method, horizon=1., guard=0., max_step=1., first_step=1.)
            passed = len(raw["integration_times"]) == 2 and not report["ordinary"]
            if offset < 0:
                passed &= len(report["reconstructed"]) == 2 and np.allclose([r["time"] for r in report["reconstructed"]], [.49, .51], rtol=0, atol=1e-10) and not report["uncertain_extrema"]
            elif offset > 0:
                passed &= not report["reconstructed"] and not report["uncertain_extrema"]
            else:
                passed &= bool(report["uncertain_extrema"])
            rows.append(dict(method=method, offset=offset, passed=bool(passed), report=report))
    return rows


def prepare(plan):
    audited = parent.audit(ROOT/plan["parent_run"], plan["parent_summary_sha256"], plan["parent_source_commit"])
    selections = []
    for witness in plan["witnesses"]:
        family = next(f for f in audited["families"] if f["id"] == witness["family_id"])
        label = f"{family['id']}--eval-{witness['evaluation']:04d}--"
        raw = {m: json.loads((ROOT/plan["parent_run"]/"trials"/(label+m+".json")).read_bytes()) for m in plan["solvers"]}
        if raw["DOP853"]["initial_state"] != raw["Radau"]["initial_state"] or len(raw["DOP853"]["events"]) != 5 or len(raw["Radau"]["events"]) != 5:
            raise ValueError("witness source identity differs")
        for a, b in zip(raw["DOP853"]["events"][:4], raw["Radau"]["events"][:4], strict=True):
            if np.max(np.abs((np.asarray(a["state"])-b["state"])/plan["scales"])) > 1e-6 or abs(a["time"]-b["time"]) > 1e-7:
                raise ValueError("witness prefix does not agree")
        if raw["DOP853"]["events"][-1]["time"]-raw["Radau"]["events"][-1]["time"] <= 1.:
            raise ValueError("witness does not contain the declared earlier Radau crossing")
        selections.append(dict(**witness, parameters=family["parameters"],
            initial_state=raw["DOP853"]["initial_state"], initial_tangent=raw["DOP853"]["initial_tangent"],
            prior_fifth={m: raw[m]["events"][-1] for m in plan["solvers"]}))
    if [s["case"] for s in selections] != ["local-a025-c083", "local-a027-c083"]:
        raise ValueError("two-case witness matrix changed")
    return selections


def compare(rows, selection, plan):
    expected = {(m, h) for m in ("DOP853", "Radau") for h in (.02, .005, .001)}
    if len(rows) != 6 or {(r["method"], r["max_step"]) for r in rows} != expected:
        raise ValueError("six-profile census matrix changed")
    accepted = lambda r: [v for v in r["reconstructed"] if v["accepted"]]
    reference = accepted(next(r for r in rows if r["method"] == "Radau" and r["max_step"] == .001))
    comparisons = []
    for row in rows:
        values = accepted(row)
        same_count = len(values) == len(reference) and len(values) >= 5
        errors = [dict(state=float(np.max(np.abs((np.asarray(a["state"])-b["state"])/plan["scales"]))),
                       time=abs(a["time"]-b["time"])) for a, b in zip(values, reference)]
        witness = selection["prior_fifth"]["Radau"]
        witness_matches = [i for i, v in enumerate(values) if abs(v["time"]-witness["time"]) <= plan["thresholds"]["time"] and np.max(np.abs((np.asarray(v["state"])-witness["state"])/plan["scales"])) <= plan["thresholds"]["scaled_state"]]
        ordinary = [r for r in row["ordinary"] if r["accepted"]]
        missing = [i for i, v in enumerate(values) if not any(abs(v["time"]-o["time"]) <= plan["thresholds"]["time"] for o in ordinary)]
        passed = same_count and not row["uncertain_extrema"] and witness_matches == [4] and all(
            e["state"] <= plan["thresholds"]["scaled_state"] and e["time"] <= plan["thresholds"]["time"] for e in errors) and all(v["angle"] >= plan["thresholds"]["minimum_angle"] and abs(v["residual"]) <= plan["thresholds"]["section_residual"] for v in values)
        comparisons.append(dict(method=row["method"], max_step=row["max_step"], passed=bool(passed),
            accepted_count=len(values), ordinary_accepted_count=len(ordinary), missing_ordinary_indices=missing,
            witness_matches=witness_matches, errors=errors, uncertain_extrema=len(row["uncertain_extrema"])))
    return dict(case=selection["case"], passed=all(r["passed"] for r in comparisons), comparisons=comparisons,
                reference_accepted=reference)


def audit(output, expected_sha):
    if sha256(output/"summary.json") != expected_sha:
        raise ValueError("summary anchor changed")
    result = json.loads((output/"summary.json").read_bytes())
    if result["status"] != "completed" or inventory(output, omit=("summary.json",)) != result["files"]:
        raise ValueError("target inventory changed")
    plan = json.loads(PLAN.read_bytes())
    if result["binding"]["plan_sha256"] != sha256(PLAN) or result["binding"]["source_files"] != {p: sha256(ROOT/p) for p in SOURCES}:
        raise ValueError("source/plan changed")
    selection = prepare(plan)
    if json.loads((output/"selection.json").read_bytes()) != selection:
        raise ValueError("input reconstruction changed")
    cases, expected = [], {"binding.json", "selection.json", "controls.json"}
    saved_controls = json.loads((output/"controls.json").read_bytes())
    if [(r["method"], r["offset"], r["passed"]) for r in saved_controls] != [(m, o, True) for m in plan["solvers"] for o in (-.0001, .0001, 0.)]:
        raise ValueError("controls changed")
    for control in saved_controls:
        report = control["report"]
        if report["ordinary"]:
            raise ValueError("hidden-crossing control ordinary roots changed")
        if control["offset"] < 0:
            if len(report["reconstructed"]) != 2 or not np.allclose([r["time"] for r in report["reconstructed"]], [.49, .51], rtol=0, atol=1e-10) or report["uncertain_extrema"]:
                raise ValueError("known hidden roots differ")
        elif control["offset"] > 0:
            if report["reconstructed"] or report["uncertain_extrema"]:
                raise ValueError("no-root control differs")
        elif not report["uncertain_extrema"]:
            raise ValueError("tangency uncertainty erased")
    for s in selection:
        rows = []
        parameters = RosslerParameters(**s["parameters"])
        section = replace(legacy_rossler_section(parameters), direction=-1)
        for method in plan["solvers"]:
            for step in plan["max_steps"]:
                label = f"{s['case']}--{method}--h{step}"
                expected.update((label+".json", label+".npz", label+"-started.json"))
                row = json.loads((output/(label+".json")).read_bytes())
                if row["initial_state"] != s["initial_state"] or row["initial_tangent"] != s["initial_tangent"] or row["method"] != method or row["max_step"] != step:
                    raise ValueError("profile identity differs")
                if any(row[k] != plan[k] for k in ("horizon", "guard", "rtol", "atol")) or json.loads((output/(label+"-started.json")).read_bytes()) != dict(case=s["case"], method=method, max_step=step):
                    raise ValueError("profile configuration/start differs")
                knots = [plan["guard"], *[e["time"] for e in row["extrema"]], plan["horizon"]]
                if row["knots"] != knots or len(row["knot_values"]) != len(knots) or not np.all(np.diff(knots) > 0):
                    raise ValueError("extremum partition differs")
                brackets = [[a, b] for a, b, x, y in zip(knots[:-1], knots[1:], row["knot_values"][:-1], row["knot_values"][1:], strict=True) if x*y < 0]
                if [r["bracket"] for r in row["reconstructed"]] != brackets or any(not r["bracket"][0] < r["time"] < r["bracket"][1] for r in row["reconstructed"]):
                    raise ValueError("complete sign-change bracket set differs")
                for event in row["ordinary"]+row["reconstructed"]:
                    x, y, z = event["state"]
                    field = np.array([-y-z, x+parameters.a*y, parameters.b+z*(x-parameters.c)])
                    angle = abs(field[1])/np.linalg.norm(field)
                    if abs(event["normal_velocity"]-field[1]) > 1e-12 or abs(event["angle"]-angle) > 1e-12 or event["accepted"] != bool(x < section.gate_upper and field[1] < 0) or abs(section.value(event["state"])) > 1e-8:
                        raise ValueError("separate section-event algebra differs")
                with np.load(output/(label+".npz"), allow_pickle=False) as raw:
                    if raw["integration_augmented_states"].shape != (len(raw["integration_times"]), 6) or not np.all(np.diff(raw["integration_times"]) > 0) or not np.isfinite(raw["integration_augmented_states"]).all():
                        raise ValueError("raw trajectory malformed")
                    if raw["integration_times"][0] != plan["guard"] or raw["integration_times"][-1] != plan["horizon"]:
                        raise ValueError("raw trajectory horizon differs")
                    endpoint_values = [section.value(raw["integration_augmented_states"][i, :3]) for i in (0, -1)]
                    if not np.allclose([row["knot_values"][0], row["knot_values"][-1]], endpoint_values, rtol=0, atol=1e-12):
                        raise ValueError("bracket endpoint values differ")
                rows.append(row)
        cases.append(compare(rows, s, plan))
    if cases != result["cases"] or set(result["files"]) != expected or result["target_integrations"] != 12:
        raise ValueError("full matrix/decision differs")
    marker = ROOT/"artifacts/EXP-487/target-once.json"
    if sha256(marker) != result["target_slot_sha256"] or json.loads(marker.read_bytes()) != result["binding"]:
        raise ValueError("consumed marker differs")
    return dict(experiment_id="EXP-487", status="completed-audited", source_commit=result["binding"]["source_commit"],
        completed_summary_sha256=expected_sha, cases=cases, target_integrations=12,
        elapsed_seconds=result["elapsed_seconds"], complete_grid_and_decision_replay=True,
        claim_boundary=plan["claim_boundary"], paid_review="not_run", selection=selection)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--audit-run", type=Path)
    parser.add_argument("--expected-summary-sha256")
    args = parser.parse_args()
    if args.audit_run:
        value = audit(args.audit_run, args.expected_summary_sha256)
        args.output_dir.mkdir(parents=True, exist_ok=False)
        write_json(args.output_dir/"summary.json", value)
        print(json.dumps(value["cases"], indent=2))
        return
    output = args.output_dir.resolve()
    if ROOT/"artifacts/EXP-487" not in output.parents:
        parser.error("fresh EXP-487 output required")
    if subprocess.check_output(["git", "status", "--porcelain"], text=True).strip():
        parser.error("clean committed source required")
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if source != subprocess.check_output(["git", "rev-parse", "@{upstream}"], text=True).strip():
        parser.error("push exact source first")
    plan = json.loads(PLAN.read_bytes())
    output.mkdir(parents=True, exist_ok=False)
    binding = dict(source_commit=source, plan_sha256=sha256(PLAN), source_files={p: sha256(ROOT/p) for p in SOURCES},
                   runtime=dict(python=sys.version, scipy=scipy.__version__, numpy=np.__version__))
    write_json(output/"binding.json", binding)
    started = time.monotonic()
    def timeout(*_):
        raise TimeoutError("EXP-487 wall limit")
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(plan["limits"]["wall_seconds"])
    try:
        selection = prepare(plan)
        write_json(output/"selection.json", selection)
        control = controls()
        write_json(output/"controls.json", control)
        if not all(r["passed"] for r in control):
            raise ValueError("analytic controls failed; no targets")
        marker = ROOT/"artifacts/EXP-487/target-once.json"
        write_json(marker, binding)
        cases = []
        for s in selection:
            rows = []
            parameters = RosslerParameters(**s["parameters"])
            section = replace(legacy_rossler_section(parameters), direction=-1)
            for method in plan["solvers"]:
                for step in plan["max_steps"]:
                    if sum(p.stat().st_size for p in output.iterdir() if p.is_file()) > plan["limits"]["output_bytes"]-16777216:
                        raise TimeoutError("output cap reached")
                    label = f"{s['case']}--{method}--h{step}"
                    write_json(output/(label+"-started.json"), dict(case=s["case"], method=method, max_step=step))
                    row, raw = collect(lambda t, q: rossler_rhs(t, q, parameters),
                        lambda t, q: rossler_jacobian(q, parameters), s["initial_state"], s["initial_tangent"],
                        section, method=method, max_step=step,
                        **{k: plan[k] for k in ("horizon", "guard", "rtol", "atol", "extremum_margin")})
                    with (output/(label+".npz")).open("xb") as stream:
                        np.savez_compressed(stream, **raw)
                    write_json(output/(label+".json"), row)
                    rows.append(row)
                    print(label+": completed", flush=True)
            cases.append(compare(rows, s, plan))
        value = dict(experiment_id="EXP-487", status="completed", binding=binding, cases=cases,
            target_integrations=12, elapsed_seconds=time.monotonic()-started, files=inventory(output),
            target_slot_sha256=sha256(marker), claim_boundary=plan["claim_boundary"])
        write_json(output/"summary.json", value)
        print(json.dumps(dict(status="completed", cases=[dict(case=r["case"], passed=r["passed"]) for r in cases], elapsed_seconds=value["elapsed_seconds"])))
    except (Exception, KeyboardInterrupt) as error:
        write_json(output/"failure.json", dict(error_type=type(error).__name__, message=str(error), elapsed_seconds=time.monotonic()-started))
        raise
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()

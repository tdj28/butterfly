#!/usr/bin/env python3
"""Bounded, one-shot EXP-484 direct flow-geometry pilot; local CPU only."""
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
from butterfly._paired_startup import sha256, write_json
from butterfly.models import RosslerParameters, rossler_rhs, rossler_jacobian
from butterfly.poincare import PoincareSection, legacy_rossler_section
from butterfly.return_geometry import first_return_geometry
from scripts.summarize_exp482_maps import RUN, CAMPAIGN_SHA, ANALYSIS_SHA

PLAN = ROOT/"experiments/manifests/EXP-484-return-geometry-pilot.json"


def serial(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {k: serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def select_points(ids, calibration, states, times, bounds, *, bins=40):
    """Deterministic actual-point coverage selection; never use target words."""
    ids, calibration = np.asarray(ids), np.asarray(calibration)
    states, times = np.asarray(states), np.asarray(times)
    if (ids.ndim != 1 or len(np.unique(ids)) != len(ids) or np.any(np.diff(ids) <= 0)
            or calibration.shape != ids.shape or calibration.dtype.kind != "b"
            or states.shape != (len(ids), 4, 2, 3) or times.shape != (len(ids), 4, 2)
            or bounds[1] <= bounds[0] or not np.isfinite(states[calibration]).all()
            or not np.isfinite(times[calibration]).all()):
        raise ValueError("invalid original calibration blocks")
    indices = np.flatnonzero(calibration)
    x = (states[calibration, :, 0, 0]-bounds[0])/(bounds[1]-bounds[0])
    if np.any((x < 0) | (x > 1)):
        raise ValueError("calibration inputs outside original bounds")
    assigned = np.minimum(np.floor(x*bins).astype(int), bins-1)
    points = []
    for b in range(bins):
        choices = np.argwhere(assigned == b)
        if not len(choices):
            raise ValueError(f"no original calibration source in bin {b}")
        row, stratum = map(int, choices[0])
        original_row = indices[row]
        points.append(dict(bin=b, global_seed_id=int(ids[original_row]), stratum=stratum,
            initial_state=states[original_row, stratum, 0].tolist(),
            saved_next_state=states[original_row, stratum, 1].tolist(),
            saved_pair_times=times[original_row, stratum].tolist()))
    return points


def prepare(plan):
    campaign = RUN/"campaign"
    if plan["campaign_sha256"] != CAMPAIGN_SHA or sha256(campaign/"receipt.json") != CAMPAIGN_SHA:
        raise ValueError("source campaign anchor changed")
    receipt = json.loads((campaign/"receipt.json").read_bytes())
    path = campaign/"analysis/phase/analysis.json"
    if plan["analysis_sha256"] != ANALYSIS_SHA or sha256(path) != ANALYSIS_SHA:
        raise ValueError("source analysis anchor changed")
    diagnostic = ROOT/"artifacts/EXP-483/support-audit-01/summary.json"
    if sha256(diagnostic) != plan["diagnostic_sha256"]:
        raise ValueError("EXP-483 diagnosis anchor changed")
    analysis = json.loads(path.read_bytes())
    result = []
    for case in plan["cases"]:
        name = case["id"]
        relative = f"analysis/phase/{name}--{plan['selection']['profile']}-pairs.npz"
        source = campaign/relative
        if sha256(source) != receipt["files"][relative]["sha256"]:
            raise ValueError("saved section blocks differ from completed campaign")
        cohort = analysis["cases"][name]["cohort"]
        with np.load(source, allow_pickle=False) as raw:
            if raw["global_seed_ids"].tolist() != cohort["global_seed_ids"]:
                raise ValueError("saved profile global IDs differ")
            w = plan["selection"]["window"]
            bounds = analysis["cases"][name]["analysis"]["primary_audits"][f"{plan['selection']['profile']}/window-{w}"]["calibration_bounds"]
            points = select_points(raw["global_seed_ids"], np.asarray(cohort["calibration"], bool),
                raw["section_0__pair_states"][:, w], raw["section_0__pair_times"][:, w], bounds,
                bins=plan["selection"]["bins"])
        if len(points) != plan["selection"]["points_per_case"]:
            raise ValueError("geometry point count differs from plan")
        result.append(dict(case=name, parameters={k: case[k] for k in ("a", "b", "c")},
            saved_profile_sha256=sha256(source), original_calibration_bounds=bounds, points=points))
    return result


def controls(plan):
    section = PoincareSection((0., 1., 0.), 0., direction=-1)
    rhs = lambda t, q: np.array([-q[1], q[0], -.3*q[2]])
    jac = lambda t, q: np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., -.3]])
    rows = []
    for method in plan["solvers"]:
        result = first_return_geometry(rhs, jac, [-1., 0., .2], section, method=method,
            rtol=plan["rtol"], atol=plan["atol"], max_step=plan["max_step"], horizon=7.)
        expected = np.diag([1., np.exp(-.3*2*np.pi)])
        passed = result["status"] == "returned" and abs(result["return_time"]-2*np.pi) < 1e-9 and np.max(np.abs(result["return_jacobian"]-expected)) < 1e-9
        rows.append(dict(method=method, passed=bool(passed), result=serial(result)))
    if not all(r["passed"] for r in rows):
        raise ValueError("analytic control failed; no target release")
    return rows


def scaled_jacobian(jacobian, scales):
    return np.asarray(jacobian)*scales[None, :]/scales[:, None]


def relative_error(actual, reference):
    return float(np.max(np.abs(actual-reference))/max(1., float(np.max(np.abs(reference)))))


def analyze_point(point, base, differences, plan):
    thresholds = plan["thresholds"]
    scales = np.asarray(plan["section_coordinate_scales"])
    if any(r["status"] != "returned" for r in base.values()):
        return dict(passed=False, reason="missing base return", finite_difference=[])
    left, right = (base[name] for name in plan["solvers"])
    state_error = float(np.max(np.abs((left["return_state"]-right["return_state"])[[0, 2]]/scales)))
    time_error = abs(left["return_time"]-right["return_time"])
    jac_error = relative_error(scaled_jacobian(left["return_jacobian"], scales), scaled_jacobian(right["return_jacobian"], scales))
    saved_state_error = float(np.max(np.abs((left["return_state"]-point["saved_next_state"])[[0, 2]]/scales)))
    saved_time_error = abs(left["return_time"]-np.ptp(point["saved_pair_times"]))
    fd_rows = []
    for step, trials in differences.items():
        if any(r["status"] != "returned" for r in trials.values()):
            fd_rows.append(dict(normalized_step=step, passed=False, reason="missing perturbed return"))
            continue
        derivative = np.column_stack([(trials[(axis, 1)]["return_state"][[0, 2]]-
            trials[(axis, -1)]["return_state"][[0, 2]])/(2*step*scales[i]) for i, axis in enumerate((0, 2))])
        error = relative_error(scaled_jacobian(derivative, scales), scaled_jacobian(left["return_jacobian"], scales))
        fd_rows.append(dict(normalized_step=step, relative_scaled_jacobian_error=error,
            passed=error <= thresholds["finite_difference_relative_scaled_jacobian_error"]))
    checks = dict(solver_state=state_error <= thresholds["solver_scaled_state_error"],
        solver_time=time_error <= thresholds["solver_return_time_error"],
        solver_jacobian=jac_error <= thresholds["solver_relative_scaled_jacobian_error"],
        saved_pair_state=saved_state_error <= thresholds["saved_pair_scaled_state_error"],
        saved_pair_time=saved_time_error <= thresholds["saved_pair_return_time_error"],
        finite_difference=all(r["passed"] for r in fd_rows))
    return dict(passed=all(checks.values()), checks=checks, solver_scaled_state_error=state_error,
        solver_return_time_error=time_error, solver_relative_scaled_jacobian_error=jac_error,
        saved_pair_scaled_state_error=saved_state_error, saved_pair_return_time_error=saved_time_error,
        finite_difference=fd_rows)


def execute(plan, selections, output):
    rows, count = [], 0
    def collect(label, rhs, jac, state, section, method):
        nonlocal count
        if count >= plan["limits"]["maximum_target_integrations"]:
            raise ValueError("integration count cap reached")
        if sum(p.stat().st_size for p in output.rglob("*") if p.is_file()) >= plan["limits"]["maximum_output_bytes"]-131072:
            raise ValueError("output byte cap reached")
        write_json(output/"trials"/(label+"-started.json"), dict(label=label, initial_state=serial(state), method=method))
        count += 1
        result = first_return_geometry(rhs, jac, state, section, method=method,
            **{k: plan[k] for k in ("rtol", "atol", "max_step", "horizon", "minimum_angle", "initial_root_guard")})
        write_json(output/"trials"/(label+".json"), serial(result))
        return result
    for selection in selections:
        parameters = RosslerParameters(**selection["parameters"])
        section = replace(legacy_rossler_section(parameters), direction=-1)
        rhs = lambda t, q: rossler_rhs(t, q, parameters)
        jac = lambda t, q: rossler_jacobian(q, parameters)
        for point in selection["points"]:
            label = f"{selection['case']}--bin-{point['bin']:02d}"
            state = np.asarray(point["initial_state"])
            base = {method: collect(f"{label}--{method}", rhs, jac, state, section, method) for method in plan["solvers"]}
            differences = {}
            fd = plan["finite_difference"]
            if point["bin"] in fd["bins"]:
                for step in fd["normalized_steps"]:
                    trials = {}
                    for i, axis in enumerate(fd["axes"]):
                        for sign in fd["signs"]:
                            displaced = state.copy()
                            displaced[axis] += sign*step*plan["section_coordinate_scales"][i]
                            trials[(axis, sign)] = collect(f"{label}--fd-{step:g}-{axis}-{sign}", rhs, jac,
                                displaced, section, fd["solver"])
                    differences[step] = trials
            audit = analyze_point(point, base, differences, plan)
            row = dict(case=selection["case"], bin=point["bin"], audit=serial(audit))
            rows.append(row)
            write_json(output/"comparisons"/(label+".json"), row)
            print(f"{label}: {'passed' if audit['passed'] else 'unresolved'} ({count} integrations)", flush=True)
    if count != plan["limits"]["maximum_target_integrations"]:
        raise ValueError("realized integration count differs from fixed matrix")
    return dict(status="completed", rows=rows, target_integrations=count,
        all_points_passed=all(r["audit"]["passed"] for r in rows),
        claim_boundary=plan["claim_boundary"], historical_symbols_verified=False, paid_review="not_run")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--execute", action="store_true", help="consume EXP-484's single target slot after controls")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if ROOT/"artifacts/EXP-484" not in output.parents:
        parser.error("fresh output must be beneath artifacts/EXP-484")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
        parser.error("clean committed source required")
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    upstream = subprocess.check_output(["git", "rev-parse", "@{upstream}"], cwd=ROOT, text=True).strip()
    if source != upstream:
        parser.error("push this exact source freeze before execution")
    plan = json.loads(PLAN.read_bytes())
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    started = time.monotonic()
    binding = dict(source_commit=source, plan_sha256=sha256(PLAN),
        started_at_utc=datetime.now(timezone.utc).isoformat(), output_directory=str(output),
        implementation_sha256=sha256(ROOT/"python/butterfly/return_geometry.py"),
        runner_sha256=sha256(Path(__file__)), execution_mode="local-audited-no-paid-review")
    write_json(output/"binding.json", binding)
    def timeout(*_):
        raise TimeoutError("EXP-484 1800-second wall bound reached")
    previous = signal.signal(signal.SIGALRM, timeout)
    signal.alarm(plan["limits"]["wall_seconds"])
    try:
        selections = prepare(plan)
        write_json(output/"selection.json", selections)
        write_json(output/"controls.json", controls(plan))
        if not args.execute:
            print("Input selection and analytic controls passed; no target integration")
            return
        marker = ROOT/"artifacts/EXP-484/target-once.json"
        with marker.open("x") as handle:
            json.dump(binding, handle, sort_keys=True)
        (output/"trials").mkdir()
        (output/"comparisons").mkdir()
        result = execute(plan, selections, output)
        result.update(binding=binding, elapsed_seconds=time.monotonic()-started,
                      target_slot_sha256=sha256(marker))
        result["files"] = {str(p.relative_to(output)): dict(sha256=sha256(p), bytes=p.stat().st_size)
            for p in sorted(output.rglob("*")) if p.is_file()}
        write_json(output/"summary.json", result)
        print(json.dumps(dict(status=result["status"], all_points_passed=result["all_points_passed"],
            target_integrations=result["target_integrations"], elapsed_seconds=result["elapsed_seconds"])))
    except (Exception, KeyboardInterrupt) as error:
        write_json(output/"failure.json", dict(binding=binding, status="failed", error_type=type(error).__name__,
            message=str(error), elapsed_seconds=time.monotonic()-started))
        raise
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


if __name__ == "__main__":
    main()

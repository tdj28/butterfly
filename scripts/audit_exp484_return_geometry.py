#!/usr/bin/env python3
"""Read-only replay of EXP-484's full realized grid, derivatives and decisions."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
from butterfly._paired_startup import inventory, sha256, write_json
from butterfly.models import RosslerParameters, rossler_rhs
from scripts import run_exp484_return_geometry as run

SOURCE = "31361e388756a7c5e680c30a5d05658dd698ea4a"
SUMMARY_SHA = "93b2ce9207a9ffdfd75c322aeb94b77d6fe9160a99fbdbb7693ce1567a2a32a3"
MARKER_SHA = "a9e5b7bac84602d65c4448db2a7f16127a051838dfbe506c71409494679c093e"
TARGET = ROOT/"artifacts/EXP-484/target-31361e3"


def restore(value):
    """Restore numerical arrays needed for a no-integration comparison replay."""
    return {k: np.asarray(v) if k in ("return_state", "return_jacobian") else v for k, v in value.items()}


def audit_trial(value, state, method, plan, parameters):
    if value["initial_state"] != list(state) or value["method"] != method or value["axes"] != [0, 2]:
        raise ValueError("trial state/method/axes differs from realized grid")
    for k in ("rtol", "atol", "max_step", "horizon", "minimum_angle", "initial_root_guard"):
        if value[k] != plan[k]:
            raise ValueError("trial numerical configuration differs")
    times = np.asarray(value["raw_event_times"])
    states = np.asarray(value["raw_event_states"])
    tangent = np.asarray(value["raw_event_tangents"])
    gate = np.asarray(value["raw_event_gate_accepted"], bool)
    if times.ndim != 1 or states.shape != (len(times), 3) or tangent.shape != (len(times), 3, 2) or gate.shape != times.shape:
        raise ValueError("raw return event shapes differ")
    if not all(np.isfinite(a).all() for a in (times, states, tangent)) or np.any(np.diff(times) <= 0):
        raise ValueError("invalid raw return events")
    from butterfly.poincare import legacy_rossler_section
    section = legacy_rossler_section(parameters)
    if not np.array_equal(gate, [section.accepts(row) for row in states]):
        raise ValueError("saved gate membership differs from actual state")
    eligible = np.flatnonzero((times > plan["initial_root_guard"]) & gate)
    if not len(eligible):
        if value["status"] != "no-return":
            raise ValueError("missing return reported as resolved")
        return None
    index = int(eligible[0])
    if value["status"] != "returned" or value["selected_event"] != index or value["return_time"] != times[index] or value["return_state"] != states[index].tolist():
        raise ValueError("reported return is not the first eligible raw event")
    velocity = rossler_rhs(times[index], states[index], parameters)
    # Separate algebraic form from the production outer-product implementation.
    normal = np.array([0., 1., 0.])
    corrected = (np.eye(3)-np.outer(velocity, normal)/(normal @ velocity)) @ tangent[index]
    error = float(np.max(np.abs(corrected-np.asarray(value["section_tangent"]))))
    if error > 1e-12*max(1., np.max(np.abs(corrected))):
        raise ValueError("event-time derivative reconstruction differs")
    if not np.array_equal(np.asarray(value["return_jacobian"]), np.asarray(value["section_tangent"])[[0, 2]]):
        raise ValueError("2D derivative differs from section tangent")
    return error


def audit():
    if sha256(TARGET/"summary.json") != SUMMARY_SHA:
        raise ValueError("completed EXP-484 receipt anchor changed")
    original = json.loads((TARGET/"summary.json").read_bytes())
    if original["status"] != "completed" or inventory(TARGET, omit=("summary.json",)) != original["files"]:
        raise ValueError("completed run inventory differs")
    marker = ROOT/"artifacts/EXP-484/target-once.json"
    if sha256(marker) != MARKER_SHA or original["target_slot_sha256"] != MARKER_SHA:
        raise ValueError("consumed EXP-484 slot differs")
    plan = json.loads(run.PLAN.read_bytes())
    binding = original["binding"]
    if (binding["source_commit"] != SOURCE or binding["plan_sha256"] != sha256(run.PLAN)
            or binding["implementation_sha256"] != sha256(ROOT/"python/butterfly/return_geometry.py")
            or binding["runner_sha256"] != sha256(ROOT/"scripts/run_exp484_return_geometry.py")
            or json.loads((TARGET/"binding.json").read_bytes()) != binding
            or json.loads(marker.read_bytes()) != binding):
        raise ValueError("implementation/source/slot binding changed")
    selections = run.prepare(plan)
    if json.loads((TARGET/"selection.json").read_bytes()) != selections:
        raise ValueError("independent calibration selection differs")
    controls = json.loads((TARGET/"controls.json").read_bytes())
    if [r["method"] for r in controls] != plan["solvers"] or not all(r["passed"] for r in controls):
        raise ValueError("analytic control grid or status differs")
    for control in controls:
        result = control["result"]
        if result["status"] != "returned" or abs(result["return_time"]-2*np.pi) >= 1e-9 or np.max(np.abs(np.asarray(result["return_jacobian"])-np.diag([1., np.exp(-.3*2*np.pi)]))) >= 1e-9:
            raise ValueError("saved analytic control does not satisfy its known solution")
    expected = {"binding.json", "selection.json", "controls.json"}
    reproduced, points, derivative_errors = [], [], []
    for selection in selections:
        parameters = RosslerParameters(**selection["parameters"])
        for point in selection["points"]:
            label = f"{selection['case']}--bin-{point['bin']:02d}"
            def read(suffix, state, method):
                stem = f"trials/{label}--{suffix}"
                expected.update((stem+".json", stem+"-started.json"))
                started = json.loads((TARGET/(stem+"-started.json")).read_bytes())
                if started != dict(label=label+"--"+suffix, initial_state=list(state), method=method):
                    raise ValueError("started trial differs from intended state grid")
                result = json.loads((TARGET/(stem+".json")).read_bytes())
                error = audit_trial(result, state, method, plan, parameters)
                if error is not None:
                    derivative_errors.append(error)
                return restore(result)
            base = {method: read(method, point["initial_state"], method) for method in plan["solvers"]}
            differences = {}
            fd = plan["finite_difference"]
            if point["bin"] in fd["bins"]:
                for step in fd["normalized_steps"]:
                    trials = {}
                    for i, axis in enumerate(fd["axes"]):
                        for sign in fd["signs"]:
                            state = np.array(point["initial_state"])
                            state[axis] += sign*step*plan["section_coordinate_scales"][i]
                            trials[(axis, sign)] = read(f"fd-{step:g}-{axis}-{sign}", state, fd["solver"])
                    differences[step] = trials
            decision = run.serial(run.analyze_point(point, base, differences, plan))
            row = dict(case=selection["case"], bin=point["bin"], audit=decision)
            compare = f"comparisons/{label}.json"
            expected.add(compare)
            if json.loads((TARGET/compare).read_bytes()) != row:
                raise ValueError("per-point decision replay differs")
            reproduced.append(row)
            points.append(dict(case=selection["case"], bin=point["bin"], global_seed_id=point["global_seed_id"],
                initial_state=point["initial_state"], solvers={m:{k:run.serial(v) for k,v in result.items()
                    if k in ("status", "return_state", "return_time", "return_jacobian", "return_time_gradient", "normalized_angle")}
                    for m,result in base.items()}))
    if (set(original["files"]) != expected or original["target_integrations"] != 240
            or len(derivative_errors) != 240 or original["rows"] != reproduced
            or original["all_points_passed"] != all(r["audit"]["passed"] for r in reproduced)):
        raise ValueError("realized grid or overall decision differs from frozen plan")
    if inventory(TARGET, omit=("summary.json",)) != original["files"] or sha256(TARGET/"summary.json") != SUMMARY_SHA:
        raise ValueError("completed run changed during audit")
    metrics = ("solver_scaled_state_error", "solver_return_time_error", "solver_relative_scaled_jacobian_error",
               "saved_pair_scaled_state_error", "saved_pair_return_time_error")
    maxima = {key:max(r["audit"][key] for r in reproduced) for key in metrics}
    maxima["finite_difference_relative_scaled_jacobian_error"] = max(f["relative_scaled_jacobian_error"]
        for r in reproduced for f in r["audit"]["finite_difference"])
    return dict(experiment_id="EXP-484", status="completed-and-audited", source_commit=SOURCE,
        original_receipt_sha256=SUMMARY_SHA, target_slot_sha256=MARKER_SHA,
        actual_grid_and_decisions_replayed_exactly=True, independent_event_correction_max_error=max(derivative_errors),
        target_integrations=240, points=points, rows=reproduced, all_points_passed=original["all_points_passed"],
        maximum_observed_errors=maxima, thresholds=plan["thresholds"], elapsed_seconds=original["elapsed_seconds"],
        verified_files=len(original["files"]), verified_bytes=sum(v["bytes"] for v in original["files"].values()),
        paid_review="not_run", historical_symbols_verified=False, claim_boundary=plan["claim_boundary"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    try:
        result = audit()
        write_json(args.output_dir/"summary.json", result)
        print(json.dumps(dict(status=result["status"], all_points_passed=result["all_points_passed"],
            maximum_observed_errors=result["maximum_observed_errors"], summary_sha256=sha256(args.output_dir/"summary.json"))))
    except (Exception, KeyboardInterrupt) as error:
        write_json(args.output_dir/"failure.json", dict(error_type=type(error).__name__, message=str(error)))
        raise


if __name__ == "__main__":
    main()

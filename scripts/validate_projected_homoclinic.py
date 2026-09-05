#!/usr/bin/env python3
"""Run a frozen, bounded endpoint-projection BVP pilot with analytic controls."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import time

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from butterfly.homoclinic_bvp import (
    ParameterBox, duffing_homoclinic, duffing_model, duffing_seed,
    local_replay_defects, rossler_bvp_model, solve_projected_homoclinic,
)
from butterfly.scan import atomic_write, canonical_json, git_value
from butterfly.homoclinic_refinement import (
    summarize_grid_sensitivity, validate_grid_manifest,
)


SCHEMA = "butterfly.projected-homoclinic-pilot.v1"
GRID_SCHEMA = "butterfly.projected-homoclinic-pilot.v2"


def positive_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive number")


def strict_json_bytes(value):
    """Keep failure evidence valid JSON without hiding nonfinite diagnostics."""
    invalid = []

    def sanitize(item, path):
        if isinstance(item, dict):
            return {key: sanitize(child, f"{path}.{key}") for key, child in item.items()}
        if isinstance(item, (list, tuple)):
            return [sanitize(child, f"{path}[{index}]") for index, child in enumerate(item)]
        if isinstance(item, (float, np.floating)) and not np.isfinite(item):
            invalid.append(path)
            return None
        return item

    safe = sanitize(value, "receipt")
    if invalid:
        safe["nonfinite_fields_replaced_by_null"] = invalid
        safe["passed"] = False
    return json.dumps(safe, sort_keys=True, separators=(",", ":"), allow_nan=False).encode() + b"\n"


def finite_numeric_tree(value):
    if isinstance(value, dict):
        return all(finite_numeric_tree(child) for child in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_numeric_tree(child) for child in value)
    return not isinstance(value, (float, np.floating)) or bool(np.isfinite(value))


def check_deadline(deadline, stage):
    if deadline is not None and time.monotonic() >= deadline:
        raise TimeoutError(f"cooperative budget exhausted during {stage}")


def committed_manifest_binding(path, content, *, root=None):
    """A clean tree is insufficient: the actual protocol must be in HEAD."""
    root = Path(__file__).resolve().parents[1] if root is None else Path(root)
    try:
        relative = path.resolve().relative_to(root.resolve()).as_posix()
        committed = subprocess.check_output(
            ["git", "show", f"HEAD:{relative}"], cwd=root, stderr=subprocess.DEVNULL,
        )
        blob = subprocess.check_output(
            ["git", "rev-parse", f"HEAD:{relative}"], cwd=root, stderr=subprocess.DEVNULL,
        ).decode().strip()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        raise ValueError("target manifest must be a tracked file in the committed source tree") from error
    if content != committed:
        raise ValueError("target manifest bytes differ from the committed HEAD protocol")
    return {"path": relative, "git_blob": blob, "sha256": hashlib.sha256(content).hexdigest(), "matches_HEAD": True}


def validate_manifest(manifest):
    is_grid = manifest.get("schema") == GRID_SCHEMA
    if manifest.get("schema") not in (SCHEMA, GRID_SCHEMA):
        raise ValueError("unsupported endpoint-projection pilot manifest")
    fixed = manifest["fixed_parameters"]
    if not all(np.isfinite(fixed[name]) for name in ("b", "c")):
        raise ValueError("fixed parameters must be finite")
    if is_grid:
        if not finite_numeric_tree(manifest):
            raise ValueError("v2 manifest contains nonfinite numerical values")
        validate_grid_manifest(manifest)
    else:
        if len(manifest["cases"]) != 4:
            raise ValueError("the pilot requires three radii and one mesh refinement")
        radii = [row["radius"] for row in manifest["cases"]]
        if not (0 < radii[2] < radii[1] < radii[0] and radii[3] == radii[2]):
            raise ValueError("endpoint radii must shrink in the frozen order")
        tolerances = [row["tolerance"] for row in manifest["cases"]]
        if not (0 < tolerances[3] < tolerances[0] == tolerances[1] == tolerances[2]):
            raise ValueError("last case must tighten collocation tolerance only")
    for key in ("maximum_total_seconds", "maximum_trial_seconds", "maximum_seed_step", "maximum_state_norm"):
        if not np.isfinite(manifest["budget"][key]) or manifest["budget"][key] <= 0:
            raise ValueError(f"invalid budget: {key}")
    bounds = manifest["physical_bounds"]
    ParameterBox((bounds["a"][0], bounds["flight_time"][0]), (bounds["a"][1], bounds["flight_time"][1]))
    if manifest["budget"]["stop_on_first_failed_case"] is not True:
        raise ValueError("this pilot requires stopping on the first failed case")
    if is_grid:
        budget, controls, replay, acceptance = (manifest[name] for name in ("budget", "analytic_controls", "replay", "acceptance"))
        for key in ("maximum_total_seconds", "maximum_trial_seconds", "maximum_seed_step", "maximum_state_norm"):
            positive_number(budget[key], f"budget.{key}")
        for mapping, keys in ((budget, ("maximum_nodes",)), (controls, ("initial_nodes", "maximum_nodes")), (replay, ("segments",))):
            for key in keys:
                if type(mapping[key]) is not int or mapping[key] < 3:
                    raise ValueError(f"{key} must be an integer of at least three")
        if budget["maximum_trial_seconds"] > budget["maximum_total_seconds"]:
            raise ValueError("per-case budget cannot exceed the total budget")
        if controls["maximum_nodes"] < controls["initial_nodes"]:
            raise ValueError("analytic initial mesh exceeds node budget")
        initial_mu = controls["initial_damping"]
        if isinstance(initial_mu, bool) or not isinstance(initial_mu, (int, float)) or not -0.1 < initial_mu < 0.1:
            raise ValueError("analytic initial mu must be strictly inside (-0.1, 0.1)")
        for key in ("tolerance", "boundary_tolerance", "maximum_absolute_damping"):
            positive_number(controls[key], f"analytic_controls.{key}")
        if controls["tolerance"] > min(manifest["refinement"]["tolerances"]):
            raise ValueError("analytic controls must reach the finest target tolerance")
        if controls.get("require_completed_negative_control") is not True:
            raise ValueError("a completed numerical negative-control rejection is required")
        if len(controls["radii"]) != 3 or not all(0 < right < left < 1 for left, right in zip(controls["radii"], controls["radii"][1:])):
            raise ValueError("analytic controls require three decreasing radii in (0,1)")
        if replay["method"] != "DOP853":
            raise ValueError("the independent replay method must be DOP853")
        for key in ("rtol", "atol", "maximum_step"):
            positive_number(replay[key], f"replay.{key}")
        if acceptance.get("maximum_replay_state_defect") != "case_tolerance":
            raise ValueError("v2 replay acceptance must use each case tolerance")
        for key in ("maximum_scaled_boundary_residual", "minimum_parameter_box_margin", "minimum_excursion", "maximum_source_a_difference"):
            positive_number(acceptance[key], f"acceptance.{key}")
        if not 1e-4 <= acceptance["minimum_parameter_box_margin"] < 0.5:
            raise ValueError("parameter interiority must respect the underlying solver gate")


def analytic_controls(configuration, *, deadline=None, progress=None):
    model = duffing_model()
    rows, errors = [], []
    for radius in configuration["radii"]:
        check_deadline(deadline, "analytic controls")
        mesh, guess, duration = duffing_seed(radius, configuration["initial_nodes"])
        result, summary = solve_projected_homoclinic(
            model, mesh, guess, parameter=configuration["initial_damping"], flight_time=duration,
            radii=(radius, radius), box=ParameterBox((-0.1, duration * 0.8), (0.1, duration * 1.2)),
            tolerance=configuration["tolerance"], boundary_tolerance=configuration["boundary_tolerance"],
            maximum_nodes=configuration["maximum_nodes"], maximum_seconds=10.0 if deadline is None else min(10.0, deadline - time.monotonic()),
        )
        row = {"radius": radius, **summary}
        if result is not None:
            points = np.linspace(0.0, 1.0, 1001)
            exact = duffing_homoclinic((points - 0.5) * summary["flight_time"])
            error = float(np.max(np.linalg.norm(result.sol(points) - exact, axis=0)))
            errors.append(error)
            row["maximum_analytic_state_error"] = error
            row["replay"] = local_replay_defects(model, result, summary["parameter"], summary["flight_time"], segments=16, deadline=deadline)
            row["passed"] = bool(
                summary["passed_numerical_gates"] and abs(summary["parameter"]) <= configuration["maximum_absolute_damping"]
                and summary["maximum_excursion"] > 1.4 and error <= radius**2
                and row["replay"]["success"] and row["replay"]["maximum_state_defect"] <= 1e-6
                and finite_numeric_tree(row)
            )
        else:
            row["passed"] = False
        rows.append(row)
        if progress is not None:
            progress({"passed": False, "complete": False, "positive_controls": rows})
        check_deadline(deadline, "analytic control acceptance")
    check_deadline(deadline, "analytic negative control")
    mesh, guess, duration = duffing_seed(0.05, configuration["initial_nodes"])
    _result, negative = solve_projected_homoclinic(
        model, mesh, guess, parameter=0.05, flight_time=duration,
        radii=(0.05, 0.05), box=ParameterBox((0.03, duration * 0.8), (0.07, duration * 1.2)),
        tolerance=configuration["tolerance"], boundary_tolerance=configuration["boundary_tolerance"],
        maximum_nodes=configuration["maximum_nodes"], maximum_seconds=10.0 if deadline is None else min(10.0, deadline - time.monotonic()),
    )
    if progress is not None:
        progress({"passed": False, "complete": False, "positive_controls": rows, "negative_control": negative})
    check_deadline(deadline, "analytic negative-control acceptance")
    shrinking = len(errors) == len(rows) and all(right <= 0.4 * left for left, right in zip(errors, errors[1:]))
    rejected = not negative["passed_numerical_gates"]
    if configuration.get("require_completed_negative_control"):
        # A node/time/domain failure is not a qualified negative-control rejection.
        rejected = bool(rejected and _result is not None and negative.get("solver_status") in (0, 2, 3) and finite_numeric_tree(negative))
    passed = bool(all(row["passed"] for row in rows) and shrinking and rejected)
    return {"passed": passed, "complete": True, "positive_controls": rows, "shrinking_truncation_error": shrinking, "negative_control": negative, "negative_control_rejection_qualified": rejected}


def reconstruct_seed(source, model, radius, budget, deadline):
    """Build only an initial guess from saved arcs; no old matching residual."""
    parameter = float(source["final_variables"]["a"])
    duration = float(source["final_variables"]["total_flight_time"])
    segments = int(source["segment_count"])
    nodes = np.vstack((source["final_nodes"], source["final_endpoint"]))
    if nodes.shape != (segments, 3) or not np.all(np.isfinite(nodes)):
        raise ValueError("source seed must contain finite saved internal nodes and endpoint")
    equilibrium = model.equilibrium(parameter)
    distances = np.linalg.norm(nodes - equilibrium, axis=1)
    candidates = np.flatnonzero((distances[:-1] < radius) & (distances[1:] >= radius))
    if not len(candidates):
        raise ValueError("source does not contain a departure bracket at the frozen radius")
    start_index = int(candidates[0])
    step = duration / segments
    maximum_step = float(budget["maximum_seed_step"])

    def field(_time, state):
        if time.monotonic() > deadline:
            raise TimeoutError("total pilot budget exhausted during seed construction")
        if not np.all(np.isfinite(state)) or np.linalg.norm(state) > budget["maximum_state_norm"]:
            raise ValueError("seed left the declared state domain")
        return model.field(state[:, None], parameter)[:, 0]

    def radius_event(_time, state):
        return float(np.linalg.norm(state - equilibrium) - radius)

    radius_event.direction = 1
    radius_event.terminal = False
    times, states, defects = [], [], []
    departure_time = None
    for index in range(start_index, len(nodes) - 1):
        trial = solve_ivp(field, (0.0, step), nodes[index], method="DOP853", rtol=1e-10, atol=1e-12, max_step=maximum_step, dense_output=True, events=radius_event if index == start_index else None)
        if not trial.success:
            raise RuntimeError(f"source arc replay failed at {index}: {trial.message}")
        first_time = 0.0
        if index == start_index:
            if not len(trial.t_events[0]):
                raise ValueError("independent seed replay lost the departure-radius crossing")
            first_time = float(trial.t_events[0][0])
            departure_time = (index + 1) * step + first_time
        count = max(2, int(np.ceil((step - first_time) / maximum_step)) + 1)
        local_times = np.linspace(first_time, step, count)[:-1]
        times.extend(((index + 1) * step + local_times).tolist())
        states.extend(trial.sol(local_times).T.tolist())
        defects.append(float(np.linalg.norm(trial.y[:, -1] - nodes[index + 1])))
    # The short final tail is an initial guess only. Boundary equations below
    # use fresh eigenspace projections, never this old matching target.
    radius_event.direction = -1
    radius_event.terminal = True
    tail = solve_ivp(field, (0.0, 2.0), nodes[-1], method="DOP853", rtol=1e-10, atol=1e-12, max_step=maximum_step, dense_output=True, events=radius_event)
    if not tail.success or not len(tail.t_events[0]):
        raise ValueError("source arrival cannot seed the frozen smaller endpoint radius")
    tail_time = float(tail.t_events[0][0])
    sample_times = np.linspace(0.0, tail_time, max(3, int(np.ceil(tail_time / maximum_step)) + 1))
    times.extend((duration + sample_times).tolist())
    states.extend(tail.sol(sample_times).T.tolist())
    full_time = duration + tail_time - departure_time
    mesh = (np.asarray(times) - departure_time) / full_time
    mesh[0], mesh[-1] = 0.0, 1.0
    return mesh, np.asarray(states).T, full_time, {
        "source_parameter": parameter, "trimmed_departure_time": departure_time,
        "appended_arrival_time": tail_time, "maximum_seed_arc_defect": max(defects),
        "initial_nodes": len(mesh), "initial_flight_time": full_time,
        "role": "archived path reused only as an initial guess",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--controls-only", action="store_true", help="synthetic development controls; no Rössler target execution")
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("output already exists; refusing to overwrite a receipt")
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    validate_manifest(manifest)
    is_grid = manifest["schema"] == GRID_SCHEMA
    status = git_value("status", "--porcelain")
    source_state = {"commit": git_value("rev-parse", "HEAD"), "branch": git_value("branch", "--show-current"), "dirty": bool(status)}
    if not args.controls_only and (source_state["commit"] is None or status is None or source_state["dirty"]):
        raise SystemExit("target execution requires the committed protocol and a clean source tree")
    protocol_binding = None
    if is_grid and not args.controls_only:
        protocol_binding = committed_manifest_binding(args.manifest, manifest_bytes)
    started = time.monotonic()
    deadline = started + manifest["budget"]["maximum_total_seconds"]
    receipt = {
        "schema": "butterfly.projected-homoclinic-pilot-receipt.v2" if is_grid else "butterfly.projected-homoclinic-pilot-receipt.v1",
        "experiment_id": manifest["experiment_id"], "source": source_state,
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "controls_only": bool(args.controls_only), "complete": False, "passed": False,
        "claim_scope": manifest["claim_scope"], "cases": [],
    }
    if is_grid:
        receipt.update({
            "committed_manifest": protocol_binding,
            "source_receipt": manifest["source_receipt"],
            "technical_passed": False,
            "discretization_passed": False,
            "pass_definition": "all target technical gates and the declared discretization refinement gates; endpoint-effect classification is separate",
            "deadline_policy": "cooperative per-case deadline covers seed, collocation, and replay within the total deadline; not hard process preemption",
        })
    current_case = None

    def checkpoint():
        receipt["elapsed_seconds"] = time.monotonic() - started
        if is_grid and not finite_numeric_tree(receipt):
            # Keep the returned/printed status consistent with the null-safe
            # serialized receipt, including diagnostics outside case rows.
            receipt["passed"] = False
        atomic_write(args.output, strict_json_bytes(receipt) if is_grid else canonical_json(receipt))

    def checkpoint_controls(snapshot):
        receipt["controls"] = snapshot
        checkpoint()

    expected_errors = (ValueError, RuntimeError, TimeoutError)
    if is_grid:
        expected_errors += (OSError, KeyError, TypeError, IndexError, FloatingPointError, np.linalg.LinAlgError)
    try:
        receipt["controls"] = analytic_controls(manifest["analytic_controls"], deadline=deadline, progress=checkpoint_controls) if is_grid else analytic_controls(manifest["analytic_controls"])
        checkpoint()
        if args.controls_only:
            receipt["passed"] = receipt["controls"]["passed"]
        elif not receipt["controls"]["passed"] or (is_grid and not finite_numeric_tree(receipt["controls"])):
            raise RuntimeError("analytic controls failed; target execution skipped")
        else:
            binding = manifest["source_receipt"]
            raw = Path(binding["path"]).read_bytes()
            if hashlib.sha256(raw).hexdigest() != binding["sha256"]:
                raise ValueError("source receipt hash mismatch")
            source = json.loads(raw)
            if source["experiment_id"] != binding["experiment_id"] or not source["passed"]:
                raise ValueError("source receipt identity/status mismatch")
            if is_grid and (source["passed"] is not True or not finite_numeric_tree(source)):
                raise ValueError("source receipt must have a true status and finite numerical evidence")
            if source["fixed_parameters"] != manifest["fixed_parameters"]:
                raise ValueError("source and target fixed parameters differ")
            model = rossler_bvp_model(**manifest["fixed_parameters"])
            bounds = manifest["physical_bounds"]
            box = ParameterBox((bounds["a"][0], bounds["flight_time"][0]), (bounds["a"][1], bounds["flight_time"][1]))
            for case in manifest["cases"]:
                case_started = time.monotonic()
                case_deadline = min(deadline, case_started + manifest["budget"]["maximum_trial_seconds"]) if is_grid else deadline
                current_case = {"case": case, "status": "preparing_seed", "passed": False}
                receipt["cases"].append(current_case)
                checkpoint()
                radius = case["radius"]
                check_deadline(case_deadline if is_grid else None, "case seed preparation")
                mesh, guess, duration, seed = reconstruct_seed(source, model, radius, manifest["budget"], case_deadline)
                remaining = min(manifest["budget"]["maximum_trial_seconds"], case_deadline - time.monotonic())
                if remaining <= 0.0:
                    raise TimeoutError("total pilot budget exhausted")
                result, summary = solve_projected_homoclinic(
                    model, mesh, guess, parameter=seed["source_parameter"], flight_time=duration,
                    radii=(radius, radius), box=box, tolerance=case["tolerance"],
                    boundary_tolerance=manifest["acceptance"]["maximum_scaled_boundary_residual"],
                    maximum_nodes=manifest["budget"]["maximum_nodes"], maximum_seconds=remaining,
                    maximum_state_norm=manifest["budget"]["maximum_state_norm"],
                )
                row = current_case
                row.update({"seed": seed, "collocation": summary, "status": "diagnosing"})
                if result is not None:
                    # Preserve a solved path even if replay subsequently raises,
                    # times out, or fails its independent numerical gate.
                    row["normalized_mesh"] = result.x.tolist()
                    row["states"] = result.y.T.tolist()
                    if is_grid:
                        checkpoint()
                        check_deadline(case_deadline, "case replay preparation")
                    row["replay"] = local_replay_defects(
                        model, result, summary["parameter"], summary["flight_time"],
                        segments=manifest["replay"]["segments"], method=manifest["replay"]["method"],
                        rtol=manifest["replay"]["rtol"], atol=manifest["replay"]["atol"],
                        maximum_step=manifest["replay"]["maximum_step"], deadline=case_deadline,
                    )
                    row["source_a_difference"] = abs(summary["parameter"] - seed["source_parameter"])
                    replay_limit = case["tolerance"] if is_grid else manifest["acceptance"]["maximum_replay_state_defect"]
                    row["passed"] = bool(
                        summary["passed_numerical_gates"] and summary["maximum_excursion"] >= manifest["acceptance"]["minimum_excursion"]
                        and summary["minimum_parameter_box_margin"] >= manifest["acceptance"]["minimum_parameter_box_margin"]
                        and row["source_a_difference"] <= manifest["acceptance"]["maximum_source_a_difference"]
                        and row["replay"]["success"] and row["replay"]["maximum_state_defect"] <= replay_limit
                    )
                    if is_grid:
                        row["replay_acceptance_limit"] = replay_limit
                        row["passed"] = bool(row["passed"] and finite_numeric_tree(row))
                if is_grid:
                    # Do not leave passed=true if an otherwise successful replay
                    # finishes after a cooperative deadline.
                    accepted = row["passed"]
                    row["passed"] = False
                    check_deadline(case_deadline, "case acceptance")
                    row["passed"] = accepted
                    row["elapsed_seconds"] = time.monotonic() - case_started
                row["status"] = "passed" if row["passed"] else "failed"
                checkpoint()
                if not row["passed"]:
                    raise RuntimeError(f"case {case['name']} failed; later cases skipped under frozen stop rule")
            if not is_grid:
                parameters = [row["collocation"]["parameter"] for row in receipt["cases"]]
                last_radius_difference = abs(parameters[2] - parameters[1])
                mesh_difference = abs(parameters[3] - parameters[2])
                receipt["sensitivity"] = {
                    "radius_a_differences": [abs(parameters[1] - parameters[0]), last_radius_difference],
                    "mesh_a_difference": mesh_difference,
                    "empirical_a_sensitivity": max(last_radius_difference, mesh_difference),
                    "interpretation": "observed finite-radius/discretization sensitivity, not a rigorous parameter error bound",
                }
                receipt["passed"] = bool(last_radius_difference <= manifest["acceptance"]["maximum_last_radius_a_difference"] and mesh_difference <= manifest["acceptance"]["maximum_mesh_a_difference"])
    except expected_errors as error:
        receipt["failure"] = f"{type(error).__name__}: {error}"
        if current_case is not None and not current_case["passed"]:
            current_case.update({"status": "failed", "failure": receipt["failure"]})
    for case in manifest["cases"][len(receipt["cases"]):]:
        receipt["cases"].append({
            "case": case, "status": "skipped", "passed": False,
            "reason": "controls-only mode" if args.controls_only else "earlier failure under the frozen stop rule",
        })
    if is_grid and not args.controls_only:
        receipt["sensitivity"] = summarize_grid_sensitivity(receipt["cases"], manifest)
        receipt["technical_passed"] = bool(receipt["controls"]["passed"] and finite_numeric_tree(receipt["controls"]) and receipt["sensitivity"]["technical_passed"]) if "controls" in receipt else False
        receipt["discretization_passed"] = receipt["sensitivity"]["discretization_passed"]
        receipt["passed"] = bool(receipt["technical_passed"] and receipt["discretization_passed"] and "failure" not in receipt)
    receipt["complete"] = True
    checkpoint()
    print(json.dumps({key: receipt[key] for key in ("experiment_id", "controls_only", "passed", "elapsed_seconds")}, sort_keys=True))
    return 0 if receipt["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

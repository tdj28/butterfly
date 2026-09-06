#!/usr/bin/env python3
"""EXP-480 event feasibility runner. Draft plans cannot execute targets.

Preflight reads only bound declarations/old input evidence. The numerical path
has no historical words or partition fitting and retains both nominations.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from scipy.integrate import solve_ivp

from butterfly import (RosslerParameters, SolverConfig, correct_periodic_orbit,
                       legacy_rossler_section, barrio_rossler_section, rossler_rhs)
from scripts import run_symbolic_center_pilot as evidence

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "experiments/manifests/EXP-480-event-transport.json"
REVIEW_RUNTIME_PATHS = ("scripts/check_historical_event_transport.py", "scripts/run_symbolic_center_pilot.py",
                        "python/butterfly/periodic.py", "python/butterfly/poincare.py",
                        "python/butterfly/models.py", "python/butterfly/integrate.py", "pyproject.toml", "uv.lock")


def design_hash(plan):
    return hashlib.sha256(json.dumps(plan["design"], sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def execution_gate(plan, root=ROOT):
    if plan.get("status") != "reviewed-frozen" or plan.get("execution_authorized") is not True:
        raise ValueError("draft or unauthorized design: no target execution")
    descriptor = plan.get("review")
    if not isinstance(descriptor, dict):
        raise ValueError("hash-bound adjudicated review required")
    path = evidence.confined_path(root, descriptor["path"])
    if evidence.sha256_file(path) != descriptor["sha256"]:
        raise ValueError("review hash mismatch")
    review = json.loads(path.read_bytes())
    if (review.get("schema") != "butterfly.design-review-adjudication.v1"
            or review.get("design_sha256") != design_hash(plan)
            or review.get("approved_for_execution") is not True or not review.get("adjudication")):
        raise ValueError("review is missing, unadjudicated, or bound to another design")
    evidence.checked_input(root, review["review_receipt"])
    for name in REVIEW_RUNTIME_PATHS:
        path = evidence.confined_path(root, name)
        if evidence.sha256_file(path) != review.get("runtime_files", {}).get(name):
            raise ValueError("runtime differs from adjudicated review")


def prepare(plan):
    if plan.get("schema") != "butterfly.event-transport-plan.v1" or plan.get("experiment_id") != "EXP-480":
        raise ValueError("wrong experiment manifest")
    design = plan["design"]
    validate_design(design)
    payloads = {}
    for key in ("candidate_input", "nomination_receipt"):
        row = design[key]
        path = evidence.confined_path(ROOT, row["path"])
        if evidence.sha256_file(path) != row["sha256"]:
            raise ValueError("bound input hash mismatch")
        payloads[key] = json.loads(path.read_bytes())
    nominations = payloads["nomination_receipt"]
    if (nominations["status"] != "completed" or nominations["nomination_result"]["direct_candidate_ids"] != design["candidate_ids"]):
        raise ValueError("must retain the complete ordered nomination set")
    by_id = {row["id"]: row for row in payloads["candidate_input"]["candidates"]}
    selected = [by_id[name] for name in design["candidate_ids"]]
    if len(set(design["candidate_ids"])) != len(selected) or not all(row["passed"] for row in selected):
        raise ValueError("invalid or duplicate candidate")
    for row in selected:
        values = np.asarray([*row["correction"]["initial_state"], row["correction"]["period_time"]])
        if values.shape != (4,) or not np.isfinite(values).all() or values[-1] <= 0:
            raise ValueError("invalid source cycle")
    return selected


def validate_design(design):
    if (design["candidate_ids"] != ["local-a025-c083", "local-a027-c083"]
            or [p["name"] for p in design["profiles"]] != ["dop853", "dop853-refined", "radau", "radau-refined"]
            or [p["method"] for p in design["profiles"]] != ["DOP853", "DOP853", "Radau", "Radau"]
            or design["sections"] != ["historical-negative", "barrio-positive"]
            or design["expected_counts"] != {"historical-negative": 6, "barrio-positive": 8}
            or design["window_start_periods"] != [0.25, 1.25] or design["observation_periods"] != 2.5
            or design["automatic_retry"] is not False):
        raise ValueError("incomplete or unsupported event-transport design")
    numbers = [*design["state_scales"], *design["acceptance"].values(), design["maximum_wall_seconds"],
               *design["correction"].values(), *[p[k] for p in design["profiles"] for k in ("rtol", "atol", "max_step")]]
    if len(design["state_scales"]) != 3 or not all(np.isfinite(x) and x > 0 for x in numbers):
        raise ValueError("finite positive numerical design required")


def sections(parameters):
    return {"historical-negative": replace(legacy_rossler_section(parameters), direction=-1),
            "barrio-positive": barrio_rossler_section(parameters)}


def collect_events(rhs, initial, period, section_map, config, design):
    """One trajectory, both raw planes and their normal-velocity extrema.

    Unoriented, ungated plane roots are retained before filtering. Extrema
    diagnostics and step/solver refinement are numerical checks, not a proof
    that solve_ivp detects every between-step root.
    """
    callbacks = []
    for section in section_map.values():
        def plane(t, y, section=section):
            return section.value(y)
        def extremum(t, y, section=section):
            return float(np.dot(section.normal, rhs(t, y)))
        for callback in (plane, extremum):
            callback.direction, callback.terminal = 0, False
            callbacks.append(callback)
    result = solve_ivp(rhs, (0, design["observation_periods"] * period), initial,
                       events=callbacks, **asdict(config))
    raw = {"integration_times": result.t, "integration_states": result.y.T}
    diagnostics = {"integration_success": bool(result.success), "message": result.message,
                   "nfev": result.nfev, "sections": {}}
    scales = np.asarray(design["state_scales"])
    for index, (name, section) in enumerate(section_map.items()):
        times = np.asarray(result.t_events[2 * index])
        states = np.asarray(result.y_events[2 * index]).reshape(-1, 3)
        fields = np.asarray([rhs(t, y) for t, y in zip(times, states, strict=True)]).reshape(-1, 3)
        normal = np.asarray(section.normal)
        velocity = fields @ normal
        denominator = np.linalg.norm(fields, axis=1) * np.linalg.norm(normal)
        angles = np.divide(np.abs(velocity), denominator, out=np.zeros_like(velocity), where=denominator > 0)
        accepted = np.asarray([section.accepts(y) for y in states], dtype=bool) & (section.direction * velocity > 0)
        etimes = np.asarray(result.t_events[2 * index + 1])
        estates = np.asarray(result.y_events[2 * index + 1]).reshape(-1, 3)
        distances = np.asarray([abs(section.value(y)) / np.linalg.norm(normal * scales) for y in estates])
        relevant = np.asarray([section.accepts(y) for y in estates], dtype=bool)
        for key, value in {"times": times, "states": states, "normal_velocity": velocity, "angles": angles,
                           "accepted": accepted, "extremum_times": etimes, "extremum_states": estates,
                           "extremum_plane_distance": distances, "extremum_gate_accepted": relevant}.items():
            raw[name + "_" + key] = value
        diagnostics["sections"][name] = {"plane_roots": len(times), "accepted_roots": int(accepted.sum()),
            "extremum_roots": len(etimes), "section": asdict(section)}
    diagnostics["finite_raw_data"] = bool(all(np.isfinite(value).all() for value in raw.values()))
    diagnostics["horizon_reached"] = bool(len(result.t) and result.t[-1] >= design["observation_periods"] * period)
    return raw, diagnostics


def summarize_events(raw, period, design):
    gate = design["acceptance"]
    summary = {}
    for name, expected in design["expected_counts"].items():
        accepted = raw[name + "_accepted"]
        phases = raw[name + "_times"][accepted] / period
        states = raw[name + "_states"][accepted]
        angles = raw[name + "_angles"][accepted]
        windows = []
        for start in design["window_start_periods"]:
            selected = (phases >= start) & (phases < start + 1)
            points = states[selected]
            separations = [float(np.linalg.norm((left-right) / design["state_scales"]))
                           for i, left in enumerate(points) for right in points[i+1:]]
            boundary = float(np.min(np.abs(phases[:, None] - np.asarray([start, start+1])))) if len(phases) else 0.0
            minimum_angle = float(np.min(angles[selected])) if np.any(selected) else 0.0
            separation = min(separations) if separations else None
            passed = (len(points) == expected and minimum_angle >= gate["minimum_normalized_crossing_angle"]
                      and (len(points) == 1 or (separation is not None and separation >= gate["minimum_distinct_event_scaled_separation"]))
                      and boundary >= gate["minimum_window_boundary_phase_distance"])
            windows.append({"count": len(points), "states": points.tolist(), "phases": (phases[selected]-start).tolist(),
                            "minimum_angle": minimum_angle, "minimum_pair_separation": separation,
                            "boundary_margin": boundary, "passed": bool(passed)})
        relevant = raw[name + "_extremum_gate_accepted"]
        distances = raw[name + "_extremum_plane_distance"][relevant]
        # No extrema is not automatically an error; all raw root data is retained.
        extremum_margin = float(np.min(distances)) if len(distances) else None
        pair = compare_windows(windows[0], windows[1], design)
        summary[name] = {"windows": windows, "repeat_comparison": pair, "minimum_extremum_distance": extremum_margin,
            "passed": bool(all(w["passed"] for w in windows) and pair["passed"]
                           and (extremum_margin is None or extremum_margin >= gate["minimum_normalized_extremum_plane_distance"]))}
    return summary


def compare_windows(left, right, design):
    a, b = np.asarray(left["states"]), np.asarray(right["states"])
    if a.shape != b.shape or a.ndim != 2 or a.shape[1:] != (3,) or len(a) == 0:
        return {"passed": False, "reason": "unequal or empty ordered event sets"}
    state_error = float(np.max(np.linalg.norm((a-b) / design["state_scales"], axis=1)))
    phase_error = float(np.max(np.abs(np.asarray(left["phases"])-right["phases"])))
    return {"maximum_scaled_state_error": state_error, "maximum_phase_error": phase_error,
            "passed": bool(np.isfinite(state_error) and np.isfinite(phase_error)
                           and state_error <= design["acceptance"]["maximum_scaled_event_state_difference"]
                           and phase_error <= design["acceptance"]["maximum_event_phase_difference"])}


def execute(plan, candidates, output, source, *, source_recheck=None):
    design = plan["design"]
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    result = {"schema": "butterfly.event-transport-result.v1", "source": source, "design_sha256": design_hash(plan),
              "claim_scope": design["claim_scope"], "started_utc": evidence.utc_now(), "profiles": [],
              "status": "running", "passed": False, "automatic_retry": False, "files": []}
    evidence.write_new_json(output / "started.json", result)
    interrupted = False
    for candidate in candidates:
        for profile in design["profiles"]:
            row = {"candidate_id": candidate["id"], "profile": profile, "passed": False}
            name = candidate["id"] + "-" + profile["name"]
            try:
                if time.monotonic() - started >= design["maximum_wall_seconds"]:
                    raise TimeoutError("cooperative profile-boundary limit")
                parameters = RosslerParameters(**candidate["parameters"])
                config = SolverConfig(**{k: v for k, v in profile.items() if k != "name"})
                seed = candidate["correction"]
                correction = correct_periodic_orbit(parameters, seed["initial_state"], seed["period_time"],
                                                    config=config, **design["correction"])
                row["correction"] = {key: value.tolist() if isinstance(value, np.ndarray) else value
                                     for key, value in asdict(correction).items()}
                result["files"].append(evidence.write_new_json(output / (name + "-correction.json"), row))
                limits = design["acceptance"]
                scaled_correction = float(np.linalg.norm((correction.initial_state - seed["initial_state"]) / design["state_scales"]))
                relative_period = abs(correction.period_time / seed["period_time"] - 1)
                if not (correction.success and correction.optimizer_success
                        and correction.closure_error <= limits["maximum_closure_error"]
                        and correction.phase_residual <= limits["maximum_phase_residual"]
                        and scaled_correction <= limits["maximum_scaled_correction"]
                        and relative_period <= limits["maximum_relative_period_change"]):
                    raise ValueError("periodic correction or source-cycle identity gate failed")
                raw, diagnostic = collect_events(lambda t, y: rossler_rhs(t, y, parameters), correction.initial_state,
                                                correction.period_time, sections(parameters), config, design)
                path = output / (name + ".npz")
                with path.open("xb") as stream:
                    np.savez_compressed(stream, **raw)
                row["raw"] = {"path": path.name, "sha256": evidence.sha256_file(path), "bytes": path.stat().st_size}
                result["files"].append(row["raw"])
                row["integration"] = diagnostic
                row["sections"] = summarize_events(raw, correction.period_time, design)
                row["passed"] = bool(diagnostic["integration_success"] and diagnostic["finite_raw_data"]
                                     and diagnostic["horizon_reached"] and all(r["passed"] for r in row["sections"].values()))
            except (Exception, KeyboardInterrupt) as error:
                row["failure"] = {"type": type(error).__name__, "message": str(error)}
                interrupted = isinstance(error, KeyboardInterrupt)
            result["files"].append(evidence.write_new_json(output / (name + "-result.json"), row))
            result["profiles"].append(row)
            if interrupted:
                break
        if interrupted:
            break
    comparisons = []
    for candidate in candidates:
        rows = [r for r in result["profiles"] if r["candidate_id"] == candidate["id"]]
        for row in rows[1:]:
            passed = False
            detail = {}
            relative = None
            if rows[0]["passed"] and row["passed"]:
                detail = {name: compare_windows(rows[0]["sections"][name]["windows"][0],
                                               row["sections"][name]["windows"][0], design)
                          for name in design["sections"]}
                relative = abs(row["correction"]["period_time"] / rows[0]["correction"]["period_time"] - 1)
                passed = all(r["passed"] for r in detail.values()) and relative <= design["acceptance"]["maximum_cross_profile_relative_period_difference"]
            comparisons.append({"candidate_id": candidate["id"], "reference": rows[0]["profile"]["name"],
                                "profile": row["profile"]["name"], "sections": detail,
                                "relative_period_difference": relative, "passed": bool(passed)})
    result.update(status="interrupted" if interrupted else "completed", comparisons=comparisons,
                  passed=bool(not interrupted and len(result["profiles"]) == len(candidates)*len(design["profiles"])
                              and all(r["passed"] for r in result["profiles"]) and all(r["passed"] for r in comparisons)),
                  elapsed_seconds=time.monotonic()-started, finished_utc=evidence.utc_now())
    try:
        for descriptor in result["files"]:
            evidence.collection_file(output, descriptor)
        if source_recheck is not None:
            source_recheck()
        if time.monotonic()-started >= design["maximum_wall_seconds"]:
            raise TimeoutError("cooperative final wall-time limit")
    except Exception as error:
        result.update(status="failed", passed=False, final_audit_failure={"type": type(error).__name__, "message": str(error)})
    result.update(elapsed_seconds=time.monotonic()-started, finished_utc=evidence.utc_now())
    evidence.write_new_json(output / "receipt.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("preflight", "execute"), default="preflight")
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    plan = json.loads(PLAN.read_bytes())
    if args.mode == "execute":
        execution_gate(plan)
        if args.output_dir is None:
            parser.error("fresh output directory required")
    source = evidence.source_binding(ROOT, args.source_commit, PLAN, PLAN.read_bytes())
    candidates = prepare(plan)
    if args.mode == "preflight":
        print(json.dumps({"prepared": True, "candidate_ids": [c["id"] for c in candidates],
                          "design_sha256": design_hash(plan), "execution_authorized": plan["execution_authorized"]}))
        return 0
    def recheck():
        evidence.source_binding(ROOT, args.source_commit, PLAN, PLAN.read_bytes())
        execution_gate(json.loads(PLAN.read_bytes()))
        prepare(json.loads(PLAN.read_bytes()))
    result = execute(plan, candidates, args.output_dir, source, source_recheck=recheck)
    print(json.dumps({"status": result["status"], "passed": result["passed"]}))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

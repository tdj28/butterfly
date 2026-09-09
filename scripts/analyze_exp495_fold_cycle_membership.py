#!/usr/bin/env python3
"""Frozen saved-state proximity test; default is result-free input preflight."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import platform
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "experiments/manifests/EXP-495-fold-cycle-membership.json"
SOURCES = [
    "scripts/analyze_exp495_fold_cycle_membership.py",
    "scripts/audit_exp495_fold_cycle_membership.py",
    "tests/test_exp495_membership.py",
    "docs/experiments/EXP-495-fold-cycle-membership.md",
    "experiments/manifests/EXP-495-fold-cycle-membership.json",
    "pyproject.toml", "uv.lock",
]


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def write(path, value):
    with path.open("xb") as stream:
        stream.write(encode(value))


def utc():
    return datetime.now(timezone.utc).isoformat()


def expected_ids():
    result = []
    for case in ("local-a025-c083", "local-a027-c083"):
        for region in (0, 1):
            for depth in (4, 8):
                for direction in (0, 1):
                    n = (2 if case == "local-a025-c083" else 1) if region == 0 else (
                        4 if case == "local-a027-c083" and depth == 8 else 1)
                    family = f"{case}--region-{region}--depth-{depth}--direction-{direction}"
                    result.extend(f"{family}--candidate-{i}" for i in range(n))
    return result


def finite_states(value, shape):
    array = np.asarray(value, dtype=float)
    if array.shape != shape or not np.isfinite(array).all():
        raise ValueError("finite state shape differs")
    return array


def validate_inputs(candidates, folds, cycles, plan):
    ids = expected_ids()
    if (plan["experiment_id"] != "EXP-495" or plan["fold_candidates"] != 26
            or plan["methods"] != ["DOP853", "Radau"] or plan["phases"] != [.25, 1.25]
            or plan["scales"] != [15., 15., .01] or plan["cycle_events"] != 6
            or plan["primary_radius"] != 1e-4
            or plan["sensitivity_radii"] != [1e-6, 1e-5, 1e-4, 1e-3]
            or plan["cases"] != ["local-a025-c083", "local-a027-c083"]):
        raise ValueError("frozen analysis constants differ")
    if ([r["id"] for r in candidates] != ids or [r["id"] for r in folds["candidates"]] != ids
            or folds["experiment_id"] != "EXP-490" or folds["status"] != "completed-audited"
            or cycles["experiment_id"] != "EXP-494" or cycles["status"] != "complete-ledger"
            or len(cycles["rows"]) != 66 or cycles["symbolic_chains_verified"] is not False):
        raise ValueError("parent identity or full census differs")
    bases = [r for r in cycles["rows"] if r["spec"]["arm"] == "base"]
    if [r["spec"]["case"] for r in bases] != plan["cases"]:
        raise ValueError("complete ordered base pair required")
    for base, case, a in zip(bases, plan["cases"], [.21575, .21577], strict=True):
        if (base["spec"]["parameters"] != dict(a=a, b=.2, c=7.212)
                or base["spec"]["step"] != 0 or base["status"] != "qualified"
                or base["pair"]["passed"] is not True
                or [p["method"] for p in base["profiles"]] != plan["methods"]):
            raise ValueError("qualified same-parameter paired base required")
        for p in base["profiles"]:
            m = p["metric"]
            if not p["qualified"] or not m["qualified"] or not m["repeat"]["passed"]:
                raise ValueError("unqualified cycle profile")
            if [w["phase"] for w in m["windows"]] != plan["phases"]:
                raise ValueError("complete repeat-window matrix required")
            for w in m["windows"]:
                if (not w["qualified"] or not w["conditional_minimal_period"]
                        or w["counts"] != dict(historical=6, barrio=8)):
                    raise ValueError("primitive six-return cycle required")
                finite_states(w["event_states"]["historical"], (6, 3))
                phases = finite_states(w["event_phases"]["historical"], (6,))
                if not (np.all(np.diff(phases) > 0) and 0 <= phases[0] < phases[-1] < 1):
                    raise ValueError("cycle event phase order differs")
        for c, r in zip(candidates, folds["candidates"], strict=True):
            if c["case"] != case:
                continue
            if (c["parameters"] != base["spec"]["parameters"] or r["case"] != case
                    or c["family_id"] != r["family_id"] or c["region"] != r["region"]
                    or [p["method"] for p in r["solvers"]] != plan["methods"]):
                raise ValueError("fold case, family or method differs")
            if r["qualified_in_region"]:
                if not r["qualified"] or not all(p["qualified"] and p["in_region"] for p in r["solvers"]):
                    raise ValueError("ineligible paired fold")
                for p in r["solvers"]:
                    for key in ("image_state", "next_state"):
                        finite_states(p["observations"][1][key], (3,))
    return bases


def pair_distances(fold_input, fold_output, events, scales):
    events = finite_states(events, (6, 3))
    first = np.abs(events - finite_states(fold_input, (3,)))
    second = np.abs(np.roll(events, -1, axis=0) - finite_states(fold_output, (3,)))
    endpoint = np.stack((first, second), axis=1)
    state = np.max(endpoint / np.asarray(scales), axis=(1, 2))
    x_only = np.max(endpoint[:, :, 0] / scales[0], axis=1)
    return dict(absolute_endpoint_differences=endpoint.tolist(),
                pair_state_distance=state.tolist(), pair_x_distance=x_only.tolist())


def envelope(variants, radii):
    if not variants:
        raise ValueError("empty comparison is not zero distance")
    state = np.max([v["pair_state_distance"] for v in variants], axis=0)
    x_only = np.max([v["pair_x_distance"] for v in variants], axis=0)
    return dict(pair_state_distance=state.tolist(), pair_x_distance=x_only.tolist(),
        minimum_state_distance=float(np.min(state)), minimum_x_distance=float(np.min(x_only)),
        nearest_state_index=int(np.argmin(state)), nearest_x_index=int(np.argmin(x_only)),
        radii=[dict(radius=radius, state_indices=np.flatnonzero(state <= radius).tolist(),
                    x_indices=np.flatnonzero(x_only <= radius).tolist()) for radius in radii])


def analyze(candidates, folds, cycles, plan):
    bases = validate_inputs(candidates, folds, cycles, plan)
    rows = []
    for c, r in zip(candidates, folds["candidates"], strict=True):
        row = dict(id=c["id"], case=c["case"], family_id=c["family_id"], region=c["region"],
            parameters=c["parameters"], parent_qualified=r["qualified"],
            parent_in_region=r["qualified_in_region"], parent_solver_outcomes=r["solvers"],
            status="not-evaluated-parent-ineligible", variants=[], envelope=None)
        if r["qualified_in_region"]:
            base = next(b for b in bases if b["spec"]["case"] == c["case"])
            for fold, cycle in zip(r["solvers"], base["profiles"], strict=True):
                o = fold["observations"][1]
                for w in cycle["metric"]["windows"]:
                    events = w["event_states"]["historical"]
                    row["variants"].append(dict(method=fold["method"], phase=w["phase"],
                        fold_input=o["image_state"], fold_output=o["next_state"], cycle_events=events,
                        **pair_distances(o["image_state"], o["next_state"], events, plan["scales"])))
            row["envelope"] = envelope(row["variants"], plan["sensitivity_radii"])
            row["status"] = ("proximate-at-primary-radius" if row["envelope"]["minimum_state_distance"]
                             <= plan["primary_radius"] else "not-proximate-at-primary-radius")
        rows.append(row)
    cases = []
    for case in plan["cases"]:
        eligible = [r for r in rows if r["case"] == case and r["region"] == 1 and r["envelope"] is not None]
        families = sorted({r["family_id"] for r in eligible})
        required = sorted(f"{case}--region-1--depth-{d}--direction-{v}" for d in (4, 8) for v in (0, 1))
        e = envelope([r["envelope"] for r in eligible], plan["sensitivity_radii"]) if eligible else None
        complete = families == required
        status = "incomplete-fold-representation" if not complete else (
            "proximate-at-primary-radius" if e["minimum_state_distance"] <= plan["primary_radius"]
            else "not-proximate-at-primary-radius")
        cases.append(dict(case=case, eligible_candidates=[r["id"] for r in eligible],
                          families=families, complete=complete, envelope=e, status=status))
    return dict(experiment_id="EXP-495", rows=rows, cases=cases, new_integrations=0,
                symbolic_chains_verified=False, exact_critical_membership_verified=False)


def load_inputs():
    p = json.loads(PLAN.read_bytes())
    values = []
    for name, digest in p["inputs"].items():
        path = ROOT / name
        if sha256(path) != digest:
            raise ValueError("upstream input hash differs: " + name)
        raw = path.read_bytes()
        values.append(json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw))
    candidates, folds, cycles, receipt = values
    if (not receipt["passed"] or receipt["summary_sha256"] != hashlib.sha256(
            gzip.decompress((ROOT / list(p["inputs"])[2]).read_bytes())).hexdigest()
            or receipt["source_commit"] != cycles["source_commit"]):
        raise ValueError("upstream periodic audit binding differs")
    validate_inputs(candidates, folds, cycles, p)
    return p, candidates, folds, cycles


def execute(output, source_commit, remote_ref):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    p, candidates, folds, cycles = load_inputs()
    if (git("rev-parse", "HEAD") != source_commit or git("status", "--porcelain")
            or git("ls-remote", "origin", remote_ref).split() != [source_commit, remote_ref]):
        raise ValueError("clean exact pushed freeze required")
    binding = dict(source_commit=source_commit, remote_ref=remote_ref, started_utc=utc(),
        plan_sha256=sha256(PLAN), sources={s: sha256(ROOT/s) for s in SOURCES},
        inputs=p["inputs"], python=platform.python_version(), numpy=np.__version__, paid_review=p["paid_review"])
    output.mkdir(parents=True, exist_ok=False)
    marker = ROOT / "artifacts/EXP-495/analysis-once.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    write(marker, binding)
    write(output / "binding.json", binding)
    try:
        result = analyze(candidates, folds, cycles, p)
        result.update(binding=binding, completed_utc=utc())
        if len(encode(result)) > p["maximum_output_bytes"]:
            raise ValueError("bounded result size exceeded")
        write(output / "result.json", result)
    except BaseException as exc:
        write(output / "failure.json", dict(error=type(exc).__name__, message=str(exc), time_utc=utc()))
        raise
    print(json.dumps(dict(completed=True, rows=len(result["rows"]), output_sha256=sha256(output/"result.json"))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--source-commit")
    parser.add_argument("--remote-ref")
    args = parser.parse_args()
    if args.execute:
        if not all((args.output_dir, args.source_commit, args.remote_ref)):
            parser.error("execution requires output directory, source commit and remote ref")
        execute(args.output_dir, args.source_commit, args.remote_ref)
    else:
        p, candidates, _, _ = load_inputs()
        print(json.dumps(dict(input_preflight_passed=True, candidates=len(candidates),
                              plan_sha256=sha256(PLAN), new_distances_measured=False)))


if __name__ == "__main__":
    main()

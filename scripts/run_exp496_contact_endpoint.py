#!/usr/bin/env python3
"""Bounded lower-a fold endpoint, reusing frozen numerical qualification."""
import argparse
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

import numpy as np
import scipy
from butterfly._paired_startup import inventory, sha256, write_json
from butterfly.models import RosslerParameters, rossler_rhs, rossler_jacobian
from butterfly.poincare import legacy_rossler_section
from butterfly.projected_fold_qualification import compare
from scripts import run_exp490_direct_folds as fold_run
from scripts import analyze_exp495_fold_cycle_membership as membership

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "experiments/manifests/EXP-496-contact-endpoint.json"
INPUT = ROOT / "experiments/manifests/EXP-496-candidates.json"
NUMERIC_KEYS = ("solvers", "rtol", "atol", "max_step", "iterations", "root_plane",
                "root_determinant", "guard", "extremum_margin", "scales", "thresholds", "controls")
EXPLICIT_SOURCES = [
    "scripts/run_exp496_contact_endpoint.py", "scripts/audit_exp496_contact_endpoint.py",
    "tests/test_exp496_contact_endpoint.py", "docs/experiments/EXP-496-contact-endpoint.md",
    "experiments/manifests/EXP-496-contact-endpoint.json",
    "experiments/manifests/EXP-496-candidates.json", "experiments/manifests/EXP-490-direct-folds.json",
    *fold_run.SOURCES, *membership.SOURCES,
]


def imported_sources():
    paths = set()
    for module in list(sys.modules.values()):
        path = getattr(module, "__file__", None)
        if path:
            path = Path(path).resolve()
            if path.is_relative_to(ROOT) and path.suffix == ".py":
                relative = path.relative_to(ROOT).as_posix()
                if relative.startswith(("python/", "scripts/")):
                    paths.add(relative)
    return paths


def cycle_node(cycles, case, lower):
    rows = [r for r in cycles["rows"] if r["spec"]["case"] == case
            and r["spec"]["arm"] == ("a-" if lower else "base")
            and r["spec"]["step"] == (3 if lower else 0)]
    if len(rows) != 1:
        raise ValueError("unique fixed cycle endpoint required")
    r = rows[0]
    if (r["status"] != "qualified" or not r["pair"]["passed"]
            or [p["method"] for p in r["profiles"]] != ["DOP853", "Radau"]):
        raise ValueError("unqualified paired endpoint")
    for p in r["profiles"]:
        m = p["metric"]
        if not (p["qualified"] and p["correction_gate"]["passed"]
                and m["qualified"] and m["repeat"]["passed"]):
            raise ValueError("endpoint profile gates failed")
        if [w["phase"] for w in m["windows"]] != [.25, 1.25]:
            raise ValueError("complete fixed repeat windows required")
        for w in m["windows"]:
            if not (w["qualified"] and w["conditional_minimal_period"]
                    and w["counts"] == dict(historical=6, barrio=8)):
                raise ValueError("endpoint is not qualified primitive six/eight")
            membership.finite_states(w["event_states"]["historical"], (6, 3))
            phases = membership.finite_states(w["event_phases"]["historical"], (6,))
            if not (np.all(np.diff(phases) > 0) and 0 <= phases[0] < phases[-1] < 1):
                raise ValueError("endpoint event order differs")
    return r


def build_inputs(candidates, folds, cycles):
    selected, ledger, seen = [], [], set()
    for c, f in zip(candidates, folds["candidates"], strict=True):
        if c["id"] != f["id"]:
            raise ValueError("parent order differs")
        status = "not-evaluated-parent-ineligible"
        if f["qualified_in_region"] and c["region"] == 1:
            status = "not-selected-duplicate-representation"
            if c["family_id"] not in seen:
                status = "selected"
                seen.add(c["family_id"])
                lower = cycle_node(cycles, c["case"], True)
                cycle_node(cycles, c["case"], False)
                new = deepcopy(c)
                new["parameters"] = deepcopy(lower["spec"]["parameters"])
                new["initial_state"][1] = legacy_rossler_section(
                    RosslerParameters(**new["parameters"])).offset
                new["seed_u"] = float(np.mean([r["root"]["u"] for r in f["solvers"]]))
                new["seed_time"] = float(np.mean([r["root"]["time"] for r in f["solvers"]]))
                new.update(u_box=[new["seed_u"]-.02, new["seed_u"]+.02],
                    time_box=[new["seed_time"]-1., new["seed_time"]+1.],
                    horizon=new["seed_time"]+3., epsilon=1e-6,
                    lower_cycle_id=lower["spec"]["id"], parent_parameters=c["parameters"])
                selected.append(new)
        ledger.append(dict(id=c["id"], family_id=c["family_id"], case=c["case"],
                           parent_qualified_in_region=f["qualified_in_region"], status=status))
    required = {f"{case}--region-1--depth-{d}--direction-{v}"
                for case in ("local-a025-c083", "local-a027-c083") for d in (4, 8) for v in (0, 1)}
    if (len(ledger) != 26 or seen != required or len(selected) != 8
            or sum(r["status"] == "not-selected-duplicate-representation" for r in ledger) != 2):
        raise ValueError("fixed parent/representative census differs")
    return dict(experiment_id="EXP-496", ledger=ledger, candidates=selected)


def prepare():
    # Import the auditor before capturing the static project-source closure.
    from scripts import audit_exp496_contact_endpoint  # noqa: F401
    old, candidates, folds, cycles = membership.load_inputs()
    data = build_inputs(candidates, folds, cycles)
    numeric = json.loads(fold_run.PLAN.read_bytes())
    p = dict(experiment_id="EXP-496", **{k: numeric[k] for k in NUMERIC_KEYS},
        inputs={**old["inputs"], "experiments/manifests/EXP-490-direct-folds.json": sha256(fold_run.PLAN)},
        primary_event=3, sign_floor=1e-6, primary_radius=1e-4,
        sensitivity_radii=[1e-6, 1e-5, 1e-4, 1e-3],
        limits=dict(max_target_trajectories=176, wall_seconds=3600, output_bytes=2*1024**3,
                    initial_free_bytes=16*1024**3, minimum_free_bytes=8*1024**3),
        paid_review="not-run-human-approval-policy",
        source_paths=sorted(set(EXPLICIT_SOURCES) | imported_sources()))
    write_json(INPUT, data)
    p["candidates_sha256"] = sha256(INPUT)
    write_json(PLAN, p)
    print(json.dumps(dict(prepared=True, candidates=8, ledger=26, new_target_integrations=0)))


def load_inputs():
    p = json.loads(PLAN.read_bytes())
    old, candidates, folds, cycles = membership.load_inputs()
    numeric = json.loads(fold_run.PLAN.read_bytes())
    if (p["experiment_id"] != "EXP-496" or any(p[k] != numeric[k] for k in NUMERIC_KEYS)
            or p["primary_event"] != 3 or p["sign_floor"] != 1e-6 or p["primary_radius"] != 1e-4
            or p["sensitivity_radii"] != [1e-6, 1e-5, 1e-4, 1e-3]
            or p["limits"] != dict(max_target_trajectories=176, wall_seconds=3600,
                output_bytes=2*1024**3, initial_free_bytes=16*1024**3, minimum_free_bytes=8*1024**3)
            or p["inputs"] != {**old["inputs"], "experiments/manifests/EXP-490-direct-folds.json": sha256(fold_run.PLAN)}
            or any(sha256(ROOT/name) != digest for name, digest in p["inputs"].items())
            or sha256(INPUT) != p["candidates_sha256"]
            or not set(EXPLICIT_SOURCES) <= set(p["source_paths"])):
        raise ValueError("frozen plan/input/source closure differs")
    data = json.loads(INPUT.read_bytes())
    if data != build_inputs(candidates, folds, cycles):
        raise ValueError("deterministic successor inputs differ")
    return p, data, folds, cycles


def representation_status(variants, p):
    if len(variants) != 4:
        raise ValueError("complete solver/window comparison required")
    if all(v["pair_state_distance"][p["primary_event"]] <= p["primary_radius"] for v in variants):
        return "endpoint-proximate"
    if all(v["opposite_sign_resolved"] for v in variants):
        return "opposite-sign-endpoints"
    return "no-qualified-bracket"


def contact_analysis(results, data, folds, cycles, p):
    if [r["id"] for r in results] != [c["id"] for c in data["candidates"]]:
        raise ValueError("complete ordered lower-fold matrix required")
    rows = []
    for c, lower_fold in zip(data["candidates"], results, strict=True):
        row = dict(id=c["id"], case=c["case"], family_id=c["family_id"],
                   status="unresolved-fold", variants=[], envelope=None)
        if lower_fold["qualified_in_region"]:
            upper_fold = next(r for r in folds["candidates"] if r["id"] == c["id"])
            upper_cycle = cycle_node(cycles, c["case"], False)
            lower_cycle = cycle_node(cycles, c["case"], True)
            for method in p["solvers"]:
                upper = next(s for s in upper_fold["solvers"] if s["method"] == method)["observations"][1]
                lower = next(s for s in lower_fold["solvers"] if s["method"] == method)["observations"][1]
                uw = next(s for s in upper_cycle["profiles"] if s["method"] == method)["metric"]["windows"]
                lw = next(s for s in lower_cycle["profiles"] if s["method"] == method)["metric"]["windows"]
                for a, b in zip(uw, lw, strict=True):
                    r0 = (a["event_states"]["historical"][3][0]-upper["image_state"][0])/15.
                    r1 = (b["event_states"]["historical"][3][0]-lower["image_state"][0])/15.
                    row["variants"].append(dict(method=method, phase=b["phase"],
                        upper_signed_residual=r0, lower_signed_residual=r1,
                        opposite_sign_resolved=bool(r0*r1 < 0 and min(abs(r0), abs(r1)) >= p["sign_floor"]),
                        fold_input=lower["image_state"], fold_output=lower["next_state"],
                        cycle_events=b["event_states"]["historical"],
                        **membership.pair_distances(lower["image_state"], lower["next_state"],
                                                   b["event_states"]["historical"], p["scales"])))
            row["envelope"] = membership.envelope(row["variants"], p["sensitivity_radii"])
            row["status"] = representation_status(row["variants"], p)
        rows.append(row)
    cases = []
    for case in ("local-a025-c083", "local-a027-c083"):
        selected = [r for r in rows if r["case"] == case]
        statuses = {r["status"] for r in selected}
        status = next(iter(statuses)) if len(statuses) == 1 else "mixed-representation-results"
        cases.append(dict(case=case, status=status, representations=[r["id"] for r in selected]))
    return dict(rows=rows, cases=cases, symbolic_chains_verified=False,
                exact_contact_verified=False, continuity_verified=False, new_periodic_integrations=0)


def execute(output, source, remote_ref):
    from scripts import audit_exp496_contact_endpoint  # noqa: F401
    p, data, folds, cycles = load_inputs()
    if not imported_sources() <= set(p["source_paths"]):
        raise ValueError("execution import closure exceeds frozen sources")
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    if (git("rev-parse", "HEAD") != source or git("status", "--porcelain")
            or git("ls-remote", "origin", remote_ref).split() != [source, remote_ref]):
        raise ValueError("clean exact live pushed freeze required")
    output = output.resolve()
    if ROOT/"artifacts/EXP-496" not in output.parents:
        raise ValueError("fresh EXP-496 output required")
    if shutil.disk_usage(ROOT).free < p["limits"]["initial_free_bytes"]:
        raise ValueError("initial free-space reserve insufficient")
    marker = ROOT/"artifacts/EXP-496/target-once.json"
    if marker.exists():
        raise ValueError("target attempt already consumed")
    output.mkdir(parents=True, exist_ok=False)
    binding = dict(source_commit=source, remote_ref=remote_ref, started_utc=membership.utc(),
        plan_sha256=sha256(PLAN), candidates_sha256=sha256(INPUT), inputs=p["inputs"],
        sources={s: sha256(ROOT/s) for s in p["source_paths"]},
        runtime=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__),
        paid_review=p["paid_review"])
    write_json(output/"binding.json", binding)
    calls = bytes_written = 0
    started = time.monotonic()
    def timeout(*_):
        raise TimeoutError("EXP-496 wall limit")
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(p["limits"]["wall_seconds"])
    try:
        controls = fold_run.controls(p)
        write_json(output/"controls.json", controls)
        if not all(r["passed"] for r in controls):
            raise ValueError("analytic controls failed; no targets")
        write_json(marker, binding)
        results = []
        for c in data["candidates"]:
            par = RosslerParameters(**c["parameters"])
            rhs = lambda t, q: rossler_rhs(t, q, par)
            jac = lambda t, q: rossler_jacobian(q, par)
            hvv = lambda t, q, v: np.array([0., 0., 2*v[0]*v[2]])
            section = replace(legacy_rossler_section(par), direction=-1)
            rows = []
            for method in p["solvers"]:
                label = c["id"]+"--"+method
                write_json(output/(label+"-started.json"), dict(candidate_id=c["id"],
                    method=method, started_utc=membership.utc()))
                def retain(suffix, raw):
                    nonlocal calls, bytes_written
                    if (calls >= p["limits"]["max_target_trajectories"]
                            or bytes_written > p["limits"]["output_bytes"]-33554432
                            or shutil.disk_usage(ROOT).free < p["limits"]["minimum_free_bytes"]):
                        raise RuntimeError("trajectory/storage reserve reached")
                    path = output/f"{label}--{suffix}.npz"
                    with path.open("xb") as stream:
                        np.savez_compressed(stream, **raw)
                    calls += 1
                    bytes_written += path.stat().st_size
                row = fold_run.run_candidate(c, method, p, rhs, jac, hvv, section, retain)
                write_json(output/(label+".json"), row)
                bytes_written += (output/(label+".json")).stat().st_size
                rows.append(row)
                print(label+": completed", flush=True)
            results.append(compare(c, rows, p))
        write_json(output/"summary.json", dict(experiment_id="EXP-496", status="completed",
            binding=binding, ledger=data["ledger"], candidates=results,
            contact=contact_analysis(results, data, folds, cycles, p), target_trajectories=calls,
            elapsed_seconds=time.monotonic()-started, completed_utc=membership.utc(),
            files=inventory(output), marker_sha256=sha256(marker)))
        print(json.dumps(dict(completed=True, profiles=16, target_trajectories=calls,
                             summary_sha256=sha256(output/"summary.json"))), flush=True)
    except BaseException as exc:
        write_json(output/"failure.json", dict(error_type=type(exc).__name__, message=str(exc),
            utc=membership.utc(), target_trajectories=calls, files=inventory(output)))
        raise
    finally:
        signal.alarm(0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--source-commit")
    parser.add_argument("--remote-ref")
    a = parser.parse_args()
    if a.prepare and a.execute:
        parser.error("prepare and execute are separate")
    if a.prepare:
        prepare()
    elif a.execute:
        if not all((a.output_dir, a.source_commit, a.remote_ref)):
            parser.error("execution needs output, source commit and remote ref")
        execute(a.output_dir, a.source_commit, a.remote_ref)
    else:
        from scripts import audit_exp496_contact_endpoint  # noqa: F401
        _, data, _, _ = load_inputs()
        print(json.dumps(dict(preflight=True, ledger=len(data["ledger"]),
                              candidates=len(data["candidates"]), target_integrations=0)))


if __name__ == "__main__":
    main()

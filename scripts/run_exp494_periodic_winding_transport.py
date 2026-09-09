#!/usr/bin/env python3
"""Frozen local periodic-family pilot; no paid services or symbolic labels."""
import argparse
from dataclasses import asdict, replace
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from unittest.mock import patch

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
from butterfly import periodic
from butterfly._paired_startup import sha256, write_json
from butterfly.integrate import SolverConfig
from butterfly.models import RosslerParameters, rossler_rhs, rossler_equilibria
from butterfly.poincare import PoincareSection, legacy_rossler_section, barrio_rossler_section
from butterfly import periodic_winding as geometry

PLAN = ROOT/"experiments/manifests/EXP-494-periodic-winding-transport.json"
PARENT = ROOT/"artifacts/EXP-480/run-5b584f4"
SOURCES = ("scripts/run_exp494_periodic_winding_transport.py", "python/butterfly/periodic_winding.py",
    "scripts/audit_exp494_periodic_winding_transport.py",
    "python/butterfly/projected_winding.py", "python/butterfly/periodic.py", "python/butterfly/models.py",
    "python/butterfly/poincare.py", "python/butterfly/integrate.py", "python/butterfly/_paired_startup.py",
    "tests/test_periodic_winding.py", "tests/test_exp494_transport.py",
    "docs/experiments/EXP-494-periodic-winding-transport.md", "pyproject.toml", "uv.lock")


def utc():
    return datetime.now(timezone.utc).isoformat()


def load_plan():
    p = json.loads(PLAN.read_bytes())
    constants = dict(rtol=1e-12, atol=1e-14, max_step=.01, max_evaluations=30, correction_tolerance=1e-11,
        maximum_closure_error=1e-9, maximum_phase_residual=1e-10, maximum_scaled_step=.25,
        maximum_relative_period_step=.05, maximum_paired_relative_period=1e-7,
        maximum_paired_scaled_state=1e-6, maximum_seconds=7200, maximum_ivps=6000,
        maximum_output_bytes=8589934592, initial_free_bytes=17179869184, minimum_free_bytes=8589934592)
    if (p["experiment_id"] != "EXP-494" or p["cases"] != ["local-a025-c083", "local-a027-c083"]
            or any(p[k] != v for k,v in constants.items())
            or p["methods"] != ["DOP853", "Radau"] or p["steps"] != 8
            or p["increments"] != dict(a=.0001, c=.002)
            or p["parent_receipt_sha256"] != "aa4556cdfbca2fa277c8e77daec00f01190e0a8bfde33d9977e5a594c58127b9"):
        raise ValueError("wrong fixed study/input/grid")
    return p


def grid(p):
    result = []
    for case in p["cases"]:
        parameters = dict(a=.21575 if case == "local-a025-c083" else .21577, b=.2, c=7.212)
        result.append(dict(id=case+"--base", case=case, arm="base", step=0, parameters=parameters.copy()))
        for axis in ("a", "c"):
            for sign in (-1, 1):
                arm = axis+("-" if sign < 0 else "+")
                for step in range(1, p["steps"]+1):
                    par = parameters.copy()
                    par[axis] += sign*step*p["increments"][axis]
                    result.append(dict(id=f"{case}--{axis}{'minus' if sign < 0 else 'plus'}--{step:02d}",
                                       case=case, arm=arm, step=step, parameters=par))
    return result


def parent_inputs(p):
    if sha256(PARENT/"receipt.json") != p["parent_receipt_sha256"]:
        raise ValueError("parent receipt changed")
    receipt = json.loads((PARENT/"receipt.json").read_bytes())
    for f in receipt["files"]:
        name = f["path"]
        if Path(name).name != name or (PARENT/name).is_symlink():
            raise ValueError("unsafe parent path")
        if (PARENT/name).stat().st_size != f["bytes"] or sha256(PARENT/name) != f["sha256"]:
            raise ValueError("parent raw inventory differs")
    expected = [(c, s) for c in p["cases"] for s in ("dop853", "dop853-refined", "radau", "radau-refined")]
    if [(r["candidate_id"], r["profile"]["name"]) for r in receipt["profiles"]] != expected or receipt["passed"] is not True:
        raise ValueError("complete qualified eight-profile input required")
    return receipt


def saved_profiles(receipt, p):
    results = []
    for row in receipt["profiles"]:
        par = RosslerParameters(.21575 if row["candidate_id"] == p["cases"][0] else .21577, .2, 7.212)
        field = lambda t, q: rossler_rhs(t, q, par)
        with np.load(PARENT/row["raw"]["path"], allow_pickle=False) as raw:
            events, extrema = {}, []
            for name, old in (("historical", "historical-negative"), ("barrio", "barrio-positive")):
                events[name] = [dict(time=float(t), state=q.tolist(), angle=float(angle), accepted=bool(accepted))
                    for t, q, angle, accepted in zip(raw[old+"_times"], raw[old+"_states"], raw[old+"_angles"], raw[old+"_accepted"], strict=True)]
                extrema += [dict(time=float(t), state=q.tolist()) for t, q in zip(raw[old+"_extremum_times"], raw[old+"_extremum_states"], strict=True)]
            metric = geometry.measure_cycle(raw["integration_times"], raw["integration_states"], extrema,
                events, row["correction"]["period_time"], rossler_equilibria(par)[0], field)
        results.append(dict(case=row["candidate_id"], profile=row["profile"]["name"],
                            period=row["correction"]["period_time"], raw=row["raw"], metric=metric))
    return results


def correction_gate(c, seed, p):
    step = float(np.linalg.norm((np.array(c["initial_state"])-seed["initial_state"])/geometry.SCALES))
    change = abs(c["period_time"]/seed["period_time"]-1)
    good = (c["success"] and c["optimizer_success"] and c["closure_error"] <= p["maximum_closure_error"]
            and c["phase_residual"] <= p["maximum_phase_residual"]
            and step <= p["maximum_scaled_step"] and change <= p["maximum_relative_period_step"])
    return dict(passed=bool(good), scaled_step=step, relative_period_step=change)


def compare_profiles(rows, p):
    if len(rows) != 2 or [r["method"] for r in rows] != p["methods"]:
        raise ValueError("exact ordered solver pair required")
    if not all(r["qualified"] for r in rows):
        return dict(passed=False, reason="one or both complete profiles unqualified")
    a, b = rows
    ca, cb = a["correction"], b["correction"]
    state = float(np.linalg.norm((np.array(ca["initial_state"])-cb["initial_state"])/geometry.SCALES))
    period = abs(ca["period_time"]/cb["period_time"]-1)
    windows = [geometry.compare_windows(x, y) for x, y in zip(a["metric"]["windows"], b["metric"]["windows"], strict=True)]
    return dict(passed=bool(state <= p["maximum_paired_scaled_state"] and period <= p["maximum_paired_relative_period"]
                           and all(w["passed"] for w in windows)),
                scaled_initial_error=state, relative_period_error=period, windows=windows)


class BudgetStop(RuntimeError):
    pass


def controls(output):
    """Exact one-/two-traversal circles through the production observer."""
    rows = []
    for method in ("DOP853", "Radau"):
        for multiplicity in (1, 2):
            field = lambda t,q: np.array([-q[1], q[0], 0.])
            sections = dict(historical=PoincareSection((0.,1.,0.),0.,-1,0,0.),
                            barrio=PoincareSection((1.,0.,0.),0.,1))
            name = f"control-{method}-{multiplicity}.npz"
            def keep(raw):
                with (output/name).open("xb") as stream:
                    np.savez_compressed(stream, **raw)
            period = 2*np.pi*multiplicity
            raw, report = geometry.observe(field, [np.cos(.2),np.sin(.2),0.], period, sections,
                dict(method=method,rtol=1e-12,atol=1e-14,max_step=.01), keep)
            metric = geometry.measure_cycle(raw["times"], raw["states"], report["extrema"], report["events"], period, np.zeros(3), field)
            passed = (metric["qualified"] == (multiplicity == 1) and metric["repeat"]["passed"]
                and not report["uncertain_extrema"] and all(w["counts"] == dict(historical=multiplicity,barrio=multiplicity)
                and abs(w["geometry"]["midpoint_enriched"]["angle_change"]-2*np.pi*multiplicity) < 1e-10
                for w in metric["windows"]))
            rows.append(dict(method=method, multiplicity=multiplicity, passed=bool(passed), metric=metric,
                             raw=dict(path=name,sha256=sha256(output/name))))
    result = dict(passed=all(r["passed"] for r in rows), rows=rows, control_ivps=4)
    write_json(output/"controls.json", result)
    if not result["passed"]:
        raise ValueError("known-orbit production controls failed")
    return result


def run_profile(spec, method, seed, p, output, budget):
    prefix = spec["id"]+"--"+method
    row = dict(method=method, qualified=False, raw_files=[])
    write_json(output/(prefix+"--started.json"), dict(spec=spec, method=method, seed=seed, utc=utc()))
    par = RosslerParameters(**spec["parameters"])
    config = dict(method=method, **{k:p[k] for k in ("rtol", "atol", "max_step")})
    original = periodic.solve_ivp
    def keep(name, raw):
        budget(False)
        with (output/name).open("xb") as stream:
            np.savez_compressed(stream, **raw)
        row["raw_files"].append(name)
    def retained_ivp(*args, **kwargs):
        budget(True)
        sol = original(*args, **kwargs)
        name = prefix+f"--shooting-{len(row['raw_files']):02d}.npz"
        keep(name, dict(times=sol.t, augmented_states=sol.y.T,
                        success=np.array(sol.success), nfev=np.array(sol.nfev)))
        return sol
    try:
        with patch.object(periodic, "solve_ivp", retained_ivp):
            result = periodic.correct_periodic_orbit(par, seed["initial_state"], seed["period_time"],
                config=SolverConfig(**config), max_evaluations=p["max_evaluations"], tolerance=p["correction_tolerance"])
        row["correction"] = {k:v.tolist() if isinstance(v, np.ndarray) else v for k,v in asdict(result).items()}
        row["correction_gate"] = correction_gate(row["correction"], seed, p)
        write_json(output/(prefix+"--correction.json"), row)
        if row["correction_gate"]["passed"]:
            field = lambda t, q: rossler_rhs(t, q, par)
            sections = dict(historical=replace(legacy_rossler_section(par), direction=-1), barrio=barrio_rossler_section(par))
            budget(True)
            raw, report = geometry.observe(field, result.initial_state, result.period_time, sections, config,
                                          lambda raw: keep(prefix+"--observation.npz", raw))
            row["observation"] = report
            row["metric"] = geometry.measure_cycle(raw["times"], raw["states"], report["extrema"], report["events"],
                                                   result.period_time, rossler_equilibria(par)[0], field)
            row["qualified"] = bool(row["metric"]["qualified"] and not report["uncertain_extrema"]
                                    and report["maximum_event_residual"] <= 1e-8)
    except BudgetStop:
        write_json(output/(prefix+"--interrupted.json"), dict(row, error="operational budget interruption", utc=utc()))
        raise
    except Exception as error:
        row["error"] = type(error).__name__+": "+str(error)
    write_json(output/(prefix+"--result.json"), row)
    return row


def campaign(p, parents, execute):
    """Complete deterministic ledger; failed arms never supply later seeds."""
    rows, seeds, bases = [], {}, {}
    interrupted = None
    for spec in grid(p):
        key = (spec["case"], spec["arm"])
        if spec["step"] == 0:
            seed = next(r["correction"] for r in parents["profiles"] if r["candidate_id"] == spec["case"] and r["profile"]["name"] == "dop853-refined")
        elif spec["step"] == 1:
            seed = bases.get(spec["case"])
        else:
            seed = seeds.get(key)
        row = dict(spec=spec, profiles=[], status="not-run", pair=None)
        if interrupted is not None:
            row["reason"] = interrupted
        elif seed is None:
            row["reason"] = "base or preceding paired node unqualified"
        else:
            try:
                for method in p["methods"]:
                    row["profiles"].append(execute(spec, method, seed))
                row["pair"] = compare_profiles(row["profiles"], p)
                row["status"] = "qualified" if row["pair"]["passed"] else "unqualified"
            except BudgetStop as error:
                interrupted = str(error)
                row["status"], row["reason"] = "interrupted", interrupted
        next_seed = row["profiles"][0]["correction"] if row["status"] == "qualified" else None
        if spec["step"] == 0:
            bases[spec["case"]] = next_seed
        else:
            seeds[key] = next_seed
        rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    p = load_plan()
    if args.controls_only:
        args.output_dir.mkdir(parents=True, exist_ok=False)
        result = controls(args.output_dir)
        print(json.dumps(dict(passed=result["passed"], control_ivps=result["control_ivps"])))
        return
    if subprocess.check_output(["git", "status", "--porcelain"], text=True).strip():
        parser.error("clean frozen worktree required")
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/"+branch], text=True).split()
    if not remote or remote[0] != source or shutil.disk_usage(ROOT).free < p["initial_free_bytes"]:
        parser.error("live pushed source and initial disk reserve required")
    output = args.output_dir.resolve()
    if ROOT/"artifacts/EXP-494" not in output.parents:
        parser.error("fresh EXP-494 namespace required")
    parents = parent_inputs(p)  # hashes/schema only, before new geometry
    output.mkdir(parents=True, exist_ok=False)
    binding = dict(source_commit=source, started_utc=utc(), plan_sha256=sha256(PLAN),
        sources={s:sha256(ROOT/s) for s in SOURCES}, parent_receipt_sha256=p["parent_receipt_sha256"],
        runtime=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__))
    write_json(output/"binding.json", binding)
    controls(output)  # authentic control consumer before attempt/outcome access
    write_json(ROOT/"artifacts/EXP-494/target-once.json", dict(source_commit=source, started_utc=utc()))
    begin = time.monotonic()
    ivps = 0
    def budget(integration):
        nonlocal ivps
        if (time.monotonic()-begin >= p["maximum_seconds"] or (integration and ivps >= p["maximum_ivps"])
                or shutil.disk_usage(ROOT).free < p["minimum_free_bytes"]+33554432
                or sum(f.stat().st_size for f in output.iterdir()) > p["maximum_output_bytes"]-33554432):
            raise BudgetStop("fixed operational limit reached")
        if integration:
            ivps += 1
    def deadline(*_):
        raise BudgetStop("whole-run wall deadline")
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(p["maximum_seconds"])
    try:
        saved = saved_profiles(parents, p)
        write_json(output/"saved-cycle-metrics.json", saved)
        def execute(spec, method, seed):
            print(json.dumps(dict(id=spec["id"], method=method, phase="starting", ivps=ivps)), flush=True)
            return run_profile(spec, method, seed, p, output, budget)
        rows = campaign(p, parents, execute)
        result = dict(experiment_id="EXP-494", source_commit=source, completed_utc=utc(),
            status="complete-ledger", rows=rows, saved_profiles=saved, ivps=ivps,
            elapsed_seconds=time.monotonic()-begin, paid_calls=0,
            files={f.name:dict(bytes=f.stat().st_size, sha256=sha256(f)) for f in sorted(output.iterdir())},
            symbolic_chains_verified=False)
        if binding["sources"] != {s:sha256(ROOT/s) for s in SOURCES} or binding["plan_sha256"] != sha256(PLAN):
            raise ValueError("source changed during execution")
        write_json(output/"summary.json", result)
        print(json.dumps(dict(status=result["status"], rows=len(rows), ivps=ivps)), flush=True)
    except BaseException as error:
        write_json(output/"failure.json", dict(type=type(error).__name__, error=str(error), utc=utc(), ivps=ivps))
        raise
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()

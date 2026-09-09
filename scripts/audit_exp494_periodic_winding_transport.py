#!/usr/bin/env python3
"""Hash, full-grid and coefficient-level EXP-494 replay; no integrations."""
import argparse
from dataclasses import replace
import json
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from scripts import run_exp494_periodic_winding_transport as run


def numeric_equal(a, b):
    if isinstance(a, dict):
        return isinstance(b, dict) and a.keys() == b.keys() and all(numeric_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return isinstance(b, list) and len(a) == len(b) and all(numeric_equal(x,y) for x,y in zip(a,b,strict=True))
    if isinstance(a, float):
        return isinstance(b, (float, int)) and not isinstance(b, bool) and bool(np.isclose(a,b,rtol=1e-12,atol=1e-13))
    return type(a) is type(b) and a == b


def audit_observation(raw, report, par, method, period):
    """Rebuild roots from the retained interpolant, not reported root states."""
    field = lambda t,q: run.rossler_rhs(t,q,par)
    sections = dict(historical=replace(run.legacy_rossler_section(par),direction=-1),
                    barrio=run.barrio_rossler_section(par))
    dense = lambda t:run.geometry.dense_value(raw,method,t)
    extrema = []
    for name, section in sections.items():
        et = raw[name+"_extrema_times"]
        eq = raw[name+"_extrema_states"]
        knots = np.unique(np.r_[0.,et,period*2.5])
        roots = []
        for left,right in zip(knots[:-1],knots[1:],strict=True):
            if section.value(dense(left))*section.value(dense(right)) < 0:
                roots.append(brentq(lambda t:section.value(dense(t)),left,right,xtol=1e-12,rtol=1e-14))
        if len(roots) != len(report["events"][name]):
            raise ValueError("coefficient-replayed event count differs")
        for t,e in zip(roots,report["events"][name],strict=True):
            q = dense(t)
            f = field(t,q)
            velocity = float(np.dot(section.normal,f))
            accepted = bool(section.accepts(q) and section.direction*velocity > 0)
            if (abs(t-e["time"]) > 1e-9 or np.linalg.norm((q-e["state"])/run.geometry.SCALES) > 1e-8
                    or accepted is not e["accepted"] or abs(section.value(q)) > 1e-8):
                raise ValueError("coefficient-replayed event state/time/membership differs")
        for t,q in zip(et,eq,strict=True):
            if np.linalg.norm((dense(t)-q)/run.geometry.SCALES) > 1e-8:
                raise ValueError("retained extremum differs from dense coefficients")
            extrema.append(dict(time=float(t),state=q.tolist(),section=name,plane_value=float(section.value(q))))
    if not numeric_equal(extrema,report["extrema"]):
        raise ValueError("extremum inventory differs")
    uncertain = [e for e in extrema if .25*period <= e["time"] <= 2.25*period and abs(e["plane_value"]) <= 1e-8]
    if not numeric_equal(uncertain,report["uncertain_extrema"]):
        raise ValueError("uncertain extrema were changed or omitted")
    metric = run.geometry.measure_cycle(raw["times"],raw["states"],extrema,report["events"],period,
                                        run.rossler_equilibria(par)[0],field)
    return metric


def audit(directory, expected_sha):
    directory = Path(directory)
    if run.sha256(directory/"summary.json") != expected_sha:
        raise ValueError("bound summary differs")
    summary = json.loads((directory/"summary.json").read_bytes())
    binding = json.loads((directory/"binding.json").read_bytes())
    p = run.load_plan()
    if (binding["plan_sha256"] != run.sha256(run.PLAN)
            or binding["sources"] != {s:run.sha256(run.ROOT/s) for s in run.SOURCES}
            or summary["source_commit"] != binding["source_commit"] or summary["experiment_id"] != "EXP-494"
            or summary["symbolic_chains_verified"] is not False):
        raise ValueError("bound scientific source/claim differs")
    expected_names = set(summary["files"]) | {"summary.json"}
    if {f.name for f in directory.iterdir()} != expected_names:
        raise ValueError("raw file inventory incomplete or extended")
    for name,f in summary["files"].items():
        if (Path(name).name != name or (directory/name).is_symlink()
                or (directory/name).stat().st_size != f["bytes"] or run.sha256(directory/name) != f["sha256"]):
            raise ValueError("raw bytes changed")
    if [r["spec"] for r in summary["rows"]] != run.grid(p):
        raise ValueError("complete independent 66-node grid differs")
    parents = run.parent_inputs(p)
    if not numeric_equal(run.saved_profiles(parents,p),summary["saved_profiles"]):
        raise ValueError("saved eight-cycle replay differs")
    replayed = []
    for row in summary["rows"]:
        for profile in row["profiles"]:
            prefix = row["spec"]["id"]+"--"+profile["method"]
            if profile != json.loads((directory/(prefix+"--result.json")).read_bytes()):
                raise ValueError("profile differs from terminal raw result")
            seed = json.loads((directory/(prefix+"--started.json")).read_bytes())["seed"]
            if "correction" in profile:
                gate = run.correction_gate(profile["correction"],seed,p)
                if not numeric_equal(gate,profile["correction_gate"]):
                    raise ValueError("correction gate replay differs")
                # The last shooting evaluation is the final least-squares state.
                shooting = [n for n in profile["raw_files"] if "--shooting-" in n]
                with np.load(directory/shooting[-1],allow_pickle=False) as raw:
                    final,initial = raw["augmented_states"][-1,:3],raw["augmented_states"][0,:3]
                    if not numeric_equal(initial.tolist(),profile["correction"]["initial_state"]) or not numeric_equal(final.tolist(),profile["correction"]["final_state"]):
                        raise ValueError("corrected state differs from retained final shooting IVP")
                    if not np.isclose(np.linalg.norm(final-initial),profile["correction"]["closure_error"],rtol=1e-12,atol=1e-13):
                        raise ValueError("closure error differs from actual shooting states")
            if "metric" in profile:
                with np.load(directory/(prefix+"--observation.npz"),allow_pickle=False) as raw:
                    metric = audit_observation(raw,profile["observation"],run.RosslerParameters(**row["spec"]["parameters"]),
                                               profile["method"],profile["correction"]["period_time"])
                if not numeric_equal(metric,profile["metric"]):
                    raise ValueError("full-window geometry replay differs")
                qualified = bool(metric["qualified"] and not profile["observation"]["uncertain_extrema"]
                                 and profile["observation"]["maximum_event_residual"] <= 1e-8)
                if qualified is not profile["qualified"]:
                    raise ValueError("profile qualification differs")
                replayed.append(prefix)
        if row["pair"] is not None and not numeric_equal(run.compare_profiles(row["profiles"],p),row["pair"]):
            raise ValueError("paired verdict differs")
    # Re-enter the authentic branch-blocking consumer with retained outcomes.
    by_id = {r["spec"]["id"]:r for r in summary["rows"]}
    def saved_execute(spec,method,seed):
        row = by_id[spec["id"]]
        if row["status"] == "interrupted" and len(row["profiles"]) <= p["methods"].index(method):
            raise run.BudgetStop(row["reason"])
        start = json.loads((directory/(spec["id"]+"--"+method+"--started.json")).read_bytes())
        if start["seed"] != seed:
            raise ValueError("continuation seed not preceding qualified DOP853 state")
        return next(r for r in row["profiles"] if r["method"] == method)
    if not numeric_equal(run.campaign(p,parents,saved_execute),summary["rows"]):
        raise ValueError("full continuation/blocked-row replay differs")
    return dict(experiment_id="EXP-494",passed=True,summary_sha256=expected_sha,
        source_commit=summary["source_commit"],full_grid_nodes=len(summary["rows"]),
        status_counts={s:sum(r["status"] == s for r in summary["rows"]) for s in ("qualified","unqualified","not-run","interrupted")},
        replayed_observations=len(replayed),saved_profiles=len(summary["saved_profiles"]),
        raw_files=len(summary["files"]),raw_bytes=sum(f["bytes"] for f in summary["files"].values()),new_ivps=0,
        audit_code_sha256=run.sha256(Path(__file__)),symbolic_chains_verified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path,required=True)
    parser.add_argument("--summary-sha256",required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    result = audit(args.run,args.summary_sha256)
    run.write_json(args.output,result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()

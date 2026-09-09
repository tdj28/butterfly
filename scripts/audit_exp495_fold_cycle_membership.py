#!/usr/bin/env python3
"""Separate scalar-coordinate replay of every EXP-495 comparison and decision."""
import argparse
import json
from pathlib import Path

from scripts import analyze_exp495_fold_cycle_membership as run


def scalar_distances(first, second, events, scales):
    absolute, state, x_only = [], [], []
    for j in range(6):
        differences = [
            [abs(float(first[k])-float(events[j][k])) for k in range(3)],
            [abs(float(second[k])-float(events[(j+1) % 6][k])) for k in range(3)],
        ]
        absolute.append(differences)
        state.append(max(d[k]/scales[k] for d in differences for k in range(3)))
        x_only.append(max(d[0]/scales[0] for d in differences))
    return dict(absolute_endpoint_differences=absolute, pair_state_distance=state, pair_x_distance=x_only)


def scalar_envelope(rows, radii):
    if not rows:
        raise ValueError("empty comparison")
    s = [max(row["pair_state_distance"][j] for row in rows) for j in range(6)]
    x = [max(row["pair_x_distance"][j] for row in rows) for j in range(6)]
    return dict(pair_state_distance=s, pair_x_distance=x,
        minimum_state_distance=min(s), minimum_x_distance=min(x),
        nearest_state_index=s.index(min(s)), nearest_x_index=x.index(min(x)),
        radii=[dict(radius=r, state_indices=[j for j, v in enumerate(s) if v <= r],
                    x_indices=[j for j, v in enumerate(x) if v <= r]) for r in radii])


def reconstruct(candidates, folds, cycles, plan):
    bases = run.validate_inputs(candidates, folds, cycles, plan)
    rows = []
    for c, f in zip(candidates, folds["candidates"], strict=True):
        variants, e = [], None
        status = "not-evaluated-parent-ineligible"
        if f["qualified_in_region"]:
            base = [b for b in bases if b["spec"]["case"] == c["case"]][0]
            for method in plan["methods"]:
                fold = [v for v in f["solvers"] if v["method"] == method][0]
                cycle = [v for v in base["profiles"] if v["method"] == method][0]
                first, second = (fold["observations"][1][key] for key in ("image_state", "next_state"))
                for phase in plan["phases"]:
                    w = [w for w in cycle["metric"]["windows"] if w["phase"] == phase][0]
                    events = w["event_states"]["historical"]
                    variants.append(dict(method=method, phase=phase, fold_input=first,
                        fold_output=second, cycle_events=events,
                        **scalar_distances(first, second, events, plan["scales"])))
            e = scalar_envelope(variants, plan["sensitivity_radii"])
            status = "proximate-at-primary-radius" if min(e["pair_state_distance"]) <= plan["primary_radius"] else "not-proximate-at-primary-radius"
        rows.append(dict(id=c["id"], case=c["case"], family_id=c["family_id"], region=c["region"],
            parameters=c["parameters"], parent_qualified=f["qualified"], parent_in_region=f["qualified_in_region"],
            parent_solver_outcomes=f["solvers"], status=status, variants=variants, envelope=e))
    cases = []
    for case in plan["cases"]:
        selected = [r for r in rows if r["case"] == case and r["region"] == 1 and r["envelope"] is not None]
        families = sorted(set(r["family_id"] for r in selected))
        required = sorted(f"{case}--region-1--depth-{d}--direction-{v}" for d in (4, 8) for v in (0, 1))
        complete = families == required
        e = scalar_envelope([r["envelope"] for r in selected], plan["sensitivity_radii"]) if selected else None
        status = "incomplete-fold-representation" if not complete else (
            "proximate-at-primary-radius" if min(e["pair_state_distance"]) <= plan["primary_radius"] else "not-proximate-at-primary-radius")
        cases.append(dict(case=case, eligible_candidates=[r["id"] for r in selected],
            families=families, complete=complete, envelope=e, status=status))
    return dict(experiment_id="EXP-495", rows=rows, cases=cases, new_integrations=0,
                symbolic_chains_verified=False, exact_critical_membership_verified=False)


def check_result(result, candidates, folds, cycles, plan):
    expected = reconstruct(candidates, folds, cycles, plan)
    if {k: result[k] for k in expected} != expected:
        raise ValueError("scalar raw-state replay differs")
    return expected


def audit(path, anchor, public=False):
    if run.sha256(path) != anchor:
        raise ValueError("result anchor differs")
    p, candidates, folds, cycles = run.load_inputs()
    result = json.loads(path.read_bytes())
    b = result["binding"]
    if (b["sources"] != {s: run.sha256(run.ROOT/s) for s in run.SOURCES}
            or b["inputs"] != p["inputs"] or b["plan_sha256"] != run.sha256(run.PLAN)
            or result["completed_utc"] < b["started_utc"]):
        raise ValueError("source/input/attempt binding differs")
    if not public and (b != json.loads((path.parent/"binding.json").read_bytes())
            or b != json.loads((run.ROOT/"artifacts/EXP-495/analysis-once.json").read_bytes())):
        raise ValueError("local attempt witness differs")
    expected = check_result(result, candidates, folds, cycles, p)
    return dict(experiment_id="EXP-495", passed=True, result_sha256=anchor,
        source_commit=b["source_commit"], input_hashes=p["inputs"],
        candidates=len(expected["rows"]), eligible=sum(bool(r["variants"]) for r in expected["rows"]),
        comparison_cells=sum(6*len(r["variants"]) for r in expected["rows"]),
        cases=expected["cases"], new_integrations=0, symbolic_chains_verified=False,
        audit_source_sha256=run.sha256(Path(__file__)),
        local_attempt_witness_checked=not public,
        mode="public-saved-result-replay" if public else "local-primary-audit")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--public", action="store_true", help="Replay published states without private local attempt files")
    args = parser.parse_args()
    result = audit(args.result, args.expected_sha256, public=args.public)
    run.write(args.output, result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()

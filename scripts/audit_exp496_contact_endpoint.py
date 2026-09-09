#!/usr/bin/env python3
"""Read-only mesh/qualification replay and separate scalar endpoint arithmetic."""
import argparse
from dataclasses import replace
import json
from pathlib import Path

import numpy as np
from butterfly._paired_startup import inventory, sha256, write_json
from butterfly.models import RosslerParameters, rossler_rhs
from butterfly.poincare import legacy_rossler_section
from butterfly.projected_fold_qualification import qualify, compare
from scripts import audit_exp490_direct_folds as fold_audit
from scripts import audit_exp495_fold_cycle_membership as scalar
from scripts import run_exp496_contact_endpoint as run
from scripts.run_exp488_event_accuracy import validate_geometry


def reconstruct_contact(results, data, folds, cycles, p):
    rows = []
    for c, lower in zip(data["candidates"], results, strict=True):
        row = dict(id=c["id"], case=c["case"], family_id=c["family_id"],
                   status="unresolved-fold", variants=[], envelope=None)
        if lower["qualified_in_region"]:
            old = next(f for f in folds["candidates"] if f["id"] == c["id"])
            ends = [run.cycle_node(cycles, c["case"], lower=b) for b in (False, True)]
            for method in ("DOP853", "Radau"):
                observations = [next(s for s in f["solvers"] if s["method"] == method)["observations"][1]
                                for f in (old, lower)]
                profiles = [next(s for s in node["profiles"] if s["method"] == method) for node in ends]
                for phase in (.25, 1.25):
                    states = [next(w for w in profile["metric"]["windows"] if w["phase"] == phase)
                              ["event_states"]["historical"] for profile in profiles]
                    residual = [(float(events[3][0])-float(o["image_state"][0]))/15.
                                for events, o in zip(states, observations, strict=True)]
                    a, b = residual
                    opposite = ((a >= 1e-6 and b <= -1e-6) or (a <= -1e-6 and b >= 1e-6))
                    o = observations[1]
                    row["variants"].append(dict(method=method, phase=phase,
                        upper_signed_residual=a, lower_signed_residual=b,
                        opposite_sign_resolved=opposite, fold_input=o["image_state"],
                        fold_output=o["next_state"], cycle_events=states[1],
                        **scalar.scalar_distances(o["image_state"], o["next_state"], states[1], [15., 15., .01])))
            row["envelope"] = scalar.scalar_envelope(row["variants"], [1e-6, 1e-5, 1e-4, 1e-3])
            near = max(v["pair_state_distance"][3] for v in row["variants"]) <= 1e-4
            opposite = sum(v["opposite_sign_resolved"] for v in row["variants"]) == 4
            row["status"] = "endpoint-proximate" if near else (
                "opposite-sign-endpoints" if opposite else "no-qualified-bracket")
        rows.append(row)
    cases = []
    for case in ("local-a025-c083", "local-a027-c083"):
        selected = [r for r in rows if r["case"] == case]
        if len(selected) != 4:
            raise ValueError("four representations per case required")
        status = selected[0]["status"] if all(r["status"] == selected[0]["status"] for r in selected) else "mixed-representation-results"
        cases.append(dict(case=case, status=status, representations=[r["id"] for r in selected]))
    return dict(rows=rows, cases=cases, symbolic_chains_verified=False,
                exact_contact_verified=False, continuity_verified=False, new_periodic_integrations=0)


def audit(output, anchor, public=False):
    output = Path(output)
    if sha256(output/"summary.json") != anchor:
        raise ValueError("completed summary anchor changed")
    saved = json.loads((output/"summary.json").read_bytes())
    p, data, folds, cycles = run.load_inputs()
    b = json.loads((output/"binding.json").read_bytes())
    if (saved["status"] != "completed" or saved["experiment_id"] != "EXP-496"
            or saved["binding"] != b or b["sources"] != {s: sha256(run.ROOT/s) for s in p["source_paths"]}
            or b["plan_sha256"] != sha256(run.PLAN) or b["candidates_sha256"] != sha256(run.INPUT)
            or b["inputs"] != p["inputs"] or b["paid_review"] != p["paid_review"]
            or inventory(output, omit=("summary.json",)) != saved["files"]):
        raise ValueError("source/input/output binding differs")
    fold_audit.check_controls(json.loads((output/"controls.json").read_bytes()), p)
    expected = {"binding.json", "controls.json"}
    results, calls = [], 0
    for c in data["candidates"]:
        rows = []
        par = RosslerParameters(**c["parameters"])
        section = replace(legacy_rossler_section(par), direction=-1)
        rhs = lambda t, q: rossler_rhs(t, q, par)
        for method in p["solvers"]:
            label = c["id"]+"--"+method
            expected.update((label+".json", label+"-started.json"))
            row = json.loads((output/(label+".json")).read_bytes())
            start = json.loads((output/(label+"-started.json")).read_bytes())
            if (row["method"] != method or start["method"] != method or start["candidate_id"] != c["id"]
                    or not b["started_utc"] <= start["started_utc"] <= saved["completed_utc"]):
                raise ValueError("profile/start identity differs")
            names = fold_audit.check_trace(row["shooting"], c, method, p, output, label, par, section)
            expected.update(names)
            calls += len(names)
            if row["shooting"]["converged"]:
                u = row["shooting"]["trace"][-1]["u"]
                eligible = c["u_box"][0] <= u-c["epsilon"] < u+c["epsilon"] <= c["u_box"][1]
                if (eligible and len(row["censuses"]) != 3) or (not eligible and row["censuses"]):
                    raise ValueError("prescribed census eligibility differs")
            elif row["censuses"]:
                raise ValueError("unconverged shooting acquired censuses")
            for i, census in enumerate(row["censuses"]):
                name = f"{label}--census-{i}.npz"
                expected.add(name)
                calls += 1
                report = census["report"]
                initial = np.asarray(c["initial_state"])+(u+census["offset"])*np.asarray(c["initial_tangent"])
                shifted = dict(c, initial_state=initial.tolist())
                if (report["method"] != method or any(report[k] != p[k] for k in ("rtol", "atol", "max_step", "guard"))
                        or report["horizon"] != c["horizon"]):
                    raise ValueError("census configuration differs")
                validate_geometry(report, output/name, shifted, dict(p, horizon=c["horizon"]))
            if qualify(row["shooting"], row["censuses"], c, rhs, section, p) != row["qualification"]:
                raise ValueError("qualification replay differs")
            rows.append(row)
        results.append(compare(c, rows, p))
    if (results != saved["candidates"] or saved["ledger"] != data["ledger"]
            or calls != saved["target_trajectories"] or calls > 176 or set(saved["files"]) != expected):
        raise ValueError("complete matrix/decisions/inventory differs")
    if not public:
        marker = run.ROOT/"artifacts/EXP-496/target-once.json"
        if sha256(marker) != saved["marker_sha256"] or json.loads(marker.read_bytes()) != b:
            raise ValueError("local consumed-attempt witness differs")
    contact = reconstruct_contact(results, data, folds, cycles, p)
    if contact != saved["contact"]:
        raise ValueError("separate scalar contact replay differs")
    return dict(experiment_id="EXP-496", passed=True, source_commit=b["source_commit"],
        summary_sha256=anchor, target_trajectories=calls, candidates=results, ledger=data["ledger"],
        contact=contact, elapsed_seconds=saved["elapsed_seconds"],
        audit_source_sha256=sha256(Path(__file__)), local_attempt_witness_checked=not public,
        same_agent_local_audit=True, paid_review="not_run", symbolic_chains_verified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--public", action="store_true")
    a = parser.parse_args()
    result = audit(a.run, a.expected_sha256, a.public)
    write_json(a.output, result)
    print(json.dumps(dict(passed=True, cases=result["contact"]["cases"], target_trajectories=result["target_trajectories"])))


if __name__ == "__main__":
    main()

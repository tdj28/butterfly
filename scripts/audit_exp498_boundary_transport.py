#!/usr/bin/env python3
"""Replay the complete EXP-498 raw ledger without generating trajectories."""
import argparse
import json
import math
from pathlib import Path

import numpy as np
from scripts import run_exp498_boundary_transport as run
from butterfly._paired_startup import inventory,sha256,write_json
from butterfly.event_boundary_shooting import assess
from scripts.run_exp488_event_accuracy import validate_geometry


def check_inputs(p,anchor):
    _,_,_,table,old,_ = run.inputs()
    selected = [c for c in table["intervals"] if c["case"] == "local-a025-c083" and c["status"] == "nominated"]
    if [c["parent_id"] for c in p["candidates"]] != [c["id"] for c in selected]:
        raise ValueError("independent selection differs")
    for c,parent in zip(p["candidates"],selected,strict=True):
        prior = next(r for r in old["intervals"] if r["id"] == parent["id"])
        a,b = [s["root"] for s in prior["analysis"]["solvers"]]
        u,t = (a["u"]+b["u"])/2.,(a["time"]+b["time"])/2.
        if (c["seed_u"] != u or c["seed_time"] != t or c["u_box"] != [u-.02,u+.02]
                or c["time_box"] != [t-1,t+1] or c["parameters"] != anchor["spec"]["parameters"]
                or any(c[k] != parent[k] for k in ("doses","accepted_prefix","horizon","initial_tangent"))
                or c["initial_state"][::2] != parent["initial_state"][::2]
                or c["parent_qualified"] != prior["analysis"]["qualified"]):
            raise ValueError("independent transport seed/unchanged contract differs")


def scalar_predecessors(c,result,anchor,p):
    rows = []
    for side in result["sides"]:
        for j,report in enumerate(side["reports"]):
            cutoff = result["roots"][j]["shooting"]["trace"][-1]["time"]-.05
            eligible_events = [e for e in report["reconstructed"] if e["accepted"] and e["time"] <= cutoff]
            eligible = len(eligible_events) == c["accepted_prefix"] and len(eligible_events) > 0
            event = eligible_events[-1] if eligible else None
            row = dict(method=report["method"],dose=side["dose"],u=side["u"],prefix_count=len(eligible_events),
                eligible=eligible,event=event,windows=[])
            if eligible:
                profile = next(v for v in anchor["result"]["cycle"]["profiles"] if v["method"] == report["method"])
                for w in profile["metric"]["windows"]:
                    distances = [max(abs(float(q[k])-float(event["state"][k]))/s for k,s in enumerate((15.,15.,.01)))
                                 for q in w["event_states"]["historical"]]
                    row["windows"].append(dict(phase=w["phase"],state_distances=distances))
            rows.append(row)
    return rows


def scalar_diagnostic(rows,anchor,p):
    records = [v for r in rows for v in r["predecessors"] if v["eligible"]]
    complete = len(rows) == 8 and len(records) == 64 and all(r["geometry"]["analysis"] and r["geometry"]["analysis"]["qualified"] for r in rows)
    folds = [v["fold_input"][0] for r in anchor["result"]["contact"]["rows"] for v in r["variants"]]
    result = dict(complete_qualified_matrix=bool(complete),predecessors=len(records),
        comparison_cells=sum(len(w["state_distances"]) for r in records for w in r["windows"]),
        state_envelope=None,max_pairwise_scaled_spread=None,worst_cycle_distances=None,sensitivity=[],
        fold_input_x_range=[min(folds),max(folds)],predecessor_minus_fold_x_scaled_range=None,
        ordering="unresolved",symbolic_chains_verified=False)
    if not records: return result
    states = [v["event"]["state"] for v in records]
    low = [min(q[k] for q in states) for k in range(3)]
    high = [max(q[k] for q in states) for k in range(3)]
    # Explicit pairwise scalar reference, not the producer's range identity.
    spread = max(abs(a[k]-b[k])/s for a in states for b in states for k,s in enumerate((15.,15.,.01)))
    worst = [max(w["state_distances"][j] for r in records for w in r["windows"]) for j in range(6)]
    gaps = [(q[0]-f)/15. for q in states for f in folds]
    result.update(state_envelope=[low,high],max_pairwise_scaled_spread=spread,worst_cycle_distances=worst,
        sensitivity=[dict(radius=r,all_realized_predecessors_proximate=[d<=r for d in worst]) for r in (1e-6,1e-5,1e-4,1e-3)],
        predecessor_minus_fold_x_scaled_range=[min(gaps),max(gaps)])
    if complete:
        result["ordering"] = "left" if max(gaps) < -1e-4 else ("right" if min(gaps) > 1e-4 else "overlap-or-unresolved-gap")
    return result


def check_polygons(value,p):
    for side in value["sides"]:
        for v in side["profiles"]:
            nodes = {k:[(q[0],np.array(q[1:])) for q in data] for k,data in v["polygons"].items()}
            measured = run.polygon_audit.compare_polygons(nodes,v["equilibrium"][:2],
                **{k:p[k] for k in ("radius_floor","angle_ceiling","angle_agreement")})
            if not run.polygon_audit.same_numeric(measured,v["geometry"]):
                raise ValueError("polygon arithmetic differs")
            index = run.polygon_audit.ray_index(np.array([q[1:3] for q in v["polygons"]["midpoint_enriched"]])-v["equilibrium"][:2])
            stored = measured["measures"]["midpoint_enriched"]["cut_index"]
            if stored is not None and index != stored:
                raise ValueError("independent signed-ray index differs")


def check_boundary(output,c,row,p,b,completed):
    if row["id"] != c["id"] or [v["method"] for v in row["roots"]] != p["solvers"]:
        raise ValueError("complete paired root identity required")
    expected,starts,calls = set(),[],0
    for method,r in zip(p["solvers"],row["roots"],strict=True):
        names = run.boundary_audit.check_shooting(output,r,c,p,method)
        expected.update(names)
        calls += len(names)
        starts.append((c["id"]+"--"+method+"-started.json",dict(candidate_id=c["id"],method=method,phase="shooting")))
    decision = assess(row["roots"],row["sides"],c,p)
    if decision != row["analysis"] or row["skipped_doses"] != ([] if decision["roots"]["eligible"] else c["doses"]):
        raise ValueError("boundary decision or skipped arms differ")
    for i,side in enumerate(row["sides"]):
        names = [f"{c['id']}--side-{i}--{m}.npz" for m in p["solvers"]]
        if names != side["raw_files"]: raise ValueError("side inventory differs")
        for m,report,name in zip(p["solvers"],side["reports"],names,strict=True):
            if report["method"] != m or report["horizon"] != c["horizon"] or any(report[k] != p[k] for k in ("rtol","atol","max_step","guard")):
                raise ValueError("census settings differ")
            initial = (np.asarray(c["initial_state"])+side["u"]*np.asarray(c["initial_tangent"])).tolist()
            validate_geometry(report,output/name,dict(c,initial_state=initial),dict(p,horizon=c["horizon"]))
            expected.add(name)
            calls += 1
            starts.append((name.removesuffix(".npz")+"-started.json",dict(candidate_id=c["id"],method=m,phase="side",dose=side["dose"],u=side["u"])))
    for name,metadata in starts:
        start = json.loads((output/name).read_bytes())
        if {k:v for k,v in start.items() if k != "started_utc"} != metadata or not b["started_utc"] <= start["started_utc"] <= completed:
            raise ValueError("start identity/time differs")
        expected.add(name)
    return expected,calls


def audit(output,anchor_hash,public=False):
    output = Path(output)
    if sha256(output/"summary.json") != anchor_hash: raise ValueError("summary anchor differs")
    saved = json.loads((output/"summary.json").read_bytes())
    p,anchor = run.load()
    check_inputs(p,anchor)
    b = json.loads((output/"binding.json").read_bytes())
    if (saved["experiment_id"] != "EXP-498" or saved["status"] != "completed" or saved["binding"] != b
            or b["inputs"] != p["inputs"] or b["plan_sha256"] != sha256(run.PLAN)
            or b["sources"] != {s:sha256(run.ROOT/s) for s in p["source_paths"]}
            or saved["ledger"] != p["ledger"] or inventory(output,omit=("summary.json",)) != saved["files"]):
        raise ValueError("source/input/inventory/complete ledger differs")
    controls = json.loads((output/"controls.json").read_bytes())
    run.boundary_audit.check_controls(controls["boundary"],p["boundary"])
    # Exact-data consumer controls are replayed without numerical integration.
    if not controls["winding"]["passed"] or not run.polygon_audit.same_numeric(run.winding.controls(p["winding"]),controls["winding"]):
        raise ValueError("analytic winding controls differ")
    if [r["id"] for r in saved["rows"]] != [c["id"] for c in p["candidates"]]:
        raise ValueError("all eight target identities required")
    expected,calls = {"binding.json","controls.json"},0
    compact = []
    for row,c in zip(saved["rows"],p["candidates"],strict=True):
        name = c["id"]+".json"
        if json.loads((output/name).read_bytes()) != row or row["parent_id"] != c["parent_id"] or row["parent_qualified"] != c["parent_qualified"]:
            raise ValueError("terminal/old failure identity differs")
        expected.add(name)
        names,n = check_boundary(output,c,row["boundary"],p["boundary"],b,saved["completed_utc"])
        expected.update(names)
        calls += n
        geometry = run.geometry(output,c,row["boundary"],p["winding"])
        if not run.polygon_audit.same_numeric(geometry,row["geometry"]): raise ValueError("raw-to-polygon replay differs")
        check_polygons(geometry,p["winding"])
        if not run.polygon_audit.same_numeric(scalar_predecessors(c,row["boundary"],anchor,p),row["predecessors"]):
            raise ValueError("independent predecessor arithmetic differs")
        reduced = dict(row)
        reduced["geometry"] = dict(analysis=geometry["analysis"],sides=[dict(dose=s["dose"],u=s["u"],profiles=[
            dict({k:v for k,v in profile.items() if k != "polygons"},
                 polygon_sha256=run.boundary.builder.digest(profile["polygons"])) for profile in s["profiles"]]) for s in geometry["sides"]])
        compact.append(reduced)
    diagnostic = scalar_diagnostic(saved["rows"],anchor,p)
    if not run.polygon_audit.same_numeric(diagnostic,saved["diagnostic"]) or calls != saved["target_ivps"] or calls > 192 or set(saved["files"]) != expected:
        raise ValueError("complete diagnostic/IVP inventory differs")
    if not public:
        marker = run.ROOT/"artifacts/EXP-498/target-once.json"
        if sha256(marker) != saved["marker_sha256"] or json.loads(marker.read_bytes()) != b:
            raise ValueError("consumed attempt witness differs")
    return dict(experiment_id="EXP-498",passed=True,source_commit=b["source_commit"],summary_sha256=anchor_hash,
        audit_source_sha256=sha256(Path(__file__)),ledger=p["ledger"],rows=compact,diagnostic=diagnostic,
        target_ivps=calls,new_integrations=0,local_attempt_witness_checked=not public,
        symbolic_chains_verified=False,paid_review="not_run",
        raw_replay_scope="Raw meshes and full local-window polygons remain local; this compact result is not a full public trajectory archive.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path,required=True)
    parser.add_argument("--expected-sha256",required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--public",action="store_true")
    a = parser.parse_args()
    result = audit(a.run,a.expected_sha256,a.public)
    write_json(a.output,result)
    print(json.dumps(dict(passed=True,target_ivps=result["target_ivps"],diagnostic=result["diagnostic"])))


if __name__ == "__main__": main()

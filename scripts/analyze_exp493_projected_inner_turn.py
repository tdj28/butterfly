#!/usr/bin/env python3
"""Complete saved-trajectory check of relative projected winding; no IVPs."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
import numpy as np
from butterfly._paired_startup import sha256,write_json
from butterfly.models import RosslerParameters,rossler_rhs,rossler_equilibria
from butterfly.projected_winding import window_nodes,compare_polygons
from scripts import audit_exp492_event_boundaries as parent

PLAN = ROOT/"experiments/manifests/EXP-493-projected-inner-turn.json"
SOURCES = ("scripts/analyze_exp493_projected_inner_turn.py","python/butterfly/projected_winding.py",
    "tests/test_projected_winding.py","tests/test_exp493_projected_inner_turn.py",
    "docs/experiments/EXP-493-projected-inner-turn.md",*parent.run.SOURCES)


def load_plan():
    p = json.loads(PLAN.read_bytes())
    expected = dict(experiment_id="EXP-493",parent_source="919f16f1846d145ff14ad1da35e3fb516cd1e849",
        parent_summary_sha256="4a856360eb1c8da8099fd39ca09e4543423ed32a8a4dd20766f175a7c98e86a6",
        parent_receipt_path="docs/experiments/receipts/EXP-492-event-boundary-result.json",
        parent_receipt_sha256="7544eb230106e6b1f6fccf658fb6f60e6ef53230bcc0709b0b6e912addc268bf",
        window=.05,radius_floor=1e-10,angle_ceiling=2.9,angle_agreement=1e-6,
        paired_angle=1e-6,paired_scaled_endpoint=1e-6,paired_radius_relative=.01,
        relative_turn_error=.01,scales=[15.,15.,.01],max_seconds=300,max_output_bytes=33554432)
    if any(p[k] != v for k,v in expected.items()):
        raise ValueError("frozen prospective plan required")
    return p


def profile(raw,report,c,root_time,p,*,control_field=None):
    par = RosslerParameters(**c["parameters"])
    equilibrium = rossler_equilibria(par)[0]
    field = control_field if control_field is not None else lambda t,q:rossler_rhs(t,q,par)
    nodes = window_nodes(raw["integration_times"],raw["integration_augmented_states"][:,:3],
        report["extrema"],field,root_time-p["window"],root_time+p["window"])
    result = compare_polygons(nodes,equilibrium[:2],**{k:p[k] for k in ("radius_floor","angle_ceiling","angle_agreement")})
    measure = result["measures"]["midpoint_enriched"]
    events = [e for e in report["reconstructed"] if root_time-p["window"] < e["time"] < root_time+p["window"] and e["accepted"]]
    agrees = measure["cut_index"] == len(events)
    q = np.array([v for _,v in nodes["midpoint_enriched"]])-equilibrium
    a,delta = q[:-1],np.diff(q,axis=0)
    lengths = np.sum(delta*delta,axis=1)
    fraction = np.divide(-np.sum(a*delta,axis=1),lengths,out=np.zeros_like(lengths),where=lengths>0)
    minimum_3d = float(np.min(np.linalg.norm(a+np.clip(fraction,0.,1.)[:,None]*delta,axis=1)))
    return dict(method=report["method"],equilibrium=equilibrium.tolist(),geometry=result,
        local_negative_crossings=len(events),event_index_agrees=bool(agrees),qualified=bool(result["qualified"] and agrees),
        minimum_polygon_distance_3d=minimum_3d,
        endpoints=[nodes["extrema_augmented"][i][1].tolist() for i in (0,-1)],
        polygons={k:[[t,*q.tolist()] for t,q in v] for k,v in nodes.items()})


def compare(rows,c,p,parent_qualified):
    if len(rows) != 4 or [r["dose"] for r in rows] != c["doses"] or any([v["method"] for v in r["profiles"]] != ["DOP853","Radau"] for r in rows):
        raise ValueError("complete four-dose/two-solver geometric matrix required")
    pairs = []
    for r in rows:
        a,b = r["profiles"]
        ma,mb = [v["geometry"]["measures"]["midpoint_enriched"] for v in (a,b)]
        angle = abs(ma["angle_change"]-mb["angle_change"]) if ma["angle_change"] is not None and mb["angle_change"] is not None else None
        radius = abs(ma["minimum_radius"]-mb["minimum_radius"])/max(ma["minimum_radius"],mb["minimum_radius"],p["radius_floor"])
        endpoint = float(np.max(np.abs((np.asarray(a["endpoints"])-b["endpoints"])/p["scales"])))
        passed = all(v["qualified"] for v in (a,b)) and ma["cut_index"] == mb["cut_index"] and angle is not None and angle <= p["paired_angle"] and radius <= p["paired_radius_relative"] and endpoint <= p["paired_scaled_endpoint"]
        pairs.append(dict(dose=r["dose"],angle_error=angle,radius_relative_error=radius,scaled_endpoint_error=endpoint,passed=bool(passed)))
    transitions = []
    for j,method in enumerate(("DOP853","Radau")):
        for left,right in ((0,3),(1,2)):
            a,b = [rows[i]["profiles"][j] for i in (left,right)]
            ma,mb = [v["geometry"]["measures"]["midpoint_enriched"] for v in (a,b)]
            # Determine which side has the extra event only after measuring
            # both polygons. No angle is constructed from that event count.
            sign = b["local_negative_crossings"]-a["local_negative_crossings"]
            excess = sign*(mb["angle_change"]-ma["angle_change"])/(2*np.pi) if ma["angle_change"] is not None and mb["angle_change"] is not None else None
            cut = sign*(mb["cut_index"]-ma["cut_index"]) if ma["cut_index"] is not None and mb["cut_index"] is not None else None
            passed = abs(sign) == 1 and cut == 1 and excess is not None and abs(excess-1) <= p["relative_turn_error"] and a["qualified"] and b["qualified"]
            transitions.append(dict(method=method,doses=[rows[i]["dose"] for i in (left,right)],
                event_difference_positive_minus_negative=sign,extra_cut_index=cut,relative_open_arc_turns=excess,passed=bool(passed)))
    return dict(qualified=bool(parent_qualified and all(v["passed"] for v in pairs+transitions)),
        parent_boundary_qualified=parent_qualified,paired_profiles=pairs,relative_turns=transitions)


def controls(p):
    """Exact polynomial data through the actual consumer; zero integrations."""
    c = dict(parameters=dict(a=.2,b=.2,c=7.),doses=[-2e-5,-2e-6,2e-6,2e-5])
    eq = rossler_equilibria(RosslerParameters(**c["parameters"]))[0]
    field = lambda t,q:np.array([-1.,-(t-1.),0.])
    def one(height,method,keep_extremum=True):
        q = lambda t:eq+np.array([-(t-1.),height-.5*(t-1.)**2,13.])
        raw = dict(integration_times=np.array([.9,1.1]),integration_augmented_states=np.column_stack([np.array([q(.9),q(1.1)]),np.zeros((2,3))]))
        events = [dict(time=1+np.sqrt(2*height),accepted=True)] if height > 0 else []
        report = dict(method=method,extrema=[dict(time=1.,state=q(1).tolist())] if keep_extremum else [],reconstructed=events)
        return profile(raw,report,c,1.,p,control_field=field)
    sides = [dict(dose=d,profiles=[one(d,m) for m in ("DOP853","Radau")]) for d in c["doses"]]
    positive = compare(sides,c,p,True)
    origin = [one(0.,m) for m in ("DOP853","Radau")]
    missing = [one(2e-5,m,False) for m in ("DOP853","Radau")]
    exact = all(v["geometry"]["measures"]["midpoint_enriched"]["cut_index"] == int(s["dose"] > 0)
        for s in sides for v in s["profiles"])
    exact_angles = all(abs(v["geometry"]["measures"]["midpoint_enriched"]["angle_change"]-
        ((np.pi if s["dose"] > 0 else -np.pi)+2*np.arctan((.00125-s["dose"])/.05))) <= 1e-12
        for s in sides for v in s["profiles"])
    return dict(positive_sides=sides,positive_analysis=positive,origin_negative=origin,undersampled_negative=missing,
        passed=bool(positive["qualified"] and exact and exact_angles and all(not v["qualified"] for v in origin+missing)),
        analytic_profiles=12,new_integrations=0,
        note="Exact polynomial state arrays, not solver runs; method labels exercise ordered production-matrix handling.")


def analyze(directory,p):
    receipt = parent.audit(directory,p["parent_summary_sha256"])
    if receipt["source_commit"] != p["parent_source"] or sha256(ROOT/p["parent_receipt_path"]) != p["parent_receipt_sha256"] or receipt != json.loads((ROOT/p["parent_receipt_path"]).read_bytes()):
        raise ValueError("audited complete parent/public receipt differ")
    saved = json.loads((directory/"summary.json").read_bytes())
    table,candidates = parent.run.load(json.loads(parent.run.PLAN.read_bytes()))
    by_id = {c["id"]:c for c in candidates}
    outcomes = {r["id"]:r for r in saved["candidates"]}
    results = []
    for item in table["intervals"]:
        row = dict(id=item["id"],family_id=item["family_id"],selection_status=item["status"],profiles=[],analysis=None)
        if item["status"] == "nominated":
            c,r = by_id[item["id"]],outcomes[item["id"]]
            row["parent_boundary_qualified"] = r["analysis"]["qualified"]
            if not r["analysis"]["roots"]["eligible"]:
                row["status"] = "unresolved-parent-root-gate"
            else:
                center_time = r["roots"][0]["shooting"]["trace"][-1]["time"]
                row["root_time"] = center_time
                for side in r["sides"]:
                    profiles = []
                    for report,name in zip(side["reports"],side["raw_files"],strict=True):
                        with np.load(directory/name,allow_pickle=False) as raw:
                            v = profile(raw,report,c,center_time,p)
                        profiles.append(dict(v,raw_path=name,raw_sha256=saved["files"][name]["sha256"]))
                    row["profiles"].append(dict(dose=side["dose"],u=side["u"],profiles=profiles))
                row["analysis"] = compare(row["profiles"],c,p,r["analysis"]["qualified"])
                row["status"] = "qualified" if row["analysis"]["qualified"] else "unresolved"
        else:
            row["status"] = "not-selected"
        results.append(row)
    return dict(experiment_id="EXP-493",status="complete-saved-data-analysis",intervals=results,
        parent_summary_sha256=p["parent_summary_sha256"],parent_source=p["parent_source"],new_integrations=0,
        paid_review="not_run",claim_boundary=p["claim_boundary"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--verify-receipt",type=Path)
    args = parser.parse_args()
    p = load_plan()
    if not args.verify_receipt:
        if subprocess.check_output(["git","status","--porcelain"],text=True).strip() or subprocess.check_output(["git","rev-parse","HEAD"]) != subprocess.check_output(["git","rev-parse","@{upstream}"]):
            parser.error("clean pushed source required for first saved-data analysis")
    start = time.monotonic()
    control = controls(p)
    if not control["passed"]:
        raise ValueError("analytic consumer controls failed")
    result = analyze(args.run,p)
    if time.monotonic()-start > p["max_seconds"]:
        raise TimeoutError("read-only analysis runtime exceeded; no partial verdict")
    if args.verify_receipt:
        previous = json.loads(args.verify_receipt.read_bytes())
        binding = json.loads((args.verify_receipt.parent/"binding.json").read_bytes())
        if binding["plan_sha256"] != sha256(PLAN) or binding["sources"] != {s:sha256(ROOT/s) for s in SOURCES} or control != json.loads((args.verify_receipt.parent/"controls.json").read_bytes()) or result != previous:
            raise ValueError("complete read-only replay differs")
    else:
        args.output_dir.mkdir(parents=True,exist_ok=False)
        binding = dict(source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
            utc=datetime.now(timezone.utc).isoformat(),plan_sha256=sha256(PLAN),sources={s:sha256(ROOT/s) for s in SOURCES},
            runtime=dict(python=sys.version,numpy=np.__version__))
        data = (json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()
        if len(data) > p["max_output_bytes"]:
            raise ValueError("saved-data result exceeds declared output cap")
        write_json(args.output_dir/"binding.json",binding)
        write_json(args.output_dir/"controls.json",control)
        write_json(args.output_dir/"summary.json",result)
    print(json.dumps(dict(intervals=len(result["intervals"]),qualified=sum(r["status"] == "qualified" for r in result["intervals"]),new_integrations=0)))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Raw coefficient/mesh audit and independent scalar contact replay; no IVPs."""
import argparse
from dataclasses import replace
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from butterfly._paired_startup import inventory,sha256,write_json
from butterfly.models import RosslerParameters,rossler_rhs
from butterfly.poincare import legacy_rossler_section
from butterfly.projected_fold_qualification import qualify,compare
from scripts import run_exp497_contact_localization as run
from scripts import audit_exp490_direct_folds as fold_audit
from scripts import audit_exp494_periodic_winding_transport as periodic_audit
from scripts import audit_exp495_fold_cycle_membership as scalar
from scripts.run_exp488_event_accuracy import validate_geometry


def scalar_contact(folds,cycle):
    rows,variants = [],[]
    for f in folds:
        row = dict(id=f["id"],family_id=f["family_id"],variants=[],envelope=None)
        if f["qualified_in_region"]:
            for method in ("DOP853","Radau"):
                o = next(s for s in f["solvers"] if s["method"] == method)["observations"][1]
                profile = next(s for s in cycle["profiles"] if s["method"] == method)
                for phase in (.25,1.25):
                    w = next(w for w in profile["metric"]["windows"] if w["phase"] == phase)
                    events = w["event_states"]["historical"]
                    v = dict(method=method,phase=phase,fold_input=o["image_state"],fold_output=o["next_state"],
                        cycle_events=events,signed_residual=(float(events[3][0])-float(o["image_state"][0]))/15.,
                        **scalar.scalar_distances(o["image_state"],o["next_state"],events,[15.,15.,.01]))
                    row["variants"].append(v)
                    variants.append(v)
            row["envelope"] = scalar.scalar_envelope(row["variants"],[1e-6,1e-5,1e-4,1e-3])
        rows.append(row)
    mean,env,status = None,None,"fold-unqualified"
    if len(variants) == 16:
        env = scalar.scalar_envelope(variants,[1e-6,1e-5,1e-4,1e-3])
        values = [v["signed_residual"] for v in variants]
        mean = math.fsum(values)/16
        if max(v["pair_state_distance"][3] for v in variants) <= 1e-4: status = "proximate"
        elif min(values) >= 1e-6: status = "replace-high"
        elif max(values) <= -1e-6: status = "replace-low"
        else: status = "sign-unresolved"
    return dict(status=status,rows=rows,envelope=env,mean_residual=mean,
                exact_contact_verified=False,symbolic_chains_verified=False)


def load_raw(path):
    # Materialize each compressed array once; never repeatedly decompress it.
    with np.load(path,allow_pickle=False) as archive:
        return {k:archive[k] for k in archive.files}


def check_periodic_controls(output):
    receipt = json.loads((output/"controls.json").read_bytes())
    rows = receipt["rows"]
    if (not receipt["passed"] or receipt["control_ivps"] != 4
            or [(r["method"],r["multiplicity"]) for r in rows] != [(m,n) for m in ("DOP853","Radau") for n in (1,2)]):
        raise ValueError("periodic control matrix differs")
    names = {"controls.json"}
    for row in rows:
        name = f"control-{row['method']}-{row['multiplicity']}.npz"
        if row["raw"] != dict(path=name,sha256=sha256(output/name)):
            raise ValueError("periodic control raw binding differs")
        raw = load_raw(output/name)
        t,q = raw["times"],raw["states"]
        expected = np.c_[np.cos(t+.2),np.sin(t+.2),np.zeros(len(t))]
        if q.shape != expected.shape or np.max(np.abs(q-expected)) > 1e-8:
            raise ValueError("analytic circle trajectory differs")
        field = lambda t,q:np.array([-q[1],q[0],0.])
        sections = dict(historical=run.cycles_run.PoincareSection((0.,1.,0.),0.,-1,0,0.),
                        barrio=run.cycles_run.PoincareSection((1.,0.,0.),0.,1))
        events,extrema = {},[]
        for key,section in sections.items():
            events[key] = []
            dense = lambda t:run.cycles_run.geometry.dense_value(raw,row["method"],t)
            knots = np.unique(np.r_[0.,raw[key+"_extrema_times"],5*np.pi*row["multiplicity"]])
            roots = [brentq(lambda t:section.value(dense(t)),left,right,xtol=1e-12,rtol=1e-14)
                     for left,right in zip(knots[:-1],knots[1:],strict=True)
                     if section.value(dense(left))*section.value(dense(right)) < 0]
            for time in roots:
                state = dense(time)
                f = field(time,state)
                velocity = float(np.dot(section.normal,f))
                events[key].append(dict(time=float(time),state=state.tolist(),
                    angle=abs(velocity)/float(np.linalg.norm(f)),accepted=bool(section.accepts(state) and section.direction*velocity > 0)))
            extrema += [dict(time=float(time),state=state.tolist()) for time,state in
                        zip(raw[key+"_extrema_times"],raw[key+"_extrema_states"],strict=True)]
        metric = run.cycles_run.geometry.measure_cycle(t,q,extrema,events,2*np.pi*row["multiplicity"],np.zeros(3),field)
        if (not periodic_audit.numeric_equal(metric,row["metric"]) or not row["passed"]
                or metric["qualified"] != (row["multiplicity"] == 1)):
            raise ValueError("periodic control geometry/primitive replay differs")
        names.add(name)
    return names


def check_cycle(output,cycle,spec,seed,p):
    names = set()
    calls = 0
    par = RosslerParameters(**spec["parameters"])
    for profile in cycle["profiles"]:
        method = profile["method"]
        prefix = spec["id"]+"--"+method
        start = json.loads((output/(prefix+"--started.json")).read_bytes())
        if start["spec"] != spec or start["seed"] != seed or start["method"] != method:
            raise ValueError("periodic phase seed/spec differs")
        if json.loads((output/(prefix+"--result.json")).read_bytes()) != profile:
            raise ValueError("periodic terminal profile differs")
        names.update((prefix+"--started.json",prefix+"--result.json"))
        shooting = [n for n in profile["raw_files"] if "--shooting-" in n]
        for i,name in enumerate(shooting):
            if name != prefix+f"--shooting-{i:02d}.npz":
                raise ValueError("periodic shooting inventory differs")
            raw = load_raw(output/name)
            t,q = raw["times"],raw["augmented_states"]
            if (q.shape != (len(t),12) or t[0] != 0 or not np.all(np.diff(t)>0)
                    or not np.array_equal(q[0,3:],np.eye(3).ravel())
                    or (bool(raw["success"]) and not np.isfinite(q).all())):
                raise ValueError("periodic raw mesh differs")
        names.update(profile["raw_files"])
        calls += len(profile["raw_files"])
        if "correction" in profile:
            c = profile["correction"]
            names.add(prefix+"--correction.json")
            if not shooting: raise ValueError("missing correction meshes")
            raw = load_raw(output/shooting[-1])
            initial,final = raw["augmented_states"][[0,-1],:3]
            direction = rossler_rhs(0.,np.asarray(seed["initial_state"]),par)
            direction /= np.linalg.norm(direction)
            phase = abs(float(np.dot(initial-seed["initial_state"],direction)))
            if (not periodic_audit.numeric_equal(initial.tolist(),c["initial_state"])
                    or not periodic_audit.numeric_equal(final.tolist(),c["final_state"])
                    or abs(raw["times"][-1]-c["period_time"]) > 1e-12
                    or abs(float(np.linalg.norm(final-initial))-c["closure_error"]) > 1e-13
                    or abs(phase-c["phase_residual"]) > 1e-13
                    or not periodic_audit.numeric_equal(run.cycles_run.correction_gate(c,seed,p),profile["correction_gate"])):
                raise ValueError("periodic closure/phase/correction replay differs")
        if "metric" in profile:
            raw = load_raw(output/(prefix+"--observation.npz"))
            metric = periodic_audit.audit_observation(raw,profile["observation"],par,method,profile["correction"]["period_time"])
            qualified = bool(profile["correction_gate"]["passed"] and metric["qualified"]
                and not profile["observation"]["uncertain_extrema"] and profile["observation"]["maximum_event_residual"] <= 1e-8)
            if not periodic_audit.numeric_equal(metric,profile["metric"]) or qualified != profile["qualified"]:
                raise ValueError("periodic primitive observation replay differs")
        elif profile["qualified"]:
            raise ValueError("qualified cycle lacks metric")
    pair = run.cycles_run.compare_profiles(cycle["profiles"],p)
    counts = pair["passed"] and all(w["counts"] == dict(historical=6,barrio=8)
        for profile in cycle["profiles"] for w in profile["metric"]["windows"])
    expected = dict(spec=spec,profiles=cycle["profiles"],pair=pair,status="qualified" if counts else "unqualified")
    if pair["passed"] and not counts: expected["count_failure"] = True
    if expected != cycle: raise ValueError("paired six/eight cycle decision differs")
    return names,calls


def check_fold(output,c,p,binding,completed):
    par = RosslerParameters(**c["parameters"])
    section = replace(legacy_rossler_section(par),direction=-1)
    rhs = lambda t,q:rossler_rhs(t,q,par)
    names,rows,calls = set(),[],0
    for method in p["solvers"]:
        label = c["id"]+"--"+method
        row = json.loads((output/(label+".json")).read_bytes())
        start = json.loads((output/(label+"-started.json")).read_bytes())
        if (start["candidate_id"] != c["id"] or start["method"] != method or row["method"] != method
                or not binding["started_utc"] <= start["started_utc"] <= completed):
            raise ValueError("fold start identity differs")
        names.update((label+".json",label+"-started.json"))
        meshes = fold_audit.check_trace(row["shooting"],c,method,p,output,label,par,section)
        names.update(meshes)
        calls += len(meshes)
        if row["shooting"]["converged"]:
            u = row["shooting"]["trace"][-1]["u"]
            eligible = c["u_box"][0] <= u-c["epsilon"] < u+c["epsilon"] <= c["u_box"][1]
            if len(row["censuses"]) != (3 if eligible else 0):
                raise ValueError("prescribed fold census missing")
        elif row["censuses"]: raise ValueError("unconverged fold acquired census")
        for i,census in enumerate(row["censuses"]):
            name = f"{label}--census-{i}.npz"
            initial = np.asarray(c["initial_state"])+(u+census["offset"])*np.asarray(c["initial_tangent"])
            report = census["report"]
            if report["method"] != method or any(report[k] != p[k] for k in ("rtol","atol","max_step","guard")) or report["horizon"] != c["horizon"]:
                raise ValueError("fold census configuration differs")
            validate_geometry(report,output/name,dict(c,initial_state=initial.tolist()),dict(p,horizon=c["horizon"]))
            names.add(name)
            calls += 1
        if qualify(row["shooting"],row["censuses"],c,rhs,section,p) != row["qualification"]:
            raise ValueError("fold qualification replay differs")
        rows.append(row)
    return dict(compare(c,rows,p),parent_id=c["parent_id"]),names,calls


def audit(output,anchor,public=False):
    output = Path(output)
    if sha256(output/"summary.json") != anchor: raise ValueError("summary anchor differs")
    saved = json.loads((output/"summary.json").read_bytes())
    p,source = run.load()
    b = json.loads((output/"binding.json").read_bytes())
    if (saved["binding"] != b or saved["status"] != "completed" or saved["experiment_id"] != "EXP-497"
            or b["plan_sha256"] != sha256(run.PLAN) or b["inputs"] != p["inputs"]
            or b["sources"] != {s:sha256(run.ROOT/s) for s in p["source_paths"]}
            or saved["parent_ledger"] != source["data"]["ledger"]
            or inventory(output,omit=("summary.json",)) != saved["files"]):
        raise ValueError("source/input/raw ledger binding differs")
    fold_audit.check_controls(json.loads((output/"fold-controls.json").read_bytes()),p["fold"])
    expected = {"binding.json","fold-controls.json"} | check_periodic_controls(output)
    calls,points = 0,0
    def replay(spec,candidates,seed):
        nonlocal calls,points
        rows = [r for r in saved["rows"] if r["case"] == spec["case"] and r["level"] == spec["level"]]
        if len(rows) != 1: raise ValueError("unique adaptive point required")
        row = rows[0]
        if row["spec"] != spec or row["candidates"] != candidates or row["seed"] != seed:
            raise ValueError("adaptive parameter/fold seed/phase reference differs")
        left,right = row["bracket_before"]
        a = (right["a"]*left["mean_residual"]-left["a"]*right["mean_residual"])/(left["mean_residual"]-right["mean_residual"])
        if abs(a-spec["parameters"]["a"]) > 1e-15:
            raise ValueError("separate scalar interpolation differs")
        name = spec["id"]+"--point.json"
        result = json.loads((output/name).read_bytes())
        if result != row["result"]: raise ValueError("terminal point differs")
        expected.add(name)
        names,n = check_cycle(output,result["cycle"],spec,seed,p["periodic"])
        expected.update(names)
        calls += n
        actual = []
        if result["cycle"]["status"] == "qualified":
            for c in candidates:
                f,names,n = check_fold(output,c,p["fold"],b,saved["completed_utc"])
                expected.update(names)
                calls += n
                actual.append(f)
            contact = scalar_contact(actual,result["cycle"])
        else: contact = None
        if actual != result["folds"] or not periodic_audit.numeric_equal(contact,result["contact"]):
            raise ValueError("complete fold/scalar contact replay differs")
        points += 1
        return result
    if run.campaign(p,source,replay) != saved["rows"] or len(saved["rows"]) != 6:
        raise ValueError("complete adaptive/blocked-level ledger differs")
    if calls != saved["target_ivps"] or calls > 512 or set(saved["files"]) != expected:
        raise ValueError("all target IVPs/files differ")
    if not public:
        marker = run.ROOT/"artifacts/EXP-497/target-once.json"
        if sha256(marker) != saved["marker_sha256"] or json.loads(marker.read_bytes()) != b:
            raise ValueError("consumed attempt witness differs")
    return dict(experiment_id="EXP-497",passed=True,source_commit=b["source_commit"],summary_sha256=anchor,
        rows=saved["rows"],target_ivps=calls,points=points,parent_ledger=saved["parent_ledger"],
        audit_source_sha256=sha256(Path(__file__)),local_attempt_witness_checked=not public,
        new_integrations=0,symbolic_chains_verified=False,exact_contact_verified=False,paid_review="not_run")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path,required=True)
    parser.add_argument("--expected-sha256",required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--public",action="store_true")
    a = parser.parse_args()
    result = audit(a.run,a.expected_sha256,a.public)
    write_json(a.output,result)
    print(json.dumps(dict(passed=True,target_ivps=result["target_ivps"],points=result["points"],
                         statuses=[r["status"] for r in result["rows"]])))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Raw coefficient and complete decision audit, without integrations."""
import argparse
from decimal import Decimal as D, localcontext
import json
import math
from pathlib import Path

from butterfly._paired_startup import inventory, sha256, write_json
from scripts import run_exp499_decimal_reference as run
from scripts import exp499_reference_controls as analytic


def agree(a,b):
    if type(a) is not type(b): return False
    if isinstance(a,dict): return a.keys() == b.keys() and all(agree(a[k],b[k]) for k in a)
    if isinstance(a,list): return len(a) == len(b) and all(agree(x,y) for x,y in zip(a,b,strict=True))
    if isinstance(a,float): return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-30)
    return a == b


def check_inputs(plan,old):
    expected = []
    with localcontext() as ctx:
        ctx.prec = 70
        for candidate in old["rows"]:
            for index,side in enumerate(candidate["boundary"]["sides"]):
                row = plan["trials"][len(expected)]
                if (row["id"] != candidate["id"]+f"--side-{index}" or row["candidate_id"] != candidate["id"]
                        or row["initial"] != side["reports"][0]["initial_state"] or row["dose"] != side["dose"]
                        or row["historical_parent_qualified"] != candidate["parent_qualified"]
                        or row["original_candidate_qualified"] != candidate["geometry"]["analysis"]["qualified"]):
                    raise ValueError("independent parent identity differs")
                a,b = [[e for e in r["reconstructed"] if e["accepted"]] for r in side["reports"]]
                if len(a) != len(b) or len(row["boxes"]) != len(a):
                    raise ValueError("independent event count differs")
                for box,x,y in zip(row["boxes"],a,b,strict=True):
                    lo,hi = map(D,box)
                    if hi-lo != D("0.00002") or lo+hi != D.from_float(x["time"])+D.from_float(y["time"]):
                        raise ValueError("independent root box differs")
                expected.append(row["id"])
    if len(expected) != 32 or len(set(expected)) != 32 or plan["ledger"] != old["ledger"]:
        raise ValueError("complete ledger/trial set required")


def check_raw(raw,initial,field,horizon,config,scales):
    """Check derivatives times factorial order, using scalar sums, not builder."""
    if (raw["config"] != config or raw["field"] != field or raw["scales"] != scales
            or raw["initial"] != [str(run.taylor.exact(v)) for v in initial]
            or raw["horizon"] != str(run.taylor.exact(horizon)) or raw["rigorous_enclosure"] is not False):
        raise ValueError("raw input/config identity differs")
    with localcontext() as ctx:
        ctx.prec = config["digits"]+16
        epsilon = D(10)**(-config["digits"]+8)
        close = lambda x,y: abs(x-y) <= epsilon*max(D(1),abs(x),abs(y))
        previous = [run.taylor.exact(v) for v in initial]
        expected_time, maximum_tail = D(0), D(0)
        end, step = run.taylor.exact(horizon), D(config["step"])
        for row in raw["steps"]:
            time,h = D(row["time"]),D(row["step"])
            coefficients = [[D(v) for v in values] for values in row["coefficients"]]
            if (not close(time,expected_time) or h <= 0 or not close(h,min(step,end-time))
                    or len(coefficients) != 3 or any(len(q) != config["order"]+1 for q in coefficients)
                    or not all(v.is_finite() for q in coefficients for v in q)):
                raise ValueError("raw mesh/coefficient structure differs")
            if not all(close(coefficients[i][0],previous[i]) for i in range(3)):
                raise ValueError("raw trajectory continuity differs")
            for n in range(config["order"]):
                for axis in range(3):
                    terms = [run.taylor.exact(field["constant"][axis]) if n == 0 else D(0)]
                    for i,j,value in field["linear"]:
                        if i == axis: terms.append(run.taylor.exact(value)*coefficients[j][n])
                    for i,j,k,value in field["quadratic"]:
                        if i == axis:
                            terms.extend(run.taylor.exact(value)*coefficients[j][r]*coefficients[k][n-r] for r in range(n+1))
                    if not close(coefficients[axis][n+1]*(n+1),sum(terms)):
                        raise ValueError("independent coefficient recurrence differs")
            powers = [h**n for n in range(config["order"]+1)]
            previous = [sum(v*p for v,p in zip(q,powers,strict=True)) for q in coefficients]
            if not all(v.is_finite() and abs(v) <= D("1e4") for v in previous):
                raise ValueError("raw endpoint state guard")
            tail = max(sum(abs(coefficients[i][n]*powers[n]) for n in range(config["order"]-2,config["order"]+1))
                       /run.taylor.exact(scales[i]) for i in range(3))
            if tail > D("1e-20"): raise ValueError("raw tail diagnostic failed")
            maximum_tail = max(maximum_tail,tail)
            expected_time = time+h
        if (not raw["steps"] or not close(expected_time,end)
                or not all(close(x,D(y)) for x,y in zip(previous,raw["final"],strict=True))
                or not close(maximum_tail,D(raw["maximum_tail"]))):
            raise ValueError("raw completion/tail differs")


def check_event(curve,event,box,offset,gate):
    repeated = run.taylor.root(curve,box,offset,gate_upper=gate)
    if repeated != event: raise ValueError("saved root consumer differs")
    with localcontext() as ctx:
        ctx.prec = 70
        time = D(event["time"])
        i = curve.index(time)
        delta = time-curve.times[i]
        q = [sum(coefficient*delta**n for n,coefficient in enumerate(poly)) for poly in curve.poly[i]]
        tolerance = D(10)**(-curve.raw["config"]["digits"]+8)
        if (not D(box[0]) <= time <= D(box[1]) or abs(q[1]-run.taylor.exact(offset)) > D("1e-20")
                or any(abs(x-D(y)) > tolerance*max(1,abs(x)) for x,y in zip(q,event["state"],strict=True))):
            raise ValueError("independent root state/residual differs")


def scalar_comparison(trial,profiles,old,p):
    parent = next(r for r in old["rows"] if r["id"] == trial["candidate_id"])["boundary"]["sides"][trial["side_index"]]
    rows = []
    with localcontext() as ctx:
        ctx.prec = 80
        def error(a,b):
            differences = []
            for j in range(3):
                differences.append(abs(run.taylor.exact(a["state"][j])-run.taylor.exact(b["state"][j]))/run.taylor.exact(p["scales"][j]))
            return dict(time=float(abs(run.taylor.exact(a["time"])-run.taylor.exact(b["time"]))),state=float(max(differences)))
        for index in range(len(trial["boxes"])):
            difference = error(profiles[0]["events"][index],profiles[1]["events"][index])
            comparisons = []
            for report in parent["reports"]:
                original = [e for e in report["reconstructed"] if e["accepted"]][index]
                for profile in profiles:
                    d = error(original,profile["events"][index])
                    comparisons.append(dict(method=report["method"],configuration=profile["configuration"],**d,
                        within_original_thresholds=bool(d["time"] <= 1e-7 and d["state"] <= 1e-6)))
            rows.append(dict(index=index,reference_error=difference,
                reference_qualified=bool(difference["time"] <= 1e-12 and difference["state"] <= 1e-9),original_comparisons=comparisons))
    return dict(reference_qualified=all(r["reference_qualified"] for r in rows),events=rows,
                repairs_exp498=False,symbolic_chains_verified=False)


def check_controls(output,receipt):
    if not receipt["passed"] or receipt["new_target_integrations"] != 0 or len(receipt["profiles"]) != 6:
        raise ValueError("complete analytic controls required")
    expected = [(c,k) for c in analytic.CONFIGS for k in ("rotation","near-tangent","polynomial")]
    for saved,(config,kind) in zip(receipt["profiles"],expected,strict=True):
        field = analytic.polynomial() if kind == "polynomial" else analytic.rotation()
        initial = [0,0,1] if kind == "polynomial" else [1,0,0]
        name = config["name"]+"--"+kind+".json.gz"
        header,raw = run.taylor.load_stream(output/name)
        if saved["raw_path"] != name or saved["config"] != config["name"] or saved["kind"] != kind or not saved["passed"]:
            raise ValueError("analytic identity differs")
        if header != dict(label=name,initial=initial,field=field,horizon=4,config=config,scales=analytic.SCALES):
            raise ValueError("analytic header differs")
        check_raw(raw,initial,field,4,config,analytic.SCALES)
        curve = run.taylor.Curve(raw)
        with localcontext() as ctx:
            ctx.prec = 60
            events = saved["events"]
            if len(events) != (2 if kind == "near-tangent" else 1):
                raise ValueError("analytic event count differs")
            for event in events:
                actual = curve.value(D(event["time"]))
                if any(abs(q-D(v)) > D(10)**(-config["digits"]+8)*max(1,abs(q))
                       for q,v in zip(actual,event["state"],strict=True)):
                    raise ValueError("analytic event is not on its stored curve")
            if kind == "rotation":
                error = max(abs(D(events[0]["time"])-analytic.PI),abs(D(events[0]["state"][0])+1))
            elif kind == "near-tangent":
                error = max(abs(analytic.sine(D(e["time"]))-D("0.99999999")) for e in events)
            else:
                error = max(abs(D(events[0]["time"])-2),abs(D(events[0]["state"][2])-D(2).exp()))
            if abs(error-D(saved["error"])) > D("1e-40") or error > D("1e-22"):
                raise ValueError("independent analytic identity failed")


def audit(output,expected_sha,public=False):
    output = Path(output)
    if sha256(output/"summary.json") != expected_sha: raise ValueError("raw summary anchor differs")
    saved = json.loads((output/"summary.json").read_bytes())
    p,old = run.load()
    check_inputs(p,old)
    b = json.loads((output/"binding.json").read_bytes())
    if (saved["binding"] != b or b["plan_sha256"] != sha256(run.PLAN) or b["inputs"] != p["inputs"]
            or b["sources"] != {s:sha256(run.ROOT/s) for s in p["source_paths"]}
            or saved["files"] != inventory(output,omit=("summary.json",)) or saved["target_ivps"] != 64
            or saved["experiment_id"] != "EXP-499" or saved["status"] != "completed"
            or saved["ledger"] != p["ledger"] or [r["id"] for r in saved["rows"]] != [r["id"] for r in p["trials"]]):
        raise ValueError("complete frozen inventory/ledger differs")
    marker = run.ROOT/"artifacts/EXP-499/target-once.json"
    if not public and (sha256(marker) != saved["marker_sha256"] or json.loads(marker.read_bytes()) != b):
        raise ValueError("local attempt witness differs")
    control = json.loads((output/"controls.json").read_bytes())
    check_controls(output/"controls",control)
    names = {"binding.json","controls.json"}|{"controls/"+v["raw_path"] for v in control["profiles"]}
    for trial,row in zip(p["trials"],saved["rows"],strict=True):
        if [v["configuration"] for v in row["profiles"]] != [c["name"] for c in analytic.CONFIGS]:
            raise ValueError("complete profile configurations required")
        for config,profile in zip(p["configurations"],row["profiles"],strict=True):
            label = trial["id"]+"--"+config["name"]
            name = label+".json.gz"
            header,raw = run.taylor.load_stream(output/name)
            if profile["raw_path"] != name or header != dict(label=label,initial=trial["initial"],field=p["field"],
                    horizon=trial["horizon"],config=config,scales=p["scales"]):
                raise ValueError("profile raw identity differs")
            check_raw(raw,trial["initial"],p["field"],trial["horizon"],config,p["scales"])
            curve = run.taylor.Curve(raw)
            if len(profile["events"]) != len(trial["boxes"]) or profile["steps"] != len(raw["steps"]) or profile["maximum_tail"] != raw["maximum_tail"]:
                raise ValueError("profile complete root/mesh count differs")
            for event,box in zip(profile["events"],trial["boxes"],strict=True):
                check_event(curve,event,box,p["section"]["offset"],p["section"]["gate_upper"])
            start = json.loads((output/(label+"-started.json")).read_bytes())
            if {k:v for k,v in start.items() if k != "started_utc"} != dict(id=trial["id"],configuration=config["name"]) or not b["started_utc"] <= start["started_utc"] <= saved["completed_utc"]:
                raise ValueError("profile start identity/time differs")
            if json.loads((output/(label+"-events.json")).read_bytes()) != profile:
                raise ValueError("profile event artifact differs")
            names.update((name,label+"-started.json",label+"-events.json"))
        rebuilt = scalar_comparison(trial,row["profiles"],old,p)
        if not agree(rebuilt,row["analysis"]) or json.loads((output/(trial["id"]+".json")).read_bytes()) != row:
            raise ValueError("independent full decision matrix differs")
        names.add(trial["id"]+".json")
    if set(saved["files"]) != names: raise ValueError("unplanned or missing evidence file")
    return dict(experiment_id="EXP-499",passed=True,source_commit=b["source_commit"],summary_sha256=expected_sha,
        audit_source_sha256=sha256(Path(__file__)),ledger=saved["ledger"],rows=saved["rows"],target_ivps=64,
        reference_qualified=all(r["analysis"]["reference_qualified"] for r in saved["rows"]),
        root_evaluations=sum(len(v["events"]) for r in saved["rows"] for v in r["profiles"]),
        raw_replay_scope="Full decimal coefficient trajectories checked locally; compact table alone does not replay them.",
        local_attempt_witness_checked=not public,new_integrations=0,repairs_exp498=False,symbolic_chains_verified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path,required=True)
    parser.add_argument("--expected-sha256",required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--public",action="store_true")
    args = parser.parse_args()
    value = audit(args.run,args.expected_sha256,args.public)
    write_json(args.output,value)
    print(json.dumps(dict(passed=True,new_integrations=0)))


if __name__ == "__main__": main()

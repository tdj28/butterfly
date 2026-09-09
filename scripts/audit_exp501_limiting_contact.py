#!/usr/bin/env python3
"""Audit every EXP-501 coefficient and decision without generating trajectories."""
import argparse
from decimal import Decimal as D, localcontext
import json
from pathlib import Path

from butterfly.decimal_taylor import exact, load_stream
from butterfly._paired_startup import inventory, sha256, write_json
from scripts import run_exp501_limiting_contact as run
from scripts import exp501_analytic_controls as controls


def check_raw(raw,initial,field,horizon,config):
    if (raw["initial"] != initial or raw["field"] != field or raw["horizon"] != horizon
            or raw["config"] != config or raw["rigorous_enclosure"] is not False):
        raise ValueError("raw input/configuration identity")
    with localcontext() as ctx:
        ctx.prec = config["digits"]+16
        eps = D(10)**(-config["digits"]+8)
        def close(a,b):
            return abs(a-b) <= eps*max(D(1),abs(a),abs(b))
        previous = list(map(D,initial))
        t, end, step = D(0), D(horizon), D(config["step"])
        maxima = [D(0),D(0)]
        for row in raw["steps"]:
            poly = [list(map(D,values)) for values in row["coefficients"]]
            h = D(row["step"])
            if (not close(D(row["time"]),t) or not close(h,min(step,end-t)) or h <= 0
                    or len(poly) != 6 or any(len(q) != config["order"]+1 for q in poly)
                    or not all(v.is_finite() for q in poly for v in q)
                    or not all(close(q[0],v) for q,v in zip(poly,previous,strict=True))):
                raise ValueError("coefficient mesh/continuity")
            for n in range(config["order"]):
                for axis in range(6):
                    terms = [exact(field["constant"][axis]) if n == 0 else D(0)]
                    terms += [exact(v)*poly[j][n] for i,j,v in field["linear"] if i == axis]
                    for i,j,k,v in field["quadratic"]:
                        if i == axis:
                            terms.extend(exact(v)*poly[j][r]*poly[k][n-r] for r in range(n+1))
                    if not close(poly[axis][n+1]*(n+1),sum(terms)):
                        raise ValueError("independent scalar coefficient recurrence")
            powers = [h**n for n in range(config["order"]+1)]
            previous = [sum(v*w for v,w in zip(q,powers,strict=True)) for q in poly]
            if any(abs(v) > (D("1e4") if i < 3 else D("1e12")) for i,v in enumerate(previous)):
                raise ValueError("raw endpoint guard")
            for block,cap in enumerate((D("1e-20"),D("1e-16"))):
                tail = max(sum(abs(poly[i][n]*powers[n]) for n in range(config["order"]-2,config["order"]+1))
                           /exact(run.numeric.SCALES[i % 3]) for i in range(3*block,3*block+3))
                if tail > cap:
                    raise ValueError("raw tail guard")
                maxima[block] = max(maxima[block],tail)
            t = D(row["time"])+h
        if (not raw["steps"] or not close(t,end)
                or not all(close(a,D(b)) for a,b in zip(previous,raw["final"],strict=True))
                or not all(close(a,D(b)) for a,b in zip(maxima,raw["maximum_tails"],strict=True))):
            raise ValueError("raw completion")


def check_shooting(output,saved,c,field,offset,config,label,minimum="1"):
    seen = []
    def replay(iteration,initial,end,f,configuration):
        name = label+f"--iteration-{iteration}.json.gz"
        header,raw = load_stream(output/name)
        if header != dict(initial=initial,field=f,horizon=end,config=configuration):
            raise ValueError("raw header identity")
        check_raw(raw,initial,f,end,configuration)
        seen.append(name)
        return raw,name
    rebuilt,raw = run.numeric.shooting(c,field,offset,config,replay,minimum=minimum)
    if rebuilt != saved:
        raise ValueError("full Newton trace replay differs")
    # Independent target residual/Jacobian evaluation, using Rössler equations.
    if minimum == "1":
        a = exact(field["linear"][3][2])
        with localcontext() as ctx:
            ctx.prec = 70
            for item in saved["trace"]:
                x,y,z = map(D,item["state"])
                wx,wy,_ = map(D,item["tangent"])
                fy = x+a*y
                expected = [y-exact(offset),fy,wy,fy,wx+a*wy,-y-z+a*fy]
                actual = item["residual"]+sum(item["jacobian"],[])
                eps = D(10)**(-config["digits"]+8)
                if any(abs(v-D(w)) > eps*max(1,abs(v)) for v,w in zip(expected,actual,strict=True)):
                    raise ValueError("independent Rössler grazing system differs")
    return raw,seen


def check_controls(output,receipt):
    if receipt["passed"] is not True or receipt["new_target_integrations"] != 0 or len(receipt["profiles"]) != 4:
        raise ValueError("complete analytic controls required")
    for row,(config,kind) in zip(receipt["profiles"],[(c,k) for c in run.numeric.CONFIGS for k in ("rotation","parabola")],strict=True):
        if row["kind"] != kind or row["configuration"] != config["name"]:
            raise ValueError("analytic identity/order")
        c,field,offset = controls.case(kind)
        label = config["name"]+"--"+kind
        check_shooting(output,row["shooting"],c,field,offset,config,label,minimum="0.5")
        if controls.identity(kind,row["shooting"]) != row["error"]:
            raise ValueError("analytic identity differs")
        initial = [str(v) for v in c["initial_state"]+c["initial_tangent"]]
        header,raw = load_stream(output/row["census_raw"])
        end = "4" if kind == "rotation" else "2"
        if header != dict(initial=initial,field=field,horizon=end,config=config):
            raise ValueError("analytic census header")
        check_raw(raw,initial,field,end,config)
        projected = dict(raw,steps=[dict(r,coefficients=r["coefficients"][:3]) for r in raw["steps"]],
            field=dict(constant=field["constant"][:3],linear=[v for v in field["linear"] if v[0] < 3],
                       quadratic=[v for v in field["quadratic"] if v[0] < 3]),scales=run.numeric.SCALES)
        section = dict(offset=0 if kind == "rotation" else "0.25",gate_upper=10)
        proof = json.loads((output/(label+"-certificates.json")).read_bytes())
        result,_ = run.census.profile(projected,section,certificate=proof)
        if result != row["census"] or not result["complete"]:
            raise ValueError("analytic complete certificate replay")


def audit(output,expected_sha,public=False):
    p = run.load()
    output = Path(output)
    if sha256(output/"summary.json") != expected_sha:
        raise ValueError("summary anchor differs")
    saved = json.loads((output/"summary.json").read_bytes())
    b = saved["binding"]
    if (saved["experiment_id"] != "EXP-501" or saved["status"] != "completed"
            or saved["files"] != inventory(output,omit=("summary.json",))
            or b["plan_sha256"] != sha256(run.PLAN) or b["inputs"] != run.INPUTS
            or b["sources"] != {s:sha256(run.ROOT/s) for s in p["source_paths"]}
            or saved["ledger"] != p["ledger"] or len(saved["rows"]) != 8
            or json.loads((output/"binding.json").read_bytes()) != b):
        raise ValueError("complete raw/source binding differs")
    if not public:
        marker = run.ROOT/"artifacts/EXP-501/target-once.json"
        if sha256(marker) != saved["marker_sha256"] or json.loads(marker.read_bytes()) != b:
            raise ValueError("consumed attempt witness differs")
    control = json.loads((output/"controls.json").read_bytes())
    check_controls(output/"controls",control)
    names = {"binding.json","controls.json"}|{"controls/"+n for n in inventory(output/"controls")}
    ivps = 0
    for c,row in zip(p["candidates"],saved["rows"],strict=True):
        if row["id"] != c["id"] or len(row["profiles"]) != 2:
            raise ValueError("complete candidate/profile identity")
        for config,v in zip(run.numeric.CONFIGS,row["profiles"],strict=True):
            label = c["id"]+"--"+config["name"]
            if v["configuration"] != config["name"]:
                raise ValueError("precision order differs")
            raw,paths = check_shooting(output,v["shooting"],c,p["field"],p["section"]["offset"],config,label)
            ivps += len(paths)
            names.update(paths)
            if v["shooting"]["status"] == "qualified":
                with localcontext() as ctx:
                    ctx.prec = config["digits"]
                    end = D(v["shooting"]["trace"][-1]["time"])-D("0.05")
                prefix = run.numeric.prefix_state(raw,end)
                name = label+"-certificates.json"
                rebuilt,_ = run.census.profile(prefix,p["section"],certificate=json.loads((output/name).read_bytes()))
                if rebuilt != v["census"]:
                    raise ValueError("complete prefix census differs")
                names.add(name)
            elif v["census"] is not None:
                raise ValueError("failed root cannot license a prefix")
            start = json.loads((output/(label+"-started.json")).read_bytes())
            if (start["id"] != c["id"] or start["configuration"] != config["name"]
                    or not b["started_utc"] <= start["started_utc"] <= saved["completed_utc"]
                    or json.loads((output/(label+"-result.json")).read_bytes()) != v):
                raise ValueError("profile start/result differs")
            names.update([label+"-started.json",label+"-result.json"])
        if (run.analysis.compare(row["profiles"],c,p["cycles"]) != row["comparison"]
                or json.loads((output/(c["id"]+".json")).read_bytes()) != row):
            raise ValueError("complete contact matrix differs")
        names.add(c["id"]+".json")
        print(json.dumps(dict(audited_candidates=len([n for n in names if n.endswith("--anchor.json")]),audited_ivps=ivps)),flush=True)
    if (set(saved["files"]) != names or ivps != saved["target_ivps"] or ivps > 128
            or run.analysis.aggregate(saved["rows"]) != saved["analysis"]):
        raise ValueError("complete file/count/aggregate identity")
    return dict(experiment_id="EXP-501",passed=True,source_commit=b["source_commit"],summary_sha256=expected_sha,
        audit_source_sha256=sha256(Path(__file__)),plan_sha256=b["plan_sha256"],inputs=b["inputs"],
        rows=saved["rows"],analysis=saved["analysis"],ledger=p["ledger"],target_ivps=ivps,
        raw_replay_scope="Full state/tangent coefficient and prefix-certificate audit performed locally; compact receipt alone cannot repeat it.",
        local_attempt_witness_checked=not public,new_integrations=0,paid_review=p["paid_review"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path,required=True)
    parser.add_argument("--expected-sha256",required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--public",action="store_true")
    args = parser.parse_args()
    write_json(args.output,audit(args.run,args.expected_sha256,args.public))


if __name__ == "__main__":
    main()

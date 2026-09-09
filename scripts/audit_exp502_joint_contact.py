#!/usr/bin/env python3
"""Replay all target evidence and complete response decisions without new IVPs."""
import argparse
from copy import deepcopy
from decimal import Decimal as D, localcontext
import json
from pathlib import Path

import numpy as np
from butterfly._paired_startup import inventory, sha256, write_json
from scripts import run_exp502_joint_contact as run
from scripts import audit_exp497_contact_localization as old
from scripts import audit_exp501_limiting_contact as decimal_audit


def check_scalar(matrix, base, anchor):
    scalar = run.response.scalar_proposal(matrix, base, anchor)
    if scalar is not None and not old.periodic_audit.numeric_equal(scalar, matrix["proposal"]["parameters"]):
        raise ValueError("independent scalar joint step differs")


def synthetic(matrix=None, f0=None, cubic=0.):
    anchor = dict(a=.2,b=.2,c=7.)
    matrix = np.asarray([[2.,.3],[-.4,1.5]] if matrix is None else matrix)
    f0 = np.asarray([.2,-.3] if f0 is None else f0)
    base = [dict(key=[str(i)],value=f0.tolist()) for i in range(256)]
    points = []
    for spec in run.response.stencil(anchor):
        delta = np.array([(spec["parameters"][k]-anchor[k])/h for k,h in zip(run.response.AXES,run.response.INCREMENTS,strict=True)])
        value = f0+matrix@delta+cubic*delta**3
        points.append(dict(spec=spec,qualified=True,vectors=[dict(key=r["key"],value=value.tolist()) for r in base]))
    return anchor,base,points


def response_controls():
    cases = []
    for kind in ("linear","singular","scale-disagreement","missing","unqualified","clipped"):
        anchor,base,points = synthetic(matrix=[[1.,1.],[1.,1.]] if kind == "singular" else None,
            f0=[100.,-200.] if kind == "clipped" else None,cubic=1. if kind == "scale-disagreement" else 0.)
        if kind == "missing":
            points[-1]["vectors"].pop()
        if kind == "unqualified":
            points[-1]["qualified"] = False
        result = run.response.response(points,base,anchor)
        check_scalar(result,base,anchor)
        if result["qualified"] != (kind in ("linear","clipped")):
            raise ValueError("synthetic response qualification failed: "+kind)
        if kind == "linear":
            expected = np.linalg.solve([[2.,.3],[-.4,1.5]],[-.2,.3])
            if not np.allclose(result["unclipped_step"],expected,rtol=1e-12,atol=1e-13):
                raise ValueError("known linear solution")
        if kind == "clipped" and not np.isclose(max(abs(np.array(result["unclipped_step"])*result["clipping_factor"])),10.):
            raise ValueError("radial trust bound")
        cases.append(dict(kind=kind,passed=True,qualified=result["qualified"]))
    return dict(passed=True,cases=cases,target_integrations=0)


def check_guard(raw, main, report, guard):
    t,q = raw["times"],raw["augmented_states"]
    if (t.ndim != 1 or len(t) < 2 or q.shape != (len(t),6) or not bool(raw["success"])
            or t[0] != 0. or t[-1] != guard or not np.all(np.diff(t) > 0) or not np.isfinite(q).all()
            or not np.array_equal(q[0],report["initial_state"]+report["initial_tangent"])
            or main["integration_times"][0] != guard
            or not np.array_equal(q[-1],main["integration_augmented_states"][0])):
        raise ValueError("guard mesh continuity/identity differs")


def check_point(output,row,p,binding,completed):
    spec = row["spec"]
    folds,boundaries,field,section = run.point_inputs(p,spec)
    inputs = dict(spec=spec,folds=folds,boundaries=boundaries,field=field,section=section)
    if json.loads((output/"inputs.json").read_bytes()) != inputs or json.loads((output/"point.json").read_bytes()) != row:
        raise ValueError("point input/output identity")
    names,calls = old.check_cycle(output,row["cycle"],spec,p["cycle_seed"],p["periodic"])
    names.update(("inputs.json","point.json"))
    products = calls
    if len(row["folds"]) != 4 or len(row["boundaries"]) != 8:
        raise ValueError("complete point matrix")
    for c,fold in zip(folds,row["folds"],strict=True):
        rebuilt,paths,count = old.check_fold(output,c,p["fold"],binding,completed)
        if rebuilt != fold:
            raise ValueError("fold raw replay differs")
        names.update(paths)
        calls += count
        products += count
        for method in p["fold"]["solvers"]:
            label = c["id"]+"--"+method
            saved = json.loads((output/(label+".json")).read_bytes())
            for i,entry in enumerate(saved["censuses"]):
                name = label+f"--guard-{i}.npz"
                raw = old.load_raw(output/name)
                main = old.load_raw(output/(label+f"--census-{i}.npz"))
                check_guard(raw,main,entry["report"],p["fold"]["guard"])
                names.add(name)
                calls += 1
    cycles = [dict(method=v["method"],phase=w["phase"],states=w["event_states"]["historical"])
        for v in row["cycle"]["profiles"] for w in v.get("metric",{}).get("windows",[])] if row["cycle"]["status"] == "qualified" else []
    for c,boundary in zip(boundaries,row["boundaries"],strict=True):
        if c["id"] != boundary["id"] or len(boundary["profiles"]) != 2:
            raise ValueError("boundary identity/profile count")
        for config,v in zip(run.numeric.CONFIGS,boundary["profiles"],strict=True):
            label = c["id"]+"--"+config["name"]
            if v["configuration"] != config["name"]:
                raise ValueError("boundary precision order")
            raw,paths = decimal_audit.check_shooting(output,v["shooting"],c,field,section["offset"],config,label)
            names.update(paths)
            calls += len(paths)
            products += len(paths)
            if v["shooting"]["status"] == "qualified":
                with localcontext() as ctx:
                    ctx.prec = config["digits"]
                    end = D(v["shooting"]["trace"][-1]["time"])-D('.05')
                name = label+"-certificates.json"
                rebuilt,_ = run.census.profile(run.numeric.prefix_state(raw,end),section,
                    certificate=json.loads((output/name).read_bytes()))
                if rebuilt != v["census"]:
                    raise ValueError("complete boundary prefix replay")
                names.add(name)
            elif v["census"] is not None:
                raise ValueError("failed root cannot supply census")
            start = json.loads((output/(label+"-started.json")).read_bytes())
            if (start["id"] != c["id"] or start["configuration"] != config["name"]
                    or not binding["started_utc"] <= start["started_utc"] <= completed
                    or json.loads((output/(label+"-result.json")).read_bytes()) != v):
                raise ValueError("boundary start/result")
            names.update((label+"-started.json",label+"-result.json"))
        if (run.boundary_analysis.compare(boundary["profiles"],c,cycles) != boundary["comparison"]
                or json.loads((output/(c["id"]+".json")).read_bytes()) != boundary):
            raise ValueError("boundary full comparison matrix")
        names.add(c["id"]+".json")
    rebuilt = run.summarize(p,row["cycle"],row["folds"],row["boundaries"])
    if any(row[k] != v for k,v in rebuilt.items()):
        raise ValueError("point response/qualification")
    if row["contact"] is not None and not old.periodic_audit.numeric_equal(old.scalar_contact(row["folds"],row["cycle"]),row["contact"]):
        raise ValueError("independent scalar fold distances")
    if set(inventory(output)) != names:
        raise ValueError("complete point raw inventory")
    return names,calls,products


def audit(output,expected_sha):
    p = run.load()
    output = Path(output)
    if sha256(output/"summary.json") != expected_sha:
        raise ValueError("summary anchor")
    saved = json.loads((output/"summary.json").read_bytes())
    b = saved["binding"]
    if (saved["experiment_id"] != "EXP-502" or saved["status"] != "completed"
            or saved["files"] != inventory(output,omit=("summary.json",))
            or b["inputs"] != run.INPUTS or b["plan_sha256"] != sha256(run.PLAN)
            or b["sources"] != {n:sha256(run.ROOT/n) for n in p["source_paths"]}
            or saved["ledger"] != p["ledger"] or json.loads((output/"binding.json").read_bytes()) != b
            or saved["symbolic_chains_verified"] is not False):
        raise ValueError("raw/source/claim binding")
    marker = run.ROOT/"artifacts/EXP-502/target-once.json"
    if sha256(marker) != saved["marker_sha256"] or json.loads(marker.read_bytes()) != b:
        raise ValueError("consumed attempt witness")
    startup = json.loads((output/"startup.json").read_bytes())
    if (not startup["passed"] or not startup["isolated"] or startup["target_integrations"] != 0
            or startup["sources"] != {n:sha256(run.ROOT/n) for n in set(p["source_paths"])|set(run.INPUTS)}
            or json.loads(startup["stdout"]) != dict(valid=True,target_integrations=0,stencil_points=8)):
        raise ValueError("copied source startup")
    old.fold_audit.check_controls(json.loads((output/"fold-controls.json").read_bytes()),p["fold"])
    decimal_audit.check_controls(output/"decimal-controls",json.loads((output/"decimal-controls.json").read_bytes()))
    if json.loads((output/"response-controls.json").read_bytes()) != response_controls():
        raise ValueError("response control replay")
    names = {"binding.json","startup.json","fold-controls.json","decimal-controls.json","response-controls.json","response.json"}
    names |= old.check_periodic_controls(output)
    names |= {"decimal-controls/"+n for n in inventory(output/"decimal-controls")}
    if len(saved["rows"]) != 8 or [r["spec"] for r in saved["rows"]] != p["stencil"]:
        raise ValueError("complete fixed stencil")
    calls,products = 0,0
    for row in saved["rows"]+([saved["proposal"]] if saved["proposal"] is not None else []):
        prefix = row["spec"]["id"]
        paths,count,archived = check_point(output/prefix,row,p,b,saved["completed_utc"])
        names |= {prefix+"/"+n for n in paths}
        calls += count
        products += archived
        print(json.dumps(dict(audited_point=prefix,audited_actual_ivps=calls)),flush=True)
    matrix = run.response.response(saved["rows"],p["base_vectors"],p["anchor"])
    check_scalar(matrix,p["base_vectors"],p["anchor"])
    slots = [dict(spec=s,status="completed") for s in p["stencil"]]+[dict(spec=None,status="not-run",role="proposal")]
    if matrix["qualified"]:
        if saved["proposal"] is None or saved["proposal"]["spec"] != matrix["proposal"]:
            raise ValueError("unique measured proposal required")
        slots[-1].update(spec=matrix["proposal"],status="completed")
    else:
        if saved["proposal"] is not None:
            raise ValueError("failed stencil cannot license proposal")
        slots[-1]["reason"] = matrix["reason"]
    if (matrix != saved["response"] or json.loads((output/"response.json").read_bytes()) != matrix
            or saved["analysis"] != run.response.verdict(matrix,saved["proposal"],p["base_vectors"])
            or set(saved["files"]) != names or calls != saved["target_ivps"] or calls > p["limits"]["target_ivps"]
            or products != saved["inherited_archive_products"] or saved["slots"] != slots):
        raise ValueError("complete response/count/inventory/verdict")
    return dict(experiment_id="EXP-502",passed=True,source_commit=b["source_commit"],summary_sha256=expected_sha,
        plan_sha256=b["plan_sha256"],audit_source_sha256=sha256(Path(__file__)),inputs=p["inputs"],
        rows=saved["rows"],proposal=saved["proposal"],response=matrix,analysis=saved["analysis"],
        ledger=p["ledger"],target_ivps=calls,inherited_archive_products=products,new_integrations=0,
        symbolic_chains_verified=False,paid_review=p["paid_review"],
        raw_replay_scope="All target meshes, decimal coefficients and prefix certificates replayed locally; compact receipt is not the full raw archive.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path,required=True)
    parser.add_argument("--expected-sha256",required=True)
    parser.add_argument("--output",type=Path,required=True)
    a = parser.parse_args()
    write_json(a.output,audit(a.run,a.expected_sha256))


if __name__ == "__main__":
    main()

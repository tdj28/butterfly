#!/usr/bin/env python3
"""Rebuild complete polynomial count certificates before scientific reporting."""
import argparse
import json
from pathlib import Path
import signal

from scripts import run_exp500_polynomial_census as run
from scripts import exp500_census_analysis as analysis


def audit(output,expected_sha,public=False):
    output = Path(output)
    if run.sha256(output/"summary.json") != expected_sha: raise ValueError("census summary anchor differs")
    saved = json.loads((output/"summary.json").read_bytes())
    p,old = run.load()
    raw_summary = run.authenticate_raw(p)
    binding = json.loads((output/"binding.json").read_bytes())
    if (saved["experiment_id"] != "EXP-500" or saved["status"] != "completed" or saved["profiles"] != 64
            or saved["new_integrations"] != 0 or saved["binding"] != binding or saved["ledger"] != old["ledger"]
            or binding["sources"] != {s:run.sha256(run.ROOT/s) for s in p["source_paths"]}
            or binding["inputs"] != p["inputs"] or binding["raw_summary_sha256"] != run.RAW_SHA
            or binding["plan_sha256"] != run.sha256(run.PLAN)
            or saved["files"] != run.inventory(output,omit=("summary.json",))
            or [r["id"] for r in saved["rows"]] != [r["id"] for r in p["trials"]]):
        raise ValueError("complete frozen census identities/inventory differ")
    marker = run.ROOT/"artifacts/EXP-500/analysis-once.json"
    if not public and (run.sha256(marker) != saved["marker_sha256"] or json.loads(marker.read_bytes()) != binding):
        raise ValueError("local analysis witness differs")
    def forbidden(*args,**kwargs): raise RuntimeError("census audit must not integrate")
    run.taylor.integrate = forbidden
    controls = json.loads((output/"controls.json").read_bytes())
    known = json.loads((run.RAW/"controls.json").read_bytes())["profiles"]
    expected_controls = [(c,k) for c in run.parent.run.CONFIGS for k in ("rotation","near-tangent","polynomial")]
    if not controls["passed"] or controls["new_integrations"] != 0 or len(controls["profiles"]) != 6:
        raise ValueError("complete controls required")
    files = {"binding.json","controls.json"}
    for (config,kind),row in zip(expected_controls,controls["profiles"],strict=True):
        name = config["name"]+"--"+kind+".json.gz"
        _,raw = run.taylor.load_stream(run.RAW/"controls"/name)
        proof = json.loads((output/"controls"/(name+".json")).read_bytes())
        section = dict(offset="0.99999999" if kind == "near-tangent" else (2 if kind == "polynomial" else 0),gate_upper=10)
        replay,_ = analysis.profile(raw,section,certificate=proof["certificates"])
        baseline = next(v for v in known if v["config"] == config["name"] and v["kind"] == kind)["events"]
        if kind == "rotation": baseline = [dict(time="0",state=raw["initial"])]+baseline
        identity = analysis.compare_events(replay["events"],baseline,raw["scales"])
        expected = dict(configuration=config["name"],kind=kind,roots=len(replay["events"]),identity=identity,passed=True)
        if (row != expected or not identity["passed"] or replay != proof["result"] or not replay["complete"]
                or len(replay["events"]) != (1 if kind == "polynomial" else 2)
                or proof["raw_sha256"] != run.sha256(run.RAW/"controls"/name)):
            raise ValueError("analytic census replay differs")
        files.add("controls/"+name+".json")
    segments = 0
    for trial,row,prior in zip(p["trials"],saved["rows"],old["rows"],strict=True):
        if [r["configuration"] for r in row["profiles"]] != [v["configuration"] for v in trial["profiles"]]:
            raise ValueError("all configurations required")
        for item,profile in zip(trial["profiles"],row["profiles"],strict=True):
            label = trial["id"]+"--"+item["configuration"]
            start = json.loads((output/(label+"-started.json")).read_bytes())
            if ({k:v for k,v in start.items() if k != "started_utc"} != dict(id=trial["id"],configuration=item["configuration"])
                    or not binding["started_utc"] <= start["started_utc"] <= saved["completed_utc"]):
                raise ValueError("profile start witness differs")
            _,raw = run.taylor.load_stream(run.RAW/item["raw_path"])
            proof = json.loads((output/(label+"-certificates.json")).read_bytes())
            replay,_ = analysis.profile(raw,p["section"],certificate=proof)
            expected_profile = dict(configuration=item["configuration"],raw_path=item["raw_path"],
                raw_sha256=raw_summary["files"][item["raw_path"]]["sha256"],analysis=replay)
            if expected_profile != profile or json.loads((output/(label+"-result.json")).read_bytes()) != profile:
                raise ValueError("complete profile census/geometry replay differs")
            segments += replay["segments"]
            files.update((label+"-started.json",label+"-certificates.json",label+"-result.json"))
        if (analysis.compare(row["profiles"],prior,p["scales"]) != row["comparison"]
                or json.loads((output/(trial["id"]+".json")).read_bytes()) != row):
            raise ValueError("complete paired/nomination comparisons differ")
        files.add(trial["id"]+".json")
        print(json.dumps(dict(audited_inputs=saved["rows"].index(row)+1)),flush=True)
    if set(saved["files"]) != files or saved["segments"] != segments:
        raise ValueError("complete file/segment census differs")
    return dict(experiment_id="EXP-500",passed=True,source_commit=binding["source_commit"],
        summary_sha256=expected_sha,audit_source_sha256=run.sha256(Path(__file__)),parent_sha256=run.PARENT_SHA,
        raw_summary_sha256=run.RAW_SHA,ledger=saved["ledger"],rows=saved["rows"],profiles=64,segments=segments,
        qualified=all(r["comparison"]["qualified"] for r in saved["rows"]),new_integrations=0,
        local_attempt_witness_checked=not public,repairs_exp498=False,symbolic_chains_verified=False,
        exact_flow_all_roots_proved=False,
        audit_scope="Exact polynomial leaf counts by direct affine expansion; shared interval-classification replay. Full certificates and coefficient archives remain local.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path,required=True)
    parser.add_argument("--expected-sha256",required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--public",action="store_true")
    args = parser.parse_args()
    def timeout(*_): raise TimeoutError("EXP-500 audit deadline")
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(7200)
    try:
        result = audit(args.run,args.expected_sha256,args.public)
        run.write_json(args.output,result)
        print(json.dumps(dict(passed=True,new_integrations=0)))
    finally: signal.alarm(0)


if __name__ == "__main__": main()

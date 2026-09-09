#!/usr/bin/env python3
"""Explicit post-run half-period diagnostic; never changes primary verdicts."""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np

from scripts import run_exp494_periodic_winding_transport as run

SUMMARY = "3a51ec4aaf07d15975c25e9dc47a907b0e43cc6d9a8cee7fddfe1d3f85263e6e"
IDS = ["local-a025-c083--aminus--04", "local-a027-c083--aminus--04"]


def shorter_metric(raw, observation, period, origin, field):
    return run.geometry.measure_cycle(raw["times"],raw["states"],observation["extrema"],observation["events"],
                                       period/2,origin,field)


def analyze(directory):
    if run.sha256(directory/"summary.json") != SUMMARY:
        raise ValueError("fixed completed primary data required")
    s = json.loads((directory/"summary.json").read_bytes())
    failed = [r for r in s["rows"] if r["status"] == "unqualified"]
    if [r["spec"]["id"] for r in failed] != IDS:
        raise ValueError("retain the complete two-node failure set")
    results = []
    for row in failed:
        par = run.RosslerParameters(**row["spec"]["parameters"])
        field = lambda t,q:run.rossler_rhs(t,q,par)
        profiles = []
        if [p["method"] for p in row["profiles"]] != ["DOP853","Radau"]:
            raise ValueError("complete paired-method set required")
        for p in row["profiles"]:
            name = row["spec"]["id"]+"--"+p["method"]+"--observation.npz"
            if run.sha256(directory/name) != s["files"][name]["sha256"]:
                raise ValueError("bound observation changed")
            if p["qualified"] or any(w["conditional_minimal_period"] for w in p["metric"]["windows"]):
                raise ValueError("original nonprimitive failures must remain failures")
            with np.load(directory/name,allow_pickle=False) as f:
                raw = {k:f[k] for k in f.files}
            metric = shorter_metric(raw,p["observation"],p["correction"]["period_time"],run.rossler_equilibria(par)[0],field)
            profiles.append(dict(method=p["method"],candidate_period=p["correction"]["period_time"]/2,
                original_period=p["correction"]["period_time"],original_profile_qualified=False,metric=metric))
        paired = [run.geometry.compare_windows(a,b) for a,b in zip(profiles[0]["metric"]["windows"],profiles[1]["metric"]["windows"],strict=True)]
        results.append(dict(id=row["spec"]["id"],parameters=row["spec"]["parameters"],profiles=profiles,paired=paired,
            half_period_qualified=bool(all(p["metric"]["qualified"] for p in profiles) and all(w["passed"] for w in paired)),
            primary_status="unqualified"))
    return dict(experiment_id="EXP-494",analysis="post-run-shorter-cycle-diagnostic",parent_summary_sha256=SUMMARY,
        rows=results,new_integrations=0,source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        analysis_sha256=run.sha256(Path(__file__)),primary_verdict_replaced=False,
        scope="Conditional numerical period check on already-inspected failed profiles, not a period-doubling bifurcation or Jones insertion-arrow certificate.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    result = analyze(args.run)
    run.write_json(args.output,result)
    print(json.dumps(dict(rows=len(result["rows"]),qualified=sum(r["half_period_qualified"] for r in result["rows"]),new_integrations=0)))


if __name__ == "__main__":
    main()

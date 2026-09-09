#!/usr/bin/env python3
"""Replay public all-event comparisons; not the private coefficient proof audit."""
import argparse
import json
import math
from pathlib import Path

from scripts import run_exp500_polynomial_census as run
from scripts import audit_exp500_polynomial_census as audit
from scripts import exp500_census_analysis as analysis

SOURCE = "966fd814bb62bbb42947fa357070a38c8f22bd11"
SUMMARY = "418d3c7ec4a9e87be6db9cda485d2674c7b31d6387418fcdfb2f38b688514773"


def validate(result):
    p,old = run.load()
    if (result.get("experiment_id") != "EXP-500" or result.get("passed") is not True
            or result.get("source_commit") != SOURCE or result.get("audit_source_sha256") != run.sha256(Path(audit.__file__))
            or result.get("parent_sha256") != run.PARENT_SHA or result.get("raw_summary_sha256") != run.RAW_SHA
            or result.get("summary_sha256") != SUMMARY
            or result.get("ledger") != p["ledger"] or result.get("profiles") != 64
            or result.get("new_integrations") != 0 or result.get("repairs_exp498") is not False
            or result.get("symbolic_chains_verified") is not False or result.get("exact_flow_all_roots_proved") is not False
            or [r["id"] for r in result.get("rows",[])] != [r["id"] for r in p["trials"]]):
        raise ValueError("complete source-bound census result required")
    segments = 0
    for trial,row,prior in zip(p["trials"],result["rows"],old["rows"],strict=True):
        if [v["configuration"] for v in row["profiles"]] != [v["configuration"] for v in trial["profiles"]]:
            raise ValueError("complete ordered profiles required")
        for declared,profile,original in zip(trial["profiles"],row["profiles"],prior["profiles"],strict=True):
            a = profile["analysis"]
            if (profile["raw_path"] != declared["raw_path"] or a["segments"] != original["steps"]
                    or a["polynomial_census_only"] is not True
                    or a["complete"] != (not a["unresolved"] and not a["join_failures"]
                                           and all(e["classification_qualified"] for e in a["events"]))):
                raise ValueError("profile identity/completeness differs")
            segments += a["segments"]
            times = [analysis.exact(e["time"]) for e in a["events"]]
            if any(x >= y for x,y in zip(times,times[1:])): raise ValueError("events not strictly ordered")
            for event in a["events"]:
                if (len(event["state"]) != 3 or not all(math.isfinite(float(v)) for v in event["state"])
                        or event["accepted"] != (event["classification_qualified"] and event["direction"] == -1
                        and event["half_plane"] == "inside" and event["time_class"] == "after")):
                    raise ValueError("event acceptance/finiteness differs")
        if analysis.compare(row["profiles"],prior,p["scales"]) != row["comparison"]:
            raise ValueError("complete all-event comparison differs")
    if result["segments"] != segments or result["qualified"] != all(r["comparison"]["qualified"] for r in result["rows"]):
        raise ValueError("complete aggregate census differs")
    profiles = [v["analysis"] for r in result["rows"] for v in r["profiles"]]
    events = [e for a in profiles for e in a["events"]]
    return dict(verified=True,inputs=len(result["rows"]),profiles=result["profiles"],segments=segments,
        qualified=result["qualified"],new_integrations=0,
        plane_roots=len(events),accepted=sum(e["accepted"] for e in events),
        initial=sum(e["time_class"] == "initial" for e in events),
        upward_outside=sum(e["direction"] == 1 and e["half_plane"] == "outside" for e in events),
        complete_profiles=sum(a["complete"] for a in profiles),
        unresolved_regions=sum(len(a["unresolved"]) for a in profiles),join_failures=sum(len(a["join_failures"]) for a in profiles),
        scope="Public comparison replay only; coefficient/certificate audit needs retained local raw files.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result",type=Path,required=True)
    parser.add_argument("--expected-sha256",required=True)
    args = parser.parse_args()
    if run.sha256(args.result) != args.expected_sha256: raise ValueError("public result hash differs")
    print(json.dumps(validate(json.loads(args.result.read_bytes()))))


if __name__ == "__main__": main()

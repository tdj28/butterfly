#!/usr/bin/env python3
"""Post-run public comparison replay; not the full coefficient/certificate audit."""
import argparse
from decimal import Decimal as D
import json
from pathlib import Path
from scripts import run_exp501_limiting_contact as run
from scripts import audit_exp501_limiting_contact as audit

SOURCE = "a8816a5cd82eae79b6a8947bbc2876f767063771"
SUMMARY = "3e47be50a4633dac544d12a1a9fdb2c0bd63430549f02afbfe8d88a3bbb0cba2"


def validate(result):
    p = run.load()
    if (result.get("experiment_id") != "EXP-501" or result.get("passed") is not True
            or result.get("source_commit") != SOURCE or result.get("summary_sha256") != SUMMARY
            or result.get("audit_source_sha256") != run.sha256(Path(audit.__file__))
            or result.get("plan_sha256") != run.sha256(run.PLAN) or result.get("inputs") != run.INPUTS
            or result.get("ledger") != p["ledger"] or result.get("new_integrations") != 0
            or result.get("paid_review") != p["paid_review"]
            or [r["id"] for r in result.get("rows",[])] != [c["id"] for c in p["candidates"]]):
        raise ValueError("complete source-bound public receipt required")
    ivps, qualified_profiles, accepted = 0, 0, 0
    for candidate,row in zip(p["candidates"],result["rows"],strict=True):
        if [v["configuration"] for v in row["profiles"]] != [c["name"] for c in run.numeric.CONFIGS]:
            raise ValueError("both ordered configurations required")
        for v in row["profiles"]:
            trace = v["shooting"]["trace"]
            if len(trace) > 8 or [r["iteration"] for r in trace] != list(range(len(trace))):
                raise ValueError("bounded ordered iteration trace required")
            ivps += len(trace)
            if v["shooting"]["status"] == "qualified":
                if (not trace or not trace[-1]["converged"] or not trace[-1]["nondegenerate"]
                        or any(not D(x).is_finite() or abs(D(x)) > D("1e-24") for x in trace[-1]["residual"])
                        or abs(D(trace[-1]["jacobian"][0][0])) < 1 or abs(D(trace[-1]["jacobian"][1][1])) < 1):
                    raise ValueError("compact root qualification differs")
                census = v["census"]
                if census["complete"] != (not census["unresolved"] and not census["join_failures"]
                                            and all(e["classification_qualified"] for e in census["events"])):
                    raise ValueError("compact census completeness differs")
                events = [e for e in census["events"] if e["accepted"]]
                qualified_profiles += census["complete"] and len(events) == candidate["accepted_prefix"]
                accepted += len(events)
            elif v["census"] is not None:
                raise ValueError("failed shooting cannot license a census")
        if run.analysis.compare(row["profiles"],candidate,p["cycles"]) != row["comparison"]:
            raise ValueError("all-event contact comparison differs")
    if (ivps != result["target_ivps"] or ivps > 128
            or run.analysis.aggregate(result["rows"]) != result["analysis"]):
        raise ValueError("complete aggregate differs")
    return dict(verified=True,candidates=len(result["rows"]),qualified_profiles=qualified_profiles,
                target_ivps=ivps,accepted_prefix_events=accepted,analysis=result["analysis"],
                proximate_cells=sum(c["proximate"] for r in result["rows"] for c in r["comparison"]["comparisons"]),
                scope="Public compact comparison replay only; full raw trajectory audit requires retained local archives.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result",type=Path,required=True)
    parser.add_argument("--expected-sha256",required=True)
    args = parser.parse_args()
    if run.sha256(args.result) != args.expected_sha256:
        raise ValueError("public receipt hash differs")
    print(json.dumps(validate(json.loads(args.result.read_bytes()))))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Replay compact EXP-503 comparisons; this is not the full raw-data audit."""
import argparse
import hashlib
import json
from pathlib import Path

from butterfly._paired_startup import sha256
from scripts import run_exp502_joint_contact as run
from scripts import audit_exp502_joint_contact as audit
from scripts import run_exp503_joint_continuation as continuation

# Only reconstructed floating arithmetic uses this existing scalar-audit bound.
# Input bytes, source hashes, discrete identities and every gate remain exact.
# This public replay does not change the frozen, full raw-data audit.
numeric_equal = audit.old.periodic_audit.numeric_equal


def verify(path, expected_sha):
    path = Path(path)
    if sha256(path) != expected_sha:
        raise ValueError("public receipt hash differs")
    p = run.load()
    policy = json.loads(continuation.PLAN.read_bytes())
    saved = json.loads(path.read_bytes())
    if (saved["experiment_id"] != "EXP-503" or saved["passed"] is not True
            or saved["base_source_commit"] != continuation.BASE_SOURCE
            or saved["plan_sha256"] != sha256(continuation.PLAN)
            or policy["base_plan_sha256"] != sha256(run.PLAN)
            or policy["original"]["binding"]["inputs"] != p["inputs"] or saved["ledger"] != p["ledger"]
            or saved["original_failure_sha256"] != policy["original"]["failure_sha256"]
            or saved["original_completed_prefix"] != policy["original"]["completed_prefix"]
            or saved["original_reserved_ivps"] != policy["original"]["reserved_ivps"]
            or any(sha256(run.ROOT/n) != h for n,h in policy["original"]["binding"]["sources"].items())
            or saved["symbolic_chains_verified"] is not False or saved["new_integrations"] != 0
            or saved["original_attempt_reset"] is not False
            or saved["paid_review"] != p["paid_review"]):
        raise ValueError("public source/input/claim binding differs")
    if len(saved["rows"]) != 8 or [r["spec"] for r in saved["rows"]] != p["stencil"]:
        raise ValueError("complete fixed stencil required")
    points = saved["rows"]+([saved["proposal"]] if saved["proposal"] is not None else [])
    if len(saved["point_counts"]) != len(points):
        raise ValueError("complete point-count ledger required")
    for index,(row,count) in enumerate(zip(points,saved["point_counts"],strict=True)):
        point_bytes = (json.dumps(row,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()
        reused = (index < policy["original"]["completed_prefix"] if index < 8 else
                  policy["original"]["slots"][-1]["status"] == "completed")
        if (count["id"] != row["spec"]["id"] or hashlib.sha256(point_bytes).hexdigest() != count["point_sha256"]
                or count["provenance"] != ("original" if reused else "continuation")
                or type(count["target_ivps"]) is not int or count["target_ivps"] <= 0
                or type(count["inherited_archive_products"]) is not int
                or not 0 < count["inherited_archive_products"] <= count["target_ivps"]):
            raise ValueError("compact point byte identity/provenance/counts differ")
        if reused and policy["original"]["files"][row["spec"]["id"]+"/point.json"]["sha256"] != count["point_sha256"]:
            raise ValueError("original completed checkpoint differs")
        folds,boundaries,_,_ = run.point_inputs(p,row["spec"])
        if ([f["id"] for f in row["folds"]] != [c["id"] for c in folds]
                or [b["id"] for b in row["boundaries"]] != [c["id"] for c in boundaries]
                or row["cycle"]["spec"] != row["spec"]):
            raise ValueError("complete point identity differs")
        pair = run.previous.cycles_run.compare_profiles(row["cycle"]["profiles"],p["periodic"])
        counts = pair["passed"] and all(w["counts"] == dict(historical=6,barrio=8)
            for v in row["cycle"]["profiles"] for w in v["metric"]["windows"])
        if not numeric_equal(pair,row["cycle"]["pair"]) or row["cycle"]["status"] != ("qualified" if counts else "unqualified"):
            raise ValueError("compact cycle qualification differs")
        cycles = [dict(method=v["method"],phase=w["phase"],states=w["event_states"]["historical"])
            for v in row["cycle"]["profiles"] for w in v.get("metric",{}).get("windows",[])] if counts else []
        for c,boundary in zip(boundaries,row["boundaries"],strict=True):
            if run.boundary_analysis.compare(boundary["profiles"],c,cycles) != boundary["comparison"]:
                raise ValueError("compact boundary comparisons differ")
        rebuilt = run.summarize(p,row["cycle"],row["folds"],row["boundaries"])
        if any(not numeric_equal(row[k],v) for k,v in rebuilt.items()):
            raise ValueError("compact point comparisons differ")
        if row["contact"] is not None and not audit.old.periodic_audit.numeric_equal(
                audit.old.scalar_contact(row["folds"],row["cycle"]),row["contact"]):
            raise ValueError("separate scalar fold comparison differs")
    matrix = run.response.response(saved["rows"],p["base_vectors"],p["anchor"])
    audit.check_scalar(matrix,p["base_vectors"],p["anchor"])
    if not numeric_equal(matrix,saved["response"]):
        raise ValueError("complete response reconstruction differs")
    if matrix["qualified"]:
        if saved["proposal"] is None or not numeric_equal(saved["proposal"]["spec"],matrix["proposal"]):
            raise ValueError("unique measured proposal required")
    elif saved["proposal"] is not None:
        raise ValueError("unqualified response cannot license proposal")
    if not numeric_equal(saved["analysis"],run.response.verdict(matrix,saved["proposal"],p["base_vectors"])):
        raise ValueError("public verdict differs")
    calls = sum(c["target_ivps"] for c in saved["point_counts"])
    fresh = sum(c["target_ivps"] for c in saved["point_counts"] if c["provenance"] == "continuation")
    if (calls != saved["completed_matrix_ivps"] or fresh != saved["new_target_ivps"]
            or sum(c["inherited_archive_products"] for c in saved["point_counts"]) != saved["inherited_archive_products"]
            or calls-fresh > saved["original_reserved_ivps"]
            or fresh+saved["original_reserved_ivps"] > policy["limits"]["cumulative_reserved_ivps"]):
        raise ValueError("compact integration accounting differs")
    return dict(passed=True,experiment_id="EXP-503",stencil_points=8,
        measured_proposal=saved["proposal"] is not None,analysis=saved["analysis"],
        new_integrations=0,full_raw_audit_repeated=False,symbolic_chains_verified=False,
        floating_replay_tolerance=dict(rtol=1e-12,atol=1e-13,discrete_gates="exact"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result",type=Path,required=True)
    parser.add_argument("--expected-sha256",required=True)
    a = parser.parse_args()
    print(json.dumps(verify(a.result,a.expected_sha256),sort_keys=True))


if __name__ == "__main__":
    main()

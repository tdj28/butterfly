#!/usr/bin/env python3
"""Audit every original/new complete point and preserve failed-run provenance."""
import argparse
import json
from pathlib import Path

from butterfly._paired_startup import inventory,sha256,write_json
from scripts import run_exp503_joint_continuation as run


def audit(output,original,expected_sha):
    p,numerical = run.load(original),run.base.load()
    output,original = Path(output),Path(original)
    if sha256(output/"summary.json") != expected_sha:
        raise ValueError("continuation summary anchor differs")
    saved = json.loads((output/"summary.json").read_bytes())
    b = json.loads((output/"binding.json").read_bytes())
    if (saved["experiment_id"] != "EXP-503" or saved["status"] != "completed"
            or saved["binding"] != b or b["plan_sha256"] != sha256(run.PLAN)
            or b["sources"] != {n:sha256(run.ROOT/n) for n in p["source_paths"]}
            or b["original_failure_sha256"] != p["original"]["failure_sha256"]
            or saved["original_failure_sha256"] != p["original"]["failure_sha256"]
            or saved["files"] != inventory(output,omit=("summary.json",))
            or saved["ledger"] != numerical["ledger"] or saved["symbolic_chains_verified"] is not False
            or saved["original_attempt_reset"] is not False
            or saved["original_reserved_ivps"] != p["original"]["reserved_ivps"]):
        raise ValueError("continuation source/raw/claim binding")
    marker = run.ROOT/"artifacts/EXP-503/target-once.json"
    if sha256(marker) != saved["marker_sha256"] or json.loads(marker.read_bytes()) != b:
        raise ValueError("new attempt marker identity")
    startup = json.loads((output/"startup.json").read_bytes())
    if (not startup["passed"] or not startup["isolated"] or startup["new_integrations"] != 0
            or startup["sources"] != {n:sha256(run.ROOT/n) for n in set(p["source_paths"])|set(run.base.INPUTS)}
            or json.loads(startup["stdout"]) != dict(valid=True,new_integrations=0,reused_stencil_points=p["original"]["completed_prefix"])):
        raise ValueError("copied-source continuation startup")
    if run.replay_controls(original,numerical) != json.loads((output/"control-replay.json").read_bytes()):
        raise ValueError("original control replay differs")
    if len(saved["rows"]) != 8 or [r["spec"] for r in saved["rows"]] != numerical["stencil"]:
        raise ValueError("complete fixed matrix required")
    progress = [dict(spec=s,provenance="original" if i < p["original"]["completed_prefix"] else "continuation",status="completed")
                for i,s in enumerate(numerical["stencil"])]+[dict(spec=None,provenance=None,status="not-run",role="proposal")]
    matrix = run.base.response.response(saved["rows"],numerical["base_vectors"],numerical["anchor"])
    run.prior_audit.check_scalar(matrix,numerical["base_vectors"],numerical["anchor"])
    if matrix["qualified"]:
        if saved["proposal"] is None or saved["proposal"]["spec"] != matrix["proposal"]:
            raise ValueError("exact sole proposal required")
        previous = p["original"]["slots"][-1]
        if previous["spec"] is not None and previous["spec"] != matrix["proposal"]:
            raise ValueError("resource failure cannot change proposal")
        progress[-1].update(spec=matrix["proposal"],provenance="original" if previous["status"] == "completed" else "continuation",status="completed")
    else:
        if saved["proposal"] is not None or p["original"]["slots"][-1]["status"] != "not-run":
            raise ValueError("unqualified response cannot license proposal")
        progress[-1]["reason"] = matrix["reason"]
    if (progress != saved["progress"] or matrix != saved["response"]
            or matrix != json.loads((output/"response.json").read_bytes())
            or saved["analysis"] != run.base.response.verdict(matrix,saved["proposal"],numerical["base_vectors"])):
        raise ValueError("combined response/provenance/verdict")
    names = {"binding.json","startup.json","control-replay.json","response.json"}
    total_calls,new_calls,products = 0,0,0
    point_counts = []
    for row,entry in zip(saved["rows"]+([saved["proposal"]] if saved["proposal"] is not None else []),
            [r for r in progress if r["status"] == "completed"],strict=True):
        reused = entry["provenance"] == "original"
        root = original if reused else output
        binding = p["original"]["binding"] if reused else b
        paths,calls,archived = run.prior_audit.check_point(root/row["spec"]["id"],row,numerical,binding,saved["completed_utc"])
        total_calls += calls
        products += archived
        point_counts.append(dict(id=row["spec"]["id"],provenance=entry["provenance"],target_ivps=calls,
                                 inherited_archive_products=archived,point_sha256=sha256(root/row["spec"]["id"]/"point.json")))
        if not reused:
            new_calls += calls
            names |= {row["spec"]["id"]+"/"+n for n in paths}
        print(json.dumps(dict(audited_point=row["spec"]["id"],provenance=entry["provenance"],completed_matrix_ivps=total_calls)),flush=True)
    if (names != set(saved["files"]) or new_calls != saved["new_target_ivps"]
            or total_calls-new_calls > p["original"]["reserved_ivps"]
            or new_calls+p["original"]["reserved_ivps"] > p["limits"]["cumulative_reserved_ivps"]):
        raise ValueError("combined raw inventory/attempt accounting")
    return dict(experiment_id="EXP-503",passed=True,source_commit=b["source_commit"],summary_sha256=expected_sha,
        plan_sha256=b["plan_sha256"],audit_source_sha256=sha256(Path(__file__)),base_source_commit=run.BASE_SOURCE,
        original_failure_sha256=p["original"]["failure_sha256"],original_completed_prefix=p["original"]["completed_prefix"],
        rows=saved["rows"],proposal=saved["proposal"],response=matrix,analysis=saved["analysis"],ledger=numerical["ledger"],
        point_counts=point_counts,completed_matrix_ivps=total_calls,new_target_ivps=new_calls,
        original_reserved_ivps=p["original"]["reserved_ivps"],inherited_archive_products=products,
        new_integrations=0,paid_review=p["paid_review"],symbolic_chains_verified=False,original_attempt_reset=False,
        raw_replay_scope="Every complete original/new point audited; incomplete original attempts remain hash-inventoried, not promoted into completed evidence.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",type=Path,required=True)
    parser.add_argument("--original-run",type=Path,required=True)
    parser.add_argument("--expected-sha256",required=True)
    parser.add_argument("--output",type=Path,required=True)
    a = parser.parse_args()
    write_json(a.output,audit(a.run,a.original_run,a.expected_sha256))


if __name__ == "__main__":
    main()

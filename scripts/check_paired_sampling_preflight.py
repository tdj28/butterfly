#!/usr/bin/env python3
"""EXP-481 draft integrity preflight; target execution deliberately unavailable."""
import argparse
import json
from pathlib import Path

from scripts import run_symbolic_center_pilot as evidence

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "experiments/manifests/EXP-481-paired-sampling-draft.json"
IDS = ["local-a025-c083", "local-a027-c083"]
INPUT_HASHES = {"candidates": "71aab52016abc8163887b2bdfd4e8124bde0e436be2239751f19d29bed490012",
    "nominations": "4147ff20adefb6adf536137cb0a92809446ce66d40c20b6c00f909fa6235755f",
    "event_qualification": "05454ac4ed6a7c7618809303bf99aca6fd73e94a6575ecf2ee9bdb3cae55a557"}
MISSING_DECISIONS = ["global_seed_table_and_distribution", "capture_reference_provenance_and_geometry",
    "common_population_and_censoring", "integration_profiles", "capture_and_event_tolerances",
    "physical_time_windows", "record_and_process_limits", "trajectory_or_event_weighting",
    "seed_level_holdout_and_bootstrap", "scalar_coordinates", "adequacy_and_support",
    "critical_membership", "review_and_adjudication"]


def prepare(plan, root=ROOT):
    if (plan.get("schema") != "butterfly.paired-sampling-draft.v1" or plan.get("experiment_id") != "EXP-481"
            or plan.get("status") != "design-incomplete" or plan.get("execution_authorized") is not False
            or plan.get("review") is not None or plan.get("decisions") != {} or plan.get("candidate_ids") != IDS):
        raise ValueError("this preflight handles the incomplete, unauthorized design only")
    if set(plan["inputs"]) != set(INPUT_HASHES):
        raise ValueError("missing or unexpected input")
    payloads = {}
    for name, expected in INPUT_HASHES.items():
        descriptor = plan["inputs"][name]
        if descriptor["sha256"] != expected:
            raise ValueError("input differs from independently anchored historical evidence")
        payloads[name] = json.loads(evidence.checked_input(root, descriptor))
    if payloads["nominations"]["nomination_result"]["direct_candidate_ids"] != IDS:
        raise ValueError("ordered complete nomination set differs")
    candidates = {row["id"]: row for row in payloads["candidates"]["candidates"]}
    if not all(candidates[name]["passed"] for name in IDS):
        raise ValueError("prior candidate input not qualified")
    qualification = payloads["event_qualification"]
    if (qualification["experiment_id"] != "EXP-480" or qualification["passed"] is not True
            or qualification["case_outcomes"] != [{"candidate_id": name, "outcome": "qualified"} for name in IDS]):
        raise ValueError("both prior event qualifications required")
    return {"mechanical_preflight_passed": True, "candidate_ids": IDS,
            "scientific_plan_complete": False, "target_execution_authorized": False,
            "missing_decisions": MISSING_DECISIONS, "target_trajectories_generated": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--mode", choices=("preflight", "execute"), default="preflight")
    args = parser.parse_args()
    if args.mode == "execute":
        raise ValueError("EXP-481 target execution is unavailable: complete reviewed plan and target runner required")
    raw = PLAN.read_bytes()
    source = evidence.source_binding(ROOT, args.source_commit, PLAN, raw)
    result = prepare(json.loads(raw))
    result["source"] = source
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

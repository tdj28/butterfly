#!/usr/bin/env python3
"""Publish a minimal receipt for an owned EXP-477 failure before qualification.

Read saved local records only. Never read .env, contact a provider, retry a
worker, or copy private identity/credential/provider-response fields. The cost
calculation is conditional on the requested hourly cap, not an invoice or a
verified actual-rate bound when deployment qualification never completed.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING
import hashlib
import json
import math
from pathlib import Path
import re

from scripts import run_symbolic_center_pilot as pilot


MAXIMUM_JSON_BYTES = 4 * 1048576
SOURCE_PRODUCERS = ("scripts/runpod_symbolic_worker.py", "scripts/execute_symbolic_center_cloud.py")


def read_json(path):
    path = Path(path)
    if any(part.is_symlink() for part in (path, *path.parents)) or not path.is_file() or path.stat().st_size > MAXIMUM_JSON_BYTES:
        raise ValueError("input must be a bounded regular local JSON file without symlink ancestors")
    raw = path.read_bytes()
    if len(raw) > MAXIMUM_JSON_BYTES:
        raise ValueError("JSON input exceeded its bound while reading")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("input must be a JSON object")
    return value, {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def number(value, name, *, minimum=0, maximum=None):
    if (type(value) not in (int, float) or not math.isfinite(value) or value < minimum
            or (maximum is not None and value > maximum)):
        raise ValueError(f"invalid finite {name}")
    return value


def summarize(lifecycle, ownership, preparation, *, input_hashes, source_inventory, producer_sha256):
    if (not isinstance(input_hashes, dict) or set(input_hashes) != {"lifecycle", "ownership", "preparation", "source_inventory"}
            or any(not isinstance(row, dict) or set(row) != {"sha256", "bytes"}
                   or not isinstance(row["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])
                   or type(row["bytes"]) is not int or not 0 <= row["bytes"] <= MAXIMUM_JSON_BYTES
                   for row in input_hashes.values())):
        raise ValueError("summary input provenance must contain only bounded SHA-256/size descriptors")
    if (lifecycle.get("schema") != "butterfly.runpod-symbolic-worker.v1"
            or ownership.get("schema") != "butterfly.runpod-ownership.v1"
            or preparation.get("schema") != "butterfly.symbolic-cloud-preparation.v1"):
        raise ValueError("unsupported attempt record schemas")
    for key in ("nonce", "pod_id", "name", "preexisting_ids"):
        if lifecycle.get(key) != ownership.get(key):
            raise ValueError("lifecycle differs from immutable owned-worker identity")
    identifier, nonce = ownership.get("pod_id"), ownership.get("nonce")
    preexisting = ownership.get("preexisting_ids")
    after = lifecycle.get("post_delete_inventory_ids")
    if (not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", identifier)
            or not isinstance(nonce, str) or not re.fullmatch(r"[0-9a-f]{32}", nonce)
            or ownership.get("name") != "butterfly-exp477-" + nonce
            or not isinstance(preexisting, list) or not isinstance(after, list)
            or any(not isinstance(item, str) for item in [*preexisting, *after])
            or identifier in preexisting or identifier in after):
        raise ValueError("owned-worker identity or post-delete absence is invalid")
    if (lifecycle.get("create_attempted") is not True or lifecycle.get("create_aborted_before_post") is True
            or lifecycle.get("termination_verified") is not True
            or lifecycle.get("post_delete_direct_lookup") != "HTTP 404"
            or lifecycle.get("delete_request_completed") is not True
            or lifecycle.get("persistent_volume_requested") is not False
            or lifecycle.get("unrelated_resources_mutated") is not False
            or lifecycle.get("controller_finished") is not True):
        raise ValueError("completed exact-owned create/teardown evidence is required")
    if (lifecycle.get("create_or_contract_failed") is not True
            or lifecycle.get("contract_qualified") is not None and lifecycle.get("contract_qualified") is not False
            or lifecycle.get("actual_hourly_usd") is not None):
        raise ValueError("this summary is limited to an unqualified deployment with no saved actual rate")
    retirement = lifecycle.get("local_watchdog_retirement", {})
    if (not isinstance(retirement, dict) or any(retirement.get(key) is not True for key in
            ("verified", "service_absence_verified", "known_process_exit_verified"))):
        raise ValueError("local owned watchdog service/process retirement must be verified")
    plan = lifecycle.get("plan")
    if not isinstance(plan, dict) or plan != preparation.get("plan"):
        raise ValueError("attempt plan differs from public preparation")
    commit = plan.get("source_commit")
    if (not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit)
            or plan.get("experiment_id") != "EXP-477" or preparation.get("source_commit") != commit
            or source_inventory.get("schema") != "butterfly.source-inventory.v1"
            or source_inventory.get("source_commit") != commit or source_inventory.get("pushed_source_commit") != commit):
        raise ValueError("attempt source is not the consistently declared frozen pushed commit")
    source_hashes = {name: source_inventory.get("files", {}).get(name) for name in SOURCE_PRODUCERS}
    if any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
           for value in [producer_sha256, *source_hashes.values()]):
        raise ValueError("attempt and summary producer SHA-256 values are required")
    start = number(lifecycle.get("create_attempted_at"), "create-attempt timestamp", minimum=1)
    end = number(lifecycle.get("terminated_at"), "termination timestamp", minimum=start)
    hourly = number(plan.get("maximum_hourly_usd"), "frozen hourly cap", minimum=.001, maximum=.5)
    budget = number(plan.get("maximum_spend_usd"), "frozen attempt budget", minimum=.01, maximum=3)
    lifetime = number(plan.get("maximum_lifetime_seconds"), "frozen lifetime", minimum=1, maximum=10800)
    reserve = number(plan.get("storage_transfer_reserve_usd"), "frozen reserve", minimum=0, maximum=budget)
    elapsed = Decimal(str(end)) - Decimal(str(start))
    estimate = (Decimal(str(hourly)) * elapsed / Decimal(3600)).quantize(Decimal("0.000000000001"), rounding=ROUND_CEILING)
    # Every output field is constructed explicitly: no private record is merged.
    return {
        "schema": "butterfly.symbolic-deployment-attempt-summary.v1", "experiment_id": "EXP-477",
        "status": "deployment_not_qualified", "frozen_source_commit": commit,
        "producer": {"path": "scripts/summarize_symbolic_attempt.py", "sha256": producer_sha256},
        "attempt_producer_sha256": source_hashes, "input_hashes": input_hashes,
        "create": {"attempted": True, "owned_worker_id": identifier, "immutable_ownership_consistent": True,
                   "create_or_contract_failed": True, "contract_qualified": False,
                   "failure_detail": "specific failing provider fields were not retained in these input receipts"},
        "teardown": {"delete_request_completed": True, "direct_lookup": "HTTP 404",
                     "owned_worker_absent_from_inventory": True, "verified": True,
                     "local_watchdog_service_absent": True, "known_watchdog_processes_exited": True,
                     "unrelated_resources_mutated": False},
        "timing": {"create_attempted_utc": datetime.fromtimestamp(start, timezone.utc).isoformat(),
                   "termination_verified_utc": datetime.fromtimestamp(end, timezone.utc).isoformat(),
                   "create_attempt_to_verified_absence_seconds": float(elapsed),
                   "basis": "saved controller wall-clock timestamps; not provider billing timestamps"},
        "budget": {"maximum_hourly_usd": hourly, "maximum_spend_usd": budget,
                   "maximum_lifetime_seconds": lifetime, "storage_transfer_reserve_usd": reserve,
                   "actual_hourly_usd": None, "actual_rate_status": "unavailable: deployment never qualified",
                   "conditional_prorated_upper_estimate_usd": float(estimate), "is_invoice": False,
                   "estimate_assumption": "actual hourly rate at or below the requested cap; continuous prorating over the recorded interval",
                   "estimate_limitations": "actual provider rate, minimum charges, billing rounding, and additional charges are unverified"},
        "evidence_boundary": {"scientific_result": False, "workload_callback_reached": False,
                              "target_collection_started": False,
                              "basis": "failure before contract qualification; no workload receipt exists",
                              "source_uploads_performed": False},
        "privacy": {"private_record_contents_copied": False, "unrelated_resource_ids_published": False},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lifecycle-receipt", type=Path, required=True)
    parser.add_argument("--ownership-receipt", type=Path, required=True)
    parser.add_argument("--preparation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    documents, hashes = {}, {}
    for name, path in (("lifecycle", args.lifecycle_receipt), ("ownership", args.ownership_receipt), ("preparation", args.preparation)):
        documents[name], hashes[name] = read_json(path)
    workload = args.preparation.parent / "workload.json"
    if workload.exists() or workload.is_symlink():
        raise ValueError("an existing workload receipt is outside this pre-qualification failure summary")
    source_path = args.preparation.parent / "prepared-inputs/source-inventory.json"
    inventory, hashes["source_inventory"] = read_json(source_path)
    expected = documents["preparation"].get("assets", {}).get("source-inventory.json")
    if expected != {"path": "source-inventory.json", **hashes["source_inventory"]}:
        raise ValueError("source inventory hash/size differs from public preparation")
    result = summarize(**documents, input_hashes=hashes, source_inventory=inventory,
                       producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    if any(path.is_symlink() for path in (args.output, *args.output.parents)):
        raise ValueError("summary output may not use symlinks")
    pilot.write_new_json(args.output, result)
    print(json.dumps({"status": result["status"], "teardown_verified": result["teardown"]["verified"],
                      "conditional_prorated_upper_estimate_usd": result["budget"]["conditional_prorated_upper_estimate_usd"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

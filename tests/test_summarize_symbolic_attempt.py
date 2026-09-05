"""Saved-record summary tests; no credentials, API calls, or worker retries."""

from copy import deepcopy
import hashlib
import json

import pytest

from scripts import summarize_symbolic_attempt as summary


COMMIT = "a" * 40


@pytest.fixture
def records():
    plan = {"experiment_id": "EXP-477", "source_commit": COMMIT, "maximum_hourly_usd": .5,
            "maximum_spend_usd": 3., "maximum_lifetime_seconds": 10800, "storage_transfer_reserve_usd": 1.5}
    owner = {"schema": "butterfly.runpod-ownership.v1", "pod_id": "owned-test", "nonce": "b" * 32,
             "name": "butterfly-exp477-" + "b" * 32, "preexisting_ids": ["UNRELATED-ONE", "UNRELATED-TWO"]}
    lifecycle = {**owner, "schema": "butterfly.runpod-symbolic-worker.v1", "plan": plan,
                 "create_attempted": True, "create_or_contract_failed": True,
                 "create_attempted_at": 1700000000.0, "terminated_at": 1700000005.0,
                 "termination_verified": True, "delete_request_completed": True,
                 "post_delete_direct_lookup": "HTTP 404", "post_delete_inventory_ids": ["UNRELATED-ONE", "UNRELATED-TWO"],
                 "persistent_volume_requested": False, "unrelated_resources_mutated": False, "controller_finished": True,
                 "local_watchdog_retirement": {"verified": True, "service_absence_verified": True,
                                               "known_process_exit_verified": True, "service": "PRIVATE-SERVICE",
                                               "known_processes": [{"pid": 12345, "ps_start": "PRIVATE-START"}]},
                 "controller_credential_fingerprint": "PRIVATE-FINGERPRINT", "public_key": "PRIVATE-KEY-MARKER",
                 "env": {"SECRET": "PRIVATE-ENV"}, "provider_raw": {"token": "PRIVATE-PROVIDER"}}
    preparation = {"schema": "butterfly.symbolic-cloud-preparation.v1", "source_commit": COMMIT, "plan": deepcopy(plan)}
    inventory = {"schema": "butterfly.source-inventory.v1", "source_commit": COMMIT, "pushed_source_commit": COMMIT,
                 "files": {name: "c" * 64 for name in summary.SOURCE_PRODUCERS}}
    return {"lifecycle": lifecycle, "ownership": owner, "preparation": preparation,
            "source_inventory": inventory, "producer_sha256": "d" * 64,
            "input_hashes": {name: {"sha256": "e" * 64, "bytes": 123}
                             for name in ("lifecycle", "ownership", "preparation", "source_inventory")}}


def test_summary_is_allowlisted_and_actual_rate_is_not_invented(records):
    result = summary.summarize(**records)
    encoded = json.dumps(result, sort_keys=True, allow_nan=False)
    assert "PRIVATE" not in encoded and "UNRELATED" not in encoded and "12345" not in encoded
    assert "credential" not in encoded and "public_key" not in encoded and "provider_raw" not in encoded
    assert result["status"] == "deployment_not_qualified"
    assert result["budget"]["actual_hourly_usd"] is None and not result["budget"]["is_invoice"]
    assert result["budget"]["conditional_prorated_upper_estimate_usd"] == .000694444445
    assert result["timing"]["create_attempt_to_verified_absence_seconds"] == 5.0
    assert result["teardown"]["owned_worker_absent_from_inventory"]
    assert result["evidence_boundary"]["scientific_result"] is False
    assert result["frozen_source_commit"] == COMMIT


@pytest.mark.parametrize("key,value", [
    ("termination_verified", False), ("post_delete_direct_lookup", "HTTP 200"),
    ("post_delete_inventory_ids", ["owned-test"]), ("pod_id", "other-test"),
    ("contract_qualified", True), ("contract_qualified", "false"), ("actual_hourly_usd", .4),
    ("create_or_contract_failed", False), ("create_attempted", False), ("create_aborted_before_post", True),
    ("delete_request_completed", False), ("controller_finished", False),
    ("persistent_volume_requested", True), ("unrelated_resources_mutated", True),
    ("terminated_at", 1699999999.0), ("create_attempted_at", float("nan")),
])
def test_summary_rejects_inconsistent_or_unverified_records(records, key, value):
    records["lifecycle"][key] = value
    with pytest.raises(ValueError):
        summary.summarize(**records)


@pytest.mark.parametrize("field", ["verified", "service_absence_verified", "known_process_exit_verified"])
def test_summary_requires_saved_local_retirement_proof(records, field):
    records["lifecycle"]["local_watchdog_retirement"][field] = False
    with pytest.raises(ValueError, match="retirement"):
        summary.summarize(**records)


@pytest.mark.parametrize("mutation", ["preexisting", "commit", "producer_hash", "budget", "injected_provenance"])
def test_summary_rejects_nonfrozen_ownership_source_budget_and_input_fields(records, mutation):
    if mutation == "preexisting":
        records["ownership"]["preexisting_ids"].append("owned-test")
    elif mutation == "commit":
        records["source_inventory"]["source_commit"] = "f" * 40
    elif mutation == "producer_hash":
        records["source_inventory"]["files"][summary.SOURCE_PRODUCERS[0]] = "not-a-sha"
    elif mutation == "budget":
        records["lifecycle"]["plan"]["maximum_hourly_usd"] = float("inf")
        records["preparation"]["plan"]["maximum_hourly_usd"] = float("inf")
    else:
        records["input_hashes"]["lifecycle"]["private"] = "SECRET"
    with pytest.raises(ValueError):
        summary.summarize(**records)


def input_files(tmp_path, records):
    args = []
    inventory_path = tmp_path / "public/prepared-inputs/source-inventory.json"
    inventory_path.parent.mkdir(parents=True)
    raw = json.dumps(records["source_inventory"], sort_keys=True).encode()
    inventory_path.write_bytes(raw)
    records["preparation"]["assets"] = {"source-inventory.json": {"path": "source-inventory.json",
                                         "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}}
    for name, option in (("lifecycle", "lifecycle-receipt"), ("ownership", "ownership-receipt"), ("preparation", "preparation")):
        path = tmp_path / ("public" if name == "preparation" else "private") / (name + ".json")
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(records[name], sort_keys=True))
        args.extend(["--" + option, str(path)])
    return args + ["--output", str(tmp_path / "summary.json")]


def test_cli_hashes_saved_inputs_and_writes_exclusively(tmp_path, records):
    args = input_files(tmp_path, records)
    assert summary.main(args) == 0
    result = json.loads((tmp_path / "summary.json").read_bytes())
    assert result["input_hashes"]["lifecycle"]["sha256"] == hashlib.sha256((tmp_path / "private/lifecycle.json").read_bytes()).hexdigest()
    assert result["producer"]["sha256"] == hashlib.sha256(summary.Path(summary.__file__).read_bytes()).hexdigest()
    assert str(tmp_path) not in json.dumps(result)
    with pytest.raises(FileExistsError):
        summary.main(args)


@pytest.mark.parametrize("mutation", ["inventory", "workload", "symlink"])
def test_cli_rejects_changed_inventory_workload_or_private_symlink(tmp_path, records, mutation):
    args = input_files(tmp_path, records)
    if mutation == "inventory":
        (tmp_path / "public/prepared-inputs/source-inventory.json").write_text("{}")
    elif mutation == "workload":
        (tmp_path / "public/workload.json").write_text("{}")
    else:
        path = tmp_path / "private/ownership.json"
        target = tmp_path / "retained.json"
        path.rename(target)
        path.symlink_to(target)
    with pytest.raises(ValueError):
        summary.main(args)
    assert not (tmp_path / "summary.json").exists()

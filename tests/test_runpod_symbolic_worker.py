"""Mocked lifecycle tests; never read credentials, create jobs, or contact APIs."""

import json
from pathlib import Path

import pytest

from scripts import runpod_symbolic_worker as worker


@pytest.fixture(autouse=True)
def no_credentials_or_network(monkeypatch):
    monkeypatch.setattr(worker.runpodctl, "api_key", lambda: pytest.fail("credentials must not be read"))
    monkeypatch.setattr(worker.runpodctl.urllib.request, "urlopen", lambda *_a, **_k: pytest.fail("network forbidden"))


def plan():
    return {"experiment_id": "EXP-477", "source_commit": "a" * 40,
            "image": "frozen-image", "gpu_type": "frozen-gpu",
            "maximum_hourly_usd": 0.5, "maximum_spend_usd": 3.0,
            "maximum_lifetime_seconds": 10800, "maximum_no_progress_seconds": 600,
            "heartbeat_timeout_seconds": 30, "storage_transfer_reserve_usd": 0.5}


@pytest.fixture
def store(tmp_path):
    directory = tmp_path / "private-lifecycle"
    directory.mkdir(mode=0o700)
    result = worker.Store(directory)
    worker.atomic_json(result.path, {
        "schema": worker.SCHEMA, "nonce": "unique", "name": worker.NAME_PREFIX + "unique",
        "plan": plan(), "controller": {"pid": 123, "ps_start": "controller-start"},
        "prepared_at": 80.0, "last_progress_at": 90.0, "create_attempted": False,
        "pod_id": None, "termination_verified": False, "controller_finished": False,
        "preexisting_ids": [], "public_key": "ssh-ed25519 AAAA synthetic-key",
    })
    worker.atomic_json(directory / "controller-heartbeat.json",
                       {"nonce": "unique", "pid": 123, "ps_start": "controller-start", "time": 100.0})
    worker.atomic_json(directory / "watchdog-heartbeat.json",
                       {"nonce": "unique", "pid": 456, "ps_start": "watchdog-start", "time": 100.0})
    return result


def lookup(pid):
    return {123: "controller-start", 456: "watchdog-start"}.get(pid)


class Provider:
    def __init__(self, store, *, price=0.25, timeout_after_create=False):
        self.store = store
        self.calls = []
        self.price = price
        self.timeout_after_create = timeout_after_create
        self.pods = {"unrelated-a": {"id": "unrelated-a", "name": "another-study"},
                     "unrelated-b": {"id": "unrelated-b", "name": "personal-pod"}}

    def __call__(self, method, url, *, payload=None):
        self.calls.append((method, url, payload))
        if method == "GET" and url.endswith("/pods?includeMachine=true"):
            return list(self.pods.values())
        if method == "POST":
            assert url.endswith("/pods")
            self.pods["created-owned"] = {
                "id": "created-owned", "name": payload["name"], "adjustedCostPerHr": self.price,
                "interruptible": False, "containerDiskInGb": 20, "volumeInGb": 0,
                "ports": ["22/tcp"], "machine": {"secureCloud": True, "gpuTypeId": "frozen-gpu"},
                "gpu": {"count": 1}, "image": "frozen-image",
                "env": payload["env"],
            }
            if self.timeout_after_create:
                raise TimeoutError("simulated timeout after provider accepted POST")
            return self.pods["created-owned"]
        identifier = url.rsplit("/", 1)[1]
        if method == "GET":
            if identifier not in self.pods:
                raise SystemExit("Runpod API returned HTTP 404: absent")
            return self.pods[identifier]
        if method == "DELETE":
            assert identifier == "created-owned", "unrelated resource mutation is forbidden"
            del self.pods[identifier]
            return None
        pytest.fail(f"unexpected fake provider method {method}")


def test_payload_is_one_secure_on_demand_gpu_and_only_public_key(store):
    payload = worker.create_payload(store.read())
    assert payload["cloudType"] == "SECURE"
    assert payload["gpuCount"] == 1
    assert payload["interruptible"] is False
    assert payload["containerDiskInGb"] == 20 and payload["volumeInGb"] == 0
    assert payload["ports"] == ["22/tcp"]
    assert set(payload["env"]) == {"PUBLIC_KEY"}
    assert "networkVolumeId" not in payload


def test_single_launch_then_verified_teardown_preserves_two_unrelated_pods(store):
    provider = Provider(store)
    pod = worker.provision_once(store, provider, lookup=lookup, now=100.0)
    assert pod["id"] == "created-owned"
    assert store.read()["preexisting_ids"] == ["unrelated-a", "unrelated-b"]
    assert worker.terminate_owned(store, provider, pause=lambda _: None)
    record = store.read()
    assert record["termination_verified"]
    assert record["post_delete_inventory_ids"] == ["unrelated-a", "unrelated-b"]
    assert set(provider.pods) == {"unrelated-a", "unrelated-b"}
    assert "delete_http_status" not in record  # request_json does not expose it.


@pytest.mark.parametrize("heartbeat", [None,
    {"nonce": "unique", "pid": 456, "ps_start": "watchdog-start", "time": 50.0},
    {"nonce": "unique", "pid": 456, "ps_start": "old-reused-PID", "time": 100.0},
    {"nonce": "unique", "pid": 123, "ps_start": "controller-start", "time": 100.0},
    {"nonce": "wrong", "pid": 456, "ps_start": "watchdog-start", "time": 100.0},
])
def test_no_create_without_independent_live_watchdog(store, heartbeat):
    path = store.directory / "watchdog-heartbeat.json"
    if heartbeat is None:
        path.unlink()
    else:
        worker.atomic_json(path, heartbeat)
    provider = Provider(store)
    with pytest.raises(worker.LifecycleError, match="watchdog"):
        worker.provision_once(store, provider, lookup=lookup, now=100.0)
    assert not provider.calls


def test_controller_pid_reuse_and_absent_heartbeat_trigger_teardown(store):
    record = store.read()
    heartbeat = worker.heartbeat_record(store, "controller")
    assert worker.watchdog_reason(record, heartbeat, 100, lookup=lookup) is None
    assert worker.watchdog_reason(record, heartbeat, 100, lookup=lambda _pid: "reused") == "controller-missing-stale-or-pid-reused"
    assert worker.watchdog_reason(record, None, 100, lookup=lookup) == "controller-missing-stale-or-pid-reused"


def test_lifetime_no_progress_and_clock_regression_trigger_teardown(store):
    record = store.read()
    heartbeat = worker.heartbeat_record(store, "controller")
    record["prepared_at"] = -11000
    assert worker.watchdog_reason(record, heartbeat, 100, lookup=lookup) == "lifetime-limit-or-clock-regression"
    record["prepared_at"] = 80
    record["last_progress_at"] = -501
    assert worker.watchdog_reason(record, heartbeat, 100, lookup=lookup) == "no-progress-limit"
    record["prepared_at"] = 120
    assert worker.watchdog_reason(record, heartbeat, 100, lookup=lookup) == "lifetime-limit-or-clock-regression"


@pytest.mark.parametrize("price", [0.50001, None, float("nan"), float("inf"), -0.1, True])
def test_cost_gate_retains_ownership_for_teardown(store, price):
    provider = Provider(store, price=price)
    with pytest.raises(worker.LifecycleError, match="actual hourly"):
        worker.provision_once(store, provider, lookup=lookup, now=100)
    assert store.read()["pod_id"] == "created-owned"
    assert worker.terminate_owned(store, provider, pause=lambda _: None)
    assert set(provider.pods) == {"unrelated-a", "unrelated-b"}


def test_timeout_reconciles_exact_new_name_and_public_key_without_retry(store):
    provider = Provider(store, timeout_after_create=True)
    with pytest.raises(TimeoutError):
        worker.provision_once(store, provider, lookup=lookup, now=100)
    assert store.read()["pod_id"] == "created-owned"
    assert "public key" in store.read()["ownership_basis"]
    with pytest.raises(worker.LifecycleError, match="already attempted"):
        worker.provision_once(store, provider, lookup=lookup, now=100)
    assert sum(method == "POST" for method, _, _ in provider.calls) == 1
    assert worker.terminate_owned(store, provider, pause=lambda _: None)


def test_name_only_cannot_establish_ambiguous_ownership(store):
    provider = Provider(store)
    store.update(create_attempted=True, create_attempted_at=100,
                 preexisting_ids=["unrelated-a", "unrelated-b"])
    provider.pods["lookalike"] = {"id": "lookalike", "name": store.read()["name"],
                                 "env": {"PUBLIC_KEY": "another key"}}
    assert worker.reconcile_ambiguous_create(store, provider) is None
    assert not worker.terminate_owned(store, provider, pause=lambda _: None)
    assert not any(method == "DELETE" for method, _, _ in provider.calls)


@pytest.mark.parametrize("mutation", ["id", "name", "baseline", "absent-id"])
def test_wrong_identity_never_deletes_any_resource(store, mutation):
    provider = Provider(store)
    worker.provision_once(store, provider, lookup=lookup, now=100)
    if mutation == "id":
        store.update(pod_id="unrelated-a")
    elif mutation == "name":
        provider.pods["created-owned"]["name"] = "unexpected-name"
    elif mutation == "absent-id":
        store.update(pod_id="another-absent-id")
    else:
        store.update(preexisting_ids=["created-owned", "unrelated-a", "unrelated-b"])
    with pytest.raises(worker.OwnershipError):
        worker.terminate_owned(store, provider, pause=lambda _: None)
    assert not any(method == "DELETE" for method, _, _ in provider.calls)


def test_immutable_ownership_receipt_cannot_be_rebound(store):
    provider = Provider(store)
    worker.provision_once(store, provider, lookup=lookup, now=100)
    original = (store.directory / "ownership.json").read_bytes()
    with pytest.raises(worker.OwnershipError, match="conflicts"):
        worker.bind_ownership(store, "different-new-id", "invalid-rebinding")
    assert (store.directory / "ownership.json").read_bytes() == original


def test_duplicate_name_in_prelaunch_inventory_prevents_post(store):
    provider = Provider(store)
    provider.pods["unrelated-a"]["name"] = store.read()["name"]
    with pytest.raises(worker.LifecycleError, match="already exists"):
        worker.provision_once(store, provider, lookup=lookup, now=100)
    assert not any(method == "POST" for method, _, _ in provider.calls)


def test_teardown_requires_both_direct_404_and_inventory_absence(store):
    provider = Provider(store)
    worker.provision_once(store, provider, lookup=lookup, now=100)
    original = provider.__call__

    def stale_inventory(method, url, *, payload=None):
        result = original(method, url, payload=payload)
        if method == "GET" and url.endswith("includeMachine=true") and "created-owned" not in provider.pods:
            result = result + [{"id": "created-owned", "name": store.read()["name"]}]
        return result

    assert not worker.terminate_owned(store, stale_inventory, attempts=2, pause=lambda _: None)
    assert not store.read()["termination_verified"]


def test_uncertain_delete_is_verified_without_issuing_a_second_delete(store):
    provider = Provider(store)
    worker.provision_once(store, provider, lookup=lookup, now=100)

    def delete_times_out_after_success(method, url, *, payload=None):
        result = provider(method, url, payload=payload)
        if method == "DELETE":
            raise TimeoutError("response lost after deletion")
        return result

    assert worker.terminate_owned(store, delete_times_out_after_success, pause=lambda _: None)
    assert store.read()["termination_verified"]
    assert store.read()["delete_request_completed"] is False
    assert sum(method == "DELETE" for method, _, _ in provider.calls) == 1


@pytest.mark.parametrize("field,value", [("maximum_hourly_usd", 0.51), ("maximum_spend_usd", 3.01),
                                        ("maximum_lifetime_seconds", 10801), ("maximum_no_progress_seconds", float("nan")),
                                        ("maximum_hourly_usd", "0.25")])
def test_invalid_cost_policy_prevents_local_preparation(field, value):
    configuration = plan()
    configuration[field] = value
    with pytest.raises(worker.LifecycleError):
        worker.validate_plan(configuration)


def test_controller_callback_failure_still_terminates(store, monkeypatch):
    provider = Provider(store)
    monkeypatch.setattr(worker, "prepare_store", lambda *_args: store)
    original_provision = worker.provision_once
    monkeypatch.setattr(worker, "provision_once", lambda target, api: original_provision(target, api, lookup=lookup, now=100))
    retired = []

    def fail_workload(_pod, _store, _progress):
        raise RuntimeError("qualification failed")

    with pytest.raises(RuntimeError, match="qualification failed"):
        worker.run_owned_worker(plan(), Path("unused"), fail_workload, request=provider,
                                start_watchdog=lambda _: None, stop_watchdog=lambda target: retired.append(target))
    assert store.read()["termination_verified"]
    assert retired == [store]
    assert set(provider.pods) == {"unrelated-a", "unrelated-b"}


def test_request_adapter_only_treats_exact_404_as_absent():
    for message in ("Runpod API returned HTTP 500: not found", "request failed: 404"):
        def fail(*_args, **_kwargs):
            raise SystemExit(message)
        with pytest.raises(SystemExit):
            worker.direct_lookup("owned-id", fail)


def test_linux_cannot_substitute_an_ordinary_detached_watchdog(store, monkeypatch):
    monkeypatch.setattr(worker.sys, "platform", "linux")
    with pytest.raises(worker.LifecycleError, match="macOS launchd"):
        worker.launchd_watchdog(store)

"""Mocked lifecycle tests; never read credentials, create jobs, or contact APIs."""

import json
from pathlib import Path
import subprocess

import pytest

from scripts import runpod_symbolic_worker as worker


REAL_CREDENTIAL_FINGERPRINT = worker.control_plane_credential_fingerprint
SYNTHETIC_CREDENTIAL_FINGERPRINT = "f" * 64


@pytest.fixture(autouse=True)
def no_credentials_or_network(monkeypatch, tmp_path):
    monkeypatch.setattr(worker.runpodctl, "api_key", lambda: pytest.fail("credentials must not be read"))
    monkeypatch.setattr(worker.runpodctl.urllib.request, "urlopen", lambda *_a, **_k: pytest.fail("network forbidden"))
    monkeypatch.setattr(worker, "CONTROLLER_LOCK_PATH", tmp_path / "shared-controller.lock")
    monkeypatch.setattr(worker, "control_plane_credential_fingerprint", lambda: SYNTHETIC_CREDENTIAL_FINGERPRINT)


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
        "controller_credential_fingerprint": SYNTHETIC_CREDENTIAL_FINGERPRINT,
        "prepared_at": 80.0, "last_progress_at": 90.0, "create_attempted": False,
        "pod_id": None, "termination_verified": False, "controller_finished": False,
        "preexisting_ids": [], "public_key": "ssh-ed25519 AAAA synthetic-key",
    })
    worker.atomic_json(directory / "controller-heartbeat.json",
                       {"nonce": "unique", "pid": 123, "ps_start": "controller-start", "time": 100.0})
    worker.atomic_json(directory / "watchdog-heartbeat.json",
                       {"nonce": "unique", "pid": 456, "ps_start": "watchdog-start", "time": 100.0})
    readiness = {"schema": "butterfly.watchdog-control-plane-readiness.v1",
                 "nonce": "unique", "pid": 456, "ps_start": "watchdog-start", "time": 100.0,
                 "passed": True, "method": "GET", "operation": "inventory",
                 "credential_fingerprint": SYNTHETIC_CREDENTIAL_FINGERPRINT,
                 "history_file": "watchdog-probe-" + "a" * 32 + ".json"}
    worker.atomic_json(directory / readiness["history_file"], readiness)
    worker.atomic_json(directory / "watchdog-control-plane.json", readiness)
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
        identifier = url.split("?", 1)[0].rsplit("/", 1)[1]
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


def test_direct_lookup_explicitly_requests_contract_details(store):
    calls = []
    def request(method, url):
        calls.append((method, url))
        return {"id": "created-owned"}
    worker.direct_lookup("created-owned", request)
    assert calls == [("GET", worker.runpodctl.REST_BASE +
                      "/pods/created-owned?includeMachine=true&includeNetworkVolume=true")]


@pytest.mark.parametrize("rental_type,passes", [("RESERVED", True),
    ("INTERRUPTABLE", False), ("BID", False), ("BACKGROUND", False), (None, False)])
def test_missing_rest_rental_status_needs_exact_graphql_confirmation(store, rental_type, passes):
    provider = Provider(store)
    pod = worker.provision_once(store, provider, lookup=lookup, now=100)
    del pod["interruptible"]
    def query(statement):
        assert statement == 'query { pod(input: {podId: "created-owned"}) { id name podType } }'
        return {"pod": {"id": pod["id"], "name": pod["name"], "podType": rental_type}}
    if passes:
        assert worker.observed_actual_contract(store, pod, query) == 0.25
    else:
        with pytest.raises(worker.LifecycleError, match="interruptible"):
            worker.observed_actual_contract(store, pod, query)
    assert "interruptible" not in store.read()["observed_contract"]
    assert store.read()["observed_rental_contract"]["podType"] == rental_type


def test_graphql_cannot_override_explicit_spot_or_wrong_identity(store):
    provider = Provider(store)
    pod = worker.provision_once(store, provider, lookup=lookup, now=100)
    pod["interruptible"] = True
    with pytest.raises(worker.LifecycleError, match="interruptible"):
        worker.observed_actual_contract(store, pod, lambda _: pytest.fail("no override"))
    del pod["interruptible"]
    with pytest.raises(worker.OwnershipError):
        worker.observed_actual_contract(store, pod, lambda _: {"pod": {
            "id": "unrelated-a", "name": pod["name"], "podType": "RESERVED"}})


def test_real_ssh_connection_path_uses_rental_evidence(store, monkeypatch):
    from scripts import execute_symbolic_center_cloud as cloud
    provider = Provider(store)
    pod = worker.provision_once(store, provider, lookup=lookup, now=100)
    del pod["interruptible"]
    pod.update(publicIp="203.0.113.1", portMappings={"22": 22022})
    monkeypatch.setattr(worker, "direct_lookup", lambda _: pod)
    monkeypatch.setattr(worker.runpodctl, "graphql", lambda _: {"pod": {
        "id": pod["id"], "name": pod["name"], "podType": "RESERVED"}})
    class PinnedSSH:
        def __init__(self, host, port, directory):
            self.host, self.port, self.strict = host, port, True
        def call(self, command, timeout):
            assert command == "true"
    monkeypatch.setattr(cloud, "SSH", PinnedSSH)
    progress = []
    result = cloud.connect_owned(store, progress.append, seconds=1)
    assert result.strict and progress == ["ssh-authenticated"]
    assert store.read()["observed_rental_contract"]["podType"] == "RESERVED"


@pytest.mark.parametrize("field,value", [("interruptible", True),
    ("containerDiskInGb", 50), ("volumeInGb", None),
    ("networkVolume", {"id": "synthetic"}), ("ports", ["22/tcp", "8888/http"])])
def test_failed_contract_retains_observations_before_teardown(store, field, value):
    provider = Provider(store)
    def mismatch(method, url, *, payload=None):
        result = provider(method, url, payload=payload)
        if method == "GET" and "/created-owned?" in url:
            result[field] = value
        return result
    with pytest.raises(worker.LifecycleError, match=field):
        worker.provision_once(store, mismatch, lookup=lookup, now=100)
    observed = store.read()["observed_contract"]
    assert observed["adjustedCostPerHr"] == 0.25
    assert "env" not in observed
    assert "synthetic-key" not in json.dumps(observed)
    assert worker.terminate_owned(store, provider, pause=lambda _: None)
    assert store.read()["observed_contract"] == observed


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


def test_another_exp477_record_name_prevents_a_second_worker_without_mutation(store):
    provider = Provider(store)
    provider.pods["prior-exp477"] = {"id": "prior-exp477", "name": worker.NAME_PREFIX + "different-record"}
    with pytest.raises(worker.LifecycleError, match="refusing another worker"):
        worker.provision_once(store, provider, lookup=lookup, now=100)
    assert not store.read()["create_attempted"]
    assert all(method == "GET" for method, _, _ in provider.calls)
    assert "prior-exp477" in provider.pods


def test_task_wide_lock_blocks_other_state_directory_before_preparation(monkeypatch):
    monkeypatch.setattr(worker, "prepare_store", lambda *_args: pytest.fail("blocked controller must not prepare"))
    with worker.single_controller_lock():
        with pytest.raises(worker.LifecycleError, match="another EXP-477 controller"):
            worker.run_owned_worker(plan(), "a-different-record", lambda *_args: None)
    # Release is reusable; the same empty inode is retained, never unlinked.
    before = worker.CONTROLLER_LOCK_PATH.stat().st_ino
    with worker.single_controller_lock():
        assert worker.CONTROLLER_LOCK_PATH.stat().st_ino == before


def test_task_wide_lock_releases_on_exception_and_rejects_links(tmp_path):
    with pytest.raises(RuntimeError):
        with worker.single_controller_lock():
            raise RuntimeError("synthetic controller failure")
    with worker.single_controller_lock():
        pass
    target = tmp_path / "unrelated-file"
    target.write_text("preserve unrelated content")
    link = tmp_path / "linked-lock"
    link.symlink_to(target)
    with pytest.raises(worker.LifecycleError, match="safely"):
        with worker.single_controller_lock(link):
            pytest.fail("must not acquire a symlink")
    with pytest.raises(worker.LifecycleError, match="empty private"):
        with worker.single_controller_lock(target):
            pytest.fail("must not repurpose an unrelated nonempty file")
    assert target.read_text() == "preserve unrelated content"


def test_crashed_unresolved_record_blocks_new_record_before_any_inventory_or_preparation(store, monkeypatch):
    # In particular, a create may still be in flight and absent from inventory.
    store.update(create_attempted=True, create_attempted_at=100, pod_id=None)
    worker.register_controller(store)
    monkeypatch.setattr(worker, "prepare_store", lambda *_args: pytest.fail("unresolved earlier create must block preparation"))
    with pytest.raises(worker.LifecycleError, match="earlier EXP-477 controller"):
        worker.run_owned_worker(plan(), "another-state-directory", lambda *_args: None)
    # A durable watchdog can later verify termination; only then may a new run proceed.
    store.update(termination_verified=True)
    worker.require_no_unresolved_controller()


def test_missing_previous_lifecycle_record_fails_closed(store):
    worker.register_controller(store)
    store.path.unlink()
    with pytest.raises(worker.LifecycleError, match="cannot be verified"):
        worker.require_no_unresolved_controller()


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


@pytest.mark.parametrize("mutation", ["missing", "failed", "pid", "reused", "stale", "history", "method"])
def test_live_watchdog_without_its_own_bound_authenticated_probe_prevents_every_provider_call(store, mutation):
    path = store.directory / "watchdog-control-plane.json"
    readiness = json.loads(path.read_bytes())
    if mutation == "missing":
        path.unlink()
    else:
        if mutation == "failed": readiness["passed"] = False
        elif mutation == "pid": readiness["pid"] = 123
        elif mutation == "reused": readiness["ps_start"] = "different-start"
        elif mutation == "stale": readiness["time"] = -100
        elif mutation == "method": readiness["method"] = "POST"
        worker.atomic_json(path, readiness)
        if mutation != "history":
            worker.atomic_json(store.directory / readiness["history_file"], readiness)
        else:
            (store.directory / readiness["history_file"]).unlink()
    provider = Provider(store)
    with pytest.raises(worker.LifecycleError, match="watchdog"):
        worker.provision_once(store, provider, lookup=lookup, now=100)
    assert not provider.calls
    assert not store.read()["create_attempted"]


def test_watchdog_probe_uses_one_get_and_preserves_a_private_key_free_history(store, monkeypatch):
    monkeypatch.setattr(worker.os, "getpid", lambda: 456)
    calls = []
    def authenticated_inventory(method, url):
        calls.append((method, url))
        return [{"id": "unrelated", "env": {"SECRET": "must-not-retain"}}]
    probe = worker.probe_watchdog_control_plane(store, authenticated_inventory, lookup=lookup, clock=lambda: 100)
    assert calls == [("GET", worker.runpodctl.REST_BASE + "/pods?includeMachine=true")]
    assert probe["passed"] and probe["pid"] == 456
    history = store.directory / probe["history_file"]
    assert json.loads(history.read_bytes()) == probe
    assert history.stat().st_mode & 0o077 == 0
    assert "must-not-retain" not in history.read_text()
    assert "unrelated" not in history.read_text()
    worker.require_watchdog(store, now=100, lookup=lookup)


def test_failed_probe_details_are_suppressed_and_history_survives_success(store, monkeypatch):
    monkeypatch.setattr(worker.os, "getpid", lambda: 456)
    def failed_inventory(*_args):
        raise SystemExit("synthetic secret text must not be recorded")
    with pytest.raises(worker.LifecycleError, match="readiness failed"):
        worker.probe_watchdog_control_plane(store, failed_inventory, lookup=lookup, clock=lambda: 100)
    failed = json.loads((store.directory / "watchdog-control-plane.json").read_bytes())
    assert not failed["passed"] and failed["status"] == "failed"
    original = (store.directory / failed["history_file"]).read_bytes()
    assert b"synthetic secret" not in original
    with pytest.raises(worker.LifecycleError):
        worker.require_watchdog(store, now=100, lookup=lookup)
    passed = worker.probe_watchdog_control_plane(store, lambda *_args: [], lookup=lookup, clock=lambda: 101)
    assert passed["history_file"] != failed["history_file"]
    assert (store.directory / failed["history_file"]).read_bytes() == original


def test_controller_cannot_substitute_its_own_authentication_for_watchdog_readiness(store, monkeypatch):
    monkeypatch.setattr(worker.os, "getpid", lambda: 123)
    with pytest.raises(worker.LifecycleError, match="independently identified"):
        worker.probe_watchdog_control_plane(store, lambda *_args: pytest.fail("controller must not probe"), lookup=lookup)


def test_fresh_watchdog_probes_before_heartbeat_and_existing_create_recovery_does_not_wait(store, monkeypatch):
    events = []
    def probe(_store):
        events.append("authenticated-inventory")
    def heartbeat(_store, *, role):
        events.append(role + "-heartbeat")
        store.update(termination_verified=True)
    monkeypatch.setattr(worker, "probe_watchdog_control_plane", probe)
    monkeypatch.setattr(worker, "write_heartbeat", heartbeat)
    assert worker.watchdog_loop(store) == 0
    assert events == ["authenticated-inventory", "watchdog-heartbeat"]
    store.update(termination_verified=False, create_attempted=True)
    events.clear()
    assert worker.watchdog_loop(store) == 0
    assert events == ["watchdog-heartbeat"]


def test_launchd_start_allows_one_thirty_second_probe_and_retains_bootstrap_failure(store, monkeypatch):
    import inspect
    assert inspect.signature(worker.launchd_watchdog).parameters["timeout"].default >= 45
    monkeypatch.setattr(worker.sys, "platform", "darwin")
    def bootstrap_failed(*_args, **_kwargs):
        raise subprocess.CalledProcessError(1, "launchctl", stderr="synthetic private diagnostic")
    monkeypatch.setattr(worker.subprocess, "run", bootstrap_failed)
    with pytest.raises(subprocess.CalledProcessError):
        worker.launchd_watchdog(store)
    record = store.read()
    assert record["watchdog_start_status"] == "bootstrap-failed"
    assert "synthetic private diagnostic" not in json.dumps(record)


@pytest.mark.parametrize("status", [400, 401, 403, 404, 422])
def test_authoritative_create_rejection_closes_record_without_retry_or_deletion(store, status):
    calls = []
    def rejected(method, url, *, payload=None):
        calls.append(method)
        if method == "GET":
            return []
        if method == "POST":
            raise worker.runpodctl.RunpodHTTPError(status, "synthetic private provider response")
        pytest.fail("rejected create must not trigger a DELETE")
    with pytest.raises(worker.runpodctl.RunpodHTTPError):
        worker.provision_once(store, rejected, lookup=lookup, now=100)
    assert calls == ["GET", "POST"]
    assert worker.terminate_owned(store, rejected)
    assert calls == ["GET", "POST"]
    record = store.read()
    assert record["termination_verified"] and record["create_rejection_http_status"] == status
    assert record["create_attempted"] and record["pod_id"] is None
    assert "private provider response" not in json.dumps(record)
    with pytest.raises(worker.LifecycleError, match="already attempted"):
        worker.provision_once(store, rejected, lookup=lookup, now=100)
    assert calls.count("POST") == 1


@pytest.mark.parametrize("error", [
    worker.runpodctl.RunpodHTTPError(500, "server error"),
    worker.runpodctl.RunpodHTTPError(503, "unavailable"),
    worker.runpodctl.RunpodHTTPError(408, "request timeout"),
    worker.runpodctl.RunpodHTTPError(409, "conflict"),
    worker.runpodctl.RunpodHTTPError(429, "rate limit"),
    SystemExit("Runpod API returned HTTP 403: only untyped text"),
    TimeoutError("connection timed out"),
])
def test_uncertain_create_outcomes_remain_unresolved_and_never_retry(store, error):
    calls = []
    def uncertain(method, url, *, payload=None):
        calls.append(method)
        if method == "GET":
            return []
        if method == "POST":
            raise error
        pytest.fail("no exact ownership means no DELETE")
    with pytest.raises((Exception, SystemExit)):
        worker.provision_once(store, uncertain, lookup=lookup, now=100)
    assert not worker.create_was_definitively_rejected(store.read())
    assert not worker.terminate_owned(store, uncertain)
    assert not store.read()["termination_verified"]
    assert calls.count("POST") == 1
    assert "DELETE" not in calls


def test_later_get_4xx_cannot_reclassify_a_successful_create_as_rejected(store):
    provider = Provider(store)
    def missing_contract_permission(method, url, *, payload=None):
        if method == "GET" and url.split("?", 1)[0].endswith("/created-owned"):
            raise worker.runpodctl.RunpodHTTPError(403, "lookup not permitted")
        return provider(method, url, payload=payload)
    with pytest.raises(worker.runpodctl.RunpodHTTPError):
        worker.provision_once(store, missing_contract_permission, lookup=lookup, now=100)
    assert store.read()["pod_id"] == "created-owned"
    assert not worker.create_was_definitively_rejected(store.read())
    assert not store.read()["termination_verified"]


def service_for(store):
    return f"gui/{worker.os.getuid()}/io.butterfly.exp477.{store.read()['nonce']}"


def absent_service_result(service):
    from types import SimpleNamespace
    return SimpleNamespace(returncode=113, stdout="", stderr=(
        "Bad request.\nCould not find service \"" + service.rsplit("/", 1)[1]
        + f"\" in domain for user gui: {worker.os.getuid()}\n"))


def test_retirement_checks_exact_service_and_both_watchdog_and_caffeinate_identity_exit(store, monkeypatch):
    from types import SimpleNamespace
    service = service_for(store)
    store.update(termination_verified=True, launchd_service=service)
    commands = []
    responses = iter([SimpleNamespace(returncode=0, stdout="\tpid = 789\n", stderr=""),
                      SimpleNamespace(returncode=0), absent_service_result(service)])
    def run(argv, **_kwargs):
        commands.append(argv)
        return next(responses)
    def process_identity(pid):
        # Capture launcher identity before bootout; afterward both are gone.
        return "launcher-start" if pid == 789 and len(commands) == 1 else None
    monkeypatch.setattr(worker.subprocess, "run", run)
    worker.retire_watchdog(store, lookup=process_identity)
    record = store.read()["local_watchdog_retirement"]
    assert record["requested"] and record["verified"]
    assert record["service_absence_verified"] and record["known_process_exit_verified"]
    assert {row["pid"] for row in record["known_processes"]} == {456, 789}
    assert commands == [["/bin/launchctl", "print", service], ["/bin/launchctl", "bootout", service],
                        ["/bin/launchctl", "print", service]]


def test_nonzero_launchctl_permission_failure_cannot_be_called_service_absence(store, monkeypatch):
    from types import SimpleNamespace
    store.update(termination_verified=True, launchd_service=service_for(store))
    monkeypatch.setattr(worker.subprocess, "run", lambda *_args, **_kwargs: SimpleNamespace(
        returncode=5, stdout="", stderr="Input/output error"))
    with pytest.raises(worker.LifecycleError, match="absence could not"):
        worker.retire_watchdog(store, lookup=lambda _pid: None)
    record = store.read()["local_watchdog_retirement"]
    assert not record["requested"] and not record["verified"]


def test_absent_service_with_still_live_owned_pid_is_not_verified_retired(store, monkeypatch):
    from types import SimpleNamespace
    service = service_for(store)
    store.update(termination_verified=True, launchd_service=service)
    def run(argv, **_kwargs):
        return absent_service_result(service) if argv[1] == "print" else SimpleNamespace(returncode=113)
    monkeypatch.setattr(worker.subprocess, "run", run)
    stamp = [0.0]
    def pause(seconds):
        stamp[0] += seconds
    with pytest.raises(worker.LifecycleError, match="retirement remains unconfirmed"):
        worker.retire_watchdog(store, timeout=1, lookup=lookup, clock=lambda: stamp[0], pause=pause)
    record = store.read()["local_watchdog_retirement"]
    assert record["requested"] and not record["verified"]
    assert record["service_absence_verified"] and not record["known_process_exit_verified"]


def test_retirement_rejects_wrong_service_before_any_local_mutation(store, monkeypatch):
    store.update(termination_verified=True, launchd_service="gui/501/unrelated-service")
    monkeypatch.setattr(worker.subprocess, "run", lambda *_args, **_kwargs: pytest.fail("wrong service touched"))
    with pytest.raises(worker.OwnershipError):
        worker.retire_watchdog(store)


def test_retirement_treats_reused_pid_as_original_process_exited(store, monkeypatch):
    from types import SimpleNamespace
    service = service_for(store)
    store.update(termination_verified=True, launchd_service=service)
    monkeypatch.setattr(worker.subprocess, "run", lambda argv, **_kwargs:
                        absent_service_result(service) if argv[1] == "print" else SimpleNamespace(returncode=113))
    worker.retire_watchdog(store, lookup=lambda _pid: "different-process-start")
    assert store.read()["local_watchdog_retirement"]["verified"]


def test_private_credential_fingerprint_hashes_only_injected_key():
    import hashlib
    secret = "synthetic-high-entropy-key-for-local-test-only"
    assert REAL_CREDENTIAL_FINGERPRINT(lambda: secret) == hashlib.sha256(secret.encode()).hexdigest()
    for invalid in (None, "", 123):
        with pytest.raises(worker.LifecycleError):
            REAL_CREDENTIAL_FINGERPRINT(lambda: invalid)


def test_watchdog_different_credential_cannot_probe_or_authorize_create(store, monkeypatch):
    monkeypatch.setattr(worker.os, "getpid", lambda: 456)
    monkeypatch.setattr(worker, "control_plane_credential_fingerprint", lambda: "b" * 64)
    with pytest.raises(worker.LifecycleError, match="readiness failed"):
        worker.probe_watchdog_control_plane(store, lambda *_args: pytest.fail("different account must not be queried"),
                                          lookup=lookup, clock=lambda: 100)
    assert json.loads((store.directory / "watchdog-control-plane.json").read_bytes())["passed"] is False
    provider = Provider(store)
    with pytest.raises(worker.LifecycleError, match="credential"):
        worker.provision_once(store, provider, lookup=lookup, now=100)
    assert not provider.calls


def test_passing_watchdog_probe_from_another_account_is_rejected_before_create(store):
    path = store.directory / "watchdog-control-plane.json"
    readiness = json.loads(path.read_bytes())
    readiness["credential_fingerprint"] = "b" * 64
    worker.atomic_json(path, readiness)
    worker.atomic_json(store.directory / readiness["history_file"], readiness)
    provider = Provider(store)
    with pytest.raises(worker.LifecycleError, match="watchdog"):
        worker.provision_once(store, provider, lookup=lookup, now=100)
    assert not provider.calls


def test_changed_controller_credential_cannot_claim_wrong_account_absence(store, monkeypatch):
    provider = Provider(store)
    worker.provision_once(store, provider, lookup=lookup, now=100)
    before = len(provider.calls)
    monkeypatch.setattr(worker, "control_plane_credential_fingerprint", lambda: "b" * 64)
    with pytest.raises(worker.LifecycleError, match="credential"):
        worker.terminate_owned(store, provider)
    assert len(provider.calls) == before
    assert not store.read()["termination_verified"]


def test_ambiguous_create_and_restarted_watchdog_cannot_query_another_account(store, monkeypatch):
    store.update(create_attempted=True, create_attempted_at=100)
    monkeypatch.setattr(worker, "control_plane_credential_fingerprint", lambda: "b" * 64)
    with pytest.raises(worker.LifecycleError, match="credential"):
        worker.reconcile_ambiguous_create(store, lambda *_args: pytest.fail("wrong-account inventory forbidden"))
    monkeypatch.setattr(worker, "write_heartbeat", lambda *_args, **_kwargs: None)
    with pytest.raises(worker.LifecycleError, match="wrong-account"):
        worker.watchdog_loop(store)
    assert store.read()["watchdog_credential_binding_failed"]
    assert not store.read()["termination_verified"]


def test_fingerprint_is_not_part_of_worker_create_payload(store):
    assert SYNTHETIC_CREDENTIAL_FINGERPRINT not in json.dumps(worker.create_payload(store.read()))

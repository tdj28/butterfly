"""Synthetic watchdog smoke controls; no credentials, launchd or network."""

from contextlib import nullcontext

import pytest

from scripts import smoke_symbolic_watchdog as smoke


def test_smoke_request_forbids_mutations_before_network(monkeypatch):
    monkeypatch.setattr(smoke.worker.runpodctl, "request_json", lambda *_a, **_k: pytest.fail("network"))
    for method in ("POST", "DELETE", "PATCH", "PUT"):
        with pytest.raises(smoke.worker.LifecycleError, match="forbids"):
            smoke.read_only_request(method, "synthetic")


@pytest.mark.parametrize("fail_start", [False, True])
def test_smoke_success_or_failure_always_retires_without_create(tmp_path, monkeypatch, fail_start):
    state = {"create_attempted": False, "pod_id": None}
    calls = []

    class Store:
        def read(self):
            return dict(state)

        def update(self, **values):
            state.update(values)

    monkeypatch.setattr(smoke.worker, "single_controller_lock", nullcontext)
    monkeypatch.setattr(smoke.worker, "require_no_unresolved_controller", lambda: None)
    monkeypatch.setattr(smoke.worker, "prepare_store", lambda *_: Store())
    monkeypatch.setattr(smoke.worker, "register_controller", lambda *_: None)
    monkeypatch.setattr(smoke.worker, "write_heartbeat", lambda *_: None)
    monkeypatch.setattr(smoke.worker, "require_watchdog", lambda *_: calls.append("readiness"))
    monkeypatch.setattr(smoke.worker, "heartbeat_record", lambda *_: {"synthetic": True})
    monkeypatch.setattr(smoke.worker, "provision_once", lambda *_: pytest.fail("no creation in smoke"))

    def terminate(store, *, request):
        assert request is smoke.read_only_request
        calls.append("terminate-no-create")
        store.update(termination_reason="no create request was issued", termination_verified=True)
        return True

    def start(_):
        calls.append("start")
        if fail_start:
            raise RuntimeError("synthetic startup failure")

    monkeypatch.setattr(smoke.worker, "terminate_owned", terminate)
    result = smoke.run_control({"source_commit": "a" * 40}, tmp_path / "private", tmp_path / "receipt.json",
                               start_watchdog=start, stop_watchdog=lambda _: calls.append("retire"))
    assert result["passed"] is not fail_start
    assert result["provider_create_called"] is False
    assert result["provider_mutations_performed"] is False
    assert calls[-2:] == ["terminate-no-create", "retire"]
    assert (tmp_path / "receipt.json").is_file()


def test_existing_receipt_is_never_overwritten(tmp_path):
    path = tmp_path / "receipt.json"
    path.write_text("preserve")
    with pytest.raises(ValueError, match="new"):
        smoke.run_control({"source_commit": "a" * 40}, tmp_path / "private", path)
    assert path.read_text() == "preserve"

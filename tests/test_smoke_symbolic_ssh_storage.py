"""Synthetic CLI controls only; no Git, SSH, provider, or trajectory execution."""

import hashlib
import inspect
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import smoke_symbolic_ssh_storage as smoke


COMMIT = "a" * 40
REMOTE = smoke.storage.BASE_DIRECTORY + "/synthetic-smoke"


def source_value():
    return {"commit": COMMIT, "source_files": {name: "b" * 64 for name in smoke.SOURCE_FILES},
            "exact_origin_refs": ["refs/remotes/origin/synthetic"],
            "remote_check": "local remote-tracking refs only; no Git network call"}


def test_default_is_source_preflight_without_ssh(tmp_path, monkeypatch):
    monkeypatch.setattr(smoke, "frozen_source", lambda _: source_value())
    monkeypatch.setattr(smoke, "execute_smoke", lambda *args: pytest.fail("SSH smoke invoked"))
    assert smoke.main(["--source-commit", COMMIT, "--remote-dir", REMOTE, "--output-dir", str(tmp_path / "new")]) == 0
    assert not (tmp_path / "new").exists()


def test_execute_is_explicit_and_reports_failed_smoke_nonzero(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(smoke, "execute_smoke", lambda *args: calls.append(args) or {"passed": False})
    assert smoke.main(["--source-commit", COMMIT, "--remote-dir", REMOTE,
                       "--output-dir", str(tmp_path / "new"), "--execute"]) == 2
    assert calls[0] == (COMMIT, REMOTE, tmp_path / "new")


@pytest.mark.parametrize("content", [b"REMOTE_PROGRAM = str('dynamic')", b"REMOTE_PROGRAM=1",
                                      b"REMOTE_PROGRAM='first'\nREMOTE_PROGRAM='second'", b"unrelated='x'"])
def test_bootstrap_must_be_one_literal_without_evaluating_code(content):
    with pytest.raises((smoke.storage.StorageError, ValueError)):
        smoke.worker_literal(content)


def test_literal_bootstrap_is_extracted_without_importing_wrapper():
    assert smoke.worker_literal(b"raise RuntimeError('never run')\nREMOTE_PROGRAM = r'''owned control'''\n") == "owned control"


def test_synthetic_grandchild_has_self_expiry_if_controller_disappears():
    source = inspect.getsource(smoke.storage.quiescence_smoke)
    assert "deadline=time.monotonic()+20" in source
    assert "while time.monotonic()<deadline" in source
    assert "while True" not in source


@pytest.mark.parametrize("mutation", [None, "dirty", "uncommitted_file", "unpushed"])
def test_clean_committed_pushed_source_binding_uses_mock_git_only(tmp_path, monkeypatch, mutation):
    source = {name: ("# synthetic " + name).encode() for name in smoke.SOURCE_FILES}
    for name, content in source.items():
        path = tmp_path / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(content)
    def git(argv, **kwargs):
        args = argv[1:]
        if args[0] == "rev-parse": return (COMMIT + "\n").encode()
        if args[0] == "status": return b" M tracked.py\n" if mutation == "dirty" else b""
        if args[0] == "for-each-ref": return b"" if mutation == "unpushed" else (COMMIT + " refs/remotes/origin/frozen\n").encode()
        if args[0] == "show":
            name = args[1].split(":", 1)[1]
            return b"changed" if mutation == "uncommitted_file" else source[name]
        pytest.fail("unexpected Git command")
    monkeypatch.setattr(smoke.subprocess, "check_output", git)
    if mutation:
        with pytest.raises(smoke.storage.StorageError):
            smoke.frozen_source(COMMIT, root=tmp_path)
    else:
        value = smoke.frozen_source(COMMIT, root=tmp_path)
        assert value["commit"] == COMMIT
        assert value["source_files"] == {name: hashlib.sha256(content).hexdigest() for name, content in source.items()}


@pytest.mark.parametrize("changed", [False, True])
def test_remote_quiescence_receipt_must_match_frozen_source(tmp_path, monkeypatch, changed):
    content = b"REMOTE_PROGRAM = 'synthetic control'"
    source = source_value()
    source["source_files"]["scripts/execute_symbolic_center_cloud.py"] = hashlib.sha256(content).hexdigest()
    store = SimpleNamespace(binding={"remote_directory": REMOTE, "helper_sha256": "c" * 64,
                                     "expected_binding_sha256": "d" * 64})
    def fake_output(argv, output, **kwargs):
        assert argv[0] == "/usr/bin/ssh" and smoke.storage.HOST in argv
        assert "StrictHostKeyChecking=yes" in argv and "ForwardAgent=no" in argv
        payload = json.loads(kwargs["input_bytes"])
        assert payload["source_commit"] == COMMIT
        receipt = {"schema": "butterfly.symbolic-quiescence-smoke.v1", "passed": True,
                   "source_commit": "0" * 40 if changed else COMMIT,
                   "wrapper_sha256": source["source_files"]["scripts/execute_symbolic_center_cloud.py"],
                   "helper_sha256": "c" * 64}
        output.write(json.dumps(receipt).encode())
    monkeypatch.setattr(smoke.storage, "bounded_output", fake_output)
    if changed:
        with pytest.raises(smoke.storage.StorageError, match="source binding"):
            smoke.run_quiescence(store, content, source, tmp_path)
    else:
        assert smoke.run_quiescence(store, content, source, tmp_path)["passed"]


@pytest.mark.parametrize("failure", [None, "storage", "storage_false", "quiescence", "changed_source"])
def test_orchestrator_retains_source_bound_success_or_honest_failure(tmp_path, monkeypatch, failure):
    source = source_value()
    path = tmp_path / smoke.SOURCE_FILES[2]
    path.parent.mkdir(parents=True)
    path.write_bytes(b"REMOTE_PROGRAM = 'synthetic control'")
    source_calls = []
    def frozen(*args, **kwargs):
        source_calls.append(1)
        return {**source, "commit": "0" * 40} if failure == "changed_source" and len(source_calls) > 1 else source
    monkeypatch.setattr(smoke, "frozen_source", frozen)
    def transport(remote, output, **kwargs):
        output.mkdir()
        if failure == "storage": raise smoke.storage.StorageError("synthetic transport failure")
        return {"passed": failure != "storage_false", "remote_storage_binding": {"schema": "synthetic binding"}}
    monkeypatch.setattr(smoke.storage, "storage_smoke", transport)
    monkeypatch.setattr(smoke.storage.SshEvidenceStore, "open_existing", lambda *args, **kwargs: SimpleNamespace())
    def quiescence(*args):
        if failure == "quiescence": raise smoke.storage.StorageError("synthetic quiescence failure")
        return {"passed": True}
    monkeypatch.setattr(smoke, "run_quiescence", quiescence)
    output = tmp_path / "receipt"
    result = smoke.execute_smoke(COMMIT, REMOTE, output, root=tmp_path)
    assert result["passed"] is (failure is None)
    assert result["source_commit"] == COMMIT
    assert json.loads((output / "qualification-smoke.json").read_bytes()) == result
    assert result["runpod_calls_performed"] is False and result["target_computation_performed"] is False
    with pytest.raises(smoke.storage.StorageError, match="must be new"):
        smoke.execute_smoke(COMMIT, REMOTE, output, root=tmp_path)

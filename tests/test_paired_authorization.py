"""Actual controller/worker grant controls; no private inputs or target field calls."""
import copy
from dataclasses import asdict
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import threading
import time

import pytest

from butterfly import paired_authorization as auth
from butterfly._paired_startup import sha256
from butterfly.paired_phase_control import make_control
from butterfly.paired_phases import phase_limits
from butterfly.paired_supervisor import StageLimits, process_table, supervise
from scripts.build_paired_runtime import ROOT, build
from scripts.dispatch_paired_phases import completed_worker


def control_grant(runtime_sha):
    design, _ = make_control()
    return dict(schema="butterfly.paired-phase-grant.v1", kind="analytic-circle", phase="qualification",
        runtime_contract_sha256=runtime_sha, source_commit=design.source_commit, plan_sha256=design.plan_sha256,
        design_sha256=design.identity(), campaign_slot_sha256="a"*64, release_sha256=None,
        release_mode=None, preflight_sha256=None,
        input_root=None, input_contract_sha256=None, previous=None,
        limits=asdict(phase_limits(design.plan, "qualification")), deadline_monotonic=time.monotonic()+60.)


def test_kernel_socketpair_credential_is_creator():
    left, right = socket.socketpair()
    try:
        assert auth.peer_pid(left) == auth.peer_pid(right) == os.getpid()
    finally:
        left.close()
        right.close()


def test_actual_process_executable_is_not_inferred_from_argv():
    assert auth.process_executable(os.getpid()) == Path(sys.executable).resolve()


def test_fictional_executable_cannot_be_rescued_by_correct_controller_bytes(monkeypatch):
    contract = dict(controller=dict(path=str(ROOT/"scripts/run_paired_campaign.py"), sha256=auth.CONTROLLER_SOURCE_SHA256),
        interpreter=dict(path=str(Path(sys.executable).resolve())))
    argv = [sys.executable, "-B", contract["controller"]["path"], "--mode", "control"]
    monkeypatch.setattr(auth, "process_executable", lambda pid: Path("/not-the-interpreter"))
    with pytest.raises(ValueError, match="actual parent executable differs"):
        auth.verify_parent(os.getppid(), argv, contract, "analytic-circle")


def test_controller_authority_is_independent_of_received_contract(tmp_path):
    assert sha256(ROOT/"scripts/run_paired_campaign.py") == auth.CONTROLLER_SOURCE_SHA256
    fake = tmp_path/"different-controller.py"
    fake.write_text("# A caller-supplied, coherently hashed substitute is not authority.\n")
    contract = dict(controller=dict(path=str(fake), sha256=sha256(fake)))
    with pytest.raises(ValueError, match="independently frozen"):
        auth.verify_parent(os.getppid(), [], contract, "target")


@pytest.mark.parametrize("kind", ["correct", "wrong-phase", "expired", "too-long", "bad-hash", "research-input", "previous", "fake-target-review"])
def test_phase_policy_rejects_rehashed_inconsistent_grants(kind):
    grant = control_grant("b"*64)
    if kind == "wrong-phase": grant["phase"] = "analysis"
    elif kind == "expired": grant["deadline_monotonic"] = time.monotonic()-1
    elif kind == "too-long": grant["limits"]["wall_seconds"] = 20000
    elif kind == "bad-hash": grant["design_sha256"] = "short"
    elif kind == "research-input": grant["input_root"] = "/not-a-control-input"
    elif kind == "previous": grant["previous"] = {}
    elif kind == "fake-target-review": grant["kind"] = "target"
    assert len(auth.digest(grant)) == 64
    if kind == "correct": assert 0 < auth.validate_grant(grant, "qualification", "b"*64) <= 60
    else:
        with pytest.raises((ValueError, TypeError)):
            auth.validate_grant(grant, "qualification", "b"*64)


@pytest.mark.parametrize("raw", [b"", b"{} ", b"{\"value\":NaN}", b"{\"x\":1,\"x\":2}"])
def test_noncanonical_or_nonfinite_wire_messages_fail(raw):
    left, right = socket.socketpair()
    try:
        left.sendall(struct.pack("!I", len(raw))+raw)
        with pytest.raises(ValueError): auth.receive(right)
    finally:
        left.close()
        right.close()


def test_message_bound_is_symmetric_at_exact_ceiling():
    left, right = socket.socketpair()
    value = "x"*(auth.MAXIMUM_MESSAGE_BYTES-2)
    try:
        assert len(auth.canonical(value)) == auth.MAXIMUM_MESSAGE_BYTES
        thread = threading.Thread(target=auth.send, args=(left, value))
        thread.start()
        assert auth.receive(right) == value
        thread.join(timeout=2)
        assert not thread.is_alive()
        with pytest.raises(ValueError): auth.send(left, value+"x")
        left.sendall(struct.pack("!I", auth.MAXIMUM_MESSAGE_BYTES+1))
        with pytest.raises(ValueError): auth.receive(right)
    finally:
        left.close()
        right.close()


def test_issuer_consumes_failed_attempt_too():
    left, right = socket.socketpair()
    try:
        callback = auth.issuer(left, control_grant("b"*64), [])
        auth.send(right, dict(pid=-1, challenge="a"*64, grant_sha256="b"*64))
        process = type("Process", (), dict(pid=os.getpid()))()
        with pytest.raises(ValueError, match="actual launched"): callback(process)
        with pytest.raises(ValueError, match="already consumed"): callback(process)
    finally:
        left.close()
        right.close()


@pytest.fixture(scope="module", params=["EXP-481", "EXP-482"])
def actual_control(tmp_path_factory, request):
    output = tmp_path_factory.mktemp("authorized-phases")/"run"
    command = [sys.executable, "-B", str(ROOT/"scripts/run_paired_campaign.py"), "--mode", "control", "--output-dir", str(output)]
    if request.param == "EXP-482": command += ["--experiment-id", request.param]
    result = subprocess.run(command, capture_output=True, text=True, timeout=100)
    assert result.returncode == 0, result.stdout+result.stderr
    return output, command


def test_actual_controller_runs_complete_fixed_control_with_verified_parent(actual_control):
    output, command = actual_control
    summary = json.loads((output/"campaign/receipt.json").read_bytes())
    assert summary["status"] == "completed" and summary["all_cases_primary_resolved"]
    assert summary["target_slot_consumed"] is False and summary["target_trajectories_generated"] == 0
    assert not summary["historical_symbols_verified"]
    for phase in auth.STAGES:
        root = output/"campaign"/phase
        authorization = json.loads((root/"authorization.json").read_bytes())
        assert authorization["actual_parent_verified"] and authorization["guard_alive"]
        assert not authorization["scientific_imports_before_guard"]
        assert authorization["grant"]["limits"]["wall_seconds"] == 60
        assert authorization["grant"]["kind"] == "analytic-circle"
        witness = json.loads((root/"phase-witness.json").read_bytes())
        assert witness["target_trajectories_generated"] == 0 and not witness["target_phase_started"]
    repeated = subprocess.run(command, capture_output=True, text=True, timeout=10)
    assert repeated.returncode != 0 and "FileExistsError" in repeated.stderr


@pytest.mark.parametrize("fault", ["wrong-grant", "wrong-parent-argv", "wrong-predecessor", "missing-grant"])
def test_real_controller_negative_grants_stop_without_next_phase(tmp_path, fault):
    output = tmp_path/"run"
    command = [sys.executable, "-B", str(ROOT/"scripts/run_paired_campaign.py"), "--mode", "control",
        "--output-dir", str(output), "--control-fault", fault]
    result = subprocess.run(command, capture_output=True, text=True, timeout=80)
    assert result.returncode != 0
    root = output/"campaign"
    failure = json.loads((root/"failure.json").read_bytes())
    assert failure["target_trajectories_generated"] == 0 and not failure["target_slot_consumed"]
    phase = "collection" if fault == "wrong-predecessor" else "qualification"
    receipt = json.loads((root/phase/"supervisor/terminal.json").read_bytes())
    assert receipt["status"] == "incomplete" and receipt["owned_group_cleanup_verified"]
    assert not (root/phase/"phase").exists() and not (root/"analysis").exists()
    assert not (root/"receipt.json").exists()


def test_correct_hashes_and_copied_controller_argv_do_not_authorize_foreign_parent(tmp_path):
    runtime = build(tmp_path/"runtime")
    contract = json.loads((tmp_path/"runtime/runtime-contract.json").read_bytes())
    grant = control_grant(runtime["sha256"])
    output = tmp_path/"worker"
    output.mkdir()
    left, right = socket.socketpair()
    try:
        # Every field/hash names real valid bytes, but this process is pytest,
        # not that ordinary controller command. Kernel PID alone is not enough.
        fictional = [sys.executable, "-B", contract["controller"]["path"], "--mode", "control", "--output-dir", str(tmp_path)]
        command = [sys.executable, "-I", "-S", "-B", "-X", "utf8", str(tmp_path/"runtime/worker.py"),
            "--contract-sha256", runtime["sha256"], "--output-dir", str(output), "--mode", "authorized-phase",
            "--phase", "qualification", "--grant-fd", str(right.fileno()), "--grant-sha256", auth.digest(grant)]
        result = supervise(command, cwd=tmp_path, evidence_directory=output, state_directory=output/"supervisor",
            environment=contract["environment"], binding=dict(kind="foreign-parent-negative-control"),
            limits=StageLimits(20., 512*1024**2, 128*1024**2, 0), pass_fds=(right.fileno(),),
            on_spawn=auth.issuer(left, grant, fictional))
        assert result["status"] == "incomplete" and result["owned_group_cleanup_verified"]
        failure = json.loads((output/"failure.json").read_bytes())
        assert "actual parent argv differs" in failure["message"]
        assert failure["target_trajectories_generated"] == 0
        assert not (output/"startup.json").exists() and not (output/"phase").exists()
    finally:
        left.close()
        right.close()


@pytest.mark.parametrize("kind", ["supervisor", "witness", "phase-bytes"])
def test_next_phase_gate_rejects_modified_predecessor(actual_control, tmp_path, kind):
    import shutil
    output, _ = actual_control
    design, _ = make_control()
    root = tmp_path/"qualification"
    shutil.copytree(output/"campaign/qualification", root)
    summary = json.loads((output/"campaign/receipt.json").read_bytes())
    row = copy.deepcopy(summary["phases"]["qualification"])
    if kind in ("supervisor", "witness"):
        path = root/row["receipts"][kind]["path"]
        payload = json.loads(path.read_bytes())
        if kind == "supervisor": payload["owned_group_cleanup_verified"] = False
        else: payload["grant_sha256"] = "0"*64
        path.write_text(json.dumps(payload))
        row["receipts"][kind].update(bytes=path.stat().st_size, sha256=sha256(path))
    else:
        with (root/"phase/comparisons.json").open("ab") as stream: stream.write(b"\n")
    runtime_sha = json.loads((root/"phase-witness.json").read_bytes())["runtime_contract_sha256"]
    with pytest.raises(ValueError):
        completed_worker(root, row["receipts"], design, "qualification", row["grant_sha256"], runtime_sha, target=False)


def test_target_cli_cannot_enable_control_override(tmp_path):
    result = subprocess.run([sys.executable, "-B", str(ROOT/"scripts/run_paired_campaign.py"), "--mode", "execute",
        "--source-commit", "a"*40, "--remote-ref", "refs/heads/control", "--output-dir", str(tmp_path/"forbidden"),
        "--control-fault", "wrong-grant"], capture_output=True, text=True, timeout=10)
    assert result.returncode != 0 and "only in analytic control" in result.stderr
    assert not (tmp_path/"forbidden").exists()


def test_actual_authorized_worker_stops_on_controller_loss_and_preserves_prefix(tmp_path):
    output = tmp_path/"run"
    command = [sys.executable, "-B", str(ROOT/"scripts/run_paired_campaign.py"), "--mode", "control", "--output-dir", str(output)]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        phase = output/"campaign/collection"
        deadline = time.monotonic()+40
        while not list((phase/"phase/trials").glob("*/*.npz")):
            if process.poll() is not None or time.monotonic() > deadline:
                pytest.fail("actual authorized collection did not publish a raw prefix")
            time.sleep(.01)
        child = json.loads((phase/"supervisor/ownership.json").read_bytes())["pid"]
        assert json.loads((phase/"authorization.json").read_bytes())["actual_parent_verified"]
        process.kill()
        process.communicate(timeout=5)
        deadline = time.monotonic()+5
        while time.monotonic() < deadline:
            row = process_table().get(child)
            if row is None or row["state"].startswith("Z"):
                break
            time.sleep(.02)
        else:
            pytest.fail("authorized worker survived controller pipe loss")
        assert list((phase/"phase/trials").glob("*/*.npz"))
        assert not (phase/"phase/terminal.json").exists()
        assert not (phase/"phase-witness.json").exists()
        assert not (output/"campaign/receipt.json").exists()
        assert not (output/"campaign/analysis").exists()
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)

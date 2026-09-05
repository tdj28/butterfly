"""Synthetic local-only deployment/retention controls; no provider or numerical jobs."""

from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tarfile
from types import SimpleNamespace

import pytest

from scripts import execute_symbolic_center_cloud as cloud


COMMIT = "a" * 40
LIMITS = {"maximum_total_bytes": 4096, "maximum_files": 20}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    return cloud.pilot.write_new_json(path, value)


@pytest.mark.parametrize("name", ["docs", "docs/experiments", "experiments"])
def test_source_allows_only_necessary_ancestor_directories(name):
    assert cloud.source_allowed(name, directory=True)
    assert not cloud.source_allowed(name)


@pytest.mark.parametrize("name", ["scripts/.env", "python/id_rsa", "scripts/id_ed25519", "python/key.pem",
                                  "scripts/x.key", "scripts/__pycache__/a.py", "scripts/.cache/a.py",
                                  "docs/private.json", "experiments/unlisted.json", "scripts/../README.md",
                                  "/scripts/a.py", "scripts/a.sh", "python/a.pyc", "scripts//a.py"])
def test_source_rejects_secret_cache_and_unlisted_members(name):
    assert not cloud.source_allowed(name)


@pytest.mark.parametrize("name", ["scripts/a.py", "python/butterfly/a.py", cloud.RUNTIME_MANIFEST,
                                  "docs/experiments/receipts/EXP-001.json", "uv.lock", "LICENSE"])
def test_source_accepts_explicit_runtime_file_types(name):
    assert cloud.source_allowed(name)


def make_tar(path, files, *, dirs=(), links=()):
    with tarfile.open(path, "w:") as archive:
        for name in dirs:
            item = tarfile.TarInfo(name); item.type = tarfile.DIRTYPE
            archive.addfile(item)
        for name, content in files.items():
            item = tarfile.TarInfo(name); item.size = len(content)
            archive.addfile(item, io.BytesIO(content))
        for name in links:
            item = tarfile.TarInfo(name); item.type = tarfile.SYMTYPE; item.linkname = "/etc/passwd"
            archive.addfile(item)


def required_source_files():
    return {name: b"{}\n" for name in (cloud.PILOT_MANIFEST, cloud.RUNTIME_MANIFEST,
            "scripts/execute_symbolic_center_cloud.py", "scripts/run_symbolic_center_pilot.py",
            "scripts/qualify_symbolic_gpu_records.py", "scripts/symbolic_ssh_storage.py", "pyproject.toml", "uv.lock")}


def test_git_archive_inventory_uses_only_committed_bytes_and_safe_ancestors(tmp_path, monkeypatch):
    files = required_source_files()
    def fake_archive(argv, **kwargs):
        assert argv[:3] == ["git", "archive", "--format=tar"]
        assert argv[5:] == [COMMIT, "--", *cloud.SOURCE_PATHS]
        make_tar(Path(argv[4]), files, dirs=("docs", "docs/experiments", "experiments"))
    monkeypatch.setattr(cloud.subprocess, "run", fake_archive)
    result = cloud.build_source_archive(tmp_path, COMMIT, tmp_path / "source.tar")
    assert result["files"] == {name: hashlib.sha256(value).hexdigest() for name, value in files.items()}
    assert result["source_commit"] == result["pushed_source_commit"] == COMMIT


@pytest.mark.parametrize("kind", ["secret_filename", "secret_content", "symlink"])
def test_archive_rejects_credentials_and_links_before_upload(tmp_path, monkeypatch, kind):
    files = required_source_files()
    if kind == "secret_filename":
        files["scripts/.env"] = b"SENSITIVE=value"
    elif kind == "secret_content":
        files["scripts/ordinary.py"] = b"# " + b"-----BEGIN " + b"PRIVATE KEY-----"
    def fake_archive(argv, **kwargs):
        make_tar(Path(argv[4]), files, links=("python/link.py",) if kind == "symlink" else ())
    monkeypatch.setattr(cloud.subprocess, "run", fake_archive)
    with pytest.raises(cloud.DeploymentError, match="unsafe|credential"):
        cloud.build_source_archive(tmp_path, COMMIT, tmp_path / "source.tar")


def remote_local(mode, base, value=None):
    argv = [sys.executable, "-c", cloud.REMOTE_PROGRAM, mode, str(base)]
    if value is not None:
        argv.append(json.dumps(value))
    return subprocess.run(argv, capture_output=True, timeout=10)


@pytest.mark.parametrize("bad_name", [None, "scripts/.env", "python/id_rsa", "docs/private.json"])
def test_remote_extraction_mirrors_source_allowlist(tmp_path, bad_name):
    base = tmp_path / "worker"
    assert remote_local("init", base).returncode == 0
    files = {"scripts/control.py": b"pass\n", "experiments/manifests/control.json": b"{}"}
    if bad_name:
        files[bad_name] = b"do not stage"
    make_tar(base / "incoming/source.tar", files, dirs=("docs", "docs/experiments", "experiments"))
    (base / "incoming/candidates.json").write_bytes(b"[]")
    assets = {path.name: cloud.describe(path) for path in (base / "incoming").iterdir()}
    result = remote_local("extract", base, assets)
    assert (result.returncode == 0) is (bad_name is None)
    if bad_name is None:
        assert (base / "source/artifacts/EXP-204/candidates.json").read_bytes() == b"[]"


def test_disk_preflight_fails_before_any_directory_created(tmp_path, monkeypatch):
    monkeypatch.setattr(cloud.shutil, "disk_usage", lambda path: SimpleNamespace(free=10))
    with pytest.raises(cloud.DeploymentError, match="storage insufficient"):
        cloud.require_free_space(tmp_path / "new", LIMITS)
    assert not (tmp_path / "new").exists()
    monkeypatch.setattr(cloud.shutil, "disk_usage", lambda path: SimpleNamespace(free=10**12))
    value = cloud.require_free_space(tmp_path / "new", LIMITS)
    assert value["required_bytes"] > 2 * LIMITS["maximum_total_bytes"]


def test_ssh_task_identity_and_pinned_uploads_only(tmp_path):
    ssh = cloud.SSH("192.0.2.1", 22022, tmp_path)
    args = ssh.options()
    assert args[:2] == ["-F", "/dev/null"]
    for option in ("IdentitiesOnly=yes", "IdentityAgent=none", "ForwardAgent=no", "BatchMode=yes",
                   "GlobalKnownHostsFile=/dev/null", "StrictHostKeyChecking=accept-new"):
        assert option in args
    assert str(tmp_path / "task_ed25519") in args
    with pytest.raises(cloud.DeploymentError, match="pinned"):
        ssh.upload(tmp_path / "never-read", "/workspace/test")
    ssh.strict = True
    assert "StrictHostKeyChecking=yes" in ssh.options()


@pytest.mark.parametrize("pod", [{"publicIp": "not-a-host", "portMappings": {"22": 1}},
                                 {"publicIp": "192.0.2.1", "portMappings": {"22": True}},
                                 {"publicIp": "192.0.2.1", "portMappings": {"22": 0}}])
def test_ssh_endpoint_rejects_untrusted_host_or_invalid_port(pod):
    with pytest.raises((ValueError, cloud.DeploymentError)):
        cloud.endpoint(pod)


def test_ssh_endpoint_accepts_only_provider_direct_port_mapping():
    assert cloud.endpoint({"publicIp": "192.0.2.1", "portMappings": {"22": "22022"}}) == ("192.0.2.1", 22022)


@pytest.mark.parametrize("amount,limit,passed", [(256, 512, True), (1024 * 1024, 512, False)])
def test_stream_retrieval_enforces_byte_limit_before_disk_write(tmp_path, monkeypatch, amount, limit, passed):
    ssh = cloud.SSH("192.0.2.1", 22, tmp_path)
    monkeypatch.setattr(ssh, "argv", lambda _: [sys.executable, "-c", f"import sys; sys.stdout.buffer.write(b'x'*{amount})"])
    kwargs = dict(log_path=tmp_path / "log", seconds=5, progress=lambda _: None, base="unused",
                  binary_output=tmp_path / "raw", maximum_bytes=limit)
    if passed:
        ssh.monitored("synthetic", **kwargs)
        assert (tmp_path / "raw").stat().st_size == amount
    else:
        with pytest.raises(cloud.DeploymentError, match="byte limit"):
            ssh.monitored("synthetic", **kwargs)
        assert (tmp_path / "raw").stat().st_size <= limit


def test_stream_retrieval_deadline_preserves_partial_bytes(tmp_path, monkeypatch):
    ssh = cloud.SSH("192.0.2.1", 22, tmp_path)
    monkeypatch.setattr(ssh, "argv", lambda _: [sys.executable, "-c", "import sys,time; sys.stdout.buffer.write(b'x'); sys.stdout.flush(); time.sleep(5)"])
    with pytest.raises(TimeoutError):
        ssh.monitored("synthetic", log_path=tmp_path / "log", seconds=0.3, progress=lambda _: None,
                      base="unused", binary_output=tmp_path / "raw", maximum_bytes=10)
    assert (tmp_path / "raw").read_bytes() == b"x"


def retrieval_tar(path, files, *, alter_hash=False, links=()):
    rows = [{"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()} for name, data in files.items()]
    if alter_hash:
        rows[0]["sha256"] = "0" * 64
    inventory = {"schema": "butterfly.symbolic-remote-assets.v1", "assets": rows}
    make_tar(path, {"retrieval-manifest.json": json.dumps(inventory).encode(), **files}, links=links)
    return inventory


@pytest.mark.parametrize("kind", ["valid", "hash", "traversal", "unlisted", "symlink", "size"])
def test_safe_retrieval_hash_size_name_and_link_gates(tmp_path, kind):
    name = "gpu-control.json"
    if kind == "traversal":
        name = "../escape.json"
    if kind == "unlisted":
        name = "arbitrary.json"
    files = {name: b"{}" if kind != "size" else b"x" * (LIMITS["maximum_total_bytes"] + 1)}
    archive = tmp_path / "retrieved.tar"
    expected = retrieval_tar(archive, files, alter_hash=kind == "hash", links=("evil",) if kind == "symlink" else ())
    if kind == "valid":
        assert cloud.extract_retrieval(archive, tmp_path / "retrieved", LIMITS) == expected
        with pytest.raises(FileExistsError):
            cloud.extract_retrieval(archive, tmp_path / "retrieved", LIMITS)
    else:
        with pytest.raises(cloud.DeploymentError):
            cloud.extract_retrieval(archive, tmp_path / "retrieved", LIMITS)
    assert not (tmp_path / "escape.json").exists()


@pytest.fixture
def closure(tmp_path):
    directory = tmp_path / "retrieved"
    directory.mkdir()
    source = {"commit": COMMIT, "mode": "explicit_inventory", "inventory_sha256": "b" * 64}
    prepared = {"source_commit": COMMIT, "assets": {"source-inventory.json": {"sha256": "b" * 64}},
                "cpu_control_sha256": "c" * 64, "pilot_manifest_sha256": "d" * 64,
                "collection_binding": {"input_hashes": {"candidates": "e" * 64}, "candidate_ids": ["x", "y", "z"],
                                       "profiles": [{"dt": 0.01}, {"dt": 0.005}], "batch_size": 2}}
    write_json(tmp_path / "prepared-inputs/cpu-control.json", {"qualification_script_sha256": "f" * 64,
               "parent_sha256": cloud.qualification.PARENT_HASH, "state_atol": cloud.qualification.STATE_ATOL,
               "time_atol": cloud.qualification.TIME_ATOL})
    prepared["cpu_control_sha256"] = cloud.pilot.sha256_file(tmp_path / "prepared-inputs/cpu-control.json")
    gpu = {"schema": "butterfly.symbolic-gpu-deployment-control.v1", "mode": "gpu", "passed": True,
           "source": source, "cpu_control_sha256": prepared["cpu_control_sha256"], "parent_sha256": cloud.qualification.PARENT_HASH,
           "qualification_script_sha256": "f" * 64, "state_atol": cloud.qualification.STATE_ATOL,
           "time_atol": cloud.qualification.TIME_ATOL, "benchmark": {"projected_collection_seconds_with_margin": 1000.0}}
    write_json(directory / "gpu-control.json", gpu)
    receipt = {"schema": "butterfly.symbolic-center-collection.v1", "experiment_id": "EXP-477", "status": "completed",
               "collection_passed": True, "nomination_performed": False, "source": source,
               "manifest_sha256": prepared["pilot_manifest_sha256"], "input_hashes": prepared["collection_binding"]["input_hashes"],
               "completed_candidate_ids": ["x", "y", "z"], "uncompleted_candidate_ids": [], "batches": []}
    for index, ids in enumerate((["x", "y"], ["z"])):
        batch = {"index": index, "candidate_ids": ids, "profiles": []}
        for j, profile in enumerate(prepared["collection_binding"]["profiles"]):
            name = f"batch-{index:04d}-profile-{j}"
            path = directory / "collection" / (name + ".npz")
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(b"synthetic opaque raw bytes; closure only")
            metadata = {"schema": "butterfly.symbolic-center-raw-batch.v1", "validity_passed": True,
                        "profile": profile, "candidate_ids": ids, "raw": cloud.describe(path)}
            metadata["metadata_file"] = write_json(directory / "collection" / (name + ".json"), metadata)
            write_json(directory / "collection" / (name + "-checkpoint.json"), {"candidate_ids": ids, "raw_metadata": metadata})
            batch["profiles"].append(metadata)
        receipt["batches"].append(batch)
    write_json(directory / "collection/receipt.json", receipt)
    for name in ("collection/started.json", "environment/python.txt", "environment/pip-freeze.txt", "environment/nvidia-smi.txt",
                 "environment/torch.json", "environment/storage.json", "logs/setup.log", "logs/qualification.log", "logs/collection.log"):
        path = directory / name; path.parent.mkdir(exist_ok=True, parents=True); path.write_bytes(b"{}")
    for name in ("setup", "qualification", "collection"):
        write_json(directory / ("status/" + name + ".json"), {"passed": True})
    def inventory():
        return {"schema": "butterfly.symbolic-remote-assets.v1",
                "assets": [{**cloud.describe(path), "path": path.relative_to(directory).as_posix()}
                           for path in sorted(directory.rglob("*")) if path.is_file()]}
    return directory, prepared, inventory


def test_complete_raw_closure_is_hash_and_identity_checked_without_fitting(closure):
    directory, prepared, inventory = closure
    assert cloud.validate_retrieved_collection(directory, inventory(), prepared) == {
        "complete": True, "candidate_count": 3, "profile_batch_count": 4}


@pytest.mark.parametrize("mutation", ["missing_npz", "missing_gpu", "source", "failed", "ids", "profile", "metadata",
                                      "checkpoint", "manifest", "timing", "input", "missing_environment"])
def test_self_consistent_retrieval_cannot_pass_incomplete_or_unbound_closure(closure, mutation):
    directory, prepared, inventory = closure
    if mutation.startswith("missing_"):
        name = {"missing_npz": "collection/batch-0000-profile-0.npz", "missing_gpu": "gpu-control.json",
                "missing_environment": "environment/pip-freeze.txt"}[mutation]
        (directory / name).unlink()
    else:
        path = directory / ("gpu-control.json" if mutation == "timing" else "collection/receipt.json")
        value = json.loads(path.read_bytes())
        if mutation == "source": value["source"]["commit"] = "9" * 40
        elif mutation == "failed": value["collection_passed"] = False
        elif mutation == "ids": value["batches"][0]["candidate_ids"] = ["x", "x"]
        elif mutation == "profile": value["batches"][0]["profiles"].pop()
        elif mutation == "metadata": value["batches"][0]["profiles"][0]["metadata_file"]["sha256"] = "0" * 64
        elif mutation == "checkpoint": (directory / "collection/batch-0000-profile-0-checkpoint.json").write_text("{}")
        elif mutation == "manifest": value["manifest_sha256"] = "0" * 64
        elif mutation == "timing": value["benchmark"]["projected_collection_seconds_with_margin"] = float("nan")
        elif mutation == "input": value["input_hashes"] = {}
        path.write_text(json.dumps(value))
    with pytest.raises((cloud.DeploymentError, FileNotFoundError)):
        cloud.validate_retrieved_collection(directory, inventory(), prepared)


def test_stage_order_and_runtime_pins_and_no_remote_fitting():
    prepared = {"source_commit": COMMIT, "assets": {"source-inventory.json": {"sha256": "b" * 64}},
                "cpu_control_sha256": "c" * 64}
    stages = cloud.stages("/workspace/owned", prepared)
    assert [stage["name"] for stage in stages] == ["setup", "qualification", "collection"]
    commands = [step["argv"] for step in stages[0]["steps"]]
    assert ["uv", "sync", "--locked", "--no-dev", "--python", "3.13"] in commands
    assert any("torch==2.8.0" in command and "https://download.pytorch.org/whl/cu128" in command for command in commands)
    assert "gpu" in stages[1]["steps"][0]["argv"]
    assert "collect" in stages[2]["steps"][0]["argv"]
    assert all("analyze" not in step["argv"] for stage in stages for step in stage["steps"])


@pytest.mark.parametrize("flags", [[], ["--prepare-only"]])
def test_prepare_only_and_default_cannot_invoke_provider(tmp_path, monkeypatch, flags):
    monkeypatch.setattr(cloud, "prepare_inputs", lambda *args, **kwargs: {"prepared": True})
    monkeypatch.setattr(cloud.worker, "run_owned_worker", lambda *args, **kwargs: pytest.fail("provider called"))
    assert cloud.main(["--source-commit", COMMIT, "--cpu-control", str(tmp_path / "cpu.json"),
                       "--cpu-control-sha256", "b" * 64, "--state-dir", str(tmp_path / "private"),
                       "--output-dir", str(tmp_path / "output"), *flags]) == 0


def test_explicit_execute_is_the_only_dispatch_path(tmp_path, monkeypatch):
    calls = []
    output = tmp_path / "output"
    output.mkdir()
    prepared = {"plan": {"storage_transfer_reserve_usd": 1.5, "maximum_spend_usd": 3.0},
                "runtime": {"retrieval": LIMITS}}
    monkeypatch.setattr(cloud, "prepare_inputs", lambda *args, **kwargs: prepared)
    monkeypatch.setattr(cloud, "require_free_space", lambda *args: calls.append("storage-check"))
    monkeypatch.setattr(cloud, "workload", lambda *args, **kwargs: "synthetic-callback")
    def dispatch(plan, directory, callback):
        assert callback == "synthetic-callback" and plan == prepared["plan"]
        calls.append("dispatch")
        return {"passed": True, "retrieval_verified": True}
    monkeypatch.setattr(cloud.worker, "run_owned_worker", dispatch)
    monkeypatch.setattr(cloud.worker, "Store", lambda _: SimpleNamespace(read=lambda: {"termination_verified": True}))
    assert cloud.main(["--source-commit", COMMIT, "--cpu-control", str(tmp_path / "cpu.json"),
                       "--cpu-control-sha256", "b" * 64, "--state-dir", str(tmp_path / "private"),
                       "--output-dir", str(output), "--execute"]) == 0
    assert calls == ["storage-check", "dispatch"]


def test_execute_and_prepare_only_are_mutually_exclusive(tmp_path, monkeypatch):
    monkeypatch.setattr(cloud, "prepare_inputs", lambda *args, **kwargs: pytest.fail("conflicting flags reached preparation"))
    with pytest.raises(SystemExit) as error:
        cloud.main(["--source-commit", COMMIT, "--cpu-control", str(tmp_path / "cpu.json"),
                    "--cpu-control-sha256", "b" * 64, "--state-dir", str(tmp_path / "private"),
                    "--output-dir", str(tmp_path / "output"), "--execute", "--prepare-only"])
    assert error.value.code == 2


def test_failed_setup_still_retrieves_partial_evidence_but_never_starts_target(tmp_path, monkeypatch):
    events = []
    class FakeSSH:
        strict = True
        def call(self, command, **kwargs):
            events.append(shlex.split(command)[3])
            return SimpleNamespace(stdout=b'{"quiescent":true}')
        def monitored(self, command, **kwargs):
            mode = shlex.split(command)[3]; events.append(mode)
            if mode == "stage": raise cloud.DeploymentError("synthetic setup failure")
            retrieval_tar(kwargs["binary_output"], {"logs/setup.log": b"synthetic failure"})
    monkeypatch.setattr(cloud, "connect_owned", lambda *args, **kwargs: FakeSSH())
    monkeypatch.setattr(cloud.worker, "owned_record", lambda _: {"nonce": "a" * 32})
    monkeypatch.setattr(cloud, "stages", lambda *args: [{"name": "setup", "seconds": 1, "steps": []}])
    prepared = {"source_commit": COMMIT, "assets": {}, "runtime": {"retrieval": LIMITS}}
    result = cloud.workload(prepared, tmp_path)({}, SimpleNamespace(directory=tmp_path), lambda _: None)
    assert events == ["init", "extract", "stage", "quiesce", "pack"]
    assert result["retrieval_verified"] and not result["complete_raw_closure_verified"]
    assert not result["passed"] and not result["target_collection_started"]
    assert (tmp_path / "retrieved/logs/setup.log").read_bytes() == b"synthetic failure"
    assert (tmp_path / "workload.json").exists()


@pytest.mark.parametrize("missing", [False, True])
def test_stdlib_remote_closure_matches_complete_and_missing_raw_gates(closure, missing):
    directory, prepared, inventory = closure
    expected = {"prepared": prepared, "cpu_control": json.loads((directory.parent / "prepared-inputs/cpu-control.json").read_bytes())}
    if missing:
        (directory / "collection/batch-0000-profile-0.npz").unlink()
        with pytest.raises(cloud.ssh_storage.StorageError, match="required evidence missing"):
            cloud.ssh_storage.validate_complete(directory, inventory(), expected)
    else:
        assert cloud.ssh_storage.validate_complete(directory, inventory(), expected)["candidate_count"] == 3


def test_dead_leader_with_live_grandchild_never_qualifies_quiescence(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["helper", "unused", "/workspace/synthetic"])
    namespace = {}
    exec(cloud.REMOTE_PROGRAM.split("if mode=='init':")[0], namespace)
    record = {"pid": 12345, "pgid": 12345, "session": 12345, "start_ticks": "100", "boot_id": "synthetic", "state": "S"}
    namespace["same_process"] = lambda _: False
    namespace["identity"] = lambda _: None
    namespace["process_group_members"] = lambda _: [{"pid": 12346}]
    with pytest.raises(RuntimeError, match="outlived identifiable leader"):
        namespace["stop_owned"](record, True)
    namespace["process_group_members"] = lambda _: []
    namespace["stop_owned"](record, True)


def test_reused_process_identity_is_never_signaled(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["helper", "unused", "/workspace/synthetic"])
    namespace = {}
    exec(cloud.REMOTE_PROGRAM.split("if mode=='init':")[0], namespace)
    namespace["same_process"] = lambda _: False
    namespace["identity"] = lambda _: {"state": "S", "start_ticks": "changed"}
    with pytest.raises(RuntimeError, match="identity changed"):
        namespace["stop_owned"]({"pid": 12345}, True)


def test_remote_storage_wrapper_retains_failure_without_local_bulk_archive(tmp_path, monkeypatch):
    events = []
    class FakeSSH:
        strict = True
        def call(self, command, **kwargs):
            events.append(shlex.split(command)[3]); return SimpleNamespace(stdout=b'{"quiescent":true}')
        def argv(self, command): return ["synthetic-source", command]
    class FakeStore:
        binding = {}
        def receive(self, argv, **kwargs):
            events.append("receive"); raise TimeoutError("synthetic interruption")
        def finalize(self, **kwargs):
            events.append("finalize"); return {"retrieval_verified": True, "complete_raw_closure_verified": False}
        def retain_compact_receipts(self, **kwargs):
            events.append("compact"); return {"assets": []}
    monkeypatch.setattr(cloud, "connect_owned", lambda *args, **kwargs: FakeSSH())
    monkeypatch.setattr(cloud.worker, "owned_record", lambda _: {"nonce": "a" * 32, "pod_id": "owned-id", "name": "owned-name"})
    monkeypatch.setattr(cloud, "stages", lambda *args: [])
    prepared = {"source_commit": COMMIT, "assets": {}, "runtime": {"retrieval": LIMITS}}
    storage = FakeStore()
    result = cloud.workload(prepared, tmp_path, evidence_store=storage)({}, SimpleNamespace(directory=tmp_path), lambda _: None)
    assert events == ["init", "extract", "quiesce", "receive", "finalize", "compact"]
    assert result["retrieval_verified"] and not result["passed"] and "transfer_failure" in result
    assert storage.binding["task_worker_id"] == "owned-id" and storage.binding["source_commit"] == COMMIT
    assert not (tmp_path / "retrieved.tar").exists()


def test_no_pack_when_owned_writers_are_not_quiescent(tmp_path, monkeypatch):
    class FakeSSH:
        strict = True
        def call(self, command, **kwargs):
            if shlex.split(command)[3] == "quiesce": raise cloud.DeploymentError("owned writer remains")
            return SimpleNamespace(stdout=b"{}")
        def monitored(self, *args, **kwargs): pytest.fail("mutable raw evidence was packed")
    monkeypatch.setattr(cloud, "connect_owned", lambda *args, **kwargs: FakeSSH())
    monkeypatch.setattr(cloud.worker, "owned_record", lambda _: {"nonce": "a" * 32})
    monkeypatch.setattr(cloud, "stages", lambda *args: [])
    result = cloud.workload({"source_commit": COMMIT, "assets": {}}, tmp_path)({}, object(), lambda _: None)
    assert not result["retrieval_verified"] and not result["passed"]


@pytest.mark.skipif(sys.platform != "linux", reason="production process identity/group check uses Linux /proc")
def test_actual_linux_owned_parent_grandchild_quiescence_smoke(tmp_path, monkeypatch):
    monkeypatch.setattr(cloud.ssh_storage, "BASE_DIRECTORY", str(tmp_path))
    task = tmp_path / "task"
    task.mkdir()
    result = cloud.ssh_storage.quiescence_smoke(task / "quiescence", cloud.REMOTE_PROGRAM)
    assert result["passed"]
    assert result["cases"][0]["case"] == "interrupted"
    assert result["cases"][1]["orphan_snapshot_refused"]

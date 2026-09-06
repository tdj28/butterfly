"""CPU-specific archive controls; no SSH or provider calls in these tests."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import archive_exp479_cpu as archive


def bundle(tmp_path):
    source = tmp_path / "data.json"
    source.write_text('{"synthetic":true}\n')
    output = tmp_path / "bundle"
    output.mkdir()
    prepared = archive.pack([("collection/data.json", source)], output)
    archive.pilot.write_new_json(output / "preparation.json", prepared)
    return output, prepared


def test_pack_roundtrip_and_tamper_rejected(tmp_path):
    output, prepared = bundle(tmp_path)
    manifest = json.loads((output / "manifest.json").read_bytes())
    archive.verify_tar(output / "evidence.tar", manifest)
    assert prepared["asset_count"] == 1
    assert (output / "evidence.tar").stat().st_mode & 0o777 == 0o600
    manifest["assets"][0]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="manifest mismatch"):
        archive.verify_tar(output / "evidence.tar", manifest)


@pytest.mark.parametrize("name", ["../escape", "/absolute", "a/../b", "manifest.json"])
def test_pack_rejects_unsafe_or_reserved_names(tmp_path, name):
    source = tmp_path / "data"
    source.write_text("data")
    with pytest.raises(ValueError):
        archive.pack([(name, source)], tmp_path)


def test_pack_rejects_duplicate_names_and_symlinks(tmp_path):
    source = tmp_path / "data"
    source.write_text("data")
    with pytest.raises(ValueError):
        archive.pack([("data", source), ("data", source)], tmp_path)
    link = tmp_path / "link"
    link.symlink_to(source)
    with pytest.raises((ValueError, archive.storage.StorageError)):
        archive.pack([("data", link)], tmp_path)


@pytest.mark.parametrize("fail_transfer", [False, True])
def test_upload_is_exact_bounded_and_preserves_failures(tmp_path, monkeypatch, fail_transfer):
    output, prepared = bundle(tmp_path)
    calls = []
    def run(command, **kwargs):
        calls.append((command, kwargs))
        if fail_transfer and command[0] == "scp":
            raise TimeoutError("synthetic interruption")
        return SimpleNamespace(stdout=json.dumps({k: prepared["archive"][k] for k in ("bytes", "sha256")}))
    monkeypatch.setattr(archive.subprocess, "run", run)
    sha = archive.pilot.sha256_file(output / "preparation.json")
    result = archive.upload(output, sha, archive.BASE + "/exp479-synthetic")
    assert result["passed"] is (not fail_transfer)
    assert (output / "evidence.tar").exists() and (output / "upload.json").exists()
    assert calls[1][0][0] == "scp" and calls[1][1]["timeout"] == 7200
    assert "ForwardAgent=no" in calls[1][0] and "StrictHostKeyChecking=yes" in calls[1][0]
    with pytest.raises(FileExistsError):
        archive.upload(output, sha, archive.BASE + "/exp479-synthetic")


def test_upload_rejects_wrong_hash_and_remote_before_ssh(tmp_path, monkeypatch):
    output, _ = bundle(tmp_path)
    monkeypatch.setattr(archive.subprocess, "run", lambda *a, **kw: pytest.fail("no SSH allowed"))
    with pytest.raises(ValueError, match="receipt hash"):
        archive.upload(output, "0" * 64, archive.BASE + "/exp479-synthetic")
    with pytest.raises(ValueError, match="task-owned"):
        archive.upload(output, "0" * 64, archive.BASE)


def test_remote_python_helpers_execute_against_local_fixture(tmp_path, monkeypatch):
    import shlex
    import shutil
    import sys
    output, _ = bundle(tmp_path)
    remote = archive.BASE + "/exp479-synthetic"
    destination = tmp_path / "remote"
    real_run = archive.subprocess.run
    def run(command, **kwargs):
        if command[0] == "scp":
            shutil.copy2(output / "evidence.tar", destination / "evidence.tar")
            return SimpleNamespace(stdout="")
        args = shlex.split(command[-1])
        args[0] = sys.executable
        args = [arg.replace(remote, str(destination)) for arg in args]
        return real_run(args, **kwargs)
    monkeypatch.setattr(archive.subprocess, "run", run)
    result = archive.upload(output, archive.pilot.sha256_file(output / "preparation.json"), remote)
    assert result["passed"] and result["remote_archive_verified"]


def test_service_environment_only_passes_local_agent_not_credentials(monkeypatch):
    monkeypatch.setenv("SSH_AUTH_SOCK", "/tmp/synthetic-local-agent")
    monkeypatch.setenv("RUNPOD_API_KEY", "synthetic-not-a-real-key")
    environment = archive.service_environment()
    assert set(environment) == {"PATH", "PYTHONPATH", "SSH_AUTH_SOCK"}
    assert environment["SSH_AUTH_SOCK"] == "/tmp/synthetic-local-agent"
    assert "ForwardAgent=no" in archive.storage.ssh_options()

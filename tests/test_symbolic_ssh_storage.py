"""Local synthetic controls only: no SSH, cloud, source controls, or trajectories."""

import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile

import pytest

from scripts import symbolic_ssh_storage as storage


def make_archive(path, files, *, bad_hash=False, link=False):
    rows = [{"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            for name, data in files.items()]
    if bad_hash:
        rows[0]["sha256"] = "0" * 64
    inventory = {"schema": "butterfly.symbolic-remote-assets.v1", "assets": rows}
    with tarfile.open(path, "w:") as archive:
        for name, data in [("retrieval-manifest.json", storage.encoded(inventory)), *files.items()]:
            item = tarfile.TarInfo(name); item.size = len(data)
            archive.addfile(item, io.BytesIO(data))
        if link:
            item = tarfile.TarInfo("collection/link"); item.type = tarfile.SYMTYPE; item.linkname = "/etc/passwd"
            archive.addfile(item)
    return inventory


@pytest.mark.parametrize("path", ["/home/ubuntu/butterfly-research", "/home/ubuntu/other/run", "relative/run",
                                  "/home/ubuntu/butterfly-research/a/b", "/home/ubuntu/butterfly-research/../bad",
                                  "/home/ubuntu/butterfly-research/run;echo-bad"])
def test_remote_destination_is_one_exact_authorized_child(path):
    with pytest.raises(storage.StorageError):
        storage.validate_directory(path)


def test_remote_space_gate_is_unchanged_and_ssh_never_uses_tofu():
    assert storage.MINIMUM_REMOTE_FREE_BYTES == 17722933248
    assert storage.MINIMUM_LOCAL_FREE_BYTES == 2147483648
    assert storage.ssh_options()[:2] == ["-F", "/dev/null"]
    assert "StrictHostKeyChecking=yes" in storage.ssh_options()
    assert "ForwardAgent=no" in storage.ssh_options()
    assert "ClearAllForwardings=yes" in storage.ssh_options()
    assert "accept-new" not in " ".join(storage.ssh_options())


@pytest.mark.parametrize("kind", ["valid", "hash", "traversal", "unlisted", "link"])
def test_remote_safe_extraction_rejects_unsafe_or_changed_evidence(tmp_path, kind):
    name = {"traversal": "../outside", "unlisted": "private.key"}.get(kind, "gpu-control.json")
    archive = tmp_path / "received.tar"
    expected = make_archive(archive, {name: b"{}"}, bad_hash=kind == "hash", link=kind == "link")
    if kind == "valid":
        assert storage.safe_extract(archive, tmp_path / "retrieved") == expected
        with pytest.raises(FileExistsError):
            storage.safe_extract(archive, tmp_path / "retrieved")
    else:
        with pytest.raises(storage.StorageError):
            storage.safe_extract(archive, tmp_path / "retrieved")
    assert not (tmp_path / "outside").exists()


def test_receiver_preserves_partial_bytes_and_never_overwrites(tmp_path):
    with pytest.raises(storage.StorageError, match="byte bound"):
        storage.receive_stream(tmp_path, io.BytesIO(b"x" * 1100000), maximum_bytes=1048576)
    assert (tmp_path / "received.tar").stat().st_size == 1048576
    assert not (tmp_path / "transfer.json").exists()
    with pytest.raises(FileExistsError):
        storage.receive_stream(tmp_path, io.BytesIO(b"retry"))


@pytest.mark.parametrize("mutation", ["raw", "missing", "extra", "nested_inventory", "manifest", "symlink"])
def test_remote_full_audit_detects_changed_or_missing_data(tmp_path, mutation):
    archive = tmp_path / "received.tar"
    make_archive(archive, {"collection/batch-0000-profile-0.npz": b"synthetic bytes"})
    storage.safe_extract(archive, tmp_path / "retrieved")
    manifest = storage.descriptor(tmp_path / "retrieved/retrieval-manifest.json")
    assert len(storage.audit_remote(tmp_path, manifest["sha256"], manifest["bytes"])["assets"]) == 1
    raw = tmp_path / "retrieved/collection/batch-0000-profile-0.npz"
    if mutation == "raw": raw.write_bytes(b"changed")
    elif mutation == "missing": raw.unlink()
    elif mutation == "extra": (raw.parent / "extra.json").write_text("{}")
    elif mutation == "nested_inventory": (raw.parent / "retrieval-manifest.json").write_text("{}")
    elif mutation == "manifest": (tmp_path / "retrieved/retrieval-manifest.json").write_text("{}")
    elif mutation == "symlink": raw.unlink(); raw.symlink_to(archive)
    with pytest.raises(storage.StorageError):
        storage.audit_remote(tmp_path, manifest["sha256"], manifest["bytes"])


def test_partial_finalization_retains_inventory_without_promoting_collection(tmp_path):
    archive = tmp_path / "received.tar"
    make_archive(archive, {"logs/setup.log": b"synthetic failed setup"})
    result = storage.finalize_remote(tmp_path, {"prepared": {}, "cpu_control": {}})
    assert result["retrieval_verified"] and not result["complete_raw_closure_verified"]
    assert "required evidence missing" in result["failure"]["message"]
    assert (tmp_path / "finalization.json").exists()
    assert (tmp_path / "retrieved/logs/setup.log").exists()


def test_finalization_rejects_archive_changed_after_transfer_receipt(tmp_path):
    source = tmp_path / "source.tar"
    make_archive(source, {"logs/setup.log": b"synthetic failure"})
    storage.receive_stream(tmp_path, io.BytesIO(source.read_bytes()))
    with (tmp_path / "received.tar").open("ab") as stream:
        stream.write(b"changed")
    result = storage.finalize_remote(tmp_path, {"prepared": {}, "cpu_control": {}})
    assert not result["retrieval_verified"]
    assert "changed after transfer" in result["failure"]["message"]


def source_argv(data_size, pause=0):
    return [sys.executable, "-c", f"import sys,time; sys.stdout.buffer.write(b'x'*{data_size}); sys.stdout.flush(); time.sleep({pause})"]


def sink_argv(path, *, bad_hash=False, pause=0):
    script = ("import hashlib,json,pathlib,sys,time; "
              f"time.sleep({pause}); data=sys.stdin.buffer.read(); pathlib.Path(sys.argv[1]).write_bytes(data); "
              "print(json.dumps({'bytes':len(data),'sha256':" + ("'0'*64" if bad_hash else "hashlib.sha256(data).hexdigest()") + "}))")
    return [sys.executable, "-c", script, str(path)]


def test_real_local_pipe_relay_is_bounded_and_hash_checked(tmp_path):
    with (tmp_path / "log").open("xb") as log:
        result = storage.relay_stream(source_argv(200000), sink_argv(tmp_path / "received"),
                                      maximum_bytes=300000, seconds=5, progress=lambda _: None, log=log)
    assert result["bytes"] == 200000
    assert result["sha256"] == hashlib.sha256((tmp_path / "received").read_bytes()).hexdigest()


@pytest.mark.parametrize("kind", ["cap", "timeout", "backpressure", "hash"])
def test_relay_stops_overflow_stall_and_false_acknowledgement(tmp_path, kind):
    with (tmp_path / "log").open("xb") as log:
        with pytest.raises((storage.StorageError, TimeoutError)):
            storage.relay_stream(source_argv(2000000 if kind in {"cap", "backpressure"} else 1024,
                                            pause=5 if kind == "timeout" else 0),
                                 sink_argv(tmp_path / "received", bad_hash=kind == "hash", pause=5 if kind == "backpressure" else 0),
                                 maximum_bytes=1024 if kind == "cap" else 3000000,
                                 seconds=0.3 if kind in {"timeout", "backpressure"} else 5,
                                 progress=lambda _: None, log=log)


def binding():
    return {"schema": storage.SCHEMA, "host": storage.HOST, "remote_directory": storage.BASE_DIRECTORY + "/synthetic",
            "helper_sha256": "a" * 64, "expected_binding_sha256": "b" * 64,
            "retrieval_manifest_sha256": "c" * 64, "retrieval_manifest_bytes": 100}


def test_read_only_api_fetches_only_bound_single_asset_and_keeps_partial_on_error(tmp_path, monkeypatch):
    store = storage.SshEvidenceStore.open_existing(binding(), local_control_directory=tmp_path)
    payload = b"synthetic data"
    row = {"path": "collection/batch-0000-profile-0.npz", "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
    monkeypatch.setattr(store, "_argv", lambda *args: source_argv(len(payload)))
    with pytest.raises(storage.StorageError, match="hash mismatch"):
        store.fetch_asset(row, tmp_path / "cache.npz")
    assert (tmp_path / "cache.npz").exists()
    with pytest.raises(FileExistsError):
        store.fetch_asset(row, tmp_path / "cache.npz")
    with pytest.raises(storage.StorageError, match="cache bound"):
        store.fetch_asset({**row, "bytes": storage.MAXIMUM_CACHED_ASSET_BYTES + 1}, tmp_path / "not-created")
    assert not (tmp_path / "not-created").exists()


def test_staging_checks_frozen_helper_and_cpu_hash_before_ssh(tmp_path, monkeypatch):
    store = storage.SshEvidenceStore(storage.BASE_DIRECTORY + "/synthetic", local_control_directory=tmp_path)
    monkeypatch.setattr(storage.subprocess, "Popen", lambda *args, **kwargs: pytest.fail("network invocation"))
    with pytest.raises(storage.StorageError, match="helper differs"):
        store.prepare({"cpu_control_sha256": "b" * 64}, b"{}", helper_sha256="a" * 64)
    with pytest.raises(storage.StorageError, match="CPU control differs"):
        store.prepare({"cpu_control_sha256": "b" * 64}, b"{}", helper_sha256=storage.sha256_file(Path(storage.__file__)))


def test_smoke_source_is_deterministic_high_entropy_16mib_without_numerical_jobs(tmp_path):
    result = subprocess.run([sys.executable, "-c", storage.SMOKE_PROGRAM], capture_output=True, timeout=5, check=True)
    with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as archive:
        raw = archive.extractfile("collection/batch-0000-profile-0.npz").read()
    assert raw == hashlib.shake_256(b"butterfly-exp477-ssh-storage-smoke-v1").digest(16 * 1048576)

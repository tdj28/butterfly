"""Synthetic I/O/security controls: no SSH, GPU, target fits, or credentials."""

from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import zipfile

import numpy as np
from numpy.lib import format as numpy_format
import pytest

from scripts import analyze_symbolic_remote_collection as remote
from scripts import symbolic_ssh_storage as storage


COMMIT = "a" * 40


def describe(name, data):
    return {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


class MemoryStore:
    def __init__(self, files):
        self.files = files.copy()
        self.rows = [describe(name, data) for name, data in sorted(files.items())]
        self.audits = 0
        self.fetch_hook = None

    def audit(self):
        if self.rows != [describe(name, data) for name, data in sorted(self.files.items())]:
            raise ValueError("immutable remote asset hash mismatch")
        self.audits += 1
        return {"assets": deepcopy(self.rows)}

    def fetch_asset(self, descriptor, destination, *, maximum_bytes):
        assert descriptor in self.rows and descriptor["bytes"] <= maximum_bytes
        if self.fetch_hook is None:
            with destination.open("xb") as stream:
                stream.write(self.files[descriptor["path"]])
        else:
            self.fetch_hook(destination)
        return destination


def small_provider(store, tmp_path, **kwargs):
    return remote.RemoteCollectionAssets(store, cache_parent=tmp_path,
                                         maximum_asset_bytes=1024, maximum_cache_bytes=2048,
                                         local_reserve_bytes=32, **kwargs)


def npz_bytes():
    output = io.BytesIO()
    arrays = {name: np.arange(2, dtype=np.float64) for name in remote.RAW_ARRAY_NAMES}
    arrays["candidate_ids"] = np.asarray(["synthetic-a", "synthetic-b"])
    np.savez_compressed(output, **arrays)
    return output.getvalue()


def rewrite_npz(data, *, replace=None, extra=None):
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as source, zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as target:
        for item in source.infolist():
            target.writestr(item.filename, (replace or {}).get(item.filename, source.read(item.filename)))
        for name, content in (extra or {}).items():
            target.writestr(name, content)
    return output.getvalue()


@pytest.mark.parametrize("descriptor", [
    {"path": "../raw.npz", "bytes": 1, "sha256": "a" * 64},
    {"path": "/raw.npz", "bytes": 1, "sha256": "a" * 64},
    {"path": "x\\raw.npz", "bytes": 1, "sha256": "a" * 64},
    {"path": "raw.npz", "bytes": True, "sha256": "a" * 64},
    {"path": "raw.npz", "bytes": -1, "sha256": "a" * 64},
    {"path": "raw.npz", "bytes": remote.MAXIMUM_ASSET_BYTES + 1, "sha256": "a" * 64},
    {"path": "raw.npz", "bytes": 1, "sha256": "A" * 64},
    {"path": "raw.npz", "bytes": 1, "sha256": "a" * 64, "unbound": True},
])
def test_collection_descriptor_fail_closed(descriptor):
    with pytest.raises(ValueError):
        remote.checked_descriptor(descriptor)


def test_npz_guard_accepts_frozen_numeric_array_schema(tmp_path):
    path = tmp_path / "raw.npz"
    path.write_bytes(npz_bytes())
    result = remote.validate_npz_budget(path)
    assert result["member_count"] == 9 and result["uncompressed_bytes"] < 10000


def test_npz_guard_bounds_uncompressed_bytes_not_just_compressed_size(tmp_path):
    path = tmp_path / "raw.npz"
    path.write_bytes(npz_bytes())
    with pytest.raises(ValueError, match="uncompressed byte total"):
        remote.validate_npz_budget(path, maximum_uncompressed_bytes=100)
    with pytest.raises(ValueError, match="member count"):
        remote.validate_npz_budget(path, maximum_members=8)


@pytest.mark.parametrize("bad_shape", [(2**40,), (1, 1, 1, 1)])
def test_npz_guard_rejects_npy_header_allocations_before_numpy_load(tmp_path, bad_shape):
    header = io.BytesIO()
    numpy_format.write_array_header_1_0(header, {"descr": "<f8", "fortran_order": False, "shape": bad_shape})
    path = tmp_path / "raw.npz"
    path.write_bytes(rewrite_npz(npz_bytes(), replace={"states.npy": header.getvalue()}))
    with pytest.raises(ValueError, match="rank|shape/payload"):
        remote.validate_npz_budget(path)


def test_npz_guard_rejects_objects_and_unrecognized_members(tmp_path):
    output = io.BytesIO()
    np.save(output, np.asarray([{}], dtype=object), allow_pickle=True)
    path = tmp_path / "objects.npz"
    path.write_bytes(rewrite_npz(npz_bytes(), replace={"states.npy": output.getvalue()}))
    with pytest.raises(ValueError, match="object"):
        remote.validate_npz_budget(path)
    extra = tmp_path / "extra.npz"
    extra.write_bytes(rewrite_npz(npz_bytes(), extra={"unexpected.npy": b""}))
    with pytest.raises(ValueError, match="array set"):
        remote.validate_npz_budget(extra)


def test_cache_one_asset_only_then_removes_only_its_temporary_copies(tmp_path):
    original = tmp_path / "user-file"
    original.write_bytes(b"preserve")
    store = MemoryStore({"collection/receipt.json": b"{}"})
    descriptor = describe("receipt.json", b"{}")
    with small_provider(store, tmp_path) as assets:
        with assets._materialize(descriptor, maximum_bytes=1024) as path:
            assert path.read_bytes() == b"{}"
            with pytest.raises(ValueError, match="only one"):
                assets.metadata_bytes(descriptor)
        assert not path.exists()
        assert assets.peak_cache_bytes == 2
        assets.verify_assets([descriptor])
        assets.verify_assets([descriptor])
        assert assets.full_audits_completed == 2
    assert list(tmp_path.iterdir()) == [original]
    assert original.read_bytes() == b"preserve"
    assert store.files == {"collection/receipt.json": b"{}"}


@pytest.mark.parametrize("kind", ["wrong_bytes", "missing", "symlink", "over_combined_limit"])
def test_cache_independently_checks_fetched_file_and_always_cleans_it(tmp_path, kind):
    store = MemoryStore({"collection/receipt.json": b"{}"})
    marker = tmp_path / "marker"
    marker.write_bytes(b"preserve")
    def bad_fetch(destination):
        if kind == "wrong_bytes":
            destination.write_bytes(b"[]")
        elif kind == "symlink":
            destination.symlink_to(marker)
        elif kind == "over_combined_limit":
            destination.write_bytes(b"{}")
            (destination.parent / "extraneous.bin").write_bytes(b"x" * 2048)
    store.fetch_hook = bad_fetch
    with small_provider(store, tmp_path) as assets:
        with pytest.raises(ValueError, match="hash/size|regular|combined byte"):
            assets.metadata_bytes(describe("receipt.json", b"{}"))
    assert list(tmp_path.iterdir()) == [marker]
    assert marker.read_bytes() == b"preserve"


def test_cache_refuses_declared_oversize_before_fetch(tmp_path):
    data = b"x" * 1025
    store = MemoryStore({"collection/receipt.json": data})
    store.fetch_hook = lambda destination: pytest.fail("must not fetch oversized file")
    with small_provider(store, tmp_path) as assets, pytest.raises(ValueError, match="byte limit"):
        assets.metadata_bytes(describe("receipt.json", data))


def test_cache_preflight_reserves_disk_space_without_opening_store(tmp_path, monkeypatch):
    store = MemoryStore({})
    monkeypatch.setattr(remote.shutil, "disk_usage", lambda path: SimpleNamespace(free=2079))
    with pytest.raises(ValueError, match="insufficient local"):
        with small_provider(store, tmp_path):
            pytest.fail("must not enter cache")
    assert store.audits == 0 and not list(tmp_path.iterdir())


def test_remote_inventory_changes_between_audits_are_rejected(tmp_path):
    store = MemoryStore({"collection/receipt.json": b"{}"})
    with small_provider(store, tmp_path) as assets:
        descriptor = describe("receipt.json", b"{}")
        assets.receipt_bytes(descriptor["sha256"])
        assets.verify_assets([descriptor])
        # Even a self-consistently rewritten remote manifest may not replace the original.
        store.files["collection/receipt.json"] = b"[]"
        store.rows = [describe(name, data) for name, data in sorted(store.files.items())]
        with pytest.raises(ValueError, match="inventory changed"):
            assets.verify_assets([descriptor])


@pytest.fixture
def control_receipts():
    ownership = {"schema": "butterfly.runpod-ownership.v1", "pod_id": "test-worker",
                 "nonce": "b" * 32, "name": "butterfly-exp477-" + "b" * 32,
                 "preexisting_ids": ["unrelated-one", "unrelated-two"]}
    lifecycle = {**ownership, "schema": "butterfly.runpod-symbolic-worker.v1",
                 "termination_verified": True, "contract_qualified": True,
                 "post_delete_direct_lookup": "HTTP 404",
                 "post_delete_inventory_ids": ["unrelated-one", "unrelated-two"],
                 "persistent_volume_requested": False, "unrelated_resources_mutated": False,
                 "plan": {"experiment_id": "EXP-477", "source_commit": COMMIT}}
    binding = {"schema": "butterfly.symbolic-ssh-storage.v1", "complete_raw_closure_verified": True,
               "source_commit": COMMIT, "task_worker_id": ownership["pod_id"],
               "task_worker_name": ownership["name"], "task_worker_nonce": ownership["nonce"]}
    return lifecycle, ownership, binding


def test_verified_termination_allows_unrelated_existing_pods(control_receipts):
    lifecycle, ownership, binding = control_receipts
    remote.validate_termination(lifecycle, ownership, COMMIT)
    remote.validate_storage_worker_binding(binding, ownership, COMMIT)


@pytest.mark.parametrize("field,value", [
    ("termination_verified", False), ("contract_qualified", False),
    ("post_delete_direct_lookup", "HTTP 200"), ("post_delete_inventory_ids", ["test-worker"]),
    ("persistent_volume_requested", True), ("unrelated_resources_mutated", True),
    ("pod_id", "another-worker"), ("name", "another-name"),
    ("plan", {"experiment_id": "EXP-477", "source_commit": "c" * 40}), ("plan", None),
])
def test_termination_scope_and_source_fail_closed(control_receipts, field, value):
    lifecycle, ownership, _ = control_receipts
    lifecycle[field] = value
    with pytest.raises(ValueError):
        remote.validate_termination(lifecycle, ownership, COMMIT)


@pytest.mark.parametrize("preexisting", [["test-worker"], None, [1]])
def test_worker_cannot_be_preexisting_or_have_malformed_ownership(control_receipts, preexisting):
    lifecycle, ownership, _ = control_receipts
    lifecycle["preexisting_ids"] = ownership["preexisting_ids"] = preexisting
    with pytest.raises(ValueError, match="ownership"):
        remote.validate_termination(lifecycle, ownership, COMMIT)


@pytest.mark.parametrize("field,value", [
    ("source_commit", "c" * 40), ("task_worker_id", "another-worker"),
    ("task_worker_name", "another-name"), ("task_worker_nonce", "c" * 32),
    ("complete_raw_closure_verified", False),
])
def test_storage_must_bind_to_this_terminated_worker(control_receipts, field, value):
    _, ownership, binding = control_receipts
    binding[field] = value
    with pytest.raises(ValueError, match="terminated source worker"):
        remote.validate_storage_worker_binding(binding, ownership, COMMIT)


def driver_arguments(tmp_path, control_receipts):
    lifecycle, ownership, binding = control_receipts
    result = ["--manifest", "synthetic.json", "--source-commit", COMMIT,
              "--collection-receipt-sha256", "d" * 64,
              "--local-control-directory", str(tmp_path), "--cache-parent", str(tmp_path),
              "--source-inventory", "source-inventory.json", "--source-inventory-sha256", "e" * 64,
              "--output-dir", str(tmp_path / "analysis")]
    for option, document in (("storage-binding", binding), ("lifecycle-receipt", lifecycle), ("ownership-receipt", ownership)):
        path = tmp_path / (option + ".json")
        data = json.dumps(document, sort_keys=True).encode()
        path.write_bytes(data)
        result.extend(["--" + option, str(path), "--" + option + "-sha256", hashlib.sha256(data).hexdigest()])
    return result


def test_driver_forwards_inventory_and_rechecks_source_before_and_after_fitting(tmp_path, control_receipts, monkeypatch):
    calls = []
    def prepare(manifest, commit, **kwargs):
        assert commit == COMMIT and manifest == Path("synthetic.json")
        assert kwargs == {"inventory": Path("source-inventory.json"), "inventory_sha256": "e" * 64}
        calls.append("prepare")
        return {"source": {"commit": COMMIT}}
    monkeypatch.setattr(remote.pilot, "prepare", prepare)
    def open_existing(binding, **kwargs):
        assert calls == ["prepare"]
        calls.append("open-read-only-store")
        return MemoryStore({})
    monkeypatch.setattr(storage.SshEvidenceStore, "open_existing", open_existing)
    def analyze(prepared, local, digest, output, *, source_recheck, asset_provider):
        assert local is None and digest == "d" * 64
        assert calls == ["prepare", "open-read-only-store"]
        calls.append("synthetic-fit")
        source_recheck()
        output.mkdir()
        return {"status": "completed", "passed": True}
    monkeypatch.setattr(remote.pilot, "analyze", analyze)
    assert remote.main(driver_arguments(tmp_path, control_receipts)) == 0
    assert calls == ["prepare", "open-read-only-store", "synthetic-fit", "prepare"]
    audit = json.loads((tmp_path / "analysis/remote-io-audit.json").read_bytes())
    assert audit["worker_termination_verified_before_analysis"] and audit["gpu_calls_performed"] is False


@pytest.mark.parametrize("rejection", ["termination", "raw_closure", "storage_worker"])
def test_driver_rejects_unverified_collection_before_ssh_or_fit(tmp_path, control_receipts, monkeypatch, rejection):
    if rejection == "termination":
        control_receipts[0]["termination_verified"] = False
    elif rejection == "raw_closure":
        control_receipts[2]["complete_raw_closure_verified"] = False
    else:
        control_receipts[2]["task_worker_id"] = "another-worker"
    monkeypatch.setattr(remote.pilot, "prepare", lambda *args, **kwargs: {})
    monkeypatch.setattr(storage.SshEvidenceStore, "open_existing", lambda *args, **kwargs: pytest.fail("must not access SSH"))
    monkeypatch.setattr(remote.pilot, "analyze", lambda *args, **kwargs: pytest.fail("must not fit"))
    with pytest.raises(ValueError, match="termination|terminated source worker"):
        remote.main(driver_arguments(tmp_path, control_receipts))
    assert not (tmp_path / "analysis").exists()


def test_control_file_hash_and_symlink_are_rejected(tmp_path):
    path = tmp_path / "receipt.json"
    path.write_bytes(b"{}")
    with pytest.raises(ValueError, match="hash mismatch"):
        remote.hashed_json(path, "a" * 64)
    alias = tmp_path / "alias.json"
    alias.symlink_to(path)
    with pytest.raises(ValueError, match="regular"):
        remote.hashed_json(alias, hashlib.sha256(b"{}").hexdigest())

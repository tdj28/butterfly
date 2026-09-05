#!/usr/bin/env python3
"""Analyze immutable SSH-backed EXP-477 evidence locally, one raw profile at a time.

The remote store performs read-only hashing and file transfer. All fitting stays
in this local process; the original remote evidence is never removed or edited.
Only invocation-owned temporary cache copies are evicted. This is the same
analysis implementation/design as the default local-file path.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import signal
import tempfile
import zipfile

import numpy as np
from numpy.lib import format as numpy_format

from scripts import run_symbolic_center_pilot as pilot


MAXIMUM_ASSET_BYTES = 256 * 1024 * 1024
MAXIMUM_CACHE_BYTES = 512 * 1024 * 1024
LOCAL_RESERVE_BYTES = 256 * 1024 * 1024
MAXIMUM_METADATA_BYTES = 4 * 1024 * 1024
MAXIMUM_UNCOMPRESSED_BYTES = 256 * 1024 * 1024
MAXIMUM_NPZ_MEMBERS = 16
RAW_ARRAY_NAMES = {
    "candidate_ids", "candidate_record_offsets", "seed_ids", "trajectory_offsets",
    "states", "times", "normalized_section_transversality", "survivor_counts", "failed_counts",
}
HASH = re.compile(r"[0-9a-f]{64}\Z")


def checked_descriptor(value, *, maximum_bytes=MAXIMUM_ASSET_BYTES):
    if not isinstance(value, dict) or set(value) != {"path", "bytes", "sha256"}:
        raise ValueError("asset descriptor must contain exactly path, bytes, and sha256")
    name, size, digest = value["path"], value["bytes"], value["sha256"]
    if (not isinstance(name, str) or not name or Path(name).name != name
            or name in {".", ".."} or "\\" in name):
        raise ValueError("collection asset descriptor requires a plain basename")
    if type(size) is not int or not 0 <= size <= maximum_bytes:
        raise ValueError("collection asset exceeds its frozen byte limit")
    if not isinstance(digest, str) or not HASH.fullmatch(digest):
        raise ValueError("collection asset requires a lowercase SHA-256")
    return dict(value)


def validate_npz_budget(path, *, maximum_uncompressed_bytes=MAXIMUM_UNCOMPRESSED_BYTES,
                        maximum_members=MAXIMUM_NPZ_MEMBERS):
    """Bound decompressed arrays and declared NPY shapes before np.load allocates.

    A compressed-size check alone does not bound RAM. ZIP member sizes and NPY
    shape*dtype payload sizes must agree, with no object arrays or extra members.
    Only NPY header versions 1 and 2 emitted by the frozen numeric schema are
    accepted; this does not change a trajectory, fit, or acceptance threshold.
    """
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if len(members) > maximum_members or len({member.filename for member in members}) != len(members):
            raise ValueError("NPZ member count/uniqueness exceeds the frozen memory contract")
        expected = {name + ".npy" for name in RAW_ARRAY_NAMES}
        if {member.filename for member in members} != expected:
            raise ValueError("NPZ array set differs from the frozen raw schema")
        total = sum(member.file_size for member in members)
        if total > maximum_uncompressed_bytes:
            raise ValueError("NPZ uncompressed byte total exceeds the frozen memory limit")
        for member in members:
            if member.is_dir() or member.flag_bits & 1:
                raise ValueError("NPZ contains a directory or encrypted array")
            with archive.open(member) as stream:
                version = numpy_format.read_magic(stream)
                if version == (1, 0):
                    shape, _fortran, dtype = numpy_format.read_array_header_1_0(stream, max_header_size=10_000)
                elif version == (2, 0):
                    shape, _fortran, dtype = numpy_format.read_array_header_2_0(stream, max_header_size=10_000)
                else:
                    raise ValueError("NPZ contains an unsupported NPY header version")
                if dtype.hasobject or not 1 <= dtype.itemsize <= maximum_uncompressed_bytes:
                    raise ValueError("NPZ contains object data or an invalid dtype size")
                if len(shape) > 3 or any(type(length) is not int or length < 0 for length in shape):
                    raise ValueError("NPZ contains an invalid or excessive array rank")
                payload = math.prod(shape) * dtype.itemsize
                if payload > maximum_uncompressed_bytes or stream.tell() + payload != member.file_size:
                    raise ValueError("NPY shape/payload size is inconsistent or exceeds the memory limit")
    return {"member_count": len(members), "uncompressed_bytes": total}


class RemoteCollectionAssets:
    """Adapter for SshEvidenceStore, with one exclusive disposable cached asset."""

    def __init__(self, store, *, cache_parent=None, maximum_asset_bytes=MAXIMUM_ASSET_BYTES,
                 maximum_cache_bytes=MAXIMUM_CACHE_BYTES, local_reserve_bytes=LOCAL_RESERVE_BYTES):
        for name, value, upper in (("maximum_asset_bytes", maximum_asset_bytes, MAXIMUM_ASSET_BYTES),
                                   ("maximum_cache_bytes", maximum_cache_bytes, MAXIMUM_CACHE_BYTES),
                                   ("local_reserve_bytes", local_reserve_bytes, LOCAL_RESERVE_BYTES)):
            if type(value) is not int or not 0 < value <= upper:
                raise ValueError(f"{name} must be positive and no greater than the frozen bound")
        if maximum_asset_bytes > maximum_cache_bytes:
            raise ValueError("one asset cannot exceed the total cache limit")
        self.store = store
        self.maximum_asset_bytes = maximum_asset_bytes
        self.maximum_cache_bytes = maximum_cache_bytes
        self.local_reserve_bytes = local_reserve_bytes
        self.cache_parent = Path(tempfile.gettempdir()) if cache_parent is None else Path(cache_parent)
        if not self.cache_parent.is_dir():
            raise ValueError("cache parent must be an existing local directory")
        self._temporary = None
        self._inventory = None
        self._initial_audit_consumed = False
        self._active = False
        self.full_audits_completed = 0
        self.fetched_files = 0
        self.peak_cache_bytes = 0

    def __enter__(self):
        if self._temporary is not None:
            raise ValueError("remote provider cache context is already active")
        self._space_gate(self.maximum_cache_bytes)
        self._temporary = tempfile.TemporaryDirectory(prefix="butterfly-exp477-analysis-", dir=self.cache_parent)
        return self

    def __exit__(self, *_exception):
        if self._temporary is not None:
            self._temporary.cleanup()  # This invocation's temporary copies only.
            self._temporary = None

    def _space_gate(self, requested):
        if shutil.disk_usage(self.cache_parent).free < requested + self.local_reserve_bytes:
            raise ValueError("insufficient local free space for bounded cache plus reserve")

    def _audit(self):
        document = self.store.audit()
        rows = document["assets"]
        if not isinstance(rows, list) or len(rows) > 2000:
            raise ValueError("remote inventory has excessive or malformed asset count")
        indexed = {}
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("path"), str) or row["path"] in indexed:
                raise ValueError("remote inventory contains invalid or duplicate paths")
            # The storage layer validates its complete allowlist. This adapter
            # additionally validates every collection leaf it will materialize.
            indexed[row["path"]] = dict(row)
        if self._inventory is not None and indexed != self._inventory:
            raise ValueError("remote immutable asset inventory changed during analysis")
        self._inventory = indexed
        self.full_audits_completed += 1

    def _remote_descriptor(self, descriptor, *, maximum_bytes=None):
        cap = self.maximum_asset_bytes if maximum_bytes is None else maximum_bytes
        descriptor = checked_descriptor(descriptor, maximum_bytes=cap)
        if self._inventory is None:
            self._audit()
        remote = {**descriptor, "path": "collection/" + descriptor["path"]}
        if self._inventory.get(remote["path"]) != remote:
            raise ValueError("asset descriptor differs from immutable remote manifest")
        return remote

    def receipt_bytes(self, expected_sha256):
        if not isinstance(expected_sha256, str) or not HASH.fullmatch(expected_sha256):
            raise ValueError("collection receipt requires a lowercase SHA-256")
        if self._inventory is None:
            self._audit()
        row = self._inventory.get("collection/receipt.json")
        if row is None or row.get("sha256") != expected_sha256:
            raise ValueError("collection receipt hash mismatch")
        return self.metadata_bytes({**row, "path": "receipt.json"})

    def verify_assets(self, descriptors):
        # receipt_bytes performed the first complete audit before any fitting.
        # Reuse that audit once; the post-fit invocation rehashes the entire
        # original inventory, including assets this analysis did not download.
        if self._inventory is None or self._initial_audit_consumed:
            self._audit()
        self._initial_audit_consumed = True
        for descriptor in descriptors:
            self._remote_descriptor(descriptor)

    def metadata_bytes(self, descriptor):
        cap = min(MAXIMUM_METADATA_BYTES, self.maximum_asset_bytes)
        with self._materialize(descriptor, maximum_bytes=cap) as path:
            return path.read_bytes()

    @contextmanager
    def _materialize(self, descriptor, *, maximum_bytes):
        if self._temporary is None:
            raise ValueError("remote provider must run inside its invocation-owned cache context")
        if self._active:
            raise ValueError("only one remote evidence asset may occupy the cache at a time")
        remote = self._remote_descriptor(descriptor, maximum_bytes=maximum_bytes)
        self._space_gate(remote["bytes"])
        self._active = True
        try:
            with tempfile.TemporaryDirectory(prefix="asset-", dir=self._temporary.name) as directory:
                destination = Path(directory) / descriptor["path"]
                self.store.fetch_asset(remote, destination, maximum_bytes=maximum_bytes)
                if destination.is_symlink() or not destination.is_file():
                    raise ValueError("asset fetch did not produce a regular invocation-owned cache file")
                if destination.stat().st_size != descriptor["bytes"] or pilot.sha256_file(destination) != descriptor["sha256"]:
                    raise ValueError("fetched asset hash/size mismatch")
                actual = 0
                for path in Path(self._temporary.name).rglob("*"):
                    if path.is_symlink():
                        raise ValueError("cache contains an unexpected symlink")
                    if path.is_file():
                        actual += path.stat().st_size
                if actual > self.maximum_cache_bytes:
                    raise ValueError("local cache exceeds the combined byte limit")
                self.peak_cache_bytes = max(self.peak_cache_bytes, actual)
                self.fetched_files += 1
                yield destination
        finally:
            self._active = False

    @contextmanager
    def materialize(self, descriptor):
        with self._materialize(descriptor, maximum_bytes=self.maximum_asset_bytes) as path:
            if not descriptor["path"].endswith(".npz"):
                raise ValueError("raw materialization requires the frozen NPZ asset")
            validate_npz_budget(path)
            yield path

    def audit_receipt(self):
        return {"full_remote_audits_completed": self.full_audits_completed,
                "locally_fetched_files": self.fetched_files, "peak_cache_bytes": self.peak_cache_bytes,
                "maximum_asset_bytes": self.maximum_asset_bytes, "maximum_cache_bytes": self.maximum_cache_bytes,
                "local_reserve_bytes": self.local_reserve_bytes, "maximum_uncompressed_npz_bytes": MAXIMUM_UNCOMPRESSED_BYTES,
                "cache_policy": "one invocation-owned asset at a time; copies removed after use",
                "remote_operations": "read-only hashing and transfer; no fitting, installation, or GPU work"}


def hashed_json(path, expected_sha256, *, maximum_bytes=MAXIMUM_METADATA_BYTES):
    if not isinstance(expected_sha256, str) or not HASH.fullmatch(expected_sha256):
        raise ValueError("declared control receipt requires a lowercase SHA-256")
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > maximum_bytes:
        raise ValueError("control receipt is not a bounded regular local file")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("control receipt hash mismatch")
    return json.loads(raw)


def validate_termination(lifecycle, ownership, source_commit):
    if (not isinstance(lifecycle, dict) or not isinstance(ownership, dict)
            or lifecycle.get("schema") != "butterfly.runpod-symbolic-worker.v1"
            or ownership.get("schema") != "butterfly.runpod-ownership.v1"):
        raise ValueError("verified original worker lifecycle and ownership receipts are required")
    for name in ("nonce", "pod_id", "name", "preexisting_ids"):
        if lifecycle.get(name) != ownership.get(name):
            raise ValueError("termination and immutable ownership identities differ")
    identifier, nonce = ownership.get("pod_id"), ownership.get("nonce")
    preexisting = ownership.get("preexisting_ids")
    if (not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", identifier)
            or not isinstance(nonce, str) or not re.fullmatch(r"[0-9a-f]{32}", nonce)
            or ownership.get("name") != "butterfly-exp477-" + nonce
            or not isinstance(preexisting, list) or any(not isinstance(item, str) for item in preexisting)
            or identifier in preexisting):
        raise ValueError("worker ownership is not a new uniquely named task resource")
    if (lifecycle.get("termination_verified") is not True or lifecycle.get("contract_qualified") is not True
            or lifecycle.get("post_delete_direct_lookup") != "HTTP 404"
            or not isinstance(lifecycle.get("post_delete_inventory_ids"), list)
            or identifier in lifecycle["post_delete_inventory_ids"]
            or lifecycle.get("persistent_volume_requested") is not False
            or lifecycle.get("unrelated_resources_mutated") is not False
            or not isinstance(lifecycle.get("plan"), dict)
            or lifecycle.get("plan", {}).get("experiment_id") != "EXP-477"
            or lifecycle.get("plan", {}).get("source_commit") != source_commit):
        raise ValueError("worker termination, source binding, or resource-scope verification failed")


def validate_storage_worker_binding(binding, ownership, source_commit):
    if (not isinstance(binding, dict)
            or binding.get("schema") != "butterfly.symbolic-ssh-storage.v1"
            or binding.get("complete_raw_closure_verified") is not True
            or binding.get("source_commit") != source_commit
            or any(binding.get("task_worker_" + key) != ownership.get(key)
                   for key in ("name", "nonce"))
            or binding.get("task_worker_id") != ownership.get("pod_id")):
        raise ValueError("remote evidence is not bound to the verified terminated source worker")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-inventory", type=Path)
    parser.add_argument("--source-inventory-sha256")
    parser.add_argument("--storage-binding", type=Path, required=True)
    parser.add_argument("--storage-binding-sha256", required=True)
    parser.add_argument("--lifecycle-receipt", type=Path, required=True)
    parser.add_argument("--lifecycle-receipt-sha256", required=True)
    parser.add_argument("--ownership-receipt", type=Path, required=True)
    parser.add_argument("--ownership-receipt-sha256", required=True)
    parser.add_argument("--collection-receipt-sha256", required=True)
    parser.add_argument("--local-control-directory", type=Path, required=True)
    parser.add_argument("--cache-parent", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)

    def source_recheck():
        prepared = pilot.prepare(args.manifest, args.source_commit,
                                 inventory=args.source_inventory,
                                 inventory_sha256=args.source_inventory_sha256)
        binding = hashed_json(args.storage_binding, args.storage_binding_sha256)
        lifecycle = hashed_json(args.lifecycle_receipt, args.lifecycle_receipt_sha256)
        ownership = hashed_json(args.ownership_receipt, args.ownership_receipt_sha256)
        validate_termination(lifecycle, ownership, args.source_commit)
        validate_storage_worker_binding(binding, ownership, args.source_commit)
        return prepared, binding

    prepared, binding = source_recheck()  # Must precede SSH or fitting.
    from scripts.symbolic_ssh_storage import SshEvidenceStore
    store = SshEvidenceStore.open_existing(binding, local_control_directory=args.local_control_directory)
    previous = signal.signal(signal.SIGTERM, lambda *_args: (_ for _ in ()).throw(KeyboardInterrupt("analysis interrupted")))
    try:
        with RemoteCollectionAssets(store, cache_parent=args.cache_parent) as assets:
            receipt = pilot.analyze(prepared, None, args.collection_receipt_sha256, args.output_dir,
                                    source_recheck=source_recheck, asset_provider=assets)
            audit = assets.audit_receipt()
    finally:
        signal.signal(signal.SIGTERM, previous)
    audit.update({"schema": "butterfly.symbolic-remote-analysis-io.v1", "source_commit": args.source_commit,
                  "source_inventory_sha256": args.source_inventory_sha256,
                  "storage_binding_sha256": args.storage_binding_sha256,
                  "lifecycle_receipt_sha256": args.lifecycle_receipt_sha256,
                  "ownership_receipt_sha256": args.ownership_receipt_sha256,
                  "collection_receipt_sha256": args.collection_receipt_sha256,
                  "analysis_status": receipt["status"], "analysis_passed": receipt["passed"],
                  "worker_termination_verified_before_analysis": True, "gpu_calls_performed": False})
    pilot.write_new_json(args.output_dir / "remote-io-audit.json", audit)
    print(json.dumps({"status": receipt["status"], "nomination_passed": receipt["passed"],
                      "full_remote_audits_completed": audit["full_remote_audits_completed"]}, sort_keys=True))
    return 0 if receipt["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

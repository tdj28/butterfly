#!/usr/bin/env python3
"""Archive a complete EXP-477 local collection only after its owned GPU is gone.

Default mode verifies local evidence/source and writes a preflight receipt. Only
--execute opens SSH. Upload reads the original tar directly, retains every local
original, and never calls Runpod or performs numerical integration/fitting.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import signal
import tarfile
import time

from scripts import execute_symbolic_center_cloud as cloud
from scripts import run_symbolic_center_pilot as pilot
from scripts import symbolic_ssh_storage as storage
from scripts.analyze_symbolic_remote_collection import hashed_json, validate_termination


ROOT = Path(__file__).resolve().parents[1]
MAXIMUM_TRANSFER_SECONDS = 7200
POLICY = {"maximum_transfer_seconds": MAXIMUM_TRANSFER_SECONDS,
          "gpu_termination_required": True, "retain_local_originals": True}
LIMITS = {"maximum_total_bytes": storage.MAXIMUM_TOTAL_BYTES, "maximum_files": storage.MAXIMUM_FILES}
SOURCE_MAXIMUM_BYTES = 256 * 1048576


def regular(path, *, maximum_bytes):
    path = Path(path)
    storage.reject_symlink_chain(path)
    if not path.is_file() or not 0 <= path.stat().st_size <= maximum_bytes:
        raise ValueError("expected a bounded regular local evidence file")
    return path


def document(path):
    path = regular(path, maximum_bytes=storage.MAXIMUM_CONTROL_BYTES)
    return json.loads(path.read_bytes())


def verify_source_archive(path, inventory):
    """Check frozen tracked-file closure without extracting or copying source."""
    regular(path, maximum_bytes=SOURCE_MAXIMUM_BYTES)
    if pilot.sha256_file(path) != inventory.get("source_archive_sha256"):
        raise ValueError("source archive hash differs from frozen inventory")
    observed, total, count = {}, 0, 0
    with tarfile.open(path, "r:") as archive:
        for member in archive:
            count += 1
            if count > 10000 or not cloud.source_allowed(member.name.rstrip("/"), directory=member.isdir()):
                raise ValueError("source archive contains unbounded or unallowlisted members")
            if member.isdir():
                continue
            if not member.isfile() or member.name in observed:
                raise ValueError("source archive contains nonregular or duplicate files")
            total += member.size
            if total > SOURCE_MAXIMUM_BYTES:
                raise ValueError("source archive exceeds uncompressed bound")
            digest = hashlib.sha256()
            with archive.extractfile(member) as stream:
                for block in iter(lambda: stream.read(1048576), b""):
                    digest.update(block)
            observed[member.name] = digest.hexdigest()
    if observed != inventory.get("files"):
        raise ValueError("source archive file hashes differ from frozen inventory")


def verify_archive(path, inventory):
    """Stream-hash the exact raw tar; do not create another multi-GiB copy."""
    regular(path, maximum_bytes=storage.MAXIMUM_ARCHIVE_BYTES)
    expected = {row["path"]: row for row in inventory["assets"]}
    observed = set()
    with tarfile.open(path, "r:") as archive:
        for index, member in enumerate(archive):
            if index > storage.MAXIMUM_FILES or not member.isfile() or not storage.safe_name(member.name):
                raise ValueError("raw archive has an unsafe or excessive member set")
            if index == 0:
                if member.name != "retrieval-manifest.json" or member.size > 1048576:
                    raise ValueError("raw archive lacks its bounded leading inventory")
                with archive.extractfile(member) as stream:
                    if json.loads(stream.read()) != inventory:
                        raise ValueError("raw archive inventory differs from verified local evidence")
                continue
            row = expected.get(member.name)
            if (row is None or member.name in observed or not storage.ASSET.fullmatch(member.name)
                    or member.size != row["bytes"]):
                raise ValueError("raw archive members differ from verified local inventory")
            observed.add(member.name)
            digest = hashlib.sha256()
            with archive.extractfile(member) as stream:
                for block in iter(lambda: stream.read(1048576), b""):
                    digest.update(block)
            if digest.hexdigest() != row["sha256"]:
                raise ValueError("raw archive member hash mismatch")
    if observed != set(expected):
        raise ValueError("raw archive lacks complete local evidence")


def preflight(args, *, root=ROOT):
    """Local read-only admission checks; no SSH/provider or numerical work."""
    lifecycle = hashed_json(args.lifecycle_receipt, args.lifecycle_receipt_sha256)
    ownership = hashed_json(args.ownership_receipt, args.ownership_receipt_sha256)
    validate_termination(lifecycle, ownership, args.source_commit)
    storage.validate_directory(args.remote_dir)
    directory = Path(args.collection_output_dir).resolve()
    storage.reject_symlink_chain(args.collection_output_dir)
    prepared = document(directory / "preparation.json")
    workload = document(directory / "workload.json")
    if (prepared.get("schema") != "butterfly.symbolic-cloud-preparation.v1"
            or prepared.get("source_commit") != args.source_commit or prepared.get("plan") != lifecycle["plan"]
            or prepared.get("runtime", {}).get("post_termination_archive") != POLICY
            or prepared.get("runtime", {}).get("retrieval") != LIMITS
            or prepared.get("ssh_storage_directory") is not None):
        raise ValueError("local preparation is not bound to this terminated worker/frozen archival policy")
    if (workload.get("schema") != "butterfly.symbolic-cloud-workload.v1"
            or workload.get("source_commit") != args.source_commit
            or workload.get("remote_directory") != "/workspace/butterfly-exp477-" + ownership["nonce"]
            or any(workload.get(key) is not True for key in ("passed", "retrieval_verified", "complete_raw_closure_verified",
                                                           "owned_writers_quiescent", "target_collection_started"))
            or [row.get("name") for row in workload.get("stages", [])] != ["setup", "qualification", "collection"]):
        raise ValueError("workload lacks complete quiescent evidence from the specifically terminated worker")
    incoming = directory / "prepared-inputs"
    if set(prepared["assets"]) != {"source.tar", "source-inventory.json", "cpu-control.json", "candidates.json"}:
        raise ValueError("prepared input allowlist differs from frozen source/control/candidate closure")
    for name, row in prepared["assets"].items():
        path = regular(incoming / name, maximum_bytes=SOURCE_MAXIMUM_BYTES)
        if cloud.describe(path) != row:
            raise ValueError("prepared source/control/input hash or size changed")
    inventory = document(incoming / "source-inventory.json")
    verified = pilot.prepare(Path(root) / cloud.PILOT_MANIFEST, args.source_commit, root=root,
                             inventory=args.source_inventory, inventory_sha256=args.source_inventory_sha256)
    if (inventory.get("source_commit") != args.source_commit or inventory.get("pushed_source_commit") != args.source_commit
            or inventory.get("schema") != "butterfly.source-inventory.v1"):
        raise ValueError("prepared source inventory differs from the declared pushed source")
    # A separate optional inventory controls the active source. The original
    # collection inventory must independently match that same active source.
    pilot.source_binding(Path(root), args.source_commit, Path(root) / cloud.PILOT_MANIFEST,
                         (Path(root) / cloud.PILOT_MANIFEST).read_bytes(), inventory=incoming / "source-inventory.json",
                         inventory_sha256=prepared["assets"]["source-inventory.json"]["sha256"])
    verify_source_archive(incoming / "source.tar", inventory)
    runtime = document(Path(root) / cloud.RUNTIME_MANIFEST)
    expected_plan = {**runtime["lifecycle"], "experiment_id": "EXP-477", "source_commit": args.source_commit}
    if prepared["runtime"] != runtime or prepared["plan"] != expected_plan:
        raise ValueError("preparation runtime/plan differs from the frozen source contract")
    expected_binding = {"input_hashes": verified["input_hashes"],
                        "candidate_ids": [row["id"] for row in verified["candidates"]],
                        "profiles": verified["parent"]["profiles"],
                        "batch_size": verified["manifest"]["execution"]["batch_size"]}
    if prepared.get("pilot_manifest_sha256") != verified["manifest_sha256"] or prepared.get("collection_binding") != expected_binding:
        raise ValueError("preparation differs from the frozen scientific design/candidate set")
    candidate_asset = prepared["assets"]["candidates.json"]
    if (candidate_asset["sha256"] != verified["input_hashes"]["candidates"]
            or candidate_asset["sha256"] != cloud.worker.CANDIDATE_HASH
            or candidate_asset["bytes"] != cloud.worker.CANDIDATE_BYTES):
        raise ValueError("staged candidates differ from the frozen scientific input")
    cpu_path = incoming / "cpu-control.json"
    cpu = document(cpu_path)
    qualification = cloud.qualification
    if (prepared.get("cpu_control_sha256") != pilot.sha256_file(cpu_path)
            or cpu.get("schema") != "butterfly.symbolic-gpu-deployment-control.v1" or cpu.get("mode") != "cpu"
            or cpu.get("passed") is not True or cpu.get("source", {}).get("commit") != args.source_commit
            or cpu.get("parent_sha256") != qualification.PARENT_HASH
            or cpu.get("qualification_script_sha256") != inventory["files"].get("scripts/qualify_symbolic_gpu_records.py")
            or cpu.get("state_atol") != qualification.STATE_ATOL or cpu.get("time_atol") != qualification.TIME_ATOL):
        raise ValueError("CPU control differs from passing frozen source/design qualification")
    qualification.validate_control(cpu["control"], qualification.parent_design())
    manifest_path = regular(directory / "retrieved/retrieval-manifest.json", maximum_bytes=storage.MAXIMUM_CONTROL_BYTES)
    raw_inventory = storage.audit_remote(directory, pilot.sha256_file(manifest_path), manifest_path.stat().st_size)
    closure = cloud.validate_retrieved_collection(directory / "retrieved", raw_inventory, prepared)
    archive = regular(directory / "retrieved.tar", maximum_bytes=storage.MAXIMUM_ARCHIVE_BYTES)
    archive_descriptor = cloud.describe(archive)
    if archive_descriptor != workload.get("retrieval_archive"):
        raise ValueError("retrieved archive differs from original workload hash/size")
    verify_archive(archive, raw_inventory)
    hashes = {name: cloud.describe(directory / name) for name in ("preparation.json", "workload.json", "retrieved.tar")}
    return {"prepared": prepared, "ownership": ownership, "cpu_bytes": cpu_path.read_bytes(), "archive": archive,
            "inventory": inventory, "source": verified["source"], "local_hashes": hashes, "raw_closure": closure}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection-output-dir", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-inventory", type=Path)
    parser.add_argument("--source-inventory-sha256")
    for name in ("lifecycle-receipt", "ownership-receipt"):
        parser.add_argument("--" + name, type=Path, required=True)
        parser.add_argument("--" + name + "-sha256", required=True)
    parser.add_argument("--remote-dir", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    storage.reject_symlink_chain(args.output_dir)
    if args.output_dir.resolve().is_relative_to(args.collection_output_dir.resolve()):
        parser.error("archive control output must not be inside the original collection")
    args.output_dir.mkdir(mode=0o700, parents=False, exist_ok=False)
    receipt = {"schema": "butterfly.symbolic-post-termination-archive.v1", "source_commit": args.source_commit,
               "mode": "execute" if args.execute else "preflight", "started_utc": pilot.utc_now(),
               "passed": False, "status": "running", "phase": "local-admission", "ssh_upload_started": False,
               "worker_termination_verified_before_upload": False, "runpod_calls_performed": False,
               "local_originals_removed": False, "maximum_transfer_seconds": MAXIMUM_TRANSFER_SECONDS,
               "lifecycle_receipt_sha256": args.lifecycle_receipt_sha256,
               "ownership_receipt_sha256": args.ownership_receipt_sha256}
    previous = signal.signal(signal.SIGTERM, lambda *_args: (_ for _ in ()).throw(KeyboardInterrupt("archive interrupted")))
    try:
        checked = preflight(args)
        receipt.update(source=checked["source"], local_input_hashes=checked["local_hashes"],
                       raw_closure=checked["raw_closure"], worker_termination_verified_before_upload=True)
        if args.execute:
            deadline = time.monotonic() + MAXIMUM_TRANSFER_SECONDS
            def remaining():
                seconds = deadline - time.monotonic()
                if seconds <= 0:
                    raise TimeoutError("post-termination archive deadline")
                return seconds
            store = storage.SshEvidenceStore(args.remote_dir, local_control_directory=args.output_dir)
            owner = checked["ownership"]
            store.binding.update(task_worker_id=owner["pod_id"], task_worker_name=owner["name"],
                                 task_worker_nonce=owner["nonce"], source_commit=args.source_commit)
            receipt["phase"] = "remote-preparation"
            store.prepare(checked["prepared"], checked["cpu_bytes"],
                          helper_sha256=checked["inventory"]["files"]["scripts/symbolic_ssh_storage.py"])
            receipt["ssh_upload_started"] = True
            receipt["phase"] = "archive-upload"
            transfer = store.receive(["/bin/cat", str(checked["archive"])], seconds=remaining(), progress=lambda _stage: None)
            expected = checked["local_hashes"]["retrieved.tar"]
            if any(transfer.get(key) != expected[key] for key in ("bytes", "sha256")):
                raise ValueError("transferred archive hash/size differs from original workload")
            receipt["transfer"] = {key: transfer[key] for key in ("bytes", "sha256")}
            receipt["phase"] = "local-post-upload-recheck"
            rechecked = preflight(args)
            if rechecked["local_hashes"] != checked["local_hashes"]:
                raise ValueError("local evidence/control inputs changed during upload")
            receipt["phase"] = "remote-finalization"
            finalized = store.finalize(seconds=remaining())
            if finalized.get("retrieval_verified") is not True or finalized.get("complete_raw_closure_verified") is not True:
                raise ValueError("remote archive retained but complete raw closure was not verified")
            receipt["phase"] = "remote-compact-receipts"
            remote_inventory = store.retain_compact_receipts(seconds=remaining())
            receipt.update(remote_file_count=len(remote_inventory["assets"]),
                           remote_retrieval_manifest_sha256=store.binding["retrieval_manifest_sha256"],
                           remote_storage_binding_sha256=pilot.sha256_file(args.output_dir / "remote-storage.json"),
                           remote_complete_raw_closure_verified=True)
        receipt.update(status="completed", phase="finished", passed=True)
    except (Exception, KeyboardInterrupt) as error:
        # Details may contain machine paths; keep the public summary minimal.
        receipt.update(status="failed", failure={"type": type(error).__name__, "message": "archival admission or transfer failed; original local evidence retained"})
    finally:
        signal.signal(signal.SIGTERM, previous)
        receipt["finished_utc"] = pilot.utc_now()
        pilot.write_new_json(args.output_dir / "receipt.json", receipt)
    print(json.dumps({"status": receipt["status"], "passed": receipt["passed"], "ssh_upload_started": receipt["ssh_upload_started"]}, sort_keys=True))
    return 0 if receipt["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

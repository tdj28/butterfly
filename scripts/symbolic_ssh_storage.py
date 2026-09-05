#!/usr/bin/env python3
"""Bounded EXP-477 SSH evidence storage; stdlib-only receiver and read-only API.

The Mac retains all controller credentials. A hash-bound copy of this public
helper runs only inside a new task directory on the existing trusted prax host.
Storage does not integrate trajectories, fit models, or qualify scientific claims.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import select
import shlex
import shutil
import signal
import subprocess
import sys
import tarfile
import time


HOST = "ubuntu@prax"
BASE_DIRECTORY = "/home/ubuntu/butterfly-research"
MAXIMUM_TOTAL_BYTES = 8589934592
MAXIMUM_FILES = 2000
MAXIMUM_ARCHIVE_BYTES = MAXIMUM_TOTAL_BYTES + MAXIMUM_FILES * 2048 + 2 * 1048576
MINIMUM_REMOTE_FREE_BYTES = MAXIMUM_ARCHIVE_BYTES + MAXIMUM_TOTAL_BYTES + 512 * 1048576
MINIMUM_LOCAL_FREE_BYTES = 2147483648
MAXIMUM_CACHED_ASSET_BYTES = 268435456
MAXIMUM_CONTROL_BYTES = 4194304
SCHEMA = "butterfly.symbolic-ssh-storage.v1"
REMOTE_SCHEMA = "butterfly.symbolic-ssh-expected.v1"
ASSET = re.compile(r"(?:gpu-control\.json|logs/(?:setup|qualification|collection)\.log|"
                   r"environment/(?:python\.txt|pip-freeze\.txt|nvidia-smi\.txt|torch\.json|storage\.json)|"
                   r"status/[a-z0-9-]+\.json|collection/(?:started|receipt)\.json|"
                   r"collection/batch-[0-9]{4}-profile-[01](?:-checkpoint)?\.(?:json|npz))\Z")


class StorageError(RuntimeError):
    pass


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":")) + "\n").encode()


def write_new(path, data):
    with Path(path).open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def descriptor(path, name=None):
    path = Path(path)
    return {"path": name or path.name, "sha256": sha256_file(path), "bytes": path.stat().st_size}


def safe_name(name):
    if not isinstance(name, str):
        return False
    path = PurePosixPath(name)
    return isinstance(name, str) and bool(name and not path.is_absolute() and ".." not in path.parts
                                        and "\\" not in name and str(path) == name)


def validate_directory(directory, *, base_directory=BASE_DIRECTORY):
    path, base = Path(directory), Path(base_directory)
    if (not path.is_absolute() or path.parent != base or str(path) != str(directory)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", path.name)):
        raise StorageError("remote evidence must use one fresh named child of the authorized research directory")
    return path


def reject_symlink_chain(path):
    path = Path(path)
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise StorageError("evidence path contains a symlink")


def checked_asset(root, row, *, maximum_bytes=MAXIMUM_TOTAL_BYTES):
    if (not isinstance(row, dict) or not isinstance(row.get("path"), str) or not safe_name(row["path"])
            or not ASSET.fullmatch(row["path"]) or type(row.get("bytes")) is not int
            or not 0 <= row["bytes"] <= maximum_bytes or not isinstance(row.get("sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])):
        raise StorageError("invalid evidence descriptor")
    path = Path(root) / row["path"]
    reject_symlink_chain(path)
    if not path.is_file() or path.stat().st_size != row["bytes"] or sha256_file(path) != row["sha256"]:
        raise StorageError("evidence hash/size mismatch: " + row["path"])
    return path


def safe_extract(archive_path, destination):
    """Exact inventory, bounded sizes, exclusive regular files, no link following."""
    if Path(archive_path).stat().st_size > MAXIMUM_ARCHIVE_BYTES:
        raise StorageError("remote archive exceeds transfer bound")
    destination = Path(destination)
    reject_symlink_chain(destination)
    destination.mkdir(mode=0o700, exist_ok=False)
    with tarfile.open(archive_path, "r:") as archive:
        members = []
        for member in archive:
            if len(members) >= MAXIMUM_FILES + 1:
                raise StorageError("too many archive members")
            if not member.isfile() or not safe_name(member.name):
                raise StorageError("unsafe archive member")
            members.append(member)
        if not members or members[0].name != "retrieval-manifest.json" or members[0].size > 1048576:
            raise StorageError("missing or excessive leading inventory")
        if len({row.name for row in members}) != len(members):
            raise StorageError("duplicate archive member")
        with archive.extractfile(members[0]) as stream:
            inventory_bytes = stream.read(1048577)
        inventory = json.loads(inventory_bytes)
        rows = inventory.get("assets", [])
        if (inventory.get("schema") != "butterfly.symbolic-remote-assets.v1" or len(rows) > MAXIMUM_FILES
                or len({row["path"] for row in rows}) != len(rows)):
            raise StorageError("invalid remote inventory")
        expected = {row["path"]: row for row in rows}
        if set(expected) != {member.name for member in members[1:]}:
            raise StorageError("archive and declared evidence sets differ")
        if sum(member.size for member in members[1:]) > MAXIMUM_TOTAL_BYTES:
            raise StorageError("extracted evidence exceeds byte bound")
        for member in members[1:]:
            row = expected[member.name]
            if not ASSET.fullmatch(member.name) or type(row.get("bytes")) is not int or row["bytes"] != member.size:
                raise StorageError("invalid evidence filename or size")
            path = destination / member.name
            path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            with archive.extractfile(member) as source, path.open("xb") as output:
                for block in iter(lambda: source.read(1048576), b""):
                    output.write(block)
                output.flush()
                os.fsync(output.fileno())
            checked_asset(destination, row)
        write_new(destination / "retrieval-manifest.json", inventory_bytes)
    return inventory


def validate_complete(root, inventory, expected):
    """Validate complete declared raw closure, never load or fit numerical arrays."""
    prepared, cpu = expected["prepared"], expected["cpu_control"]
    rows = {row["path"]: row for row in inventory["assets"]}

    def asset(name):
        if name not in rows:
            raise StorageError("required evidence missing: " + name)
        return checked_asset(root, rows[name])

    def json_asset(name):
        path = asset(name)
        if path.stat().st_size > MAXIMUM_CONTROL_BYTES:
            raise StorageError("control evidence exceeds bounded JSON size")
        return json.loads(path.read_bytes())

    def source_ok(source):
        return (source.get("commit") == prepared["source_commit"] and source.get("mode") == "explicit_inventory"
                and source.get("inventory_sha256") == prepared["assets"]["source-inventory.json"]["sha256"])

    gpu = json_asset("gpu-control.json")
    projected = (gpu.get("benchmark") or {}).get("projected_collection_seconds_with_margin")
    if (gpu.get("schema") != "butterfly.symbolic-gpu-deployment-control.v1" or gpu.get("mode") != "gpu"
            or gpu.get("passed") is not True or not source_ok(gpu.get("source", {}))
            or gpu.get("cpu_control_sha256") != prepared["cpu_control_sha256"]
            or any(gpu.get(key) != cpu.get(key) for key in ("parent_sha256", "qualification_script_sha256", "state_atol", "time_atol"))
            or type(projected) not in (int, float) or not 0 < projected <= 2400.0):
        raise StorageError("GPU qualification source/control/timing mismatch")
    collection = json_asset("collection/receipt.json")
    binding = prepared["collection_binding"]
    if (collection.get("schema") != "butterfly.symbolic-center-collection.v1" or collection.get("experiment_id") != "EXP-477"
            or collection.get("status") != "completed" or collection.get("collection_passed") is not True
            or collection.get("nomination_performed") is not False or not source_ok(collection.get("source", {}))
            or collection.get("manifest_sha256") != prepared["pilot_manifest_sha256"]
            or collection.get("input_hashes") != binding["input_hashes"]
            or collection.get("completed_candidate_ids") != binding["candidate_ids"]
            or collection.get("uncompleted_candidate_ids") != []):
        raise StorageError("collection is incomplete or has incorrect source/input binding")
    ids, size, profiles = binding["candidate_ids"], binding["batch_size"], binding["profiles"]
    batches = collection["batches"]
    if len(batches) != (len(ids) + size - 1) // size:
        raise StorageError("incomplete batch set")
    for index, batch in enumerate(batches):
        candidate_ids = ids[index * size:(index + 1) * size]
        if batch.get("index") != index or batch.get("candidate_ids") != candidate_ids or len(batch["profiles"]) != len(profiles):
            raise StorageError("batch IDs/order/profile coverage mismatch")
        for j, (metadata, profile) in enumerate(zip(batch["profiles"], profiles, strict=True)):
            name = f"batch-{index:04d}-profile-{j}"
            if (metadata.get("schema") != "butterfly.symbolic-center-raw-batch.v1" or metadata.get("validity_passed") is not True
                    or metadata.get("profile") != profile or metadata.get("candidate_ids") != candidate_ids):
                raise StorageError("raw metadata validity or identity mismatch")
            for key, suffix in (("raw", ".npz"), ("metadata_file", ".json")):
                row = metadata[key]
                if row.get("path") != name + suffix:
                    raise StorageError("raw evidence filename differs from batch identity")
                path = asset("collection/" + row["path"])
                if descriptor(path) != row:
                    raise StorageError("raw descriptor differs from retained inventory")
            if json_asset("collection/" + name + ".json") != {key: value for key, value in metadata.items() if key != "metadata_file"}:
                raise StorageError("saved metadata differs from collection receipt")
            if json_asset("collection/" + name + "-checkpoint.json") != {"candidate_ids": candidate_ids, "raw_metadata": metadata}:
                raise StorageError("checkpoint differs from raw metadata")
    for name in ("collection/started.json", "environment/python.txt", "environment/pip-freeze.txt",
                 "environment/nvidia-smi.txt", "environment/torch.json", "environment/storage.json"):
        asset(name)
    for name in ("setup", "qualification", "collection"):
        asset("logs/" + name + ".log")
        if json_asset("status/" + name + ".json").get("passed") is not True:
            raise StorageError("owned stage is not completed successfully")
    return {"complete": True, "candidate_count": len(ids), "profile_batch_count": len(batches) * len(profiles)}


def receive_stream(root, stream, *, maximum_bytes=MAXIMUM_ARCHIVE_BYTES):
    """Retain even truncated transfers, never overwrite a previous attempt."""
    path = Path(root) / "received.tar"
    count = 0
    digest = hashlib.sha256()
    with path.open("xb") as output:
        for block in iter(lambda: stream.read(1048576), b""):
            if count + len(block) > maximum_bytes:
                raise StorageError("incoming archive exceeds byte bound; partial bytes retained")
            output.write(block); digest.update(block); count += len(block)
        output.flush(); os.fsync(output.fileno())
    receipt = {"bytes": count, "sha256": digest.hexdigest(), "path": "received.tar"}
    write_new(Path(root) / "transfer.json", encoded(receipt))
    return receipt


def audit_remote(root, manifest_sha256, manifest_bytes):
    root = Path(root)
    path = root / "retrieved/retrieval-manifest.json"
    reject_symlink_chain(path)
    if (path.stat().st_size != manifest_bytes or path.stat().st_size > MAXIMUM_CONTROL_BYTES
            or sha256_file(path) != manifest_sha256):
        raise StorageError("immutable retrieval inventory changed")
    inventory = json.loads(path.read_bytes())
    rows = inventory["assets"]
    if (inventory.get("schema") != "butterfly.symbolic-remote-assets.v1" or len(rows) > MAXIMUM_FILES
            or len({row["path"] for row in rows}) != len(rows)
            or sum(row["bytes"] for row in rows) > MAXIMUM_TOTAL_BYTES):
        raise StorageError("invalid retained inventory")
    actual = set()
    for path in (root / "retrieved").rglob("*"):
        if path.is_symlink():
            raise StorageError("retained evidence contains a symlink")
        if path.is_file() and path != root / "retrieved/retrieval-manifest.json":
            actual.add(path.relative_to(root / "retrieved").as_posix())
    if actual != {row["path"] for row in rows}:
        raise StorageError("retained evidence file set changed")
    for row in rows:
        checked_asset(root / "retrieved", row)
    return inventory


def finalize_remote(root, expected):
    root = Path(root)
    result = {"retrieval_verified": False, "complete_raw_closure_verified": False}
    try:
        transfer = root / "transfer.json"
        if transfer.exists() and json.loads(transfer.read_bytes()) != descriptor(root / "received.tar"):
            raise StorageError("received archive changed after transfer acknowledgement")
        inventory = safe_extract(root / "received.tar", root / "retrieved")
        result["retrieval_verified"] = True
        manifest = descriptor(root / "retrieved/retrieval-manifest.json")
        result["retrieval_manifest_sha256"] = manifest["sha256"]
        result["retrieval_manifest_bytes"] = manifest["bytes"]
        result["retrieved_file_count"] = len(inventory["assets"])
        result["raw_closure"] = validate_complete(root / "retrieved", inventory, expected)
        result["complete_raw_closure_verified"] = True
    except Exception as error:
        result["failure"] = {"type": type(error).__name__, "message": str(error)}
    finally:
        if (root / "received.tar").exists():
            result["retained_archive"] = descriptor(root / "received.tar")
        write_new(root / "finalization.json", encoded(result))
    return result


# The bootstrap cannot install packages or write outside the task directory.
# It verifies the public helper bytes before they can execute.
INIT_BOOTSTRAP = r'''
import base64,hashlib,json,os,pathlib,re,shutil,sys
p=json.loads(sys.stdin.buffer.read(4194305))
base=pathlib.Path('/home/ubuntu/butterfly-research'); d=pathlib.Path(p['remote_directory'])
if d.parent!=base or str(d)!=p['remote_directory'] or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}',d.name): raise RuntimeError('invalid evidence directory')
if any(x.is_symlink() for x in (base,*base.parents)): raise RuntimeError('symlink in evidence root')
if d.exists() or d.is_symlink(): raise RuntimeError('evidence directory must be new')
nearest=base if base.exists() else base.parent
if shutil.disk_usage(nearest).free < 17722933248: raise RuntimeError('remote evidence free-space gate failed')
helper=base64.b64decode(p['helper_base64'],validate=True); expected=base64.b64decode(p['expected_base64'],validate=True)
if len(helper)>1048576 or len(expected)>4194304 or hashlib.sha256(helper).hexdigest()!=p['helper_sha256'] or hashlib.sha256(expected).hexdigest()!=p['expected_binding_sha256']: raise RuntimeError('staged helper/binding hash mismatch')
base.mkdir(mode=0o700,exist_ok=True); d.mkdir(mode=0o700)
for name,data in (('_storage_helper.py',helper),('expected.json',expected)):
 with (d/name).open('xb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
print(json.dumps({'prepared':True,'available_bytes':shutil.disk_usage(d).free}))
'''

RUN_BOOTSTRAP = r'''
import hashlib,pathlib,sys
p=pathlib.Path(sys.argv[1]); raw=p.read_bytes()
if p.is_symlink() or hashlib.sha256(raw).hexdigest()!=sys.argv[2]: raise RuntimeError('storage helper changed')
sys.argv=[str(p),'--remote',*sys.argv[3:]]
exec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
'''


def remote_main(root, expected_sha256, action, payload):
    root = validate_directory(root)
    reject_symlink_chain(root)
    expected_path = root / "expected.json"
    if expected_path.stat().st_size > MAXIMUM_CONTROL_BYTES or sha256_file(expected_path) != expected_sha256:
        raise StorageError("immutable expected binding changed")
    expected = json.loads(expected_path.read_bytes())
    if expected.get("schema") != REMOTE_SCHEMA:
        raise StorageError("unsupported expected binding")
    if action == "receive":
        return receive_stream(root, sys.stdin.buffer)
    if action == "finalize":
        return finalize_remote(root, expected)
    if action not in {"audit", "verify", "read"}:
        raise StorageError("unsupported storage action")
    # Every read API remains bound to the immutable inventory. Full audit is
    # explicit; individual reads rehash their exact descriptor before streaming.
    path = root / "retrieved/retrieval-manifest.json"
    if (path.stat().st_size != payload["retrieval_manifest_bytes"] or path.stat().st_size > MAXIMUM_CONTROL_BYTES
            or sha256_file(path) != payload["retrieval_manifest_sha256"]):
        raise StorageError("immutable retrieval inventory changed")
    if action == "audit":
        return audit_remote(root, payload["retrieval_manifest_sha256"], payload["retrieval_manifest_bytes"])
    inventory = json.loads(path.read_bytes())
    rows = {row["path"]: row for row in inventory["assets"]}
    requests = payload["descriptors"]
    if len(requests) > MAXIMUM_FILES:
        raise StorageError("too many requested assets")
    for row in requests:
        if rows.get(row.get("path")) != row:
            raise StorageError("requested descriptor differs from bound inventory")
        checked_asset(root / "retrieved", row)
    if action == "verify":
        return {"verified": True, "count": len(requests)}
    if len(requests) != 1 or requests[0]["bytes"] > min(payload["maximum_bytes"], MAXIMUM_CACHED_ASSET_BYTES):
        raise StorageError("read exceeds the bounded single-asset contract")
    with (root / "retrieved" / requests[0]["path"]).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            sys.stdout.buffer.write(block)
    return None


def ssh_options():
    # Use the already trusted host key, never TOFU. Authentication stays local;
    # no agent forwarding, port forwarding, private keys, or API keys transfer.
    return ["-F", "/dev/null", "-o", "StrictHostKeyChecking=yes", "-o", "ForwardAgent=no",
            "-o", "ClearAllForwardings=yes", "-o", "BatchMode=yes", "-o", "PasswordAuthentication=no",
            "-o", "KbdInteractiveAuthentication=no", "-o", "RequestTTY=no", "-o", "ConnectTimeout=10",
            "-o", "ServerAliveInterval=10", "-o", "ServerAliveCountMax=3"]


def stop_process(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(timeout=5)


def bounded_output(argv, output, *, maximum_bytes, seconds, log, input_bytes=None):
    """Bound stdout before writing; no unbounded capture_output for remote data."""
    started = time.monotonic()
    process = subprocess.Popen(argv, stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=log)
    count = 0
    try:
        if input_bytes is not None:
            if len(input_bytes) > MAXIMUM_CONTROL_BYTES:
                raise StorageError("control request exceeds local bound")
            # Requests are small, but the SSH peer can still stop consuming.
            os.set_blocking(process.stdin.fileno(), False)
            pending = memoryview(input_bytes)
        else:
            pending = None
        while True:
            remaining = seconds - (time.monotonic() - started)
            if remaining <= 0:
                raise TimeoutError("bounded SSH storage operation deadline")
            readable, writable, _ = select.select([process.stdout], [process.stdin] if pending is not None else [], [], min(1, remaining))
            if writable:
                try:
                    wrote = os.write(process.stdin.fileno(), pending[:65536])
                    pending = pending[wrote:]
                    if not pending:
                        process.stdin.close(); pending = None
                except BrokenPipeError as error:
                    raise StorageError("storage peer stopped accepting control input") from error
            if readable:
                block = os.read(process.stdout.fileno(), 1048576)
                if not block:
                    break
                if count + len(block) > maximum_bytes:
                    raise StorageError("SSH output exceeds declared byte bound")
                output.write(block); count += len(block)
        process.wait(timeout=max(0.001, seconds-(time.monotonic()-started)))
        if process.returncode:
            raise StorageError("SSH storage command failed; local log retained")
        return count
    finally:
        stop_process(process)
        if process.stdin is not None and not process.stdin.closed:
            process.stdin.close()
        process.stdout.close()


def relay_stream(source_argv, destination_argv, *, maximum_bytes, seconds, progress, log):
    """Backpressured bounded RAM relay; no bulk file is opened on the Mac."""
    source = subprocess.Popen(source_argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=log)
    try:
        sink = subprocess.Popen(destination_argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)
    except BaseException:
        stop_process(source); source.stdout.close()
        raise
    os.set_blocking(sink.stdin.fileno(), False)
    started = reported = time.monotonic()
    pending, received, sent, response = bytearray(), 0, 0, bytearray()
    digest = hashlib.sha256()
    source_eof = sink_eof = False
    try:
        while not sink_eof:
            remaining = seconds - (time.monotonic() - started)
            if remaining <= 0:
                raise TimeoutError("SSH evidence relay deadline; remote partial bytes retained")
            readers = [sink.stdout]
            if not source_eof and len(pending) < 1048576:
                readers.append(source.stdout)
            writers = [sink.stdin] if pending else []
            readable, writable, _ = select.select(readers, writers, [], min(1, remaining))
            if source.stdout in readable:
                block = os.read(source.stdout.fileno(), min(65536, 1048576 - len(pending)))
                if not block:
                    source_eof = True
                else:
                    if received + len(block) > maximum_bytes:
                        raise StorageError("source transfer exceeds byte bound; remote partial bytes retained")
                    received += len(block); pending.extend(block); digest.update(block)
            if sink.stdin in writable:
                try:
                    wrote = os.write(sink.stdin.fileno(), pending[:65536])
                except BrokenPipeError as error:
                    raise StorageError("remote storage stopped consuming; partial bytes retained") from error
                del pending[:wrote]; sent += wrote
                if time.monotonic() - reported >= 30:
                    progress(f"remote-storage-bytes-{sent}"); reported = time.monotonic()
            if source_eof and not pending and not sink.stdin.closed:
                sink.stdin.close()
            if sink.stdout in readable:
                block = os.read(sink.stdout.fileno(), 65536)
                if not block:
                    sink_eof = True
                else:
                    if len(response) + len(block) > MAXIMUM_CONTROL_BYTES:
                        raise StorageError("storage acknowledgement exceeds control bound")
                    response.extend(block)
        source.wait(timeout=max(0.001, seconds-(time.monotonic()-started)))
        sink.wait(timeout=max(0.001, seconds-(time.monotonic()-started)))
        if source.returncode or sink.returncode or not source_eof or pending or sent != received:
            raise StorageError("evidence relay did not complete both authenticated SSH streams")
        result = json.loads(response)
        if result.get("bytes") != sent or result.get("sha256") != digest.hexdigest():
            raise StorageError("remote transfer acknowledgement differs from relayed stream")
        progress(f"remote-storage-bytes-{sent}")
        return result
    finally:
        stop_process(source); stop_process(sink)
        source.stdout.close(); sink.stdout.close()
        if not sink.stdin.closed:
            sink.stdin.close()


class SshEvidenceStore:
    """Fixed-host storage; existing-store methods perform remote reads only."""

    def __init__(self, remote_directory, *, local_control_directory, host=HOST):
        if host != HOST:
            raise StorageError("only the explicitly authorized prax evidence host is allowed")
        self.remote_directory = str(validate_directory(remote_directory))
        self.local_control_directory = Path(local_control_directory)
        self.binding = {"schema": SCHEMA, "host": HOST, "remote_directory": self.remote_directory}
        self._log_index = 0

    @classmethod
    def open_existing(cls, binding, *, local_control_directory):
        if binding.get("schema") != SCHEMA:
            raise StorageError("unsupported SSH storage binding")
        store = cls(binding["remote_directory"], local_control_directory=local_control_directory, host=binding["host"])
        for key in ("helper_sha256", "expected_binding_sha256", "retrieval_manifest_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", binding.get(key, "")):
                raise StorageError("missing hash in SSH storage binding")
        if type(binding.get("retrieval_manifest_bytes")) is not int or not 0 < binding["retrieval_manifest_bytes"] <= MAXIMUM_CONTROL_BYTES:
            raise StorageError("invalid inventory size in SSH storage binding")
        store.binding = dict(binding)
        return store

    def _argv(self, action, payload=None):
        arguments = ["python3", "-B", "-c", RUN_BOOTSTRAP,
                     self.remote_directory + "/_storage_helper.py", self.binding["helper_sha256"],
                     self.remote_directory, self.binding["expected_binding_sha256"], action, json.dumps(payload or {}, separators=(",", ":"))]
        return ["/usr/bin/ssh", *ssh_options(), HOST, shlex.join(arguments)]

    def _log(self, label):
        self._log_index += 1
        return (self.local_control_directory / f"storage-{self._log_index:04d}-{label}.log").open("xb")

    def _json(self, action, payload=None, *, seconds=120):
        output = io.BytesIO()
        with self._log(action) as log:
            bounded_output(self._argv(action, payload), output, maximum_bytes=MAXIMUM_CONTROL_BYTES,
                           seconds=seconds, log=log)
        return json.loads(output.getvalue())

    def prepare(self, prepared, cpu_content, *, helper_sha256):
        helper = Path(__file__).read_bytes()
        if hashlib.sha256(helper).hexdigest() != helper_sha256:
            raise StorageError("storage helper differs from the frozen source inventory")
        if hashlib.sha256(cpu_content).hexdigest() != prepared["cpu_control_sha256"]:
            raise StorageError("storage CPU control differs from frozen preparation")
        expected = {"schema": REMOTE_SCHEMA, "prepared": prepared, "cpu_control": json.loads(cpu_content)}
        data = encoded(expected)
        self.binding.update(helper_sha256=helper_sha256, expected_binding_sha256=hashlib.sha256(data).hexdigest())
        payload = {**self.binding, "helper_base64": base64.b64encode(helper).decode(),
                   "expected_base64": base64.b64encode(data).decode()}
        output = io.BytesIO()
        argv = ["/usr/bin/ssh", *ssh_options(), HOST, shlex.join(["python3", "-B", "-c", INIT_BOOTSTRAP])]
        with self._log("prepare") as log:
            bounded_output(argv, output, maximum_bytes=MAXIMUM_CONTROL_BYTES, seconds=120, log=log, input_bytes=encoded(payload))
        result = json.loads(output.getvalue())
        if result.get("prepared") is not True:
            raise StorageError("SSH evidence preparation was not acknowledged")
        write_new(self.local_control_directory / "remote-storage-preparation.json", encoded({**self.binding, "preflight": result}))
        return self.binding

    def receive(self, source_argv, *, seconds, progress):
        with self._log("receive") as log:
            return relay_stream(source_argv, self._argv("receive"), maximum_bytes=MAXIMUM_ARCHIVE_BYTES,
                                seconds=seconds, progress=progress, log=log)

    def finalize(self, *, seconds=120):
        result = self._json("finalize", seconds=seconds)
        self.binding.update({key: result[key] for key in ("retrieval_manifest_sha256", "retrieval_manifest_bytes") if key in result})
        self.binding["complete_raw_closure_verified"] = result.get("complete_raw_closure_verified") is True
        write_new(self.local_control_directory / "remote-storage-finalization.json", encoded(result))
        write_new(self.local_control_directory / "remote-storage.json", encoded(self.binding))
        return result

    def _inventory_binding(self):
        return {key: self.binding[key] for key in ("retrieval_manifest_sha256", "retrieval_manifest_bytes")}

    def audit(self, *, seconds=300):
        return self._json("audit", self._inventory_binding(), seconds=seconds)

    def verify_assets(self, descriptors):
        value = self._json("verify", {**self._inventory_binding(), "descriptors": list(descriptors)}, seconds=300)
        if value.get("verified") is not True:
            raise StorageError("remote evidence audit was not acknowledged")

    def verify_descriptor(self, row):
        self.verify_assets([row])
        return True

    def read_asset(self, row, *, maximum_bytes=MAXIMUM_CONTROL_BYTES, seconds=120):
        if type(row.get("bytes")) is not int or not 0 <= row["bytes"] <= min(maximum_bytes, MAXIMUM_CONTROL_BYTES):
            raise StorageError("metadata read exceeds local bound")
        output = io.BytesIO()
        with self._log("read") as log:
            bounded_output(self._argv("read", {**self._inventory_binding(), "descriptors": [row], "maximum_bytes": maximum_bytes}),
                           output, maximum_bytes=row["bytes"], seconds=seconds, log=log)
        data = output.getvalue()
        if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise StorageError("remote/local metadata hash mismatch")
        return data

    def fetch_asset(self, row, destination, *, maximum_bytes=MAXIMUM_CACHED_ASSET_BYTES):
        if type(row.get("bytes")) is not int or not 0 <= row["bytes"] <= min(maximum_bytes, MAXIMUM_CACHED_ASSET_BYTES):
            raise StorageError("single raw asset exceeds local cache bound")
        destination = Path(destination)
        reject_symlink_chain(destination)
        with destination.open("xb") as output, self._log("fetch") as log:
            bounded_output(self._argv("read", {**self._inventory_binding(), "descriptors": [row], "maximum_bytes": maximum_bytes}),
                           output, maximum_bytes=row["bytes"], seconds=300, log=log)
        if destination.stat().st_size != row["bytes"] or sha256_file(destination) != row["sha256"]:
            raise StorageError("remote/local raw asset hash mismatch; partial cache retained")
        return destination

    def retain_compact_receipts(self, *, seconds=300):
        deadline = time.monotonic() + seconds
        def remaining():
            value = deadline - time.monotonic()
            if value <= 0:
                raise TimeoutError("compact evidence retrieval deadline")
            return value
        inventory = self.audit(seconds=remaining())
        write_new(self.local_control_directory / "remote-retrieval-manifest.json", encoded(inventory))
        for row in inventory["assets"]:
            if row["path"] not in {"gpu-control.json", "collection/receipt.json", "collection/started.json"}:
                continue
            name = "remote-" + row["path"].replace("/", "-")
            write_new(self.local_control_directory / name, self.read_asset(row, seconds=remaining()))
        return inventory


SMOKE_PROGRAM = r'''
import hashlib,io,json,sys,tarfile
data=hashlib.shake_256(b'butterfly-exp477-ssh-storage-smoke-v1').digest(16*1048576)
files={'collection/batch-0000-profile-0.npz':data,'gpu-control.json':b'{"mode":"synthetic","passed":false}'}
rows=[{'path':n,'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()} for n,d in files.items()]
raw=json.dumps({'schema':'butterfly.symbolic-remote-assets.v1','assets':rows},sort_keys=True).encode()
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as a:
 for n,d in [('retrieval-manifest.json',raw),*files.items()]:
  i=tarfile.TarInfo(n);i.size=len(d);a.addfile(i,io.BytesIO(d))
'''


def storage_smoke(remote_directory, local_output_directory, *, helper_sha256):
    """Explicit target-free live entry point; no Runpod call or numerical data.

    Call only after authorization. Retains its new remote folder and one 16 MiB
    local synthetic cache file. Timing is Mac-to-prax only, not GPU throughput.
    """
    output = Path(local_output_directory)
    output.mkdir(mode=0o700, exist_ok=False)
    cpu = b"{}"
    store = SshEvidenceStore(remote_directory, local_control_directory=output)
    store.prepare({"cpu_control_sha256": hashlib.sha256(cpu).hexdigest()}, cpu, helper_sha256=helper_sha256)
    started = time.monotonic()
    transfer = store.receive([sys.executable, "-c", SMOKE_PROGRAM], seconds=120, progress=lambda _: None)
    uploaded = time.monotonic() - started
    finalized = store.finalize()
    if not finalized.get("retrieval_verified") or finalized.get("complete_raw_closure_verified"):
        raise StorageError("synthetic storage smoke must verify bytes without claiming a real collection")
    inventory = store.audit()
    row = next(row for row in inventory["assets"] if row["path"].endswith(".npz"))
    expected = hashlib.shake_256(b"butterfly-exp477-ssh-storage-smoke-v1").digest(16 * 1048576)
    if row["bytes"] != len(expected) or row["sha256"] != hashlib.sha256(expected).hexdigest():
        raise StorageError("synthetic payload inventory differs from deterministic expected bytes")
    started = time.monotonic()
    store.fetch_asset(row, output / "synthetic-cache.npz")
    downloaded = time.monotonic() - started
    rejected = False
    try:
        store.verify_descriptor({**row, "sha256": "0" * 64})
    except StorageError:
        rejected = True
    if not rejected:
        raise StorageError("synthetic changed-hash descriptor was not rejected")
    store.audit()
    result = {"schema": "butterfly.symbolic-ssh-storage-smoke.v1", "passed": True,
              "synthetic_payload_bytes": row["bytes"], "synthetic_payload_sha256": row["sha256"],
              "transfer": transfer, "upload_seconds": uploaded, "upload_bytes_per_second": transfer["bytes"] / uploaded,
              "download_seconds": downloaded, "download_bytes_per_second": row["bytes"] / downloaded,
              "mismatched_descriptor_rejected": rejected, "runpod_calls_performed": False,
              "scope": "deterministic high-entropy synthetic storage transport only; not Runpod end-to-end bandwidth, GPU qualification, or a scientific collection",
              "remote_storage_binding": store.binding}
    write_new(output / "storage-smoke.json", encoded(result))
    return result


def quiescence_smoke(directory, worker_program):
    """Linux-only owned parent/grandchild controls using the frozen worker literal.

    Caller must extract worker_program from the hash-verified frozen wrapper
    source (AST literal, no package import). No scientific or network operations.
    All output stays in a fresh nested directory under the authorized task root.
    """
    directory = Path(directory)
    if (sys.platform != "linux" or not directory.is_relative_to(BASE_DIRECTORY)
            or len(directory.parts) != len(Path(BASE_DIRECTORY).parts) + 2):
        raise StorageError("quiescence smoke requires Linux and one fresh task-nested directory")
    reject_symlink_chain(directory)
    directory.mkdir(mode=0o700, exist_ok=False)
    results = []
    for name in ("interrupted", "orphan"):
        case = directory / name
        subprocess.run([sys.executable, "-c", worker_program, "init", str(case)], check=True, timeout=10,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        (case / "source").mkdir()
        marker, owner = case / "writer-marker.txt", case / "writer-identity.json"
        writer = ("import json,os,pathlib,time; "
                  "raw=pathlib.Path('/proc/self/stat').read_text(); f=raw[raw.rfind(')')+2:].split(); "
                  f"pathlib.Path({str(owner)!r}).write_text(json.dumps({{'pid':os.getpid(),'start_ticks':f[19],"
                  "'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()})); "
                  f"p=pathlib.Path({str(marker)!r}); deadline=time.monotonic()+20\nwhile time.monotonic()<deadline: p.write_text(str(time.monotonic())); time.sleep(.03)\n")
        parent = "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c'," + repr(writer) + "]); time.sleep(" + ("30" if name == "interrupted" else ".2") + ")"
        spec = {"name": "collection", "seconds": 35, "steps": [{"name": "synthetic", "argv": [sys.executable, "-c", parent]}]}
        process = None
        with (case / "supervisor.log").open("xb") as log:
            try:
                process = subprocess.Popen([sys.executable, "-c", worker_program, "stage", str(case), json.dumps(spec)], stdout=log, stderr=log)
                deadline = time.monotonic() + 8
                while not marker.exists() and time.monotonic() < deadline:
                    time.sleep(.02)
                if not marker.exists():
                    raise StorageError("synthetic owned writer did not start")
                if name == "interrupted":
                    process.terminate()
                process.wait(timeout=15)
                quiet = subprocess.run([sys.executable, "-c", worker_program, "quiesce", str(case)], capture_output=True, timeout=30)
                write_new(case / "quiescence.stdout", quiet.stdout)
                write_new(case / "quiescence.stderr", quiet.stderr)
                if name == "interrupted":
                    if quiet.returncode or json.loads(quiet.stdout).get("quiescent") is not True:
                        raise StorageError("interrupted owned process group did not become quiescent")
                    before = marker.read_bytes(); time.sleep(.15)
                    if marker.read_bytes() != before:
                        raise StorageError("grandchild kept writing after quiescence")
                elif quiet.returncode == 0:
                    raise StorageError("orphaned writer group incorrectly accepted as quiescent")
                results.append({"case": name, "passed": True, "orphan_snapshot_refused": name == "orphan"})
            finally:
                if process is not None:
                    stop_process(process)
                if owner.exists():
                    record = json.loads(owner.read_bytes())
                    pid_path = Path('/proc') / str(record['pid']) / 'stat'
                    if pid_path.exists():
                        raw = pid_path.read_text(); fields = raw[raw.rfind(')')+2:].split()
                        if (fields[19] != record['start_ticks'] or Path('/proc/sys/kernel/random/boot_id').read_text().strip() != record['boot_id']):
                            raise StorageError("synthetic writer identity changed; cleanup signal refused")
                        if fields[0] != 'Z':
                            os.kill(record['pid'], signal.SIGKILL)
                            deadline = time.monotonic() + 3
                            while pid_path.exists() and time.monotonic() < deadline:
                                current = pid_path.read_text()
                                if current[current.rfind(')')+2:].split()[0] == 'Z':
                                    break
                                time.sleep(.02)
                # This retries only the read/cancel handshake after exact owned
                # synthetic-child cleanup, never a target solve or cloud create.
                final = subprocess.run([sys.executable, "-c", worker_program, "quiesce", str(case)], capture_output=True, timeout=30)
                write_new(case / "final-quiescence.json", encoded({"returncode": final.returncode, "stdout": final.stdout.decode(), "stderr": final.stderr.decode()}))
                if final.returncode:
                    raise StorageError("synthetic writer group cleanup could not be verified")
    result = {"schema": "butterfly.symbolic-quiescence-smoke.v1", "passed": True, "cases": results,
              "target_computation_performed": False, "network_calls_performed": False}
    write_new(directory / "receipt.json", encoded(result))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote", action="store_true", required=True)
    parser.add_argument("root")
    parser.add_argument("expected_sha256")
    parser.add_argument("action", choices=("receive", "finalize", "audit", "verify", "read"))
    parser.add_argument("payload")
    args = parser.parse_args(argv)
    result = remote_main(args.root, args.expected_sha256, args.action, json.loads(args.payload))
    if result is not None:
        sys.stdout.buffer.write(encoded(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

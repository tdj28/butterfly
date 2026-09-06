#!/usr/bin/env python3
"""Archive the exact completed EXP-479 CPU evidence, without GPU lifecycle fiction.

Prepare is local-only. Upload requires the hash of the preparation receipt and
a fresh task-owned prax child. Keep the verified tar remotely, without extracting
or executing its contents. Preserve all originals and failed/partial transfers.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import plistlib
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import uuid

from scripts import run_symbolic_center_pilot as pilot
from scripts import execute_symbolic_center_cloud as cloud
from scripts import symbolic_ssh_storage as storage

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "30f6c5b0aeaa4c9d8548bb2b0a60f802ebb096e2"
COLLECTION_SHA = "845e3cd783a8aee9a49a7db9b377515c45fe6bb6974ad9f0a857132e0b0b86da"
ANALYSIS_SHA = "4147ff20adefb6adf536137cb0a92809446ce66d40c20b6c00f909fa6235755f"
AUDIT_SHA = "94f7cd234fce93f0644f67d49b1d8d9887b6566266ab6df1b51610f00f2c18e4"
QUALIFICATION_SHA = "0a338530d18905bf84e57060161c0396d77bee30bd3cda6775d4d125ec62f90f"
MAX_BYTES = 8 * 1024**3
MAX_FILES = 7000  # CPU serial batches retain more files than the GPU protocol.
BASE = "/home/ubuntu/butterfly-research"


def safe_name(name):
    p = PurePosixPath(name)
    return bool(name and not p.is_absolute() and ".." not in p.parts and str(p) == name)


def describe(path, name):
    storage.reject_symlink_chain(path)
    if not Path(path).is_file() or not safe_name(name):
        raise ValueError("bounded regular evidence file required")
    return {"path": name, "bytes": Path(path).stat().st_size, "sha256": pilot.sha256_file(path)}


def pack(entries, output):
    rows = [describe(path, name) for name, path in entries]
    if (len(rows) > MAX_FILES or len({r["path"] for r in rows}) != len(rows)
            or any(r["path"] == "manifest.json" for r in rows)
            or sum(r["bytes"] for r in rows) > MAX_BYTES):
        raise ValueError("archive member count/size/uniqueness bound")
    manifest = {"schema": "butterfly.exp479-cpu-archive.v1", "source_commit": SOURCE,
                "assets": rows, "local_originals_retained": True}
    data = pilot.encoded_json(manifest)
    archive = output / "evidence.tar"
    with tarfile.open(archive, "x", format=tarfile.USTAR_FORMAT) as tar:
        info = tarfile.TarInfo("manifest.json")
        info.size, info.mode = len(data), 0o600
        tar.addfile(info, io.BytesIO(data))
        for row, (_, path) in zip(rows, entries, strict=True):
            info = tarfile.TarInfo(row["path"])
            info.size, info.mode = row["bytes"], 0o600
            with Path(path).open("rb") as stream:
                tar.addfile(info, stream)
    archive.chmod(0o600)
    verify_tar(archive, manifest)
    pilot.write_new_json(output / "manifest.json", manifest)
    return {"schema": "butterfly.exp479-cpu-archive-preparation.v1", "source_commit": SOURCE,
            "archive": describe(archive, "evidence.tar"),
            "manifest": describe(output / "manifest.json", "manifest.json"),
            "asset_count": len(rows), "uncompressed_bytes": sum(r["bytes"] for r in rows),
            "collection_receipt_sha256": COLLECTION_SHA, "analysis_receipt_sha256": ANALYSIS_SHA,
            "provider_calls": False, "local_originals_retained": True}


def verify_tar(path, manifest):
    expected = manifest["assets"]
    if len(expected) > MAX_FILES or sum(r["bytes"] for r in expected) > MAX_BYTES:
        raise ValueError("manifest exceeds bounds")
    with tarfile.open(path, "r:") as tar:
        members = iter(tar)
        first = next(members)
        if first.name != "manifest.json" or not first.isfile() or first.size > 4 * 1024**2:
            raise ValueError("invalid leading archive manifest")
        with tar.extractfile(first) as stream:
            if json.loads(stream.read()) != manifest:
                raise ValueError("archive manifest mismatch")
        for member, row in zip(members, expected, strict=True):
            if not member.isfile() or member.name != row["path"] or not safe_name(member.name) or member.size != row["bytes"]:
                raise ValueError("archive members differ from inventory")
            with tar.extractfile(member) as stream:
                if hashlib.file_digest(stream, "sha256").hexdigest() != row["sha256"]:
                    raise ValueError("archive member hash mismatch")


def prepare(output):
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    if shutil.disk_usage(output).free < MAX_BYTES + 512 * 1024**2:
        raise ValueError("insufficient local archival reserve")
    root = ROOT / "artifacts/EXP-479"
    paths = {"collection": root / "collection-30f6c5b", "analysis": root / "analysis-30f6c5b"}
    receipts = {}
    for key, sha in (("collection", COLLECTION_SHA), ("analysis", ANALYSIS_SHA)):
        path = paths[key] / "receipt.json"
        if pilot.sha256_file(path) != sha:
            raise ValueError("frozen terminal receipt hash mismatch")
        receipts[key] = json.loads(path.read_bytes())
    c, a = receipts["collection"], receipts["analysis"]
    if (c["status"] != "completed" or a["status"] != "completed" or not c["collection_passed"]
            or c["environment"]["gpu_used"] is not False or len(c["completed_candidate_ids"]) != 551
            or a["completed_candidate_ids"] != c["completed_candidate_ids"]):
        raise ValueError("complete CPU collection and analysis required")
    entries = []
    for key in paths:
        descriptors = ([m[k] for b in c["batches"] for m in b["profiles"] for k in ("raw", "metadata_file")]
                       if key == "collection" else [f for b in a["fit_batches"] for f in b["files"]])
        names = {"receipt.json", "started.json"}
        for row in descriptors:
            pilot.collection_file(paths[key], row)
            names.add(row["path"])
        if key == "collection":
            for batch in c["batches"]:
                for index, metadata in enumerate(batch["profiles"]):
                    name = f"batch-{batch['index']:04d}-profile-{index}-checkpoint.json"
                    if json.loads((paths[key] / name).read_bytes()) != {"candidate_ids": batch["candidate_ids"], "raw_metadata": metadata}:
                        raise ValueError("checkpoint differs from terminal collection")
                    names.add(name)
        else:
            names.add("wrapper.json")
        if {p.name for p in paths[key].iterdir()} != names:
            raise ValueError("unexpected or missing evidence files")
        entries.extend((key + "/" + name, paths[key] / name) for name in sorted(names))
    bound = [("audit.json", root / "audit-30f6c5b/audit.json", AUDIT_SHA),
             ("qualification.json", root / "qualification-30f6c5b/receipt.json", QUALIFICATION_SHA),
             ("cpu-control.json", ROOT / "artifacts/EXP-477/recovery-cpu-control-27a9bfd.json",
              "aca38d8df29e040563b57ccff74c29fdd2a7ca038dc1d0b5817665af4242e8f3"),
             ("candidates.json", ROOT / "artifacts/EXP-204/candidates.json", pilot.CANDIDATE_SHA256)]
    for name, path, sha in bound:
        if pilot.sha256_file(path) != sha:
            raise ValueError("frozen source/control/input hash mismatch")
        entries.append(("inputs/" + name, path))
    source = root / "source-30f6c5b"
    plan = source / "experiments/manifests/EXP-479-cpu-symbolic-center-pilot.json"
    pilot.source_binding(source, SOURCE, plan, plan.read_bytes())
    inventory = cloud.build_source_archive(source, SOURCE, output / "source.tar")
    pilot.write_new_json(output / "source-inventory.json", inventory)
    entries.extend((name, output / name) for name in ("source.tar", "source-inventory.json"))
    result = pack(entries, output)
    pilot.write_new_json(output / "preparation.json", result)
    return result


def remote_command(code, *args):
    return ["ssh", *storage.ssh_options(), "ubuntu@prax",
            shlex.join(["python3", "-c", code, *map(str, args)])]


def service_environment():
    # The local agent may authenticate SSH; its socket is never forwarded.
    environment = {"PATH": os.defpath, "PYTHONPATH": ".:python"}
    if os.environ.get("SSH_AUTH_SOCK"):
        environment["SSH_AUTH_SOCK"] = os.environ["SSH_AUTH_SOCK"]
    return environment


def upload(output, receipt_sha, remote):
    if not re.fullmatch(re.escape(BASE) + r"/exp479-[a-z0-9-]+", remote):
        raise ValueError("fresh task-owned prax child required")
    if pilot.sha256_file(output / "preparation.json") != receipt_sha:
        raise ValueError("preparation receipt hash mismatch")
    prepared = json.loads((output / "preparation.json").read_bytes())
    for key in ("archive", "manifest"):
        pilot.collection_file(output, prepared[key])
    verify_tar(output / "evidence.tar", json.loads((output / "manifest.json").read_bytes()))
    target = output / "upload.json"
    # Exclusive started receipt prevents an automatic retry into a partial destination.
    pilot.write_new_json(output / "upload-started.json", {"remote": remote, "preparation_sha256": receipt_sha})
    result = {"remote": remote, "passed": False, "local_originals_retained": True, "automatic_retry": False}
    try:
        size, sha = (prepared["archive"][key] for key in ("bytes", "sha256"))
        code = ("import pathlib,shutil,sys\np=pathlib.Path(sys.argv[1])\n"
                "if any(q.is_symlink() for q in [p,*p.parents]): raise ValueError('symlink refused')\n"
                "if shutil.disk_usage(p.parent).free <= int(sys.argv[2])+536870912: raise ValueError('disk reserve')\n"
                "p.mkdir(mode=0o700)")
        subprocess.run(remote_command(code, remote, size), check=True, timeout=60, capture_output=True)
        subprocess.run(["scp", *storage.ssh_options(), str(output / "evidence.tar"),
                        "ubuntu@prax:" + remote + "/evidence.tar"], check=True, timeout=7200, capture_output=True)
        code = ("import pathlib,hashlib,json,sys\np=pathlib.Path(sys.argv[1]); h=hashlib.sha256()\n"
                "with p.open('rb') as f:\n for b in iter(lambda:f.read(1048576),b''): h.update(b)\n"
                "if p.stat().st_size!=int(sys.argv[2]) or h.hexdigest()!=sys.argv[3]: raise ValueError('hash/size mismatch')\n"
                "if p.stat().st_mode & 0o777 != 0o600: raise ValueError('permissions')\n"
                "print(json.dumps({'bytes':p.stat().st_size,'sha256':h.hexdigest()}))")
        response = subprocess.run(remote_command(code, remote + "/evidence.tar", size, sha),
                                  check=True, timeout=180, capture_output=True, text=True)
        if pilot.sha256_file(output / "evidence.tar") != sha:
            raise ValueError("local archive changed during transfer")
        observed = json.loads(response.stdout)
        if observed != {"bytes": size, "sha256": sha}:
            raise ValueError("remote response hash/size mismatch")
        result.update(passed=True, archive=observed, remote_archive_verified=True)
    except Exception as error:
        result["failure"] = {"type": type(error).__name__, "message": "transfer failed; preserve local originals and any remote partial"}
    pilot.write_new_json(target, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("prepare", "upload"), default="prepare")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--preparation-sha256")
    parser.add_argument("--remote-dir")
    parser.add_argument("--launch-state", type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    storage.reject_symlink_chain(args.output_dir)
    if args.mode == "prepare":
        result = prepare(output)
    elif args.launch_state:
        environment = service_environment()
        subprocess.run(["ssh", *storage.ssh_options(), "ubuntu@prax", "true"],
                       env=environment, check=True, timeout=60, capture_output=True)
        state = args.launch_state.resolve()
        state.mkdir(parents=True, exist_ok=False, mode=0o700)
        label = "io.butterfly.exp479.archive." + uuid.uuid4().hex
        command = [str(Path(sys.executable).absolute()), "-m", "scripts.archive_exp479_cpu", "--mode", "upload",
                   "--output-dir", str(output), "--preparation-sha256", args.preparation_sha256,
                   "--remote-dir", args.remote_dir]
        with (state / "job.plist").open("xb") as stream:
            plistlib.dump({"Label": label, "ProgramArguments": ["/usr/bin/caffeinate", "-i", *command],
                "WorkingDirectory": str(ROOT), "EnvironmentVariables": environment,
                "RunAtLoad": True, "KeepAlive": False, "StandardOutPath": str(state / "stdout.log"),
                "StandardErrorPath": str(state / "stderr.log")}, stream)
        result = {"service": f"gui/{os.getuid()}/{label}", "command": command,
                  "wrapper_sha256": pilot.sha256_file(__file__), "automatic_restart": False}
        pilot.write_new_json(state / "launch.json", result)
        subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(state / "job.plist")], check=True)
    else:
        result = upload(output, args.preparation_sha256, args.remote_dir)
    print(json.dumps(result))
    return 0 if result.get("passed", True) else 2


if __name__ == "__main__":
    raise SystemExit(main())

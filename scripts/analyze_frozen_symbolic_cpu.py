#!/usr/bin/env python3
"""Audit/analyze EXP-479 using its immutable execution checkout, never refit code here.

This operational wrapper imports the frozen CPU preparation and unchanged pilot
analysis. It never integrates, changes thresholds, retries, or calls a provider.
Use separate fresh output directories for audit and analysis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import uuid


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def qualified_preparation(cpu, commit, qualification, qualification_sha256):
    if digest(qualification) != qualification_sha256:
        raise ValueError("CPU qualification hash mismatch")
    record = json.loads(Path(qualification).read_bytes())
    if (record.get("passed") is not True or record.get("source_commit") != commit
            or record.get("producer_sha256") != digest(cpu.__file__)):
        raise ValueError("CPU qualification source/producer/pass mismatch")
    prepared, _ = cpu.prepare(commit)
    prepared["input_hashes"]["cpu_adapter_qualification"] = qualification_sha256
    return prepared


def audit(cpu, prepared, directory, receipt_sha256):
    pilot = cpu.pilot
    assets = pilot.LocalCollectionAssets(directory)
    receipt = json.loads(assets.receipt_bytes(receipt_sha256))
    expected = [row["id"] for row in prepared["candidates"]]
    if (receipt.get("schema") != "butterfly.symbolic-center-collection.v1"
            or receipt.get("status") != "completed" or receipt.get("collection_passed") is not True
            or receipt.get("nomination_performed") is not False
            or receipt.get("uncompleted_candidate_ids") != []
            or receipt["completed_candidate_ids"] != expected
            or [name for b in receipt["batches"] for name in b["candidate_ids"]] != expected
            or receipt["manifest_sha256"] != prepared["manifest_sha256"]
            or receipt["input_hashes"] != prepared["input_hashes"]
            or receipt["source"]["commit"] != prepared["source"]["commit"]
            or receipt["environment"].get("gpu_used") is not False):
        raise ValueError("completed CPU collection/source/input binding mismatch")
    files, count, raw_bytes, failures = [], 0, 0, 0
    for batch in receipt["batches"]:
        if len(batch["profiles"]) != len(prepared["parent"]["profiles"]):
            raise ValueError("incomplete profile set")
        for metadata, profile in zip(batch["profiles"], prepared["parent"]["profiles"], strict=True):
            files.extend(metadata[key] for key in ("metadata_file", "raw"))
            assets.verify_assets(files[-2:])
            if (json.loads(assets.metadata_bytes(metadata["metadata_file"])) !=
                    {k: v for k, v in metadata.items() if k != "metadata_file"}
                    or metadata["validity_passed"] is not True or metadata["profile"] != profile
                    or metadata["candidate_ids"] != batch["candidate_ids"]
                    or "elapsed_cpu_seconds" not in metadata):
                raise ValueError("CPU metadata/profile/validity mismatch")
            with assets.materialize(metadata["raw"]) as path:
                raw = pilot.load_raw(path, batch["candidate_ids"], prepared["parent"])
                angles = raw["recorded_angles"]
                if len(angles) and min(angles) < prepared["manifest"]["validity"]["minimum_normalized_section_transversality"]:
                    raise ValueError("raw transversality gate failed")
                failures += int(raw["failed_counts"].sum())
            count += 1
            raw_bytes += metadata["raw"]["bytes"]
    assets.receipt_bytes(receipt_sha256)
    return {"collection_receipt_sha256": receipt_sha256, "candidate_count": len(expected),
            "profile_count": count, "raw_bytes": raw_bytes, "failed_integrations": failures,
            "files": files, "passed": True, "fitting_performed": False}


def launch(args):
    if args.mode != "analyze":
        raise ValueError("only analysis may use the durable launcher")
    if args.output_dir.exists():
        raise ValueError("analysis output must be fresh")
    state = args.launch_state.resolve()
    state.mkdir(parents=True, exist_ok=False, mode=0o700)
    command = [str(Path(sys.executable).absolute()), str(Path(__file__).resolve())]
    for option in ("source_directory", "source_commit", "qualification", "qualification_sha256",
                   "collection", "collection_sha256", "output_dir", "mode"):
        value = getattr(args, option)
        command.extend(["--" + option.replace("_", "-"), str(value.resolve() if isinstance(value, Path) else value)])
    label = "io.butterfly.exp479.analysis." + uuid.uuid4().hex
    service = f"gui/{os.getuid()}/{label}"
    plist = state / "job.plist"
    with plist.open("xb") as stream:
        plistlib.dump({"Label": label, "ProgramArguments": ["/usr/bin/caffeinate", "-i", *command],
            "WorkingDirectory": str(args.source_directory.resolve()),
            "EnvironmentVariables": {"PATH": os.defpath}, "RunAtLoad": True, "KeepAlive": False,
            "StandardOutPath": str(state / "stdout.log"), "StandardErrorPath": str(state / "stderr.log")}, stream)
    with (state / "launch.json").open("x") as stream:
        json.dump({"service": service, "wrapper_sha256": digest(__file__), "command": command,
                   "automatic_restart": False, "provider_calls": False}, stream, indent=2)
    subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(plist)], check=True)
    print(json.dumps({"service": service, "launched": True}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source-directory", "qualification", "collection", "output-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("source-commit", "qualification-sha256", "collection-sha256"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--mode", choices=("audit", "analyze"), default="audit")
    parser.add_argument("--launch-state", type=Path)
    args = parser.parse_args()
    source = args.source_directory.resolve()
    # An absolute external wrapper must not import the main checkout's packages.
    sys.path[:0] = [str(source), str(source / "python")]
    from scripts import run_symbolic_center_cpu as cpu
    if Path(cpu.__file__).resolve() != source / "scripts/run_symbolic_center_cpu.py" or cpu.pilot.ROOT != source:
        raise ValueError("modules did not load from the requested frozen checkout")
    def prepare():
        return qualified_preparation(cpu, args.source_commit, args.qualification, args.qualification_sha256)
    prepared = prepare()
    if args.launch_state:
        # Validate the terminal receipt now; the child repeats every full audit.
        cpu.pilot.LocalCollectionAssets(args.collection).receipt_bytes(args.collection_sha256)
        launch(args)
        return 0
    checked = audit(cpu, prepared, args.collection, args.collection_sha256)
    prepare()
    if args.mode == "audit":
        args.output_dir.mkdir(parents=True, exist_ok=False)
        cpu.pilot.write_new_json(args.output_dir / "audit.json", checked)
        print(json.dumps({k: v for k, v in checked.items() if k != "files"}))
        return 0
    result = cpu.pilot.analyze(prepared, args.collection, args.collection_sha256, args.output_dir,
                              source_recheck=prepare)
    cpu.pilot.write_new_json(args.output_dir / "wrapper.json", {
        "wrapper_sha256": digest(__file__), "frozen_source": args.source_commit,
        "collection_receipt_sha256": args.collection_sha256, "automatic_retry": False})
    print(json.dumps({"status": result["status"], "passed": result["passed"],
                      "nomination_result": result["nomination_result"]}))
    return 0 if result["status"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())

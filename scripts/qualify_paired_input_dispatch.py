#!/usr/bin/env python3
"""Run the isolated read-only input consumer on preserved, hash-bound evidence.

No new trajectory or return-map fit. Negative controls use fresh local copies;
the original EXP-479/480 data and earlier input-audit receipt stay unchanged.
"""
import argparse
import json
from pathlib import Path
import runpy
import shutil
import sys

from scripts.build_paired_runtime import ROOT, build
from butterfly.paired_input_package import build_package
from butterfly.paired_input_io import checked_input
from butterfly.paired_supervisor import StageLimits, supervise


CASES = ("correct", "wrong-input-digest", "changed-input", "extra-input", "missing-input", "missing-argument")
ERRORS = {"wrong-input-digest": "input hash mismatch", "missing-argument": "audit-inputs requires an explicit input package",
    **{name: "input package contains missing, extra or changed files" for name in ("changed-input", "extra-input", "missing-input")}}
PRIOR = {"path": "artifacts/EXP-481/capture-input-audit-02/receipt.json",
    "sha256": "a0bf343c4dc11a8e05b5359add8cbebff8e4d8c33fe0a7ee4cc196154d799e68"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.absolute()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    api = runpy.run_path(str(ROOT/"python/butterfly/_paired_startup.py"))
    prior = json.loads(checked_input(ROOT, PRIOR))
    runtime = build(output/"bundle", startup_guard_seconds=60.)
    inputs = build_package(ROOT/"experiments/manifests/EXP-481-paired-sampling-proposal.json", ROOT, output/"inputs")
    contract = api["load_contract"](output/"bundle", runtime["sha256"])
    config = {"kind": "EXP-481-sealed-input-audit", "runtime": runtime, "inputs": inputs, "prior_audit": PRIOR,
        "producer_sha256": api["sha256"](Path(__file__)), "cases": list(CASES), "target_trajectories_generated": 0}
    api["write_json"](output/"started.json", config)
    results = []
    for case in CASES:
        directory = output/case
        directory.mkdir()
        package = directory/"inputs"
        shutil.copytree(output/"inputs", package)
        digest = inputs["sha256"]
        if case == "wrong-input-digest": digest = "0"*64
        elif case == "changed-input":
            with (package/"artifacts/EXP-204/candidates.json").open("ab") as stream:
                stream.write(b"\n")
        elif case == "extra-input": (package/"extra.json").write_text("{}\n")
        elif case == "missing-input": (package/"artifacts/EXP-204/candidates.json").rename(directory/"withheld-candidates.json")
        evidence = directory/"evidence"
        evidence.mkdir()
        for name in ("worker.py", "startup.py"):
            if api["sha256"](output/"bundle"/name) != contract["source_files"][name]["sha256"]:
                raise ValueError("bootstrap changed before read-only audit spawn")
        argv = [sys.executable, "-I", "-S", "-B", "-X", "utf8=1", str(output/"bundle/worker.py"),
            "--contract-sha256", runtime["sha256"], "--output-dir", str(evidence), "--mode", "audit-inputs"]
        if case != "missing-argument":
            argv += ["--input-root", str(package), "--input-contract-sha256", digest]
        result = supervise(argv, cwd=directory, evidence_directory=directory, state_directory=directory/"supervisor",
            environment=api["canonical_environment"](), binding={"case": case, "runtime_sha256": runtime["sha256"], "input_sha256": digest},
            limits=StageLimits(60., 512*1024**2, 128*1024**2, 0, poll_seconds=.05, terminate_grace_seconds=.3))
        audit_path = evidence/"input-audit.json"
        passed = result["owned_group_cleanup_verified"]
        if case == "correct":
            audit = json.loads(audit_path.read_bytes()) if audit_path.exists() else None
            passed = (passed and result["status"] == "completed" and audit is not None
                and audit["audit"] == prior and audit["target_execution_authorized"] is False
                and audit["runtime_contract_sha256"] == runtime["sha256"] and audit["input_contract_sha256"] == inputs["sha256"]
                and not any(n.startswith(("scripts.", "torch", "triton")) for n in audit["loaded_modules"]))
        else:
            passed = (passed and result["status"] == "incomplete" and result["returncode"] != 0 and not audit_path.exists()
                and ERRORS[case] in (directory/"supervisor/stderr.log").read_text())
        row = {"case": case, "passed": bool(passed), "supervisor_status": result["status"],
            "returncode": result["returncode"], "input_audit_present": audit_path.exists(),
            "cleanup_verified": result["owned_group_cleanup_verified"], "expected_error": ERRORS.get(case)}
        results.append(row)
        print(json.dumps(row), flush=True)
    api["write_json"](output/"receipt.json", {"kind": config["kind"], "passed": all(r["passed"] for r in results),
        "configuration_sha256": api["sha256"](output/"started.json"), "cases": results, "files": api["inventory"](output),
        "target_trajectories_generated": 0, "target_execution_authorized": False,
        "scope": "same preserved references through the actual isolated read-only consumer; no new symbolic result"})
    return 0 if all(r["passed"] for r in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())

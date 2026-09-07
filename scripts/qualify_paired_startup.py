#!/usr/bin/env python3
"""Exercise the exact sealed worker and canonical environment, target-free.

All altered files are fresh task-owned control copies. No provider requests,
candidate inputs, numerical trajectory integrations or historical fits occur.
"""
import argparse
import json
from pathlib import Path
import runpy
import shutil
import sys

from scripts.build_paired_runtime import build, ROOT
from butterfly.paired_supervisor import StageLimits, supervise


CASES = ("correct", "missing-env", "wrong-env", "extra-env", "missing-source", "extra-source",
         "changed-source", "wrong-contract", "execute-refused")
ERRORS = {**{c: "worker environment differs from canonical contract" for c in CASES if c.endswith("-env")},
    **{c: "sealed runtime contains missing, extra or changed files" for c in CASES if c.endswith("-source")},
    "wrong-contract": "runtime contract differs from external digest",
    "execute-refused": "review-bound production phase dispatch is not implemented; target execution refused"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.absolute()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    api = runpy.run_path(str(ROOT/"python/butterfly/_paired_startup.py"))
    build_result = build(output/"bundle", startup_guard_seconds=30.)
    contract = api["load_contract"](output/"bundle", build_result["sha256"])
    api["write_json"](output/"started.json", {"kind": "EXP-481-sealed-startup-controls",
        "producer_sha256": api["sha256"](Path(__file__)), "contract": build_result,
        "cases": list(CASES), "target_trajectories_generated": 0})
    results = []
    for case in CASES:
        directory = output/case
        directory.mkdir()
        # The worker must not import from its unrelated current directory.
        (directory/"numpy.py").write_text('raise RuntimeError("unsealed CWD numpy imported")\n')
        (directory/"sitecustomize.py").write_text('raise RuntimeError("site hook executed")\n')
        bundle = directory/"bundle"
        shutil.copytree(output/"bundle", bundle)
        env = api["canonical_environment"]()
        expected = build_result["sha256"]
        if case == "missing-env": del env["OPENBLAS_NUM_THREADS"]
        elif case == "wrong-env": env["OMP_NUM_THREADS"] = "2"
        elif case == "extra-env": env["PAIRED_UNDECLARED_SETTING"] = "1"
        elif case == "missing-source": (bundle/"python/butterfly/models.py").rename(directory/"withheld-models.py")
        elif case == "extra-source": (bundle/"extra.py").write_text("# undeclared synthetic control\n")
        elif case == "changed-source":
            with (bundle/"python/butterfly/models.py").open("ab") as stream:
                stream.write(b"\n# changed synthetic control\n")
        elif case == "wrong-contract": expected = "0"*64
        # Controller binds the two executable bootstrap files independently
        # before running them. The worker cannot authenticate its own loader.
        for name in ("worker.py", "startup.py"):
            if api["sha256"](bundle/name) != contract["source_files"][name]["sha256"]:
                raise ValueError("bootstrap differs before spawn")
        evidence = directory/"evidence"
        evidence.mkdir()
        command = [sys.executable, "-I", "-S", "-B", "-X", "utf8=1", str(bundle/"worker.py"),
            "--contract-sha256", expected, "--output-dir", str(evidence),
            "--mode", "execute" if case == "execute-refused" else "startup"]
        result = supervise(command, cwd=directory, evidence_directory=directory,
            state_directory=directory/"supervisor", environment=env,
            binding={"kind": "synthetic-startup", "case": case, "contract_sha256": expected},
            limits=StageLimits(30., 512*1024**2, 64*1024**2, 0, poll_seconds=.05, terminate_grace_seconds=.3))
        path = evidence/"startup.json"
        startup = json.loads(path.read_bytes()) if path.exists() else None
        if case == "correct":
            passed = (result["status"] == "completed" and startup is not None
                and startup["environment"] == contract["environment"] and startup["guard_alive"]
                and startup["target_execution_authorized"] is False
                and all(startup["flags"].values())
                and "butterfly.paired_campaign" in startup["loaded_modules"]
                and "butterfly.return_map" not in startup["loaded_modules"])
        elif case == "execute-refused":
            passed = (result["status"] == "incomplete" and result["returncode"] != 0
                and startup is not None and startup["target_execution_authorized"] is False)
        else:
            passed = result["status"] == "incomplete" and result["returncode"] != 0 and startup is None
        expected_failure = None if case == "correct" else ERRORS[case]
        if expected_failure is not None:
            passed = passed and expected_failure in (directory/"supervisor/stderr.log").read_text()
        passed = bool(passed and result["owned_group_cleanup_verified"])
        row = {"case": case, "passed": passed, "supervisor_status": result["status"],
            "returncode": result["returncode"], "startup_receipt_present": startup is not None,
            "worker_cleanup_verified": result["owned_group_cleanup_verified"], "target_trajectories_generated": 0}
        row["expected_failure"] = expected_failure
        results.append(row)
        print(json.dumps(row), flush=True)
    inventory = api["inventory"](output)
    api["write_json"](output/"receipt.json", {"kind": "EXP-481-sealed-startup-controls",
        "passed": all(r["passed"] for r in results), "cases": results, "contract": build_result,
        "files": inventory, "target_trajectories_generated": 0,
        "scope": "exact target-free bootstrap/import/environment path; review-bound phase dispatcher still pending"})
    return 0 if all(r["passed"] for r in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())

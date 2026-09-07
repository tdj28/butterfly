#!/usr/bin/env python3
"""Isolated synthetic runtime controls; never loads target research inputs.

Worker roles install the pure-stdlib parent guard before scientific imports.
Only the named analytic circle and injected process-loss cases are available.
This qualifies component wiring, not the future source/review authorization CLI.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CASES = ("complete-dop853", "complete-radau", "wall-loss", "parent-loss")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--role", choices=("controller", "supervisor", "worker"), default="controller")
    parser.add_argument("--case", choices=CASES)
    args = parser.parse_args()
    output = args.output_dir.absolute()
    if args.role != "controller" and args.case is None:
        parser.error("a fixed synthetic case is required")
    guard = None
    before = "numpy" in sys.modules or "butterfly" in sys.modules
    if args.role == "worker":
        namespace = runpy.run_path(str(ROOT/"python/butterfly/_process_guard.py"))
        guard = namespace["install_parent_guard"](20.)
        if before:
            raise ValueError("scientific imports preceded guard installation")
    sys.path[:0] = [str(ROOT), str(ROOT/"python")]
    import numpy as np
    from butterfly.paired_adaptive_journal import AdaptiveJournal, audit_adaptive_journal, record_adaptive
    from butterfly.paired_supervisor import StageLimits, process_table, supervise
    from butterfly.paired_sections import CaptureSection
    from butterfly.paired_sampling import SECTIONS
    from butterfly.poincare import PoincareSection
    from scripts.qualify_paired_sampling import descriptor, write
    binding = {"kind": "EXP-481-synthetic-runtime", "case": args.case,
        "producer_sha256": descriptor(Path(__file__))["sha256"],
        "guard_sha256": descriptor(ROOT/"python/butterfly/_process_guard.py")["sha256"]}
    env = {"PATH": os.defpath, "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1"}
    if args.role == "worker":
        write(output/"worker-startup.json", {"guard_alive": guard.is_alive(), "scientific_imports_before_guard": before,
            "pid": os.getpid(), "binding": binding, "isolated": bool(sys.flags.isolated),
            "dont_write_bytecode": bool(sys.dont_write_bytecode), "environment_keys": sorted(os.environ)})
        specs = {SECTIONS[0]: CaptureSection(PoincareSection((0, 1, 0), 0, -1),
            np.array([[-15., 0, .01]]), (0, 2), (15., .01), .0002, 1),
            SECTIONS[1]: CaptureSection(PoincareSection((1, 0, 0), 0, 1),
            np.array([[0, -15., .01]]), (1, 2), (15., .01), .0002, 1)}
        config = dict(method="Radau" if args.case == "complete-radau" else "DOP853", horizon=7.,
            rtol=1e-10, atol=1e-12, max_step=.01, state_scales=[15., 15., .01], gate_margin=1e-5,
            angle_margin=1e-6, escape_radius=1e6, maximum_steps=60000, maximum_events=2048,
            maximum_field_evaluations=1000000, recording_interval=500)
        if args.case in ("wall-loss", "parent-loss"):
            original = AdaptiveJournal.append
            def pause(self, record):
                original(self, record)
                time.sleep(30)  # injected only after the first fsynced snapshot
            AdaptiveJournal.append = pause
        rhs = lambda x: np.column_stack((-x[:, 1], x[:, 0], np.zeros(len(x))))
        _, audit = record_adaptive(rhs, [15., 0, .01], 901, specs, config, directory=output/"journal", binding=binding)
        return 0 if audit["status"] == "completed" else 2
    if args.role == "supervisor":
        command = [sys.executable, "-I", "-B", str(Path(__file__)), "--role", "worker",
                   "--case", args.case, "--output-dir", str(output)]
        result = supervise(command, cwd=ROOT, evidence_directory=output, state_directory=output/"supervisor",
            environment=env, binding=binding, limits=StageLimits(5. if args.case == "wall-loss" else 15.,
                256*1024**2, 64*1024**2, 0, poll_seconds=.05, terminate_grace_seconds=.3))
        return 0 if result["status"] == "completed" else 2
    output.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), *[ROOT/f"python/butterfly/{name}.py" for name in
        ("_process_guard", "paired_supervisor", "paired_adaptive_journal", "paired_adaptive", "paired_journal", "paired_sections")]]
    write(output/"started.json", {"kind": "EXP-481-synthetic-runtime", "target_trajectories": 0,
        "cases": list(CASES), "source_sha256": {str(p.relative_to(ROOT)): descriptor(p)["sha256"] for p in sources},
        "environment": env, "isolated_worker": True, "snapshot_interval_steps": 500,
        "scope": "synthetic component wiring only; full production authorization/startup remains incomplete"})
    results = []
    for case in CASES:
        directory = output/case
        directory.mkdir()
        command = [sys.executable, "-I", "-B", str(Path(__file__)), "--role", "supervisor", "--case", case,
                   "--output-dir", str(directory)]
        with (directory/"controller-stdout.log").open("xb") as stdout, (directory/"controller-stderr.log").open("xb") as stderr:
            process = subprocess.Popen(command, env=env, cwd=ROOT, stdout=stdout, stderr=stderr)
            try:
                if case == "parent-loss":
                    deadline = time.monotonic()+15
                    while not (directory/"journal/journal-000000.json").exists():
                        if process.poll() is not None or time.monotonic() > deadline:
                            raise RuntimeError("parent-loss control failed to record first snapshot")
                        time.sleep(.02)
                    process.kill()
                returncode = process.wait(timeout=25)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=5)
        ownership = json.loads((directory/"supervisor/ownership.json").read_bytes())
        child = ownership["pid"]
        deadline = time.monotonic()+5
        while time.monotonic() < deadline:
            row = process_table().get(child)
            if row is None or row["state"].startswith("Z"):
                break
            time.sleep(.02)
        else:
            raise RuntimeError("synthetic worker cleanup not verified")
        audit = audit_adaptive_journal(directory/"journal")
        startup = json.loads((directory/"worker-startup.json").read_bytes())
        complete = case.startswith("complete-")
        passed = (audit["status"] == ("completed" if complete else "incomplete")
            and audit["records"] >= 1 and startup["guard_alive"] and not startup["scientific_imports_before_guard"]
            and startup["isolated"] and startup["dont_write_bytecode"] and (returncode == 0 if complete else returncode != 0)
            and all(e["accepted"].any() for e in audit["snapshot"]["events"].values())
            and np.isfinite(audit["snapshot"]["capture_times"]).all())
        results.append({"case": case, "passed": bool(passed), "controller_returncode": returncode,
            "journal_status": audit["status"], "durable_time": audit["durable_time"], "records": audit["records"],
            "accepted_events_retained": {name: int(e["accepted"].sum()) for name, e in audit["snapshot"]["events"].items()},
            "both_capture_labels_retained": bool(np.isfinite(audit["snapshot"]["capture_times"]).all()),
            "worker_stopped": True, "supervisor_terminal_exists": (directory/"supervisor/terminal.json").exists()})
        print(json.dumps(results[-1]), flush=True)
    files = [descriptor(p) | {"path": str(p.relative_to(output))} for p in sorted(output.rglob("*")) if p.is_file()]
    receipt = {"kind": "EXP-481-synthetic-runtime", "passed": all(r["passed"] for r in results),
        "target_trajectories": 0, "configuration": descriptor(output/"started.json"), "cases": results, "files": files}
    write(output/"receipt.json", receipt)
    return 0 if receipt["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

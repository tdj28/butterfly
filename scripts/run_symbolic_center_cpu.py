#!/usr/bin/env python3
"""EXP-479: CPU-reference successor; no provider access or desired-word search."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import shutil
import time

import numpy as np

from butterfly import RosslerParameters, barrio_rossler_section, sprinkler_survivors
from scripts.gpu_scan_jones_two_critical_residuals import _initial_ensemble
from scripts import run_symbolic_center_pilot as pilot
from scripts.qualify_symbolic_gpu_records import compare_records, validate_control, parent_design

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "experiments/manifests/EXP-479-cpu-symbolic-center-pilot.json"


def integrate_cpu(candidates, *, dt, horizon, checkpoints, midpoint, ensemble,
                  capture, gpu_options, section_name, section_code, target_cycle_state_count):
    if section_name != "barrio_positive_x" or section_code != 1 or target_cycle_state_count != 8:
        raise ValueError("CPU successor is restricted to the frozen Barrio eight-phase design")
    started = time.perf_counter()
    initial = _initial_ensemble(candidates, ensemble)
    records, counts, failures = [], [], []
    for index, candidate in enumerate(candidates):
        parameters = RosslerParameters(**candidate["parameters"])
        result = sprinkler_survivors(parameters, initial[index], barrio_rossler_section(parameters),
            candidate["section_states"], dt=dt, horizon=horizon,
            capture_coordinate_axes=(1, 2), capture_coordinate_scales=tuple(capture["coordinate_scales"]),
            capture_radius=capture["radius"], required_capture_crossings=capture["required_crossings"],
            checkpoint_times=checkpoints, midpoint_window=midpoint, escape_radius=ensemble["escape_radius"])
        states, times = [], []
        for seed in result.survivor_ids:
            selected = result.midpoint_trajectory_ids == seed
            order = np.argsort(result.midpoint_times[selected])
            states.append(result.midpoint_states[selected][order])
            times.append(result.midpoint_times[selected][order])
        records.append({"seed_ids": result.survivor_ids, "states": states, "times": times})
        counts.append(result.survivor_counts)
        failures.append(np.count_nonzero(result.failed))
    return {"records": records, "survivor_counts": np.asarray(counts, dtype=int),
            "failed_counts": np.asarray(failures, dtype=int),
            "elapsed_seconds": time.perf_counter()-started}


def prepare(commit):
    plan = json.loads(PLAN.read_bytes())
    if (plan["experiment_id"] != "EXP-479" or plan["execution"] != {
            "batch_size": 1, "maximum_wall_seconds": 43200}
            or plan["backend"] != "existing_numpy_sprinkler_reference"):
        raise ValueError("CPU execution contract differs from this successor")
    prepared = pilot.prepare(ROOT / plan["parent_manifest"], commit)
    parent_hash = prepared["manifest_sha256"]
    prepared["source"] = pilot.source_binding(ROOT, commit, PLAN, PLAN.read_bytes())
    prepared["manifest"] = dict(prepared["manifest"], experiment_id=plan["experiment_id"],
        execution={**prepared["manifest"]["execution"], **plan["execution"]},
        interpretation=plan["interpretation"])
    prepared["manifest_sha256"] = pilot.sha256_file(PLAN)
    prepared["input_hashes"]["gpu_parent_manifest"] = parent_hash
    return prepared, plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=("preflight", "qualify", "collect"), default="preflight")
    parser.add_argument("--cpu-control", type=Path)
    parser.add_argument("--cpu-control-sha256")
    parser.add_argument("--qualification", type=Path)
    parser.add_argument("--qualification-sha256")
    args = parser.parse_args()
    prepared, plan = prepare(args.source_commit)
    if shutil.disk_usage(ROOT).free < plan["minimum_free_bytes"]:
        parser.error("insufficient local archive reserve")
    if args.mode == "preflight":
        print(json.dumps({"prepared": True, "candidate_count": len(prepared["candidates"])}))
        return 0
    if args.mode == "qualify":
        if args.cpu_control is None or pilot.sha256_file(args.cpu_control) != args.cpu_control_sha256:
            parser.error("exact CPU control required")
        reference = json.loads(args.cpu_control.read_bytes())
        if reference.get("mode") != "cpu" or reference.get("passed") is not True:
            parser.error("passing CPU reference required")
        control = reference["control"]
        validate_control(control, parent_design())
        args.output_dir.mkdir(parents=True, exist_ok=False)
        rows = []
        config = control["config"]
        for profile in control["profiles"]:
            run = integrate_cpu([control["candidate"]], dt=profile["dt"],
                horizon=config["ensemble"]["horizon"], checkpoints=config["ensemble"]["checkpoint_times"],
                midpoint=config["ensemble"]["midpoint_window"], ensemble=config["ensemble"],
                capture=config["capture"], gpu_options=config["gpu"], section_name="barrio_positive_x",
                section_code=1, target_cycle_state_count=8)
            rows.append({"dt": profile["dt"], **compare_records(profile, run)})
        result = {"source_commit": args.source_commit, "producer_sha256": pilot.sha256_file(Path(__file__)),
                  "cpu_control_sha256": args.cpu_control_sha256, "profiles": rows,
                  "passed": all(row["passed"] for row in rows),
                  "scope": "adapter equivalence to existing CPU reference; not independent solver replication"}
        pilot.write_new_json(args.output_dir / "receipt.json", result)
        print(json.dumps(result))
        return 0 if result["passed"] else 2
    if args.qualification is None or pilot.sha256_file(args.qualification) != args.qualification_sha256:
        parser.error("hash-bound CPU adapter qualification required")
    qualification = json.loads(args.qualification.read_bytes())
    if (qualification.get("passed") is not True or qualification.get("source_commit") != args.source_commit
            or qualification.get("producer_sha256") != pilot.sha256_file(Path(__file__))):
        parser.error("passing source-matched qualification required")
    prepared["input_hashes"]["cpu_adapter_qualification"] = args.qualification_sha256
    result = pilot.collect(prepared, args.output_dir, source_recheck=lambda: prepare(args.source_commit),
        integrator=integrate_cpu, duration_backend="cpu",
        runtime_environment={"backend": plan["backend"], "python": platform.python_version(),
                             "numpy": np.__version__, "gpu_used": False})
    print(json.dumps({"status": result["status"], "collection_passed": result["collection_passed"]}))
    return 0 if result["collection_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

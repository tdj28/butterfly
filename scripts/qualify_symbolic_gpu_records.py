#!/usr/bin/env python3
"""EXP-477 deployment control: locally prepared CPU records, then GPU parity.

No Jones word or EXP-477 candidate is used. The known EXP-196 anchor is a
deployment control, not a new dynamical finding. No partition is fitted here.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import platform
import tempfile
import time

import numpy as np

from butterfly import RosslerParameters, barrio_rossler_section, sprinkler_survivors
from scripts.qualify_gpu_barrio_section import _anchor_cycle
from scripts.gpu_scan_jones_two_critical_residuals import _initial_ensemble, integrate_gpu
from scripts.run_symbolic_center_pilot import archive_raw, source_binding, sha256_file, utc_now, write_new_json

ROOT = Path(__file__).resolve().parents[1]
PARENT = "experiments/manifests/EXP-196-gpu-barrio-section-parity.json"
PARENT_HASH = "4604912140b520d7a6485688b966ca75b3ede15439c4837e5b906b572783ba19"
STATE_ATOL = 1e-6
TIME_ATOL = 1e-6
MAXIMUM_PROJECTED_COLLECTION_SECONDS = 2400.0


def parent_design():
    raw = (ROOT / PARENT).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PARENT_HASH:
        raise ValueError("qualification parent hash mismatch")
    return json.loads(raw)


def integrate(candidate, config, dt):
    return integrate_gpu(
        [candidate], dt=dt, horizon=config["ensemble"]["horizon"],
        checkpoints=config["ensemble"]["checkpoint_times"],
        midpoint=config["ensemble"]["midpoint_window"], ensemble=config["ensemble"],
        capture=config["capture"], gpu_options=config["gpu"],
        section_name="barrio_positive_x", section_code=1, target_cycle_state_count=8,
    )


def make_cpu_control(parent):
    candidate = _anchor_cycle(parent)
    config = copy.deepcopy(parent)
    config["ensemble"].update(x_count=8, z_count=8)
    initial = _initial_ensemble([candidate], config["ensemble"])[0]
    parameters = RosslerParameters(**candidate["parameters"])
    rows = []
    for profile in config["profiles"]:
        result = sprinkler_survivors(
            parameters, initial, barrio_rossler_section(parameters), candidate["section_states"],
            dt=profile["dt"], horizon=config["ensemble"]["horizon"],
            capture_coordinate_axes=(1, 2), capture_coordinate_scales=(15.0, 0.01),
            capture_radius=config["capture"]["radius"],
            required_capture_crossings=config["capture"]["required_crossings"],
            checkpoint_times=config["ensemble"]["checkpoint_times"],
            midpoint_window=config["ensemble"]["midpoint_window"],
            escape_radius=config["ensemble"]["escape_radius"],
        )
        records = []
        for seed in result.survivor_ids:
            selected = result.midpoint_trajectory_ids == seed
            order = np.argsort(result.midpoint_times[selected])
            records.append({"seed_id": int(seed),
                            "times": result.midpoint_times[selected][order].tolist(),
                            "states": result.midpoint_states[selected][order].tolist()})
        if np.any(result.failed) or not records or not any(row["times"] for row in records):
            raise ValueError("CPU deployment control failed or retained no event records")
        rows.append({"dt": profile["dt"], "records": records,
                     "survivor_counts": result.survivor_counts.tolist(), "failed_count": 0})
    return {"candidate": candidate, "config": config, "profiles": rows}


def compare_records(cpu, gpu):
    """No tolerance can rescue differing survivors, counts, or event cardinality."""
    checks = {
        "structure": False, "seed_identity": False, "survivor_counts": False, "no_failures": False,
        "matching_event_counts": False, "no_saturation": False, "finite": False,
    }
    state_max = time_max = None
    try:
        if len(gpu["records"]) != 1:
            raise ValueError("expected exactly one GPU candidate record")
        record = gpu["records"][0]
        cpu_ids = np.asarray([row["seed_id"] for row in cpu["records"]])
        gpu_ids = np.asarray(record["seed_ids"])
        cpu_counts, gpu_counts = np.asarray(cpu["survivor_counts"]), np.asarray(gpu["survivor_counts"])
        gpu_failures = np.asarray(gpu["failed_counts"])
        if (cpu_ids.ndim != 1 or gpu_ids.ndim != 1 or cpu_ids.dtype.kind not in "iu" or gpu_ids.dtype.kind not in "iu"
                or len(set(cpu_ids.tolist())) != len(cpu_ids) or len(set(gpu_ids.tolist())) != len(gpu_ids)
                or np.any(cpu_ids < 0) or np.any(gpu_ids < 0)
                or len(record["states"]) != len(gpu_ids) or len(record["times"]) != len(gpu_ids)
                or cpu_counts.ndim != 1 or len(cpu_counts) == 0 or gpu_counts.shape != (1, len(cpu_counts))
                or cpu_counts.dtype.kind not in "iu" or gpu_counts.dtype.kind not in "iu"
                or np.any(cpu_counts < 0) or np.any(gpu_counts < 0)
                or gpu_failures.shape != (1,) or gpu_failures.dtype.kind not in "iu"
                or type(cpu["failed_count"]) is not int
                or cpu_counts[-1] != len(cpu_ids) or gpu_counts[0, -1] != len(gpu_ids)):
            raise ValueError("malformed count, identity, or record arrays")
        checks["structure"] = True
        checks["seed_identity"] = cpu_ids.tolist() == gpu_ids.tolist()
        checks["survivor_counts"] = cpu_counts.tolist() == gpu_counts[0].tolist()
        checks["no_failures"] = cpu["failed_count"] == 0 and gpu_failures[0] == 0
        if checks["seed_identity"]:
            states, times = [], []
            same_counts = True
            for row, gpu_states, gpu_times in zip(cpu["records"], record["states"], record["times"], strict=True):
                ct, gt = np.asarray(row["times"], dtype=float), np.asarray(gpu_times, dtype=float)
                cs, gs = np.asarray(row["states"], dtype=float), np.asarray(gpu_states, dtype=float)
                if ct.shape == (0,) and cs.shape == (0,):
                    cs = cs.reshape(0, 3)
                if ct.ndim != 1 or gt.ndim != 1 or cs.shape != (len(ct), 3) or gs.shape != (len(gt), 3):
                    raise ValueError("event states/times must have exact matching dimensions")
                same_counts &= len(ct) == len(gt)
                if len(ct):
                    states.append((cs, gs))
                    times.append((ct, gt))
            checks["matching_event_counts"] = same_counts
            checks["no_saturation"] = all(len(value) < 32 for value in record["times"])
            if same_counts:
                checks["finite"] = bool(states) and all(np.all(np.isfinite(a)) and np.all(np.isfinite(b))
                                                         for a, b in states + times)
                if checks["finite"]:
                    state_max = max(float(np.max(np.abs(a - b))) for a, b in states)
                    time_max = max(float(np.max(np.abs(a - b))) for a, b in times)
    except (KeyError, IndexError, ValueError, TypeError):
        checks["structure"] = False
    checks["state_parity"] = state_max is not None and state_max <= STATE_ATOL
    checks["time_parity"] = time_max is not None and time_max <= TIME_ATOL
    return {"checks": checks, "passed": all(checks.values()),
            "maximum_absolute_state_difference": state_max,
            "maximum_absolute_time_difference": time_max}


def validate_control(control, parent):
    """Bind the transferred CPU control to both frozen deployment profiles."""
    expected = copy.deepcopy(parent)
    expected["ensemble"].update(x_count=8, z_count=8)
    if control["config"] != expected:
        raise ValueError("CPU control configuration differs from the frozen 8-by-8 design")
    if [row["dt"] for row in control["profiles"]] != [row["dt"] for row in parent["profiles"]]:
        raise ValueError("CPU control must contain both frozen step profiles in order")
    candidate = control["candidate"]
    states = np.asarray(candidate["section_states"], dtype=float)
    if candidate["parameters"] != parent["anchor"]["parameters"] or states.shape != (8, 3) or not np.all(np.isfinite(states)):
        raise ValueError("CPU control must preserve the finite eight-phase known anchor")
    if any(not row["records"] for row in control["profiles"]):
        raise ValueError("CPU control profiles must contain survivor records")


def gpu_control(control):
    validate_control(control, parent_design())
    profiles = []
    for cpu in control["profiles"]:
        gpu = integrate(control["candidate"], control["config"], cpu["dt"])
        parity = compare_records(cpu, gpu)
        profiles.append({"dt": cpu["dt"], **parity})
    if not all(row["passed"] for row in profiles):
        return {"profiles": profiles, "passed": False, "benchmark": None}
    # Batch-shaped timing uses eight copies of the known anchor, not targets.
    config = copy.deepcopy(control["config"])
    config["ensemble"].update(x_count=128, z_count=64)
    timings = []
    components = []
    for _repeat in range(2):
        candidates = [{**control["candidate"], "id": f"known-anchor-copy-{index}"} for index in range(8)]
        started = time.perf_counter()
        result = integrate_gpu(
            candidates, dt=0.005, horizon=200.0,
            checkpoints=config["ensemble"]["checkpoint_times"],
            midpoint=config["ensemble"]["midpoint_window"], ensemble=config["ensemble"],
            capture=config["capture"], gpu_options=config["gpu"],
            section_name="barrio_positive_x", section_code=1, target_cycle_state_count=8,
        )
        if np.any(result["failed_counts"]):
            raise ValueError("timing control suffered integration failures")
        integrated = time.perf_counter()
        with tempfile.TemporaryDirectory(prefix="butterfly-known-anchor-timing-") as directory:
            metadata = archive_raw(
                Path(directory), "known-anchor", candidates, result, {"dt": 0.005},
                {**config, "section": {"kind": "barrio_positive_x"}},
                {"minimum_normalized_section_transversality": 0.0},
            )
            if not metadata["validity_passed"]:
                raise ValueError("timing control raw records are nonfinite or saturated")
            elapsed = time.perf_counter() - started
            components.append({"kernel_seconds": float(result["elapsed_seconds"]),
                               "integration_call_wall_seconds": integrated - started,
                               "raw_preservation_wall_seconds": elapsed - (integrated - started),
                               "raw_bytes": metadata["raw"]["bytes"]})
        if not np.isfinite(elapsed) or elapsed <= 0:
            raise ValueError("invalid GPU collection timing")
        timings.append(elapsed)
    # Slower complete batch, 69 batches, 1.5 step-work factor, 2x margin.
    # This is a workload projection, not a guaranteed completion time.
    projected = max(timings) * 69 * 1.5 * 2
    if not np.isfinite(projected) or projected <= 0:
        raise ValueError("invalid GPU timing")
    return {"profiles": profiles,
            "benchmark": {"batch_eight_seconds": timings,
                          "timing_definition": "wall time of integration, host retrieval, and compressed raw NPZ/metadata/hash preservation; temporary-file cleanup excluded",
                          "components": components,
                          "projected_collection_seconds_with_margin": projected,
                          "maximum_projected_collection_seconds": MAXIMUM_PROJECTED_COLLECTION_SECONDS},
            "passed": projected <= MAXIMUM_PROJECTED_COLLECTION_SECONDS}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("cpu", "gpu"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-inventory", type=Path)
    parser.add_argument("--source-inventory-sha256")
    parser.add_argument("--cpu-control", type=Path)
    parser.add_argument("--cpu-control-sha256")
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        parser.error("output already exists")
    source = source_binding(ROOT, args.source_commit, ROOT / PARENT, (ROOT / PARENT).read_bytes(),
                            inventory=args.source_inventory, inventory_sha256=args.source_inventory_sha256)
    receipt = {"schema": "butterfly.symbolic-gpu-deployment-control.v1",
               "started_utc": utc_now(),
               "source": source, "parent_sha256": PARENT_HASH, "mode": args.mode,
               "qualification_script_sha256": sha256_file(Path(__file__)),
               "python": platform.python_version(), "state_atol": STATE_ATOL,
               "time_atol": TIME_ATOL, "passed": False}
    try:
        parent = parent_design()
        if args.mode == "cpu":
            receipt["control"] = make_cpu_control(parent)
            receipt["passed"] = True
        else:
            if args.cpu_control is None or sha256_file(args.cpu_control) != args.cpu_control_sha256:
                raise ValueError("CPU control hash mismatch")
            cpu = json.loads(args.cpu_control.read_bytes())
            if (cpu.get("schema") != receipt["schema"] or cpu.get("parent_sha256") != PARENT_HASH
                    or cpu.get("state_atol") != STATE_ATOL or cpu.get("time_atol") != TIME_ATOL
                    or cpu.get("qualification_script_sha256") != receipt["qualification_script_sha256"]
                    or cpu.get("mode") != "cpu" or cpu.get("passed") is not True
                    or cpu["source"]["commit"] != args.source_commit):
                raise ValueError("CPU control is not passing and source-matched")
            receipt["cpu_control_sha256"] = args.cpu_control_sha256
            receipt.update(gpu_control(cpu["control"]))
        source_binding(ROOT, args.source_commit, ROOT / PARENT, (ROOT / PARENT).read_bytes(),
                       inventory=args.source_inventory, inventory_sha256=args.source_inventory_sha256)
    except Exception as error:
        receipt["passed"] = False
        receipt["failure"] = {"type": type(error).__name__, "message": str(error)}
    receipt["finished_utc"] = utc_now()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_new_json(args.output, receipt)
    print(json.dumps({"passed": receipt["passed"], "mode": args.mode}))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

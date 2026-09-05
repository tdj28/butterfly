#!/usr/bin/env python3
"""Target-free CPU fallback benchmark using a previously frozen known anchor.

No EXP-477 search candidates or desired symbolic words are opened. This measures
the existing NumPy reference at the production seed count; it does not authorize
or impersonate the frozen CUDA collection. Raw reference outputs are retained.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import platform
import subprocess
import time

import numpy as np

from butterfly import RosslerParameters, barrio_rossler_section, sprinkler_survivors
from scripts.gpu_scan_jones_two_critical_residuals import _initial_ensemble
from scripts.run_symbolic_center_pilot import sha256_file, write_new_json, utc_now


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu-control", type=Path, required=True)
    parser.add_argument("--cpu-control-sha256", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if sha256_file(args.cpu_control) != args.cpu_control_sha256:
        parser.error("CPU control hash mismatch")
    control = json.loads(args.cpu_control.read_bytes())
    if control.get("mode") != "cpu" or control.get("passed") is not True:
        parser.error("passing CPU control required")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    candidate = control["control"]["candidate"]
    config = copy.deepcopy(control["control"]["config"])
    config["ensemble"].update(x_count=128, z_count=64)
    initial = _initial_ensemble([candidate], config["ensemble"])[0]
    parameters = RosslerParameters(**candidate["parameters"])
    receipt = {"schema": "butterfly.symbolic-cpu-fallback-benchmark.v1",
               "started_utc": utc_now(), "source_commit": subprocess.check_output(
                   ["git", "rev-parse", "HEAD"], text=True).strip(),
               "producer_sha256": sha256_file(Path(__file__)),
               "cpu_control_sha256": args.cpu_control_sha256,
               "python": platform.python_version(), "numpy": np.__version__,
               "config": config, "candidate": candidate, "profiles": [],
               "scope": "known-anchor CPU throughput only; no target nominations or symbolic verification"}
    write_new_json(args.output_dir / "started.json", receipt)
    for index, profile in enumerate(config["profiles"]):
        started = time.perf_counter()
        result = sprinkler_survivors(
            parameters, initial, barrio_rossler_section(parameters), candidate["section_states"],
            dt=profile["dt"], horizon=config["ensemble"]["horizon"],
            capture_coordinate_axes=(1, 2), capture_coordinate_scales=(15.0, 0.01),
            capture_radius=config["capture"]["radius"],
            required_capture_crossings=config["capture"]["required_crossings"],
            checkpoint_times=config["ensemble"]["checkpoint_times"],
            midpoint_window=config["ensemble"]["midpoint_window"],
            escape_radius=config["ensemble"]["escape_radius"])
        raw = args.output_dir / f"profile-{index}.npz"
        with raw.open("xb") as stream:
            np.savez_compressed(stream, survivor_ids=result.survivor_ids,
                survivor_counts=result.survivor_counts, failed=result.failed,
                midpoint_trajectory_ids=result.midpoint_trajectory_ids,
                midpoint_times=result.midpoint_times, midpoint_states=result.midpoint_states)
        row = {"dt": profile["dt"], "wall_seconds_including_save": time.perf_counter()-started,
               "failed_count": int(np.count_nonzero(result.failed)),
               "raw": {"path": raw.name, "sha256": sha256_file(raw), "bytes": raw.stat().st_size}}
        receipt["profiles"].append(row)
        write_new_json(args.output_dir / f"profile-{index}.json", row)
        print(json.dumps(row), flush=True)
    receipt["finished_utc"] = utc_now()
    receipt["serial_551_case_seconds_at_anchor_rate"] = 551 * sum(
        row["wall_seconds_including_save"] for row in receipt["profiles"])
    receipt["projection_caveat"] = "Anchor extrapolation, not a measured target runtime or completion promise."
    write_new_json(args.output_dir / "receipt.json", receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

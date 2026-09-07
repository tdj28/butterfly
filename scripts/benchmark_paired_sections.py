#!/usr/bin/env python3
"""Bounded analytic-circle benchmark only: no Rössler target entry point.

Retains both unfiltered section event arrays and capture diagnostics. This is
engineering qualification, not a prospective EXP-481 numerical plan or a
durable production collector. Partial process loss still needs a future wrapper.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import time

import numpy as np

from butterfly.paired_sections import CaptureSection, collect_paired_sections
from butterfly.poincare import PoincareSection


def write_json(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def circle(states):
    return np.column_stack((-np.pi/2*states[:, 1], np.pi/2*states[:, 0], np.zeros(len(states))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed-count", type=int, choices=(32, 128, 512), default=128)
    args = parser.parse_args()
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=False)
    initial = np.column_stack((np.linspace(.5, 4.5, args.seed_count), np.zeros((args.seed_count, 2))))
    sections = {"historical": CaptureSection(PoincareSection((0, 1, 0), 0, -1, 0, 0),
                    np.array([[-1., 0, 0]]), (0, 1), (1., 1.), .01, 2),
                "barrio": CaptureSection(PoincareSection((1, 0, 0), 0, 1),
                    np.array([[0, -2., 0]]), (0, 1), (1., 1.), .01, 2)}
    config = {"horizon": 20.5, "checkpoint_times": [10., 20.5], "state_scales": [1., 1., 1.],
              "gate_margin": 1e-4, "angle_margin": 1e-4, "escape_radius": 100.,
              "maximum_events": args.seed_count*32, "maximum_steps": 3000}
    root = Path(__file__).resolve().parents[1]
    files = [Path(__file__), root / "python/butterfly/paired_sections.py", root / "python/butterfly/saddle.py"]
    started = {"kind": "analytic-circle-engineering-control", "seed_count": args.seed_count,
        "initial_radii": [.5, 4.5], "profiles": [.02, .01], "config": config,
        "source_sha256": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform(),
        "sections": {name: {**asdict(s), "cycle_states": s.cycle_states.tolist()} for name, s in sections.items()},
        "target_trajectories": 0}
    write_json(output / "started.json", started)
    profiles, runs = [], []
    for index, dt in enumerate(started["profiles"]):
        before = time.perf_counter()
        result = collect_paired_sections(circle, initial, sections, dt=dt, **config)
        elapsed = time.perf_counter()-before
        arrays = {k: getattr(result, k) for k in ("initial_states", "final_states", "failed", "failure_steps",
            "failure_states", "capture_times", "capture_streaks", "ambiguous", "initial_on_plane")}
        arrays.update({name+"__"+k: v for name, events in result.events.items() for k, v in events.items()})
        for i, checkpoint in enumerate(result.checkpoints):
            arrays.update({f"checkpoint_{i}__{k}": np.asarray(v) for k, v in checkpoint.items()})
        raw = output / f"profile-{index}.npz"
        with raw.open("xb") as stream:
            np.savez_compressed(stream, **arrays)
        exact = initial.copy()
        theta = config["horizon"]*np.pi/2
        exact[:, 0], exact[:, 1] = initial[:, 0]*np.cos(theta), initial[:, 0]*np.sin(theta)
        error = float(np.max(np.linalg.norm(result.final_states-exact, axis=1)))
        record = {"dt": dt, "status": result.status, "completed_steps": result.completed_steps,
            "elapsed_seconds": elapsed, "events": {n: len(e["times"]) for n, e in result.events.items()},
            "contingency": result.contingency(), "failure": result.failure, "maximum_final_state_error": error,
            "passed": result.status == "completed" and not result.failed.any() and not result.ambiguous.any() and error < 1e-5,
            "raw": {"path": raw.name, "bytes": raw.stat().st_size, "sha256": hashlib.sha256(raw.read_bytes()).hexdigest()}}
        record["passed"] = bool(record["passed"])
        write_json(output / f"profile-{index}.json", record)
        profiles.append(record)
        runs.append(result)
    correspondence = {}
    for name in sections:
        a, b = (r.events[name] for r in runs)
        same = all(np.array_equal(a[k], b[k]) for k in ("seed_ids", "orientation", "accepted"))
        state_error = float(np.max(np.linalg.norm(a["states"]-b["states"], axis=1))) if same else None
        time_error = float(np.max(np.abs(a["times"]-b["times"]))) if same else None
        correspondence[name] = {"same_ordered_membership": same, "maximum_event_state_error": state_error,
            "maximum_event_time_error": time_error, "passed": same and state_error < 1e-5 and time_error < 1e-5}
    receipt = {"kind": started["kind"], "profiles": profiles, "correspondence": correspondence,
               "passed": all(p["passed"] for p in profiles) and all(p["passed"] for p in correspondence.values()),
               "target_trajectories": 0, "no_rossler_performance_extrapolation": True}
    write_json(output / "receipt.json", receipt)
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

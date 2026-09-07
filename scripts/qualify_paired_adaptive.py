#!/usr/bin/env python3
"""Synthetic anisotropic circle: all four integrator profiles and pairwise checks."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import platform

import numpy as np
import scipy

from butterfly.paired_adaptive import collect_adaptive_sections, compare_event_profiles, rk4_comparison_record
from butterfly.paired_sections import CaptureSection, collect_paired_sections
from butterfly.paired_sampling import SECTIONS
from butterfly.poincare import PoincareSection
from scripts.qualify_paired_sampling import descriptor, write

ROOT = Path(__file__).resolve().parents[1]


def save_record(output, name, record):
    arrays = {}
    def encode(value, key):
        if isinstance(value, np.ndarray):
            arrays[key] = value
            return {"array": key, "shape": list(value.shape), "dtype": str(value.dtype)}
        if isinstance(value, dict):
            return {k: encode(v, key+"__"+k) for k, v in value.items()}
        return value
    metadata = encode(record, "record")
    with (output/(name+".npz")).open("xb") as stream:
        np.savez_compressed(stream, **arrays)
    metadata["raw"] = descriptor(output/(name+".npz"))
    write(output/(name+".json"), metadata)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    output = parser.parse_args().output_dir
    output.mkdir(parents=True, exist_ok=False)
    common = dict(horizon=20., state_scales=[15., 15., .01], gate_margin=1e-5, angle_margin=1e-6,
                  escape_radius=1e6, maximum_steps=60000, maximum_events=2048)
    adaptive = dict(rtol=1e-10, atol=1e-12, max_step=.01, maximum_field_evaluations=1000000)
    specs = {SECTIONS[0]: CaptureSection(PoincareSection((0, 1, 0), 0, -1),
        np.array([[-15., 0, .01]]), (0, 2), (15., .01), .0002, 2),
        SECTIONS[1]: CaptureSection(PoincareSection((1, 0, 0), 0, 1),
        np.array([[0, -15., .01]]), (1, 2), (15., .01), .0002, 2)}
    phases = [0., .17, .91, 2.43]
    ids = [0, 512, 1024, 1536]
    config = {"kind": "EXP-481-synthetic-adaptive-qualification", "target_trajectories": 0,
        "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
        "common": common, "adaptive": adaptive, "rk4_steps": [.01, .005],
        "global_seed_ids": ids, "circle_phases": phases, "circle_radius": 15., "z": .01,
        "sections": {n: {**asdict(s), "cycle_states": s.cycle_states.tolist()} for n, s in specs.items()},
        "maximum_scaled_state_difference": 1e-4, "maximum_time_difference": 1e-4,
        "source_sha256": {str(p.relative_to(ROOT)): descriptor(p)["sha256"] for p in
            [Path(__file__), ROOT/"python/butterfly/paired_adaptive.py", ROOT/"python/butterfly/paired_sections.py",
             ROOT/"python/butterfly/poincare.py", ROOT/"python/butterfly/saddle.py",
             ROOT/"scripts/qualify_paired_sampling.py"]},
        "scope": "analytic circle only; same numerical profiles but two-crossing synthetic capture threshold"}
    write(output/"started.json", config)
    comparisons = []
    rhs = lambda x: np.column_stack((-x[:, 1], x[:, 0], np.zeros(len(x))))
    for seed, phase in zip(ids, phases, strict=True):
        initial = np.array([15*np.cos(phase), 15*np.sin(phase), .01])
        records = {}
        for dt in (.01, .005):
            name = f"rk4-{dt}"
            collection = collect_paired_sections(rhs, initial[None, :], specs, dt=dt, checkpoint_times=[20.], **common)
            record = rk4_comparison_record(collection, seed)
            record.update(final_states=collection.final_states, failed=collection.failed,
                failure_states=collection.failure_states, failure_steps=collection.failure_steps,
                capture_streaks=collection.capture_streaks, failure=collection.failure)
            records[name] = record
            save_record(output, f"seed-{seed}-{name}", record)
        for method in ("DOP853", "Radau"):
            record = collect_adaptive_sections(rhs, initial, seed, specs, method=method, **adaptive, **common)
            records[method] = record
            save_record(output, f"seed-{seed}-{method}", record)
        names = list(records)
        for i, name in enumerate(names):
            for other in names[i+1:]:
                comparisons.append({"seed": seed, "left": name, "right": other,
                    **compare_event_profiles(records[name], records[other], state_scales=common["state_scales"],
                        maximum_state_difference=1e-4, maximum_time_difference=1e-4)})
        print(f"seed {seed}: all profiles recorded", flush=True)
    files = [descriptor(p) for p in sorted(output.iterdir())]
    result = {"kind": config["kind"], "passed": len(comparisons) == 24 and all(r["passed"] for r in comparisons),
        "target_trajectories": 0, "configuration": descriptor(output/"started.json"),
        "comparisons": comparisons, "files": files}
    write(output/"receipt.json", result)
    print(json.dumps({"passed": result["passed"], "comparisons": len(comparisons),
                      "receipt": descriptor(output/"receipt.json")}, indent=2))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

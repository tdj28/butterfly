#!/usr/bin/env python3
"""Synthetic circle -> journal -> common cohort -> joint map; no target inputs.

Use a fresh output directory. Failed runs and partial raw journals are retained.
The circle's scalar return is the identity, not a model for a Rössler partition.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
import platform

import numpy as np
import scipy

from butterfly import paired_journal as journal
from butterfly.paired_decisions import analyze_case, critical_matrix
from butterfly.paired_replay import BatchExpectation, replay_batch, assemble_profile, intersect_profiles
from butterfly.paired_sampling import SECTIONS
from butterfly.paired_sections import CaptureSection
from butterfly.poincare import PoincareSection
from butterfly.seed_return_map import MapOptions, VARIANTS
from scripts.qualify_paired_sampling import descriptor, write

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=False)
    ids = np.arange(2048, dtype=np.int64)
    initial = np.zeros((len(ids), 3))
    initial[:, 0] = np.random.Generator(np.random.PCG64(481103)).uniform(1, 2, len(ids))
    split = ids >= 1024
    windows = [[0., 8.], [8., 16.]]
    sections = {SECTIONS[0]: CaptureSection(PoincareSection((0, 1, 0), 0, -1),
        np.array([[-100., 0, 0]]), (0, 2), (1., 1.), .0001, 1),
        SECTIONS[1]: CaptureSection(PoincareSection((1, 0, 0), 0, 1),
        np.array([[0, -100., 0]]), (1, 2), (1., 1.), .0001, 1)}
    section_config = {n: {**asdict(s), "cycle_states": s.cycle_states.tolist()} for n, s in sections.items()}
    numerical = dict(horizon=18., checkpoint_times=[8., 16., 18.], state_scales=[1., 1., 1.],
        gate_margin=1e-5, angle_margin=1e-6, escape_radius=1000., maximum_events=6000, maximum_steps=1000)
    recording = dict(journal_interval_steps=100, maximum_snapshot_bytes=1024**2)
    profiles = [("coarse", .1), ("fine", .05)]
    source_paths = [Path(__file__), ROOT/"scripts/qualify_paired_sampling.py"] + [
        ROOT/f"python/butterfly/{name}.py" for name in (
            "paired_sections", "paired_journal", "paired_sampling", "paired_replay", "paired_decisions",
            "seed_return_map", "poincare")]
    config = {"kind": "EXP-481-synthetic-journal-to-joint-map", "target_trajectories": 0,
        "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
        "source_sha256": {str(p.relative_to(ROOT)): descriptor(p)["sha256"] for p in source_paths},
        "field": "dx=-pi*y/2; dy=pi*x/2; dz=0", "seed_count": len(ids), "random_seed": 481103,
        "radius_range": [1., 2.], "holdout_id_start": 1024, "batch_size": 256,
        "profiles": profiles, "numerical": numerical, "recording": recording,
        "sections": section_config, "windows": windows, "strata_per_window": 1,
        "map_options": asdict(MapOptions()), "variants": [list(v) for v in VARIANTS],
        "expected": "all seeds retained; primary identity maps jointly resolve one branch; no turning-region claim",
        "scope": "synthetic plumbing control with shorter windows/one pair per window; not production numerical qualification"}
    write(output/"started.json", config)
    with (output/"seeds.npz").open("xb") as stream:
        np.savez_compressed(stream, global_seed_ids=ids, initial_states=initial, holdout=split)
    plan_hash = descriptor(output/"started.json")["sha256"]
    rhs = lambda x: np.column_stack((-np.pi/2*x[:, 1], np.pi/2*x[:, 0], np.zeros(len(x))))
    assembled = {}
    expectations = []
    for profile, dt in profiles:
        batches = {}
        for start in range(0, len(ids), 256):
            name = f"{profile}-batch-{start//256:03d}"
            batch_ids, states = ids[start:start+256], initial[start:start+256]
            binding = dict(candidate_id="synthetic-circle", profile=profile, trial_id=name,
                           source_commit="synthetic-source-hashes-in-configuration", plan_sha256=plan_hash)
            collection_config = {**numerical, "dt": dt}
            _, audit = journal.record_collection(rhs, states, batch_ids, sections, collection_config,
                directory=output/name, binding=binding, **recording)
            expected = BatchExpectation(journal.sha256(output/name/"started.json"),
                journal.sha256(output/name/"terminal.json"), batch_ids, states, collection_config,
                section_config, binding, recording)
            # Persist the external expectations, rather than infer them in a
            # later replay from whatever journal happens to be present.
            expectations.append({"batch": name, "global_seed_ids": batch_ids.tolist(),
                "initial_states": states.tolist(), "config": collection_config, "sections": section_config,
                "binding": binding, "recording": recording,
                "started_sha256": expected.started_sha256, "terminal_sha256": expected.terminal_sha256})
            write(output/(name+"-expectation.json"), expectations[-1])
            batches[name] = replay_batch(output/name, expected, windows, strata_per_window=1)
            print(f"{name}: {audit['status']}; retained {batches[name]['counts']['retained']}", flush=True)
        assembled[profile] = assemble_profile(batches, list(batches), ids, initial)
        p = assembled[profile]
        with (output/(profile+"-pairs.npz")).open("xb") as stream:
            np.savez_compressed(stream, global_seed_ids=ids, retained=p["retained"],
                seed_batch_index=p["seed_batch_index"], **{f"section_{i}__{field}": p[field][section]
                    for i, section in enumerate(SECTIONS) for field in (
                        "pair_states", "pair_times", "section_pair_indices", "section_eligible_counts")})
        write(output/(profile+"-provenance.json"), {"batch_ids": p["batch_ids"], "sources": p["sources"]})
    names = [name for name, _ in profiles]
    cohort = intersect_profiles(assembled, names, ids, split)
    write(output/"cohort.json", {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in cohort.items()})
    result = analyze_case(assembled, names, cohort, primary={"section": SECTIONS[0], "axis": 0},
        diagnostics=[{"section": SECTIONS[0], "axis": 2}, {"section": SECTIONS[1], "axis": 2}])
    result["critical_matrix"] = critical_matrix(result["joint_primary"], result["primary_audits"], [-1.25, -1.75])
    write(output/"analysis.json", result)
    passed = (cohort["retained"].all() and cohort["joint_population_passed"]
        and result["joint_primary"]["resolved"] and result["joint_primary"]["branch_count"] == 1
        and result["critical_matrix"]["status"] == "no-turning-regions"
        and not result["historical_symbols_verified"])
    files = [descriptor(p) | {"path": str(p.relative_to(output))} for p in sorted(output.rglob("*")) if p.is_file()]
    receipt = {"kind": config["kind"], "passed": bool(passed), "target_trajectories": 0,
        "configuration": descriptor(output/"started.json"), "retained_seeds": int(cohort["retained"].sum()),
        "calibration_seeds": cohort["calibration_seeds"], "validation_seeds": cohort["validation_seeds"],
        "joint_primary": result["joint_primary"], "critical_matrix_status": result["critical_matrix"]["status"],
        "raw_file_count": len(files), "raw_bytes": sum(f["bytes"] for f in files), "files": files}
    write(output/"receipt.json", receipt)
    print(f"passed={bool(passed)}; retained={cohort['retained'].sum()}; branch_count={result['joint_primary']['branch_count']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

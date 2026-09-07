#!/usr/bin/env python3
"""EXP-482 synthetic full-horizon workload; no Rössler trajectories or authority.

Default prints the fixed protocol. --execute supervises one fresh local run.
The circle includes discarded Rössler RHS arithmetic and six/eight capture
references, but cannot establish target accuracy, retention or event frequency.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
BATCH = 512
HORIZON = 300.
STEPS = (.0025, .00125)
PERIOD = 4.1  # avoid a root at the final horizon, independently of RK4 error
MAX_EVENTS = 262144
MAX_SNAPSHOT = 8*1024**2
WALL = 900.


def protocol():
    return dict(experiment_id="EXP-482", kind="full-horizon-synthetic-workload",
        target_trajectories_generated=0, target_execution_authorized=False,
        batch_size=BATCH, horizon=HORIZON, steps=list(STEPS), maximum_steps=240000,
        journal_interval_steps=1000, maximum_events_per_batch=MAX_EVENTS,
        maximum_snapshot_bytes=MAX_SNAPSHOT, circle_period=PERIOD,
        expected_raw_events_per_seed_per_section=146,
        expected_accepted_events_per_seed_per_section=73,
        maximum_analytic_state_error=1e-5, maximum_analytic_event_time_error=1e-5,
        expected_failed_ambiguous_captured_seeds=0,
        full_analysis_seeds_per_case=8192, full_analysis_bootstrap_samples=200,
        expected_cubic_branches=3,
        expected_near_matrix=[[True, False], [False, True], *[[False, False] for _ in range(4)]],
        adverse_primary_expected="unresolved", headroom_factor=2,
        limits=dict(qualification_seconds=1800., collection_seconds=14400.,
            analysis_seconds=7200., disk_bytes=8*1024**3, rss_bytes=2*1024**3),
        synthetic_worker_wall_seconds=WALL, automatic_retry=False,
        scope="engineering estimate, not target resource guarantee or numerical qualification")


def check_circle(result, initial):
    import numpy as np
    angle = 2*np.pi*HORIZON/PERIOD
    expected = initial.copy()
    expected[:, 0] = initial[:, 0]*np.cos(angle)
    expected[:, 1] = initial[:, 0]*np.sin(angle)
    error = float(np.max(np.abs(result.final_states-expected)))
    if (result.status != "completed" or result.failed.any() or result.ambiguous.any()
            or np.isfinite(result.capture_times).any() or error >= 1e-5):
        raise ValueError("analytic circle state/capture expectation failed")
    rows = {}
    for index, (name, events) in enumerate(result.events.items()):
        counts = np.bincount(events["seed_ids"], minlength=len(initial))
        accepted = events["accepted"]
        accepted_counts = np.bincount(events["seed_ids"][accepted], minlength=len(initial))
        # Raw roots: y=0 at T/2, T, ...; x=0 at T/4, 3T/4, ... .
        order = np.lexsort((events["times"], events["seed_ids"]))
        ordered = events["times"][order].reshape(len(initial), 146)
        exact = (np.arange(146)+ (1 if index == 0 else .5))*PERIOD/2
        time_error = float(np.max(np.abs(ordered-exact[None, :])))
        if not (np.all(counts == 146) and np.all(accepted_counts == 73) and time_error < 1e-5):
            raise ValueError("analytic ordered event expectation failed")
        rows[name] = dict(raw_per_seed=146, accepted_per_seed=73, maximum_time_error=time_error)
    return dict(maximum_state_error=error, sections=rows, passed=True)


def estimates(collection, qualification, analysis, scan):
    """All fixed formulas declared before measurement; no fastest-run selection."""
    batches = 2*8192//BATCH  # two cases, per profile
    disk = batches*sum(r["bytes"] for r in collection)
    files = batches*sum(r["files"] for r in collection)
    # Supervisor stat scans operate on a growing full campaign. Bound each poll
    # using twice a full-size linear extrapolation, even while the tree is small.
    scan_full = scan["seconds"]*files/max(1, scan["files"])
    base = 2*batches*sum(r["seconds"] for r in collection)
    occupancy = 2*scan_full/.25
    seconds = base/(1-occupancy) if occupancy < 1 else None
    peak = max(analysis["peak_rss_bytes"], *(r["peak_rss_bytes"] for r in collection))
    result = dict(qualification_seconds=2*qualification["seconds"]*128/8,
        collection_seconds=seconds,
        analysis_seconds=2*(analysis["seconds"] + batches*sum(r["replay_seconds"] for r in collection)),
        disk_bytes=2*(disk + qualification["bytes"]*128/8 + analysis["bytes"] + 128*1024**2),
        rss_bytes=2*(peak+128*1024**2), projected_collection_files=files,
        projected_full_tree_scan_seconds=scan_full, scan_cpu_fraction_with_headroom=occupancy)
    limits = protocol()["limits"]
    result["fits_limits"] = all(result[k] is not None and result[k] < v for k, v in limits.items())
    return result


def workload(output):
    import resource
    import runpy
    import numpy as np
    from butterfly._paired_startup import inventory, sha256, write_json
    from butterfly.models import RosslerParameters, rossler_rhs
    from butterfly.paired_journal import record_collection
    from butterfly.paired_phase_control import make_control
    from butterfly.paired_phases import run_phase
    from butterfly.paired_replay import BatchExpectation, replay_batch
    from butterfly.paired_supervisor import directory_bytes

    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    write_json(output/"started.json", protocol())
    peak = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform == "darwin" else 1024)
    design, _ = make_control()
    case = design.plan["candidate_ids"][0]
    def loaded_circle(x):
        rossler_rhs(0., x.T, RosslerParameters(a=.2, b=.2, c=5.7))
        return np.column_stack((-2*np.pi/PERIOD*x[:, 1], 2*np.pi/PERIOD*x[:, 0], np.zeros(len(x))))
    collection = []
    for dt in STEPS:
        directory = output/f"collection-{dt}"
        config = dict(dt=dt, horizon=HORIZON, checkpoint_times=[50.,100.,150.,200.,250.,300.],
            state_scales=[15.,15.,.01], gate_margin=1e-5, angle_margin=1e-6,
            escape_radius=1e6, maximum_steps=240000, maximum_events=MAX_EVENTS)
        recording = dict(journal_interval_steps=1000, maximum_snapshot_bytes=MAX_SNAPSHOT)
        initial, ids = design.initial[case][:BATCH], np.arange(BATCH)
        binding = dict(kind="EXP-482-synthetic-workload", dt=dt)
        t = time.monotonic()
        result, audit = record_collection(loaded_circle, initial, ids, design.sections[case], config,
            directory=directory, binding=binding, **recording)
        elapsed = time.monotonic()-t
        if audit["status"] != "completed" or audit["orphan_files"]:
            raise ValueError("incomplete journal")
        analytic = check_circle(result, initial)
        expected = BatchExpectation(sha256(directory/"started.json"), sha256(directory/"terminal.json"),
            ids, initial, config, design.section_config(case), binding, recording)
        t = time.monotonic()
        replay_batch(directory, expected, [[80.,140.],[180.,240.]], strata_per_window=4)
        replay_seconds = time.monotonic()-t
        t = time.monotonic()
        files = inventory(directory)
        inventory_seconds = time.monotonic()-t
        row = dict(dt=dt, seconds=elapsed, replay_seconds=replay_seconds,
            inventory_seconds=inventory_seconds, bytes=sum(r["bytes"] for r in files.values()),
            files=len(files), records=audit["records"], event_counts=audit["event_counts"],
            peak_rss_bytes=peak(), analytic=analytic)
        collection.append(row)
        write_json(output/f"measurement-{dt}.json", row)
        print(f"full-horizon synthetic dt={dt}: {elapsed:.3f}s; analytic checks pass", flush=True)

    design.plan["collection"].update(profiles=[dict(name=f"rk4-{i}",dt=dt) for i,dt in enumerate(STEPS)],
        maximum_steps_per_batch=240000,journal_interval_steps=1000,maximum_snapshot_bytes=MAX_SNAPSHOT)
    q = design.plan["adaptive_qualification"]
    q.update(global_seed_ids=[0],horizon=20.,maximum_steps_per_seed=240000,
        maximum_raw_events_per_seed=2048,maximum_field_evaluations_per_adaptive_seed=1000000,
        adaptive_recording_interval_steps=1000,maximum_adaptive_snapshot_bytes=MAX_SNAPSHOT)
    for profile in q["profiles"]: profile["max_step"] = .01
    t = time.monotonic()
    run_phase(design,"qualification",output/"qualification",
        fields={c:loaded_circle for c in design.plan["candidate_ids"]})
    qualification_seconds = time.monotonic()-t
    terminal = json.loads((output/"qualification/terminal.json").read_bytes())
    if not terminal["passed"] or len(terminal["trial_ids"]) != 8:
        raise ValueError("all-profile synthetic qualification failed")
    qualification = dict(seconds=qualification_seconds,
        bytes=sum(r["bytes"] for r in inventory(output/"qualification").values()))
    fixture = runpy.run_path(str(ROOT/"tests/test_paired_campaign.py"))
    data = fixture["synthetic"](count=8192,bootstrap_samples=200,batch_size=BATCH)
    t = time.monotonic()
    result = fixture["run"](data)
    write_json(output/"positive-analysis.json", result)
    analysis_seconds = time.monotonic()-t
    for row in result["cases"].values():
        if (not row["analysis"]["joint_primary"]["resolved"]
                or row["analysis"]["joint_primary"]["branch_count"] != 3
                or row["analysis"]["critical_matrix"]["near_every_primary_model"] != protocol()["expected_near_matrix"]):
            raise ValueError("full-size cubic analysis failed")
    fixture["test_multivalued_primary_cannot_receive_positive_turn_support"]()
    analysis = dict(seconds=analysis_seconds,bytes=(output/"positive-analysis.json").stat().st_size,
        peak_rss_bytes=peak(), positive_and_adverse_passed=True)
    # Keep all three readings, use the slowest; do not select a warm best case.
    files = inventory(output)
    scans = []
    for _ in range(3):
        t = time.monotonic()
        directory_bytes(output)
        scans.append(time.monotonic()-t)
    scan = dict(seconds=max(scans),observations_seconds=scans,files=len(files))
    projection = estimates(collection,qualification,analysis,scan)
    receipt = dict(protocol=protocol(),collection=collection,qualification=qualification,
        analysis=analysis,scan=scan,estimates=projection,files=files)
    write_json(output/"receipt.json",receipt)
    print(json.dumps({"estimates":projection}),flush=True)
    return 0 if projection["fits_limits"] else 2


def execute(output):
    from butterfly._paired_startup import sha256, write_json
    from butterfly.paired_supervisor import StageLimits, supervise
    source = subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    if subprocess.check_output(["git","status","--porcelain","--untracked-files=no"],cwd=ROOT):
        raise ValueError("commit tracked source before benchmark")
    output = output.resolve()
    output.relative_to(ROOT/"artifacts/EXP-482")
    if output == ROOT/"artifacts/EXP-482": raise ValueError("fresh child directory required")
    output.mkdir(parents=True,exist_ok=False,mode=0o700)
    sources = {str(p.relative_to(ROOT)): dict(bytes=p.stat().st_size,sha256=sha256(p)) for p in
        (Path(__file__),ROOT/"tests/test_paired_campaign.py")}
    bootstrap = ("import sys;sys.path[:0]="+repr([str(ROOT/"python"),str(ROOT)])+";"
        "from butterfly._process_guard import install_parent_guard;"
        f"install_parent_guard({WALL!r});"
        "from pathlib import Path;from scripts.benchmark_paired_refinement import workload;"
        "raise SystemExit(workload(Path(sys.argv[1])))")
    env = {"PATH":os.defpath,"PYTHONHASHSEED":"0",**{k:"1" for k in
        ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS")}}
    result = supervise([sys.executable,"-I","-B","-c",bootstrap,str(output/"workload")],
        cwd=ROOT,evidence_directory=output,state_directory=output/"supervisor",environment=env,
        binding=dict(source_commit=source,source_files=sources,protocol=protocol()),
        limits=StageLimits(WALL,2*1024**3,2*1024**3,16*1024**3))
    write_json(output/"supervised-result.json",result)
    print(json.dumps(result,indent=2))
    return 0 if result["status"] == "completed" and result["owned_group_cleanup_verified"] else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute",action="store_true")
    parser.add_argument("--output-dir",type=Path)
    args = parser.parse_args()
    if args.execute:
        if args.output_dir is None: parser.error("--execute needs --output-dir")
        raise SystemExit(execute(args.output_dir))
    print(json.dumps(protocol(),indent=2))

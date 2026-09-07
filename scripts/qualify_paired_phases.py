#!/usr/bin/env python3
"""Run all fixed phases in isolated supervised workers on an analytic circle.

Preserves successes and failures in a fresh directory. No target inputs, new
Rössler trajectories, provider requests or execution authorization are used.
"""
import argparse
import json
from pathlib import Path
import resource
import runpy
import sys
import time

from butterfly._paired_startup import inventory, load_contract, sha256, write_json
from butterfly.paired_phase_control import make_control
from butterfly.paired_phases import phase_limits
from butterfly.paired_supervisor import supervise
from scripts.build_paired_runtime import ROOT, SOURCE_MAP, build


def review_benchmark(output):
    """Fixed B01/B02 synthetic workloads; estimates, not target timing guarantees.

    Expectations: full cubic analysis has three branches and only reference
    rows 0/1 near turns 0/1, respectively. A two-sheet primary cannot pass.
    Target seeds are never integrated under a Rössler vector field. Collection
    uses the analytic circle plus a discarded Rössler RHS evaluation per call
    to include that vectorized arithmetic cost without creating target orbits.
    """
    import numpy as np
    from butterfly import paired_journal as journal
    from butterfly.models import RosslerParameters, rossler_rhs
    from butterfly.paired_phases import run_phase
    from butterfly.paired_replay import BatchExpectation, replay_batch

    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    write_json(output/"started.json", dict(kind="EXP-481-review-benchmark", findings=["B01", "B02"],
        target_trajectories_generated=0, source_sha256=sha256(Path(__file__)),
        fixture_sha256=sha256(ROOT/"tests/test_paired_campaign.py"),
        expectation="three cubic branches; only rows 0/1 near turns 0/1; two-sheet primary unresolved",
        headroom_factor=2., maximum_seconds=900., no_target_outcomes=True))
    started = time.monotonic()
    design, fields = make_control()
    case = design.plan["candidate_ids"][0]
    original = fields[case]
    def loaded_circle(x):
        rossler_rhs(0., x.T, RosslerParameters(a=.2, b=.2, c=5.7))
        return original(x)
    collection, replay_seconds = [], 0.
    for dt in (.01, .005):
        directory = output/f"collection-{dt}"
        config = dict(dt=dt, horizon=20., checkpoint_times=[5., 10., 15., 20.],
            state_scales=[15., 15., .01], gate_margin=1e-5, angle_margin=1e-6,
            escape_radius=1e6, maximum_steps=60000, maximum_events=32768)
        recording = dict(journal_interval_steps=1000, maximum_snapshot_bytes=8388608)
        initial, ids = design.initial[case][:64], np.arange(64)
        binding = dict(kind="synthetic-throughput", dt=dt)
        t = time.monotonic()
        _, audit = journal.record_collection(loaded_circle, initial, ids, design.sections[case], config,
            directory=directory, binding=binding, **recording)
        elapsed = time.monotonic()-t
        if audit["status"] != "completed" or audit["orphan_files"]:
            raise ValueError("synthetic throughput journal incomplete")
        expected = BatchExpectation(sha256(directory/"started.json"), sha256(directory/"terminal.json"),
            ids, initial, config, design.section_config(case), binding, recording)
        t = time.monotonic()
        replay_batch(directory, expected, [[0., 9.], [9., 18.]], strata_per_window=1)
        replay_elapsed = time.monotonic()-t
        replay_seconds += replay_elapsed
        files = inventory(directory)
        row = dict(dt=dt, batch_seeds=64, horizon=20., elapsed_seconds=elapsed,
            replay_seconds=replay_elapsed, bytes=sum(r["bytes"] for r in files.values()),
            records=audit["records"], event_counts=audit["event_counts"])
        collection.append(row)
        write_json(output/f"collection-{dt}-measurement.json", row)
        print(f"synthetic collection dt={dt}: {elapsed:.3f}s", flush=True)

    # Actual all-profile qualification path on two synthetic one-seed cases.
    design.plan["collection"].update(profiles=[dict(name="rk4-001", dt=.01), dict(name="rk4-0005", dt=.005)],
        maximum_steps_per_batch=60000, journal_interval_steps=1000, maximum_snapshot_bytes=8388608)
    q = design.plan["adaptive_qualification"]
    q.update(global_seed_ids=[0], horizon=20., maximum_steps_per_seed=60000,
        maximum_raw_events_per_seed=2048, maximum_field_evaluations_per_adaptive_seed=1000000,
        adaptive_recording_interval_steps=1000, maximum_adaptive_snapshot_bytes=8388608)
    for profile in q["profiles"]:
        profile["max_step"] = .01
    t = time.monotonic()
    run_phase(design, "qualification", output/"qualification", fields=fields)
    qualification_seconds = time.monotonic()-t
    terminal = json.loads((output/"qualification/terminal.json").read_bytes())
    if not terminal["passed"] or len(terminal["trial_ids"]) != 8:
        raise ValueError("synthetic numerical qualification did not pass")
    print(f"synthetic qualification: {qualification_seconds:.3f}s", flush=True)

    # Worst retained target population and all 24 map fits. Only bootstrap count
    # is shortened; estimate scales the entire measured analysis by 200/8.
    fixture = runpy.run_path(str(ROOT/"tests/test_paired_campaign.py"))
    data = fixture["synthetic"](count=8192, bootstrap_samples=8, batch_size=64)
    t = time.monotonic()
    result = fixture["run"](data)
    write_json(output/"positive-analysis.json", result)
    analysis_seconds = time.monotonic()-t
    near = [[True, False], [False, True], *[[False, False] for _ in range(4)]]
    for row in result["cases"].values():
        if (not row["analysis"]["joint_primary"]["resolved"]
                or row["analysis"]["joint_primary"]["branch_count"] != 3
                or row["analysis"]["critical_matrix"]["near_every_primary_model"] != near):
            raise ValueError("full-population cubic expectation failed")
    # The bounded adverse fixture is the same complete both-case reporting path.
    fixture["test_multivalued_primary_cannot_receive_positive_turn_support"]()
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024)
    qualification_bytes = sum(r["bytes"] for r in inventory(output/"qualification").values())
    analysis_bytes = (output/"positive-analysis.json").stat().st_size
    estimates = dict(qualification_seconds=2*qualification_seconds*128/8,
        collection_seconds=2*sum(r["elapsed_seconds"] for r in collection)*15*256,
        analysis_seconds=2*(analysis_seconds*200/8 + replay_seconds*15*256),
        collection_bytes=2*(sum(r["bytes"] for r in collection)*15*256
            + qualification_bytes*128/8 + analysis_bytes*200/8 + 128*1024**2),
        peak_rss_bytes=2*(peak + 128*1024**2))
    target = json.loads((ROOT/"experiments/manifests/EXP-481-paired-design.json").read_bytes())
    limits = {"qualification_seconds": target["resources"]["maximum_qualification_seconds"],
        "collection_seconds": target["resources"]["maximum_wall_seconds"],
        "analysis_seconds": target["resources"]["maximum_analysis_seconds"],
        "collection_bytes": target["resources"]["maximum_collection_disk_bytes"],
        "peak_rss_bytes": target["resources"]["maximum_process_rss_bytes"]}
    receipt = dict(kind="EXP-481-review-benchmark", target_trajectories_generated=0,
        target_execution_authorized=False, elapsed_seconds=time.monotonic()-started,
        collection=collection, qualification_seconds=qualification_seconds,
        analysis_seconds=analysis_seconds, measured_peak_rss_bytes=peak,
        positive_and_adverse_expectations_passed=True, headroom_factor=2,
        estimates=estimates, limits=limits,
        fits_phase_limits=all(estimates[k] < limits[k] for k in limits),
        total_phase_seconds=sum(limits[k] for k in ("qualification_seconds", "collection_seconds", "analysis_seconds")),
        scope="synthetic workload extrapolation; no target runtime, memory or retention guarantee",
        files=inventory(output))
    write_json(output/"receipt.json", receipt)
    return receipt


def qualify(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    built = build(output/"runtime", startup_guard_seconds=120.)
    contract = load_contract(output/"runtime", built["sha256"])
    design, _ = make_control()
    design.validate()
    write_json(output/"started.json", dict(kind="EXP-481-sealed-synthetic-phase-qualification",
        target_trajectories_generated=0, runtime_contract_sha256=built["sha256"], synthetic_plan=design.plan,
        design_sha256=design.identity(), source_sha256={str(p.relative_to(ROOT)): sha256(p) for p in
            [Path(__file__), ROOT/"scripts/build_paired_runtime.py", *[ROOT/p for p in sorted(set(SOURCE_MAP.values()))]]},
        expected="both cases; 24 event-profile comparisons; 2048 retained IDs per case; one primary branch; all six reference rows",
        scope="short analytic-circle control; not target numerical qualification or review/source authorization"))
    results, previous = {}, None
    for stage in ("qualification", "collection", "analysis", "wrong-previous-digest"):
        phase = "collection" if stage == "wrong-previous-digest" else stage
        evidence = output/stage
        evidence.mkdir()
        argv = [contract["interpreter"]["path"], "-I", "-S", "-B", "-X", "utf8",
            str(output/"runtime/worker.py"), "--contract-sha256", built["sha256"],
            "--output-dir", str(evidence), "--mode", "synthetic-phase", "--phase", phase]
        if stage != "qualification":
            source = output/("qualification" if stage == "wrong-previous-digest" else previous)/"phase"
            digest = "0"*64 if stage == "wrong-previous-digest" else sha256(source/"terminal.json")
            argv += ["--previous-root", str(source), "--previous-sha256", digest]
        # Bind actual bootstrap bytes before executing the first instruction.
        for name in ("worker.py", "startup.py"):
            if sha256(output/"runtime"/name) != contract["source_files"][name]["sha256"]:
                raise ValueError("bootstrap changed before launch")
        result = supervise(argv, cwd=output, evidence_directory=output, state_directory=evidence/"supervisor",
            environment=contract["environment"], binding=dict(kind="synthetic-phase", phase=phase,
                runtime_contract_sha256=built["sha256"]), limits=phase_limits(design.plan, phase))
        success = result["status"] == "completed" and result["owned_group_cleanup_verified"]
        if stage == "wrong-previous-digest":
            failure = json.loads((evidence/"failure.json").read_bytes()) if (evidence/"failure.json").exists() else {}
            passed = (not success and result["owned_group_cleanup_verified"]
                and "hash" in failure.get("message", "") and not (evidence/"synthetic-phase.json").exists()
                and not (evidence/"phase").exists())
        else:
            passed = success and (evidence/"synthetic-phase.json").exists()
            if passed:
                witness = json.loads((evidence/"synthetic-phase.json").read_bytes())
                passed = (witness["runtime_contract_sha256"] == built["sha256"]
                    and witness["target_trajectories_generated"] == 0 and not witness["target_execution_authorized"]
                    and "butterfly.paired_phases" in witness["loaded_modules"]
                    and not any(n.startswith(("scripts.", "torch", "triton")) for n in witness["loaded_modules"]))
            if passed and stage == "qualification":
                terminal = json.loads((evidence/"phase/terminal.json").read_bytes())
                passed = terminal["passed"] and terminal["comparison_count"] == 24 and len(terminal["trial_ids"]) == 16
            if passed and stage == "collection":
                passed = len(json.loads((evidence/"phase/terminal.json").read_bytes())["trial_ids"]) == 16
            if passed and stage == "analysis":
                analysis = json.loads((evidence/"phase/analysis.json").read_bytes())
                passed = analysis["all_cases_primary_resolved"] and not analysis["historical_symbols_verified"]
                for row in analysis["cases"].values():
                    passed = (passed and row["cohort"]["global_seed_ids"] == list(range(2048))
                        and row["cohort"]["calibration_seeds"] == row["cohort"]["validation_seeds"] == 1024
                        and row["reference_row_indices"] == list(range(6))
                        and row["analysis"]["joint_primary"]["branch_count"] == 1
                        and row["analysis"]["critical_matrix"]["status"] == "no-turning-regions")
            previous = stage
        results[stage] = dict(passed=bool(passed), supervisor=result)
        write_json(output/(stage+"-control.json"), results[stage])
        print(f"{stage}: passed={bool(passed)}", flush=True)
        if not passed:
            break
    files = inventory(output)
    receipt = dict(kind="EXP-481-sealed-synthetic-phase-qualification",
        passed=len(results) == 4 and all(r["passed"] for r in results.values()),
        target_trajectories_generated=0, target_execution_authorized=False,
        controls=results, files=files, file_count=len(files), bytes=sum(f["bytes"] for f in files.values()))
    write_json(output/"receipt.json", receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--review-benchmark", action="store_true", help="bounded B01/B02 synthetic workload, no target inputs")
    args = parser.parse_args()
    if args.review_benchmark:
        result = review_benchmark(args.output_dir)
        print(json.dumps({k: result[k] for k in ("fits_phase_limits", "estimates", "limits")}, indent=2))
        return 0 if result["fits_phase_limits"] else 2
    result = qualify(args.output_dir)
    print(json.dumps({k: result[k] for k in ("passed", "file_count", "bytes")}, indent=2))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run all fixed phases in isolated supervised workers on an analytic circle.

Preserves successes and failures in a fresh directory. No target inputs, new
Rössler trajectories, provider requests or execution authorization are used.
"""
import argparse
import json
from pathlib import Path

from butterfly._paired_startup import inventory, load_contract, sha256, write_json
from butterfly.paired_phase_control import make_control
from butterfly.paired_phases import phase_limits
from butterfly.paired_supervisor import supervise
from scripts.build_paired_runtime import ROOT, SOURCE_MAP, build


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
    result = qualify(parser.parse_args().output_dir)
    print(json.dumps({k: result[k] for k in ("passed", "file_count", "bytes")}, indent=2))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

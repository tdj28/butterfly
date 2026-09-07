#!/usr/bin/env python3
"""Sealed paired-section worker: startup and read-only reference audit.

The controller must independently bind this launcher and contract digest before
spawn. This executable never treats its own receipt as target authorization.
"""
import argparse
from pathlib import Path
import runpy
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract-sha256", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=("startup", "audit-inputs", "design-preflight", "synthetic-phase", "execute"), default="startup")
    parser.add_argument("--input-root", type=Path)
    parser.add_argument("--input-contract-sha256")
    parser.add_argument("--phase", choices=("qualification", "collection", "analysis"))
    parser.add_argument("--previous-root", type=Path)
    parser.add_argument("--previous-sha256")
    parser.add_argument("--source-commit")
    parser.add_argument("--plan-sha256")
    args = parser.parse_args()
    if args.mode in ("audit-inputs", "design-preflight"):
        if args.input_root is None or args.input_contract_sha256 is None:
            parser.error(f"{args.mode} requires an explicit input package and external digest")
    elif args.input_root is not None or args.input_contract_sha256 is not None:
        parser.error("input arguments are only valid for audit-inputs or design-preflight")
    if args.mode == "design-preflight":
        if args.source_commit is None or args.plan_sha256 is None:
            parser.error("design-preflight requires external source and plan bindings")
    elif args.source_commit is not None or args.plan_sha256 is not None:
        parser.error("design bindings are only valid for design-preflight")
    if args.mode == "synthetic-phase":
        if args.phase is None:
            parser.error("synthetic-phase requires the fixed phase name")
        if (args.phase != "qualification") != (args.previous_root is not None and args.previous_sha256 is not None):
            parser.error("collection/analysis require an external preceding phase digest")
        if args.phase == "qualification" and (args.previous_root is not None or args.previous_sha256 is not None):
            parser.error("qualification has no preceding numerical phase")
    elif args.phase is not None or args.previous_root is not None or args.previous_sha256 is not None:
        parser.error("phase arguments are only valid for synthetic-phase")
    root = Path(__file__).resolve().parent
    startup = runpy.run_path(str(root/"startup.py"))
    contract = startup["load_contract"](root, args.contract_sha256)
    # Load only the hash-checked stdlib guard before potentially slow dependency
    # verification. The launcher/startup files need an external controller check.
    guard_path = startup["safe_file"](root, "python/butterfly/_process_guard.py")
    if startup["sha256"](guard_path) != contract["source_files"]["python/butterfly/_process_guard.py"]["sha256"]:
        raise ValueError("startup guard differs from contract")
    guard = runpy.run_path(str(guard_path))["install_parent_guard"](contract["startup_guard_seconds"])
    output = args.output_dir.resolve(strict=True)
    if output == root or output.is_relative_to(root):
        raise ValueError("evidence must be outside immutable runtime bundle")
    try:
        startup["validate_environment"](contract)
        startup["verify_runtime"](root, contract)
        finder = startup["install_import_gate"](root, contract)
        import numpy
        import scipy
        from butterfly import paired_adaptive_journal, paired_campaign, paired_supervisor, paired_inputs, paired_input_package
        # Reach actual analysis option validation and deterministic seed inputs
        # without candidate files, solver calls, reference reading or map fits.
        from butterfly.paired_sampling import seed_table, seed_commitment
        from butterfly.seed_return_map import MapOptions, _validate_options
        _validate_options(MapOptions())
        seed_hash = seed_commitment(seed_table())
        loaded = finder.check_loaded()
        startup["validate_environment"](contract)
        startup["verify_runtime"](root, contract)
        if not guard.is_alive():
            raise ValueError("parent guard stopped before startup handshake")
        startup["write_json"](output/"startup.json", {"status": "passed", "contract_sha256": args.contract_sha256,
            "guard_alive": True, "scientific_imports_before_guard": False, "environment": dict(__import__("os").environ),
            "flags": {"isolated": bool(sys.flags.isolated), "no_site": bool(sys.flags.no_site),
                "no_bytecode": bool(sys.dont_write_bytecode), "utf8_mode": bool(sys.flags.utf8_mode)},
            "numpy": numpy.__version__, "scipy": scipy.__version__, "loaded_modules": loaded,
            "seed_commitment": seed_hash, "target_trajectories_generated": 0,
            "target_execution_authorized": False, "scope": "sealed import and setup handshake only"})
        if args.mode == "execute":
            raise ValueError("review-bound production phase dispatch is not implemented; target execution refused")
        if args.mode == "synthetic-phase":
            from butterfly.paired_phase_control import make_control
            from butterfly.paired_phases import run_phase
            design, fields = make_control()
            previous = None
            if args.previous_root is not None:
                previous = {"path": "terminal.json", "sha256": args.previous_sha256}
                prior = args.previous_root.resolve(strict=True)
                if prior == output or prior.is_relative_to(output) or output.is_relative_to(prior):
                    raise ValueError("previous phase and current evidence must be disjoint")
            receipt = run_phase(design, args.phase, output/"phase",
                fields=None if args.phase == "analysis" else fields,
                previous_directory=args.previous_root, previous_receipt=previous)
            startup["validate_environment"](contract)
            startup["verify_runtime"](root, contract)
            imported = finder.check_loaded()
            if not guard.is_alive():
                raise ValueError("parent guard stopped during synthetic phase")
            startup["write_json"](output/"synthetic-phase.json", {"status": "completed", "phase": args.phase,
                "runtime_contract_sha256": args.contract_sha256, "phase_receipt": receipt,
                "loaded_modules": imported, "target_execution_authorized": False,
                "target_trajectories_generated": 0, "scope": "analytic-circle plumbing control only"})
        if args.mode in ("audit-inputs", "design-preflight"):
            inputs = args.input_root.resolve(strict=True)
            if output == inputs or output.is_relative_to(inputs) or inputs.is_relative_to(output):
                raise ValueError("input package and writable evidence must be disjoint")
            plan = paired_input_package.load_package(inputs, args.input_contract_sha256)
            audit = paired_inputs.load_references(plan, inputs)
            design_receipt = None
            if args.mode == "design-preflight":
                if startup["sha256"](inputs/"plan.json") != args.plan_sha256:
                    raise ValueError("input plan differs from external design hash")
                from butterfly.paired_phases import from_reference_audit, phase_limits
                from dataclasses import asdict
                design, _ = from_reference_audit(plan, audit, source_commit=args.source_commit,
                    plan_sha256=args.plan_sha256)
                grid = design.validate()
                design_receipt = dict(source_commit=args.source_commit, plan_sha256=args.plan_sha256,
                    design_sha256=design.identity(), trial_counts={s: sum(t.stage == s for t in grid)
                        for s in ("qualification", "collection")},
                    phase_limits={s: asdict(phase_limits(plan, s)) for s in ("qualification", "collection", "analysis")},
                    guard_seconds=contract["startup_guard_seconds"],
                    scope="all fixed configurations validated without calling a field, integrator or map fit")
            # Recheck bytes and imports after the actual read-only consumer.
            if paired_input_package.load_package(inputs, args.input_contract_sha256) != plan:
                raise ValueError("input plan changed during reference audit")
            startup["validate_environment"](contract)
            startup["verify_runtime"](root, contract)
            imported = finder.check_loaded()
            if not guard.is_alive():
                raise ValueError("parent guard stopped during input audit")
            witness = {"status": "passed", "audit": audit,
                "runtime_contract_sha256": args.contract_sha256, "input_contract_sha256": args.input_contract_sha256,
                "loaded_modules": imported, "target_execution_authorized": False,
                "target_trajectories_generated": 0}
            if design_receipt is not None:
                witness["design"] = design_receipt
            startup["write_json"](output/("design-preflight.json" if design_receipt else "input-audit.json"), witness)
        return 0
    except (Exception, KeyboardInterrupt) as error:
        startup["write_json"](output/"failure.json", {"status": "failed", "type": type(error).__name__,
            "message": str(error), "contract_sha256": args.contract_sha256, "target_trajectories_generated": 0})
        raise


if __name__ == "__main__":
    raise SystemExit(main())

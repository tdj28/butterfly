#!/usr/bin/env python3
"""Sealed paired-section worker bootstrap; startup-only until reviewed wiring.

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
    parser.add_argument("--mode", choices=("startup", "execute"), default="startup")
    args = parser.parse_args()
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
        from butterfly import paired_adaptive_journal, paired_campaign, paired_supervisor
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
        return 0
    except (Exception, KeyboardInterrupt) as error:
        startup["write_json"](output/"failure.json", {"status": "failed", "type": type(error).__name__,
            "message": str(error), "contract_sha256": args.contract_sha256, "target_trajectories_generated": 0})
        raise


if __name__ == "__main__":
    raise SystemExit(main())

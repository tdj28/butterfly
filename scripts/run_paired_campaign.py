#!/usr/bin/env python3
"""EXP-481 setup and one-shot campaign, using the actual source/review gate.

Default source preflight never executes target phases. Execute requires fresh
reviewed setup and the fixed unused experiment slot. Control runs only the
fixed analytic circle, never target fields or user-selected scientific inputs.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
import sysconfig


ROOT = Path(__file__).resolve().parents[1]
PLAN = "experiments/manifests/EXP-481-paired-design.json"
STAGES = ("qualification", "collection", "analysis")
TEST_PACKAGES = ("pytest", "_pytest", "pluggy", "iniconfig", "packaging", "pygments")


def utc():
    return datetime.now(timezone.utc).isoformat()


def bind_setup(root, source_commit, remote_ref, mode, release):
    """Check actual pushed bytes before loading the builder or scientific code."""
    gate = runpy.run_path(str(root/"python/butterfly/paired_release.py"))
    for name in ("scripts/run_paired_campaign.py", "scripts/check_paired_release.py"):
        raw = gate["committed_file"](root, source_commit, name)
        gate["read_bound"](root, dict(path=name, sha256=gate["digest"](raw)))
    checker = runpy.run_path(str(root/"scripts/check_paired_release.py"))
    observed = checker["check"](root, source_commit, remote_ref, mode=mode, release=release)
    # The numeric design is independent of release administration and is bound
    # even before a review exists. Neither its schema nor a JSON flag is authority.
    raw = gate["committed_file"](root, source_commit, PLAN)
    gate["read_bound"](root, dict(path=PLAN, sha256=gate["digest"](raw)))
    plan = json.loads(raw)
    if plan.get("schema") != "butterfly.paired-design.v1" or plan.get("experiment_id") != "EXP-481":
        raise ValueError("numeric EXP-481 design required")
    return observed, plan, hashlib.sha256(raw).hexdigest()


def require_preflight(witness, *, source_commit, plan_sha256, runtime_sha256, input_sha256, design):
    """Independently compare the completed child's result with actual host inputs."""
    from dataclasses import asdict
    from butterfly.paired_phases import phase_limits
    grid = design.validate()
    expected = dict(source_commit=source_commit, plan_sha256=plan_sha256,
        design_sha256=design.identity(), trial_counts={s: sum(t.stage == s for t in grid)
            for s in ("qualification", "collection")},
        phase_limits={s: asdict(phase_limits(design.plan, s)) for s in STAGES},
        guard_seconds=120.,
        scope="all fixed configurations validated without calling a field, integrator or map fit")
    if (witness["status"] != "passed" or witness["runtime_contract_sha256"] != runtime_sha256
            or witness["input_contract_sha256"] != input_sha256 or witness["design"] != expected
            or witness["target_execution_authorized"] is not False or witness["target_trajectories_generated"] != 0
            or "butterfly.paired_phases" not in witness["loaded_modules"]):
        raise ValueError("actual child preflight differs from independently reconstructed setup")


def select_host_runtime(runtime):
    """Use the bound minimal package; do not impersonate the sealed child.

    This host process already ran Git and normal virtualenv startup. Its
    interpreter hooks remain host trust. Only the child uses the full isolated
    import gate, with its own actual pre-import guard and startup observations.
    """
    if any(n.split(".")[0] in ("numpy", "scipy", "butterfly") for n in sys.modules):
        raise ValueError("host scientific imports preceded source/runtime binding")
    sys.path.insert(0, str(Path(runtime)/"python"))


def preflight(output, source_commit, remote_ref, *, mode="source",
              release="experiments/manifests/EXP-481-reviewed-release.json"):
    output = Path(output).absolute()
    # Preserve a failed source check too, without fabricating a successful source
    # observation. Never reuse a directory, even when no target has been launched.
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    api = runpy.run_path(str(ROOT/"python/butterfly/_paired_startup.py"))
    api["write_json"](output/"started.json", dict(started_at=utc(), mode=mode,
        source_commit=source_commit, remote_ref=remote_ref, target_execution_authorized=False,
        target_trajectories_generated=0, scope="source-bound tests and outcome-free production setup"))
    try:
        observed, plan, plan_sha = bind_setup(ROOT, source_commit, remote_ref, mode, release)
        api["write_json"](output/"source.json", observed)
        builder = runpy.run_path(str(ROOT/"scripts/build_paired_runtime.py"))
        runtime = builder["build"](output/"runtime", startup_guard_seconds=120.)
        contract = api["load_contract"](output/"runtime", runtime["sha256"])
        api["verify_runtime"](output/"runtime", contract)
        # Host-side orchestration also uses the just-bound bundle. It is not the
        # child's isolated startup receipt; the child observes its own flags/env.
        select_host_runtime(output/"runtime")
        from butterfly.paired_input_package import build_package, load_package
        from butterfly.paired_inputs import load_references
        from butterfly.paired_phases import from_reference_audit
        from butterfly.paired_supervisor import StageLimits, supervise
        inputs = build_package(ROOT/PLAN, ROOT, output/"inputs")
        if inputs["plan_sha256"] != plan_sha:
            raise ValueError("packaged design differs from pushed design")
        audit = load_references(plan, output/"inputs")
        design, _ = from_reference_audit(plan, audit, source_commit=source_commit, plan_sha256=plan_sha)
        # Bind installed test-runner package bytes as well as code/test files.
        # This is a trusted-host test run, not hermetic OS/library attestation.
        site = Path(sysconfig.get_path("purelib"))
        test_runtime = {name: api["inventory"](site/name) for name in TEST_PACKAGES}
        api["write_json"](output/"test-runtime.json", test_runtime)
        checker = runpy.run_path(str(ROOT/"scripts/check_paired_release.py"))
        tests = [f"tests/test_{name}.py" for name in checker["MANDATORY_TESTS"]]
        tests = sorted(set(tests) | {p.relative_to(ROOT).as_posix() for p in (ROOT/"tests").glob("test_paired_*.py")})
        # An untracked test cannot enter the source-qualified command.
        if mode == "source":
            allowed = observed["source_files"]
        else:
            allowed = json.loads((ROOT/release).read_bytes())["source_files"]
        if not set(tests) <= set(allowed):
            raise ValueError("test command contains a test outside the frozen closure")
        env = dict(contract["environment"], PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
        test_bootstrap = ("import runpy,sys; "
            "runpy.run_path(sys.argv[1])['install_parent_guard'](300.); "
            "import pytest; raise SystemExit(pytest.main(sys.argv[2:]))")
        argv = [sys.executable, "-I", "-B", "-c", test_bootstrap,
            str(output/"runtime/python/butterfly/_process_guard.py"), "-q",
            "-o", f"pythonpath={ROOT} {ROOT/'python'}", *tests]
        test_result = supervise(argv, cwd=ROOT, evidence_directory=output, state_directory=output/"tests",
            environment=env, binding=dict(source_commit=source_commit, plan_sha256=plan_sha,
                source_receipt_sha256=api["sha256"](output/"source.json"),
                test_runtime_sha256=api["sha256"](output/"test-runtime.json")),
            limits=StageLimits(300., 2*1024**3, 1024**3, 0))
        if test_result["status"] != "completed" or not test_result["owned_group_cleanup_verified"]:
            raise ValueError("source-qualified tests failed; no setup authorization issued")
        if test_runtime != {name: api["inventory"](site/name) for name in TEST_PACKAGES}:
            raise ValueError("test runner changed during qualification")
        evidence = output/"worker"
        evidence.mkdir(mode=0o700)
        for name in ("worker.py", "startup.py"):
            if api["sha256"](output/"runtime"/name) != contract["source_files"][name]["sha256"]:
                raise ValueError("bootstrap changed before actual preflight")
        argv = [contract["interpreter"]["path"], "-I", "-S", "-B", "-X", "utf8",
            str(output/"runtime/worker.py"), "--contract-sha256", runtime["sha256"],
            "--output-dir", str(evidence), "--mode", "design-preflight", "--input-root", str(output/"inputs"),
            "--input-contract-sha256", inputs["sha256"], "--source-commit", source_commit, "--plan-sha256", plan_sha]
        result = supervise(argv, cwd=output, evidence_directory=output, state_directory=evidence/"supervisor",
            environment=contract["environment"], binding=dict(source_commit=source_commit, plan_sha256=plan_sha,
                runtime_contract_sha256=runtime["sha256"], input_contract_sha256=inputs["sha256"]),
            limits=StageLimits(120., 2*1024**3, 1024**3, 0))
        if result["status"] != "completed" or not result["owned_group_cleanup_verified"]:
            raise ValueError("actual isolated design preflight failed")
        witness = json.loads((evidence/"design-preflight.json").read_bytes())
        if witness["audit"] != audit:
            raise ValueError("child reference audit differs from host reconstruction")
        require_preflight(witness, source_commit=source_commit, plan_sha256=plan_sha,
            runtime_sha256=runtime["sha256"], input_sha256=inputs["sha256"], design=design)
        if load_package(output/"inputs", inputs["sha256"]) != plan:
            raise ValueError("packaged inputs changed during preflight")
        api["verify_runtime"](output/"runtime", contract)
        # Repeat the live gate and committed design checks after tests and child.
        _, final_plan, final_sha = bind_setup(ROOT, source_commit, remote_ref, mode, release)
        if final_plan != plan or final_sha != plan_sha:
            raise ValueError("pushed design changed during preflight")
        receipt = dict(status="preflight-passed", completed_at=utc(), source_commit=source_commit,
            plan_sha256=plan_sha, runtime=runtime, inputs=inputs, design=witness["design"],
            target_trajectories_generated=0, target_execution_authorized=False, target_slot_consumed=False,
            mode=mode, files=api["inventory"](output),
            scope="real source-bound tests and isolated full-design setup, not phase authorization or scientific evidence")
        api["write_json"](output/"receipt.json", receipt)
        return receipt
    except (Exception, KeyboardInterrupt) as error:
        api["write_json"](output/"failure.json", dict(status="failed", failed_at=utc(),
            error_type=type(error).__name__, message=str(error), target_trajectories_generated=0,
            target_execution_authorized=False, target_slot_consumed=False))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-commit")
    parser.add_argument("--remote-ref")
    parser.add_argument("--mode", choices=("source", "reviewed", "control", "execute"), default="source")
    parser.add_argument("--release", default="experiments/manifests/EXP-481-reviewed-release.json")
    parser.add_argument("--control-fault", choices=("wrong-grant", "wrong-parent-argv", "wrong-predecessor", "missing-grant"))
    args = parser.parse_args()
    if (args.source_commit is None) != (args.remote_ref is None) or (args.mode != "control" and args.source_commit is None):
        parser.error("source commit and remote ref are required except for an explicitly local analytic control")
    if args.control_fault is not None and args.mode != "control":
        parser.error("fault injection is allowed only in analytic control mode")
    # A strict ordinary Python invocation gives the worker an OS-observable
    # parent grammar. No -c/runpy surrogate, relative executable or argv fiction.
    prefix = [sys.executable, "-B", str(Path(__file__).resolve())]
    if sys.orig_argv[:3] != prefix:
        os.execv(sys.executable, [*prefix, *sys.argv[1:]])
    if args.mode in ("source", "reviewed"):
        result = preflight(args.output_dir, args.source_commit, args.remote_ref, mode=args.mode, release=args.release)
        print(json.dumps({k: result[k] for k in ("status", "source_commit", "plan_sha256", "target_execution_authorized")}))
        return
    if any(any(c.isspace() for c in a) for a in sys.orig_argv):
        parser.error("authorized controller paths/arguments must not contain whitespace")
    if args.mode == "execute" and (ROOT/"artifacts/EXP-481/target-once.json").exists():
        raise ValueError("target attempt already claimed; inspect preserved evidence, no retry or resume")
    output = args.output_dir.absolute()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    setup = None
    if args.source_commit is not None:
        setup = output/"preflight"
        preflight(setup, args.source_commit, args.remote_ref,
            mode="reviewed" if args.mode == "execute" else "source", release=args.release)
    else:
        builder = runpy.run_path(str(ROOT/"scripts/build_paired_runtime.py"))
        built = builder["build"](output/"runtime")
        api = runpy.run_path(str(ROOT/"python/butterfly/_paired_startup.py"))
        api["verify_runtime"](output/"runtime", api["load_contract"](output/"runtime", built["sha256"]))
        select_host_runtime(output/"runtime")
    dispatch = runpy.run_path(str(ROOT/"scripts/dispatch_paired_phases.py"))["dispatch"]
    result = dispatch(ROOT, output/"campaign", setup=setup, control=args.mode == "control", fault=args.control_fault)
    print(json.dumps({k: result[k] for k in ("status", "kind", "all_cases_primary_resolved", "historical_symbols_verified")}))


if __name__ == "__main__":
    main()

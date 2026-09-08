"""Host-only fixed phase dispatch; the user-facing controller supplies authority.

No CLI loads an old preflight or a saved grant. The production command reaches
this function only after its fresh release-validated setup. The worker independently
checks that its live parent is that ordinary frozen controller invocation.
"""
from dataclasses import asdict
import json
from pathlib import Path
import runpy
import secrets
import shutil
import socket
import sys
import time


STAGES = ("qualification", "collection", "analysis")


def completed_worker(root, expected, design, phase, grant_sha256, runtime_sha256, *, target):
    """Check actual worker and supervisor receipts, then the full phase inventory."""
    from butterfly.paired_input_io import checked_input
    from butterfly.paired_phases import require_phase
    supervisor = json.loads(checked_input(root, expected["supervisor"]))
    witness = json.loads(checked_input(root, expected["witness"]))
    if (supervisor["status"] != "completed" or supervisor["returncode"] != 0
            or supervisor["owned_group_cleanup_verified"] is not True
            or supervisor["binding"]["grant_sha256"] != grant_sha256
            or witness["status"] != "completed" or witness["phase"] != phase
            or witness["grant_sha256"] != grant_sha256
            or witness["runtime_contract_sha256"] != runtime_sha256
            or witness["target_execution_authorized"] is not target
            or witness["kind"] != ("target" if target else "analytic-circle")
            or "butterfly.paired_phases" not in witness["loaded_modules"]):
        raise ValueError("actual completed worker/supervisor evidence differs from granted phase")
    return require_phase(design, root/"phase", witness["phase_receipt"], phase), witness["phase_receipt"]


def dispatch(root, output, *, setup=None, control=False, fault=None, experiment_id="EXP-481"):
    """All three phases or one preserved failure; no retry/resume parameter.

    fault is an analytic-control-only negative-test surface, never a target
    override. No target option can bypass setup, change thresholds or select a
    subset of phases, cases, initial conditions, references or analysis variants.
    """
    from butterfly._paired_startup import inventory, load_contract, sha256, verify_runtime, write_json
    from butterfly.paired_authorization import digest, issuer
    from butterfly.paired_input_package import load_package
    from butterfly.paired_inputs import load_references
    from butterfly.paired_phases import descriptor, from_reference_audit, phase_limits
    from butterfly.paired_supervisor import supervise
    if fault not in (None, "wrong-grant", "wrong-parent-argv", "wrong-predecessor", "missing-grant") or (fault and not control):
        raise ValueError("fault injection is limited to analytic controls")
    root, output = Path(root).resolve(strict=True), Path(output).absolute()
    paths = runpy.run_path(str(root/"python/butterfly/paired_release.py"))["experiment_paths"](experiment_id)
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    target_slot = root/paths["slot"]
    target_may_have_started, slot_consumed = False, False
    try:
        if setup is not None:
            setup = Path(setup).resolve(strict=True)
            preflight = json.loads((setup/"receipt.json").read_bytes())
            if (preflight["status"] != "preflight-passed" or preflight["target_execution_authorized"] is not False
                    or preflight["target_slot_consumed"] is not False or preflight["target_trajectories_generated"] != 0
                    or inventory(setup, omit=("receipt.json",)) != preflight["files"]):
                raise ValueError("fresh complete setup evidence required")
            runtime_root, runtime_sha = setup/"runtime", preflight["runtime"]["sha256"]
            preflight_sha = sha256(setup/"receipt.json")
        elif control:
            runtime_root = output.parent/"runtime"
            runtime_sha = sha256(runtime_root/"runtime-contract.json")
            preflight, preflight_sha = None, None
        else:
            raise ValueError("target dispatch requires the fresh release-validated setup")
        contract = load_contract(runtime_root, runtime_sha)
        verify_runtime(runtime_root, contract)
        if control:
            from butterfly.paired_phase_control import make_control
            design, _ = make_control()
            release_sha, release_mode, inputs, input_sha = None, None, None, None
            slot = output/"control-once.json"
        else:
            source = json.loads((setup/"source.json").read_bytes())
            gate = runpy.run_path(str(root/"python/butterfly/paired_release.py"))
            release_sha, release_mode = gate["require_release_observation"](preflight, source, experiment_id)
            inputs, input_sha = setup/"inputs", preflight["inputs"]["sha256"]
            plan = load_package(inputs, input_sha)
            if plan.get("experiment_id") != experiment_id:
                raise ValueError("setup cannot be relabeled as a different experiment")
            if sha256(inputs/"plan.json") != preflight["plan_sha256"]:
                raise ValueError("setup plan bytes changed before dispatch")
            design, _ = from_reference_audit(plan, load_references(plan, inputs),
                source_commit=preflight["source_commit"], plan_sha256=preflight["plan_sha256"])
            if design.identity() != preflight["design"]["design_sha256"]:
                raise ValueError("target design differs from the actual setup witness")
            slot = target_slot
            if slot.parent.resolve(strict=True) != slot.parent or slot.is_symlink():
                raise ValueError("canonical fixed experiment slot required")
        design.validate()
        for phase in STAGES:
            limits = phase_limits(design.plan, phase)
            if shutil.disk_usage(output).free < limits.minimum_start_free_bytes:
                raise ValueError("insufficient free space for the declared campaign")
        # This fixed experiment path, not the output name, forbids another
        # target attempt. Interrupted runs keep it. Nothing deletes or resumes it.
        write_json(slot, dict(kind="analytic-circle" if control else "target", nonce=secrets.token_hex(32),
            source_commit=design.source_commit, plan_sha256=design.plan_sha256,
            runtime_contract_sha256=runtime_sha, preflight_sha256=preflight_sha,
            release_sha256=release_sha, release_mode=release_mode, created_unix=time.time(), output=str(output)))
        slot_consumed = True
        slot_sha = sha256(slot)
        results, previous, previous_record = {}, None, None
        for phase in STAGES:
            if sha256(slot) != slot_sha:
                raise ValueError("one-use campaign slot changed")
            verify_runtime(runtime_root, contract)
            if inputs is not None and load_package(inputs, input_sha) != design.plan:
                raise ValueError("input package changed before phase grant")
            if previous_record is not None:
                completed_worker(output/previous_record["phase"], previous_record["receipts"], design,
                    previous_record["phase"], previous_record["grant_sha256"], runtime_sha, target=not control)
            evidence = output/phase
            evidence.mkdir(mode=0o700)
            limits = phase_limits(design.plan, phase)
            grant = dict(schema="butterfly.paired-phase-grant.v1", kind="analytic-circle" if control else "target",
                phase=phase, source_commit=design.source_commit, plan_sha256=design.plan_sha256,
                design_sha256=design.identity(), runtime_contract_sha256=runtime_sha,
                input_root=None if inputs is None else str(inputs), input_contract_sha256=input_sha,
                campaign_slot_sha256=slot_sha, preflight_sha256=preflight_sha,
                release_sha256=release_sha, release_mode=release_mode,
                limits=asdict(limits), deadline_monotonic=time.monotonic()+limits.wall_seconds, previous=previous)
            if fault == "wrong-predecessor" and phase == "collection":
                grant["previous"] = {**previous, "receipt": {"path": "terminal.json", "sha256": "0"*64}}
            grant_sha = digest(grant)
            write_json(evidence/"grant.json", grant)
            with _channel_pair() as pair:
                parent, child = pair
                argv = [contract["interpreter"]["path"], "-I", "-S", "-B", "-X", "utf8",
                    str(runtime_root/"worker.py"), "--contract-sha256", runtime_sha,
                    "--output-dir", str(evidence), "--mode", "authorized-phase", "--phase", phase]
                if fault != "missing-grant":
                    argv += ["--grant-fd", str(child.fileno()), "--grant-sha256", "0"*64 if fault == "wrong-grant" else grant_sha]
                controller_argv = list(sys.orig_argv)
                if fault == "wrong-parent-argv":
                    controller_argv[-1] += "-not-the-actual-argument"
                authorize = issuer(parent, grant, controller_argv)
                target_may_have_started = not control
                result = supervise(argv, cwd=output, evidence_directory=output, state_directory=evidence/"supervisor",
                    environment=contract["environment"], binding=dict(grant_sha256=grant_sha, phase=phase,
                        campaign_slot_sha256=slot_sha), limits=limits, pass_fds=(child.fileno(),),
                    on_spawn=None if fault == "missing-grant" else authorize)
            if result["status"] != "completed" or result["owned_group_cleanup_verified"] is not True:
                raise ValueError("authorized worker failed; campaign stopped without retry")
            receipts = dict(supervisor={**descriptor(evidence/"supervisor/terminal.json"), "path": "supervisor/terminal.json"},
                witness=descriptor(evidence/"phase-witness.json"))
            terminal, phase_receipt = completed_worker(evidence, receipts, design, phase, grant_sha, runtime_sha, target=not control)
            results[phase] = dict(phase=phase, grant_sha256=grant_sha, receipts=receipts,
                phase_receipt=phase_receipt, terminal=terminal)
            write_json(output/(phase+"-verified.json"), results[phase])
            previous = dict(root=str(evidence/"phase"), receipt=phase_receipt)
            previous_record = results[phase]
            print(f"{phase}: complete worker and phase evidence verified", flush=True)
        if inputs is not None:
            load_package(inputs, input_sha)
        verify_runtime(runtime_root, contract)
        if sha256(slot) != slot_sha:
            raise ValueError("campaign slot changed before completion")
        summary = dict(status="completed", kind="analytic-circle" if control else "target",
            all_cases_primary_resolved=results["analysis"]["terminal"]["all_cases_primary_resolved"],
            historical_symbols_verified=False, campaign_slot_sha256=slot_sha,
            target_slot_consumed=not control, target_trajectories_generated=0 if control else None,
            phases={s: {k: v for k, v in row.items() if k != "terminal"} for s, row in results.items()},
            files=inventory(output), automatic_retry=False, resume=False)
        write_json(output/"receipt.json", summary)
        return summary
    except (Exception, KeyboardInterrupt) as error:
        write_json(output/"failure.json", dict(status="incomplete", error_type=type(error).__name__, message=str(error),
            target_slot_consumed=(slot_consumed or target_slot.exists()) and not control,
            target_trajectories_generated=None if target_may_have_started else 0,
            target_work_may_have_started=target_may_have_started, automatic_retry=False, resume=False))
        raise


def _channel_pair():
    from contextlib import contextmanager
    @contextmanager
    def pair():
        left, right = socket.socketpair()
        try:
            yield left, right
        finally:
            left.close()
            right.close()
    return pair()

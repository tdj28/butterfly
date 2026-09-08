#!/usr/bin/env python3
"""Read-only raw replay of completed EXP-482 qualification during collection.

Never integrates, restarts, snapshots a changing collection tree, or uploads.
The fixed anchors are observations of the completed phase, not caller options.
"""
import argparse
import json
from pathlib import Path
import sys

# Support both direct-file and module invocation, as well as pytest imports.
# This is a trusted-host read-only auditor, not the isolated numerical worker.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from butterfly._paired_startup import inventory, sha256
from butterfly.paired_input_package import load_package
from butterfly.paired_inputs import load_references
from butterfly.paired_phases import from_reference_audit, _compare_qualification
from scripts.summarize_exp481_qualification import comparison_summary

RUN = ROOT/"artifacts/EXP-482/target-8ce3716"
SOURCE = "8ce37169ef9c24c570f5e2b9d5a60e48f310c377"
ANCHORS = {
    "preflight/receipt.json": "d74ae87ec66cb9ee52204c31f3f3ca78ea173231206db0847f040735177aeeb7",
    "campaign/qualification/phase/terminal.json": "6b3cd52dd120a299b1d59d4d7d34153f7a77d50d8a55bb4aec75e37e3c6e5724",
    "campaign/qualification/phase-witness.json": "fee89f609d12e4b9470a3f220b209cde594a067a4fdc2c85b838386222307a35",
    "campaign/qualification/supervisor/terminal.json": "bdf709a76d157a8d2673ff021d041ab91dc459d392474a62733ca817bcce3435",
    "campaign/qualification-verified.json": "e5b844bb7b8341e4831382d3c98c6cc42d75210871c8e6f49e20ab402231e453",
}


def check_anchors():
    for name, expected in ANCHORS.items():
        if sha256(RUN/name) != expected:
            raise ValueError("completed qualification anchor changed")


def audit():
    check_anchors()
    pre = json.loads((RUN/"preflight/receipt.json").read_bytes())
    package = RUN/"preflight/inputs"
    plan = load_package(package, pre["inputs"]["sha256"])
    if pre["source_commit"] != SOURCE or pre["mode"] != "local-audited" or plan["experiment_id"] != "EXP-482":
        raise ValueError("qualification belongs to a different release")
    design, _ = from_reference_audit(plan, load_references(plan, package),
        source_commit=SOURCE, plan_sha256=pre["plan_sha256"])
    phase = RUN/"campaign/qualification/phase"
    terminal = json.loads((phase/"terminal.json").read_bytes())
    trials = [t for t in design.validate() if t.stage == "qualification"]
    if (terminal["status"] != "completed" or terminal["passed"] is not True
            or terminal["design_sha256"] != design.identity()
            or terminal["trial_ids"] != [t.trial_id for t in trials]
            or inventory(phase, omit=("terminal.json",)) != terminal["files"]):
        raise ValueError("completed qualification phase changed or is incomplete")
    rows = {t.trial_id: json.loads((phase/"receipts"/(t.trial_id+".json")).read_bytes()) for t in trials}
    for t in trials:
        if rows[t.trial_id]["binding"] != design.binding(t) or rows[t.trial_id]["status"] != "completed":
            raise ValueError("trial identity/status differs")
    replay = _compare_qualification(design, trials, rows, phase)
    if replay != json.loads((phase/"comparisons.json").read_bytes()):
        raise ValueError("raw journal replay differs from recorded comparisons")
    if len(trials) != 128 or len(replay) != 192 or any(r["passed"] is not True for r in replay):
        raise ValueError("not all fixed numerical comparisons passed")
    supervisor = json.loads((RUN/"campaign/qualification/supervisor/terminal.json").read_bytes())
    if (supervisor["status"] != "completed" or supervisor["returncode"] != 0
            or supervisor["owned_group_cleanup_verified"] is not True):
        raise ValueError("qualification did not cleanly complete")
    if inventory(phase, omit=("terminal.json",)) != terminal["files"]:
        raise ValueError("qualification evidence changed during replay")
    check_anchors()
    return dict(experiment_id="EXP-482", source_commit=SOURCE, status="numerically-qualified",
        paid_review="not_run", release_mode="local-audited", qualification_trials=len(trials),
        comparison_count=len(replay), comparisons_passed=sum(r["passed"] for r in replay),
        raw_comparison_replay_exact=True, groups=comparison_summary(replay),
        cases={name: dict(comparisons=sum(r["candidate_id"] == name for r in replay),
            passed=sum(r["candidate_id"] == name and r["passed"] for r in replay))
            for name in sorted({r["candidate_id"] for r in replay})},
        threshold=plan["adaptive_qualification"]["maximum_scaled_event_state_difference"],
        supervisor=supervisor, historical_symbols_verified=False,
        collection_and_analysis_assessed_by_this_audit=False,
        scope="frozen early event accuracy on new diagnostic draw; no long-time, map, symbol or homoclinic result",
        run_anchors={p: dict(path=p, bytes=(RUN/p).stat().st_size, sha256=s) for p,s in ANCHORS.items()})


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(json.dumps(audit(), indent=2, sort_keys=True, allow_nan=False))

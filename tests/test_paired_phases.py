"""Fixed phase composition and failure boundaries, with no historical artifacts."""
import copy
from dataclasses import asdict, replace
import json
from pathlib import Path
import runpy
import shutil

import numpy as np
import pytest

from butterfly import paired_phases as phases
from butterfly.models import RosslerParameters, rossler_rhs
from butterfly.paired_phase_control import make_control
from butterfly.paired_sampling import SECTIONS
from scripts.build_paired_runtime import ROOT
from scripts.qualify_paired_phases import qualify


def test_phase_limits_use_each_declared_budget():
    p = json.loads((ROOT/"experiments/manifests/EXP-481-paired-sampling-proposal.json").read_bytes())
    assert [phases.phase_limits(p, s).wall_seconds for s in ("qualification", "collection", "analysis")] == [1800, 14400, 7200]
    for s in ("qualification", "collection", "analysis"):
        limit = phases.phase_limits(p, s)
        assert (limit.maximum_rss_bytes, limit.maximum_disk_bytes, limit.minimum_start_free_bytes) == (2*1024**3, 8*1024**3, 16*1024**3)
    assert not p["execution_authorized"] and p["review"] is None


@pytest.mark.parametrize("change", ["capture-time", "raw-membership", "retry", "resume", "seed", "reference", "missing-case",
    "last-profile", "adaptive-bound", "source", "plan", "window", "variants", "primary", "cohort", "proximity", "resource"])
def test_bad_full_design_refused_before_field_or_output(tmp_path, change):
    design, fields = make_control()
    p = design.plan
    if change == "capture-time": p["adaptive_qualification"]["maximum_capture_time_difference"] *= 2
    elif change == "raw-membership": p["adaptive_qualification"]["require_ordered_raw_counts_and_membership"] = False
    elif change in ("retry", "resume"): p["collection"]["automatic_retry" if change == "retry" else "resume"] = True
    elif change == "seed": design.initial[p["candidate_ids"][1]][-1, 0] += 1
    elif change == "reference":
        case, section = p["candidate_ids"][1], SECTIONS[0]
        spec = design.sections[case][section]
        design.sections[case][section] = replace(spec, cycle_states=spec.cycle_states[:1])
    elif change == "missing-case": design.sections.pop(p["candidate_ids"][1])
    elif change == "last-profile": p["adaptive_qualification"]["profiles"][-1]["max_step"] = -1
    elif change == "adaptive-bound": p["adaptive_qualification"]["maximum_adaptive_snapshot_bytes"] = 100
    elif change == "source": design.source_commit = "short"
    elif change == "plan": design.plan_sha256 = "short"
    elif change == "window": p["sample"]["observation_windows"][-1][1] = 100
    elif change == "variants": p["analysis"]["variants"].append(p["analysis"]["variants"][0])
    elif change == "primary": p["analysis"]["primary"]["axis"] = 2
    elif change == "cohort": p["sample"]["maximum_profile_retention_disagreement_fraction"] = -1
    elif change == "proximity": p["critical_membership"]["normalized_interval_padding"] = -1
    else: p["resources"]["maximum_analysis_seconds"] = 0
    def forbidden(x):
        pytest.fail("field invoked before full design validation")
    fields = dict.fromkeys(fields, forbidden)
    with pytest.raises(ValueError):
        phases.run_phase(design, "qualification", tmp_path/"phase", fields=fields)
    assert not (tmp_path/"phase").exists()


def test_reference_factory_matches_scalar_field_and_geometry_without_integration(tmp_path):
    helpers = runpy.run_path(str(ROOT/"tests/test_paired_input_package.py"))
    synthetic = helpers["synthetic_inputs"](tmp_path/"inputs")
    from butterfly.paired_inputs import load_references
    audit = load_references(synthetic, tmp_path/"inputs")
    plan = json.loads((ROOT/"experiments/manifests/EXP-481-paired-sampling-proposal.json").read_bytes())
    plan["inputs"] = synthetic["inputs"]
    design, fields = phases.from_reference_audit(plan, audit, source_commit="a"*40, plan_sha256="b"*64)
    assert len(design.validate()) == 640
    for case, row in zip(plan["candidate_ids"], audit["cases"], strict=True):
        parameters = RosslerParameters(**row["parameters"])
        x = design.initial[case][[0, 512, 8191]]
        assert np.array_equal(fields[case](x), np.array([rossler_rhs(0., state, parameters) for state in x]))
        assert np.array_equal(design.sections[case][SECTIONS[0]].cycle_states, row["references"][SECTIONS[0]]["states"])
    bad = copy.deepcopy(audit)
    bad["cases"][1]["references"][SECTIONS[0]]["section"]["offset"] += .01
    with pytest.raises(ValueError, match="geometry"):
        phases.from_reference_audit(plan, bad, source_commit="a"*40, plan_sha256="b"*64)


@pytest.fixture(scope="module")
def completed(tmp_path_factory):
    root = tmp_path_factory.mktemp("paired-phases").resolve()
    design, fields = make_control()
    qualification = phases.run_phase(design, "qualification", root/"qualification", fields=fields)
    terminal = phases.require_phase(design, root/"qualification", qualification, "qualification")
    assert terminal["passed"] and terminal["comparison_count"] == 24
    collection = phases.run_phase(design, "collection", root/"collection", fields=fields,
        previous_directory=root/"qualification", previous_receipt=qualification)
    return root, design, qualification, collection


def test_all_raw_profiles_and_both_cases_survive_real_phase_replay(completed, tmp_path):
    root, design, _, receipt = completed
    result = phases.run_phase(design, "analysis", tmp_path/"analysis", previous_directory=root/"collection", previous_receipt=receipt)
    assert result["sha256"] == phases.journal.sha256(tmp_path/"analysis/terminal.json")
    analysis = json.loads((tmp_path/"analysis/analysis.json").read_bytes())
    assert analysis["all_cases_primary_resolved"] and not analysis["historical_symbols_verified"]
    for case in design.plan["candidate_ids"]:
        row = analysis["cases"][case]
        assert row["cohort"]["global_seed_ids"] == list(range(2048)) and row["reference_row_indices"] == list(range(6))
        assert row["cohort"]["calibration_seeds"] == row["cohort"]["validation_seeds"] == 1024
        for profile in design.plan["collection"]["profiles"]:
            with np.load(tmp_path/"analysis"/f"{case}--{profile['name']}-pairs.npz") as raw:
                assert raw["retained"].all() and np.array_equal(raw["global_seed_ids"], np.arange(2048))
                assert not raw["state__failed"].any() and np.isnan(raw["state__capture_times"]).all()
                for i in range(2):
                    assert np.all(raw[f"section_{i}__section_pair_indices"] >= 0)
    with pytest.raises(FileExistsError):
        phases.run_phase(design, "analysis", tmp_path/"analysis", previous_directory=root/"collection", previous_receipt=receipt)


@pytest.mark.parametrize("change", ["missing", "extra", "changed", "wrong-digest", "wrong-design", "wrong-grid", "failed-qualification"])
def test_incomplete_or_substituted_previous_phase_blocks_field(completed, tmp_path, change):
    original, design, qualified, _ = completed
    design = copy.deepcopy(design)
    prior = tmp_path/"qualification"
    shutil.copytree(original/"qualification", prior)
    receipt = dict(qualified)
    terminal = json.loads((prior/"terminal.json").read_bytes())
    if change == "missing": next((prior/"trials").rglob("terminal.json")).rename(tmp_path/"withheld.json")
    elif change == "extra": (prior/"extra.txt").write_text("synthetic")
    elif change == "changed": next((prior/"receipts").glob("*.json")).write_text("{}")
    elif change == "wrong-digest": receipt["sha256"] = "0"*64
    elif change == "wrong-design": design.source_commit = "f"*40
    else:
        if change == "wrong-grid": terminal["trial_ids"].pop()
        else: terminal["passed"] = False
        (prior/"terminal.json").write_text(json.dumps(terminal))
        receipt = phases.descriptor(prior/"terminal.json")
    def forbidden(x):
        pytest.fail("collection started after invalid preceding phase")
    with pytest.raises(ValueError):
        phases.run_phase(design, "collection", tmp_path/"new", fields=dict.fromkeys(design.plan["candidate_ids"], forbidden),
            previous_directory=prior, previous_receipt=receipt)
    assert not (tmp_path/"new").exists()


def test_technical_failure_stops_grid_preserves_prefix_and_never_retries(tmp_path):
    design, fields = make_control()
    design.plan["adaptive_qualification"]["maximum_steps_per_seed"] = 120  # RK4 controls need 220: fail preflight
    with pytest.raises(ValueError):
        phases.run_phase(design, "qualification", tmp_path/"preflight", fields=fields)
    assert not (tmp_path/"preflight").exists()
    design, fields = make_control()
    calls = []
    def field(x):
        calls.append(len(x))
        raise RuntimeError("synthetic injected field failure")
    with pytest.raises(ValueError, match="incomplete trial"):
        phases.run_phase(design, "qualification", tmp_path/"failed", fields=dict.fromkeys(fields, field))
    assert len(calls) == 1
    assert (tmp_path/"failed/failure.json").exists() and not (tmp_path/"failed/terminal.json").exists()
    assert len(list((tmp_path/"failed/trials").iterdir())) == 1
    assert len(list((tmp_path/"failed/receipts").iterdir())) == 1
    assert next((tmp_path/"failed/trials").rglob("terminal.json")).exists()
    with pytest.raises(FileExistsError):
        phases.run_phase(design, "qualification", tmp_path/"failed", fields=fields)


def test_collection_and_analysis_require_actual_predecessor(tmp_path):
    design, fields = make_control()
    for stage in ("collection", "analysis"):
        with pytest.raises(ValueError, match="preceding phase"):
            phases.run_phase(design, stage, tmp_path/stage, fields=fields)
    with pytest.raises(ValueError, match="unknown fixed phase"):
        phases.run_phase(design, "resume", tmp_path/"other", fields=fields)


def test_exact_isolated_three_phase_command_and_bad_digest(tmp_path):
    result = qualify(tmp_path/"sealed")
    assert result["passed"] and not result["target_execution_authorized"]
    assert result["target_trajectories_generated"] == 0
    assert set(result["controls"]) == {"qualification", "collection", "analysis", "wrong-previous-digest"}
    assert all(r["supervisor"]["owned_group_cleanup_verified"] for r in result["controls"].values())

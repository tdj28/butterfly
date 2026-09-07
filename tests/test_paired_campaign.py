"""Complete campaign composition on analytic arrays, without target integration."""
import json
from pathlib import Path

import numpy as np
import pytest

from butterfly import paired_campaign as campaign
from butterfly.paired_sampling import SECTIONS, seed_commitment, seed_table


PLAN = Path(__file__).resolve().parents[1]/"experiments/manifests/EXP-481-paired-sampling-proposal.json"
SOURCE, DIGEST = "a"*40, "b"*64


def plan():
    return json.loads(PLAN.read_bytes())


def test_production_grid_is_complete_original_id_grid_without_authorizing_execution():
    p = plan()
    grid = campaign.trial_grid(p)
    qualification = [t for t in grid if t.stage == "qualification"]
    collection = [t for t in grid if t.stage == "collection"]
    assert len(qualification) == 128 and len(collection) == 512
    assert len({t.trial_id for t in grid}) == 640
    for case in p["candidate_ids"]:
        for profile in p["collection"]["profiles"]:
            selected = [t for t in collection if t.candidate_id == case and t.profile == profile["name"]]
            assert [i for t in selected for i in t.global_seed_ids] == list(range(8192))
        for seed in p["adaptive_qualification"]["global_seed_ids"]:
            assert len([t for t in qualification if t.candidate_id == case and t.global_seed_ids == (seed,)]) == 4
    assert p["execution_authorized"] is False and p["review"] is None


@pytest.mark.parametrize("change", ["split", "rectangle", "hash", "duplicate-case", "path", "batch", "duplicate-seed", "foreign-seed", "method"])
def test_changed_grid_inputs_rejected(change):
    p = plan()
    if change == "split": p["seeds"]["holdout_ids"][0] += 1
    elif change == "rectangle": p["seeds"]["xz_ranges"][0][0] = -15
    elif change == "hash": p["seeds"]["ordered_table_sha256"] = "0"*64
    elif change == "duplicate-case": p["candidate_ids"][1] = p["candidate_ids"][0]
    elif change == "path": p["candidate_ids"][0] = "../other"
    elif change == "batch": p["collection"]["batch_size"] = 63
    elif change == "duplicate-seed": p["adaptive_qualification"]["global_seed_ids"].append(0)
    elif change == "foreign-seed": p["adaptive_qualification"]["global_seed_ids"][0] = 8192
    else: p["adaptive_qualification"]["profiles"][0]["method"] = "RK45"
    with pytest.raises(ValueError):
        campaign.trial_grid(p)


def synthetic(*, count=1024, bootstrap_samples=8, batch_size=256):
    p = plan()
    table = seed_table(count)
    p["seeds"].update(count_per_case=count, global_seed_ids=[0, count-1], holdout_ids=[count//2, count-1],
        ordered_table_sha256=seed_commitment(table))
    p["adaptive_qualification"]["global_seed_ids"] = [0, count//2]
    p["analysis"]["options"]["bootstrap_samples"] = bootstrap_samples
    p["collection"]["batch_size"] = batch_size
    grid = campaign.trial_grid(p)
    ids = table["global_seed_ids"]
    # Known cubic map with turning points at .25 and .75, independent draws
    # for calibration and holdout. These are NOT Rössler return observations.
    x = np.random.Generator(np.random.PCG64(812)).random((count, 4))
    pairs = np.stack((x, .5+4*(x-.5)**3-.75*(x-.5)), axis=-1)
    states = np.zeros((count, 2, 4, 2, 3))
    states[..., 0] = pairs[:, None]
    states[..., 2] = pairs[:, None]
    by_case, initials, references = {}, {}, {}
    for index, case in enumerate(p["candidate_ids"]):
        initial = np.column_stack((table["xz"][:, 0], np.full(count, index), table["xz"][:, 1]))
        initials[case] = initial
        references[case] = np.column_stack(([.25, .75, .5, -1, 2, .1], np.zeros((6, 2))))
        by_case[case] = {}
        for name in (r["name"] for r in p["collection"]["profiles"]):
            trials = [t for t in grid if t.stage == "collection" and t.candidate_id == case and t.profile == name]
            by_case[case][name] = dict(global_seed_ids=ids.copy(), initial_states=initial.copy(),
                windows=np.array(p["sample"]["observation_windows"]), horizon=p["collection"]["horizon"],
                binding=dict(candidate_id=case, profile=name, source_commit=SOURCE, plan_sha256=DIGEST),
                batch_ids=[t.trial_id for t in trials], sources=[{} for _ in trials],
                seed_batch_index=np.repeat(np.arange(count//batch_size), batch_size), retained=np.ones(count, bool),
                counts=dict(total=count, retained=count, failed=0, ambiguous_nonfailed=0,
                    historical_only=0, barrio_only=0, both=0, neither_insufficient=0),
                pair_states={s: states.copy() for s in SECTIONS},
                pair_times={s: np.zeros((count, 2, 4, 2)) for s in SECTIONS})
    return p, by_case, initials, references


def run(data):
    p, profiles, initial, references = data
    return campaign.analyze_campaign(profiles, initial, references, p, source_commit=SOURCE, plan_sha256=DIGEST)


def test_real_both_case_analysis_reports_every_reference_row_and_model():
    result = run(synthetic())
    assert result["status"] == "analyzed" and result["all_cases_primary_resolved"]
    assert not result["historical_symbols_verified"]
    assert "reference-conditioned" in result["claim_scope"]
    assert result["reporting_thresholds"] == dict(supported_error_quantile=.9,
        maximum_supported_q90_error=.08, maximum_unsupported_fraction=.05, minimum_coverage=.7)
    for row in result["cases"].values():
        assert row["cohort"]["global_seed_ids"] == list(range(1024))
        assert row["cohort"]["calibration_seeds"] == row["cohort"]["validation_seeds"] == 512
        assert row["reference_row_indices"] == list(range(6))
        matrix = row["analysis"]["critical_matrix"]
        assert len(matrix["orbit_values"]) == 6 and len(matrix["models"]) == 20
        assert row["analysis"]["joint_primary"]["branch_count"] == 3
        assert matrix["near_every_primary_model"] == [[True, False], [False, True],
            [False, False], [False, False], [False, False], [False, False]]
        assert len(row["analysis"]["projections"]) == 3
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("change", ["case", "profile", "batch", "batch-order", "source", "plan", "seed", "initial", "reference", "window", "pair-shape", "batch-index", "counts"])
def test_incomplete_or_substituted_second_case_rejected_before_any_fit(monkeypatch, change):
    data = synthetic()
    p, profiles, initials, references = data
    case = p["candidate_ids"][1]
    profile = profiles[case][p["collection"]["profiles"][0]["name"]]
    if change == "case": del profiles[case]
    elif change == "profile": profiles[case].pop(p["collection"]["profiles"][1]["name"])
    elif change == "batch": profile["batch_ids"].pop()
    elif change == "batch-order": profile["batch_ids"].reverse()
    elif change == "source": profile["binding"]["source_commit"] = "c"*40
    elif change == "plan": profile["binding"]["plan_sha256"] = "c"*64
    elif change == "seed": profile["global_seed_ids"][0] = 1024
    elif change == "initial": initials[case][0, 0] += 1
    elif change == "reference": references[case] = references[case][:1]
    elif change == "window": profile["windows"][0, 0] += 1
    elif change == "pair-shape": profile["pair_states"][SECTIONS[0]] = profile["pair_states"][SECTIONS[0]][:, :, :1]
    elif change == "batch-index": profile["seed_batch_index"][0] = 1
    else: profile["counts"]["retained"] = 1023
    def forbidden(*args, **kwargs):
        pytest.fail("analysis started before full campaign structural validation")
    monkeypatch.setattr(campaign, "analyze_case", forbidden)
    with pytest.raises(ValueError):
        run(data)


def test_unresolved_second_case_is_retained_and_diagnostics_do_not_rescue():
    data = synthetic()
    p, profiles, _, _ = data
    second = p["candidate_ids"][1]
    for profile in profiles[second].values():
        profile["pair_states"][SECTIONS[0]][..., 0] = 0  # degenerate primary only
    result = run(data)
    assert result["status"] == "analyzed" and not result["all_cases_primary_resolved"]
    assert result["cases"][p["candidate_ids"][0]]["analysis"]["joint_primary"]["resolved"]
    failed = result["cases"][second]["analysis"]
    assert not failed["joint_primary"]["resolved"] and failed["critical_matrix"]["status"] == "not-evaluated"
    assert all(a["resolved"] for proj in failed["projections"][1:] for a in proj["audits"].values())


def test_multivalued_primary_cannot_receive_positive_turn_support():
    data = synthetic()
    p, profiles, _, _ = data
    # A known two-sheet response, with whole-seed sheet membership. Keep the
    # cubic diagnostic and identical original IDs; no coordinate may rescue x.
    signs = np.where(np.arange(1024) % 2, .35, -.35)
    for by_name in profiles.values():
        for profile in by_name.values():
            profile["pair_states"][SECTIONS[0]][..., 1, 0] += signs[:, None, None]
    result = run(data)
    assert not result["all_cases_primary_resolved"]
    for row in result["cases"].values():
        assert not row["analysis"]["joint_primary"]["resolved"]
        assert row["analysis"]["critical_matrix"]["status"] == "not-evaluated"

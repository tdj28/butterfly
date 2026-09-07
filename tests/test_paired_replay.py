"""Synthetic integration -> durable journal -> pair/cohort replay controls."""
from dataclasses import asdict, replace
import copy
import json

import numpy as np
import pytest

from butterfly import paired_journal as journal
from butterfly.paired_replay import (BatchExpectation, replay_batch, assemble_profile,
    intersect_profiles, coordinate_blocks)
from butterfly.paired_sampling import SECTIONS
from butterfly.paired_sections import CaptureSection
from butterfly.poincare import PoincareSection


def fixture(path, ids=(901, 17), *, profile="coarse", dt=.1, trial_id="batch-a"):
    initial = np.column_stack((1+np.arange(len(ids))*.1, np.zeros((len(ids), 2))))
    sections = {SECTIONS[0]: CaptureSection(PoincareSection((0, 1, 0), 0, -1),
        np.array([[-100., 0, 0]]), (0, 2), (1., 1.), .0001, 1),
        SECTIONS[1]: CaptureSection(PoincareSection((1, 0, 0), 0, 1),
        np.array([[0, -100., 0]]), (1, 2), (1., 1.), .0001, 1)}
    config = dict(dt=dt, horizon=18., checkpoint_times=[8., 16., 18.], state_scales=[1., 1., 1.],
        gate_margin=1e-5, angle_margin=1e-6, escape_radius=1000., maximum_events=1000, maximum_steps=1000)
    binding = dict(candidate_id="synthetic-circle", profile=profile, trial_id=trial_id,
                   source_commit="synthetic-source", plan_sha256="synthetic-plan")
    rhs = lambda x: np.column_stack((-np.pi/2*x[:, 1], np.pi/2*x[:, 0], np.zeros(len(x))))
    result, audit = journal.record_collection(rhs, initial, np.array(ids), sections, config,
        directory=path, binding=binding, journal_interval_steps=20)
    assert audit["status"] == "completed"
    expected = BatchExpectation(journal.sha256(path/"started.json"), journal.sha256(path/"terminal.json"),
        np.array(ids), initial, config,
        {n: {**asdict(s), "cycle_states": s.cycle_states.tolist()} for n, s in sections.items()}, binding,
        {"journal_interval_steps": 20, "maximum_snapshot_bytes": 64*1024**2})
    return result, expected


def replay(path, expected):
    return replay_batch(path, expected, [[0, 8], [8, 16]], strata_per_window=1)


def test_raw_event_indices_replay_exactly_with_global_ids(tmp_path):
    result, expected = fixture(tmp_path/"run")
    loaded = replay(tmp_path/"run", expected)
    assert loaded["retained"].all() and loaded["counts"]["retained"] == 2
    for name in SECTIONS:
        indices = loaded["section_pair_indices"][name]
        np.testing.assert_array_equal(loaded["pair_states"][name], result.events[name]["states"][indices])
        np.testing.assert_array_equal(loaded["pair_times"][name], result.events[name]["times"][indices])
    assert loaded["global_seed_ids"].tolist() == [901, 17]
    assert loaded["source"]["terminal_sha256"] == expected.terminal_sha256


@pytest.mark.parametrize("kind", ["seed", "state", "source", "config", "recording", "digest"])
def test_external_expected_contract_cannot_be_replaced_by_journal_fields(tmp_path, kind):
    _, expected = fixture(tmp_path/"run")
    if kind == "seed":
        expected = replace(expected, global_seed_ids=np.array([17, 901]))
    elif kind == "state":
        expected = replace(expected, initial_states=expected.initial_states+1)
    elif kind == "source":
        expected = replace(expected, binding={**expected.binding, "source_commit": "wrong"})
    elif kind == "config":
        expected = replace(expected, config={**expected.config, "dt": .2})
    elif kind == "recording":
        expected = replace(expected, recording={**expected.recording, "journal_interval_steps": 1})
    else:
        expected = replace(expected, terminal_sha256="0"*64)
    with pytest.raises(ValueError):
        replay(tmp_path/"run", expected)


def test_incomplete_terminal_is_rejected_even_with_its_correct_hash(tmp_path):
    _, expected = fixture(tmp_path/"run")
    path = tmp_path/"run/terminal.json"
    terminal = json.loads(path.read_bytes())
    terminal.update(collection_complete=False, status="incomplete", collector_status="interrupted")
    path.write_text(json.dumps(terminal))
    expected = replace(expected, terminal_sha256=journal.sha256(path))
    with pytest.raises(ValueError, match="complete audited"):
        replay(tmp_path/"run", expected)


def assembled(tmp_path, profile="coarse", dt=.1):
    batches = {}
    for name, ids in (("batch-a", (901, 24)), ("batch-b", (17, 8))):
        path = tmp_path/f"{profile}-{name}"
        _, expected = fixture(path, ids, profile=profile, dt=dt, trial_id=name)
        batches[name] = replay(path, expected)
    ids = np.array([901, 17, 24, 8])
    initial = np.array([[1., 0, 0], [1., 0, 0], [1.1, 0, 0], [1.1, 0, 0]])
    return assemble_profile(batches, ["batch-a", "batch-b"], ids, initial), batches


def test_assembly_preserves_global_order_and_replay_batch_provenance(tmp_path):
    profile, batches = assembled(tmp_path)
    assert profile["global_seed_ids"].tolist() == [901, 17, 24, 8]
    assert profile["seed_batch_index"].tolist() == [0, 1, 0, 1]
    other = assemble_profile(batches, ["batch-b", "batch-a"], profile["global_seed_ids"], profile["initial_states"])
    np.testing.assert_array_equal(other["pair_states"][SECTIONS[0]], profile["pair_states"][SECTIONS[0]])
    for invalid in ({"batch-a": batches["batch-a"]}, {**batches, "extra": batches["batch-a"]}):
        with pytest.raises(ValueError, match="batch set"):
            assemble_profile(invalid, ["batch-a", "batch-b"], profile["global_seed_ids"], profile["initial_states"])


def test_duplicate_seed_and_mislabeled_batch_rejected(tmp_path):
    profile, batches = assembled(tmp_path)
    for kind in ("duplicate", "identity"):
        bad = copy.deepcopy(batches)
        if kind == "duplicate":
            bad["batch-b"]["global_seed_ids"][0] = 901
        else:
            bad["batch-b"]["binding"]["trial_id"] = "batch-a"
        with pytest.raises(ValueError):
            assemble_profile(bad, ["batch-a", "batch-b"], profile["global_seed_ids"], profile["initial_states"])


def test_cohort_intersection_reports_disagreement_and_does_not_refill(tmp_path):
    a, _ = assembled(tmp_path)
    b, _ = assembled(tmp_path, "fine", .05)
    b["retained"][0] = False  # deliberate synthetic mask difference
    b["counts"].update(retained=3, neither_insufficient=1)
    cohort = intersect_profiles({"coarse": a, "fine": b}, ["coarse", "fine"], a["global_seed_ids"],
                                np.array([False, False, True, True]), minimum_seeds=1)
    assert cohort["retained"].tolist() == [False, True, True, True]
    assert cohort["intersection_loss"] == {"coarse": 1, "fine": 0}
    assert cohort["disagreement_fraction"] == .25 and not cohort["joint_population_passed"]
    blocks = coordinate_blocks(a, cohort, SECTIONS[0], 0, 0)
    assert blocks["calibration_ids"].tolist() == [17] and blocks["validation_ids"].tolist() == [24, 8]
    assert blocks["calibration"].shape == (1, 1, 2)


def test_matching_profiles_and_empty_common_cohort_are_distinct(tmp_path):
    a, _ = assembled(tmp_path)
    b = copy.deepcopy(a)
    b["binding"]["profile"] = "fine"
    split = np.array([False, False, True, True])
    kwargs = dict(minimum_seeds=2)
    result = intersect_profiles({"coarse": a, "fine": b}, ["coarse", "fine"], a["global_seed_ids"], split, **kwargs)
    assert result["joint_population_passed"]
    a["retained"][:] = False
    b["retained"][:] = False
    for profile in (a, b):
        profile["counts"].update(retained=0, neither_insufficient=4)
    result = intersect_profiles({"coarse": a, "fine": b}, ["coarse", "fine"], a["global_seed_ids"], split, **kwargs)
    assert result["retention_compatible"] and not result["sufficient_seeds"] and not result["joint_population_passed"]


def test_foreign_candidate_or_missing_profile_cannot_join(tmp_path):
    a, _ = assembled(tmp_path)
    b = copy.deepcopy(a)
    b["binding"].update(profile="fine", candidate_id="other-candidate")
    for profiles in ({"coarse": a}, {"coarse": a, "fine": b}):
        with pytest.raises(ValueError):
            intersect_profiles(profiles, ["coarse", "fine"], a["global_seed_ids"],
                               np.array([False, False, True, True]), minimum_seeds=1)


def test_population_totals_cannot_hide_excluded_seeds(tmp_path):
    a, _ = assembled(tmp_path)
    b = copy.deepcopy(a)
    b["binding"]["profile"] = "fine"
    b["retained"][0] = False
    with pytest.raises(ValueError, match="population counts"):
        intersect_profiles({"coarse": a, "fine": b}, ["coarse", "fine"], a["global_seed_ids"],
                           np.array([False, False, True, True]), minimum_seeds=1)

"""Adaptive/RK4 analytic agreement and partial-prefix failure controls."""
from dataclasses import replace
import copy

import numpy as np
import pytest

from butterfly.paired_adaptive import collect_adaptive_sections, compare_event_profiles, rk4_comparison_record
from butterfly.paired_sections import CaptureSection, collect_paired_sections
from butterfly.paired_sampling import SECTIONS
from butterfly.poincare import PoincareSection


def field(x):
    return np.column_stack((-x[:, 1], x[:, 0], np.zeros(len(x))))


def sections():
    return {SECTIONS[0]: CaptureSection(PoincareSection((0, 1, 0), 0, -1),
        np.array([[-1., 0, 0]]), (0, 2), (1., 1.), .01, 1),
        SECTIONS[1]: CaptureSection(PoincareSection((1, 0, 0), 0, 1),
        np.array([[0, -1., 0]]), (1, 2), (1., 1.), .01, 1)}


COMMON = dict(horizon=13., state_scales=[1., 1., 1.], gate_margin=1e-5, angle_margin=1e-6,
              escape_radius=1000., maximum_steps=10000, maximum_events=1000)


def adaptive(method="DOP853", **changes):
    args = dict(method=method, rtol=1e-10, atol=1e-12, max_step=.05,
                maximum_field_evaluations=100000, **COMMON)
    args.update(changes)
    return collect_adaptive_sections(field, [1., 0, 0], 901, sections(), **args)


def compare(a, b):
    return compare_event_profiles(a, b, state_scales=[1., 1., 1.],
                                  maximum_state_difference=1e-4, maximum_time_difference=1e-4)


@pytest.mark.parametrize("method", ["DOP853", "Radau"])
def test_analytic_crossings_capture_continues_and_both_rk4_profiles_agree(method):
    result = adaptive(method)
    assert result["completed"] and result["observed_until"] == 13
    assert result["initial_on_plane"].tolist() == [[True, False]]
    np.testing.assert_allclose(result["capture_times"], [[np.pi, 1.5*np.pi]], atol=1e-9)
    for name, expected in zip(SECTIONS, ([np.pi, 3*np.pi], [1.5*np.pi, 3.5*np.pi])):
        e = result["events"][name]
        np.testing.assert_allclose(e["times"][e["accepted"]], expected, atol=1e-9)
        assert (e["times"] > 0).all() and (e["global_seed_ids"] == 901).all()
    for dt in (.01, .005):
        rk = collect_paired_sections(field, np.array([[1., 0, 0]]), sections(), dt=dt,
            checkpoint_times=[13.], **COMMON)
        comparison = compare(result, rk4_comparison_record(rk, 901))
        assert comparison["passed"], comparison


@pytest.mark.parametrize("limit", ["maximum_steps", "maximum_field_evaluations", "maximum_events"])
def test_caps_preserve_consistent_incomplete_prefix(limit):
    value = {"maximum_steps": 100, "maximum_field_evaluations": 1500, "maximum_events": 1}[limit]
    result = adaptive(**{limit: value})
    assert result["status"] == "failed" and not result["completed"]
    assert result["observed_until"] < result["horizon"]
    assert result["integration_times"][-1] == result["observed_until"]
    np.testing.assert_array_equal(result["integration_states"][-1], result["final_states"][0])
    assert all(np.all(e["times"] <= result["observed_until"]) for e in result["events"].values())
    assert not compare(result, result)["passed"]


def test_progress_is_detached_and_final_callback_explicitly_completed():
    snapshots = []
    def callback(snapshot):
        snapshots.append(snapshot)
        snapshot["final_states"][:] = 500
    result = adaptive(progress=callback, recording_interval=1, horizon=.1)
    assert result["completed"] and snapshots[-1]["completed"]
    assert snapshots[-2]["status"] == "running"
    assert result["final_states"][0, 0] < 2


def test_failed_callback_is_not_retried_or_marked_complete():
    calls = []
    def callback(snapshot):
        calls.append(snapshot)
        raise OSError("synthetic recording failure")
    result = adaptive(progress=callback, recording_interval=2)
    assert len(calls) == 1 and result["status"] == "failed"
    assert result["completed_steps"] == 2 and result["failure"]["phase"] == "recording"


def test_interrupt_and_bad_field_keep_prefix():
    for error in (KeyboardInterrupt, ValueError):
        calls = 0
        def broken(x):
            nonlocal calls
            calls += 1
            if calls > 100:
                raise error("synthetic failure")
            return field(x)
        result = collect_adaptive_sections(broken, [1., 0, 0], 901, sections(), method="DOP853",
            rtol=1e-10, atol=1e-12, max_step=.05, maximum_field_evaluations=10000, **COMMON)
        assert result["status"] == ("interrupted" if error is KeyboardInterrupt else "failed")
        assert 0 < result["observed_until"] < 13


def test_gate_edge_is_nominally_rejected_and_explicitly_ambiguous():
    specs = sections()
    specs[SECTIONS[0]] = replace(specs[SECTIONS[0]], section=PoincareSection((0, 1, 0), 0, -1, 2, 0.))
    result = collect_adaptive_sections(field, [1., 0, 0], 901, specs, method="DOP853",
        rtol=1e-10, atol=1e-12, max_step=.05, maximum_field_evaluations=100000, **COMMON)
    event = result["events"][SECTIONS[0]]
    assert not event["accepted"].any() and event["gate_unresolved"].any()
    assert result["ambiguous"][0, 0] and np.isnan(result["capture_times"][0, 0])
    assert not compare(result, result)["passed"]


def test_sliding_plane_and_initial_escape_cannot_qualify():
    zero = lambda x: np.zeros_like(x)
    result = collect_adaptive_sections(zero, [0., 0, 0], 901, sections(), method="DOP853",
        rtol=1e-10, atol=1e-12, max_step=.05, maximum_field_evaluations=100000, **COMMON)
    assert result["completed"] and result["ambiguous"].all() and not compare(result, result)["passed"]
    escaped = adaptive(escape_radius=.5)
    assert not escaped["completed"] and escaped["observed_until"] == 0


@pytest.mark.parametrize("kind", ["seed", "count", "orientation", "time", "state", "capture", "raw-ambiguity"])
def test_comparison_does_not_align_away_mismatches(kind):
    a = adaptive()
    b = copy.deepcopy(a)
    e = b["events"][SECTIONS[0]]
    if kind == "seed":
        b["global_seed_ids"][0] += 1
        with pytest.raises(ValueError):
            compare(a, b)
        return
    if kind == "count":
        for k in e:
            e[k] = e[k][1:]
    elif kind == "orientation":
        e["orientation"][0] *= -1
    elif kind == "time":
        e["times"][0] += .001
    elif kind == "state":
        e["states"][0, 0] += .001
    elif kind == "capture":
        b["capture_times"][0, 0] = np.nan
    else:
        # Even two equally forged summaries cannot hide ambiguous raw roots.
        a["events"][SECTIONS[0]]["gate_unresolved"][0] = True
        e["gate_unresolved"][0] = True
    assert not compare(a, b)["passed"]


@pytest.mark.parametrize("change", [{"method": "unknown"}, {"rtol": 1e-30}, {"max_step": np.nan},
                                    {"recording_interval": 0}, {"maximum_events": -1}])
def test_invalid_config_fails_before_rhs(change):
    with pytest.raises(ValueError):
        adaptive(**change)

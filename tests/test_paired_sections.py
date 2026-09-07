"""EXP-481 collector engineering controls: analytic/synthetic fields only."""
from dataclasses import replace

import numpy as np
import pytest

from butterfly.paired_sections import CaptureSection, collect_paired_sections, rk4_step
from butterfly.poincare import PoincareSection


def circle(states):
    return np.column_stack((-np.pi/2*states[:, 1], np.pi/2*states[:, 0], np.zeros(len(states))))


def specs():
    return {"historical": CaptureSection(PoincareSection((0, 1, 0), 0, -1, 0, 0),
                np.array([[-1., 0, 0], [-3., 0, 0]]), (0, 1), (1., 1.), .01, 2),
            "barrio": CaptureSection(PoincareSection((1, 0, 0), 0, 1),
                np.array([[0, -2., 0], [0, -3., 0]]), (0, 1), (1., 1.), .01, 2)}


def collect(**overrides):
    args = dict(rhs=circle, initial_states=[[r, 0, 0] for r in (1, 2, 3, 4)], sections=specs(),
                dt=.05, horizon=11.5, checkpoint_times=[5., 11.5], state_scales=[1., 1., 1.],
                gate_margin=1e-4, angle_margin=1e-4, escape_radius=100., maximum_events=1000, maximum_steps=1000)
    args.update(overrides)
    return collect_paired_sections(**args)


def test_all_capture_categories_share_complete_trajectories():
    result = collect()
    assert result.status == "completed" and result.completed_steps == result.requested_steps
    assert result.contingency() == {"neither": 1, "first_only": 1, "second_only": 1, "both": 1,
                                    "failed": 0, "ambiguous_nonfailed": 0}
    assert result.capture_times[:, 0] == pytest.approx([6., np.nan, 6., np.nan], abs=1e-5, nan_ok=True)
    assert result.capture_times[:, 1] == pytest.approx([np.nan, 7., 7., np.nan], abs=1e-5, nan_ok=True)
    # Both-captured seed 2 still reaches 11.5 and has late events on BOTH planes.
    for event in result.events.values():
        assert event["times"][event["seed_ids"] == 2].max() > 9
        assert set(event["orientation"]) == {-1, 1}
        assert (~event["accepted"]).any()
    assert not result.failed.any() and not result.ambiguous.any()
    theta = 11.5*np.pi/2
    expected = np.array([[r*np.cos(theta), r*np.sin(theta), 0] for r in (1, 2, 3, 4)])
    np.testing.assert_allclose(result.final_states, expected, atol=3e-5)
    np.testing.assert_array_equal(result.checkpoints[-1]["captured"], np.isfinite(result.capture_times))
    assert result.initial_on_plane[:, 0].all()
    assert all(np.all(x["times"] > 0) for x in result.events.values())


def test_refinement_keeps_ids_membership_and_chronology():
    base, refined = collect(), collect(dt=.025)
    for name in base.events:
        a, b = base.events[name], refined.events[name]
        for key in ("seed_ids", "accepted", "orientation"):
            np.testing.assert_array_equal(a[key], b[key])
        np.testing.assert_allclose(a["times"], b["times"], atol=5e-6)
        np.testing.assert_allclose(a["states"], b["states"], atol=5e-6)


def test_no_batch_order_dependence_and_inputs_are_unchanged():
    initial = np.array([[r, 0., 0.] for r in (1, 2, 3, 4)])
    original = initial.copy()
    a, b = collect(initial_states=initial), collect(initial_states=initial[::-1])
    np.testing.assert_array_equal(initial, original)
    np.testing.assert_allclose(a.final_states, b.final_states[::-1])
    np.testing.assert_allclose(a.capture_times, b.capture_times[::-1])


def test_gate_ambiguous_rejected_events_remain_and_do_not_capture():
    sections = specs()
    sections["historical"] = replace(sections["historical"],
        section=replace(sections["historical"].section, gate_upper=-1-5e-5))
    result = collect(sections=sections)
    events = result.events["historical"]
    selected = (events["seed_ids"] == 0) & (events["orientation"] == -1)
    assert selected.sum() == 3
    assert events["gate_unresolved"][selected].all()
    assert not events["accepted"][selected].any()
    assert result.ambiguous[0, 0] and np.isnan(result.capture_times[0, 0])


def test_event_cap_stops_before_committing_either_section_of_overflow_step():
    result = collect(maximum_events=1)
    assert result.status == "event-limit"
    assert result.completed_steps < result.requested_steps
    assert result.failure["attempted_step"] == result.completed_steps+1
    assert result.failure["uncommitted_step_events"] == 4
    assert all(len(x["times"]) == 0 for x in result.events.values())
    assert not np.isfinite(result.capture_times).any()
    theta = result.completed_steps*.05*np.pi/2
    np.testing.assert_allclose(result.final_states[0], [np.cos(theta), np.sin(theta), 0], atol=1e-6)


def test_failure_after_capture_does_not_erase_capture_or_earlier_raw_events():
    def finite_lifetime(states):
        field = circle(states)
        field[:, 2] = 1
        field[states[:, 2] > 8] = np.nan
        return field
    result = collect(rhs=finite_lifetime, initial_states=[[3, 0, 0], [3, 0, -20]])
    assert result.status == "completed" and result.failed.tolist() == [True, False]
    assert np.isfinite(result.capture_times).all()
    assert not np.isfinite(result.failure_states[0]).all()
    assert result.failure_steps[0] > 140  # after both section capture times
    for event in result.events.values():
        assert (event["seed_ids"] == 0).any()
        assert event["times"][event["seed_ids"] == 1].max() > 9
    assert result.contingency()["failed"] == 1


def test_field_interrupt_returns_prefix_without_retry():
    calls = 0
    def interrupted(states):
        nonlocal calls
        calls += 1
        if calls == 80:
            raise KeyboardInterrupt("synthetic")
        return circle(states)
    result = collect(rhs=interrupted)
    assert result.status == "interrupted" and calls == 80
    assert 0 < result.completed_steps < result.requested_steps
    assert result.failure["type"] == "KeyboardInterrupt"


def test_sliding_plane_is_unresolved_not_a_false_no_return():
    result = collect(rhs=lambda states: np.zeros_like(states))
    assert result.status == "completed"
    assert result.ambiguous[:, 0].all()
    assert result.contingency()["ambiguous_nonfailed"] == 4


@pytest.mark.parametrize("changes", [
    {"dt": float("nan")}, {"dt": .03}, {"maximum_steps": 10}, {"maximum_events": 0},
    {"state_scales": [1, 0, 1]}, {"checkpoint_times": [11.5, 5]}, {"checkpoint_times": [5]},
    {"initial_states": [[0, float("nan"), 0]]}, {"sections": {"only": specs()["barrio"]}},
])
def test_invalid_design_rejected_before_field_call(changes):
    def forbidden(states):
        pytest.fail("field called before design validation")
    with pytest.raises(ValueError):
        collect(rhs=forbidden, **changes)


def test_rk4_matches_analytic_one_step_without_an_orbit_corrector():
    step = rk4_step(circle, np.array([[1., 0, 0]]), .001)
    np.testing.assert_allclose(step[0], [np.cos(np.pi/2000), np.sin(np.pi/2000), 0], atol=1e-14)


def test_rk4_arithmetic_matches_existing_kernel_on_synthetic_field(monkeypatch):
    from butterfly import saddle
    monkeypatch.setattr(saddle, "_rossler_rhs_batch", lambda states, ignored: circle(states))
    states = np.array([[1., 0, 0], [.5, .7, .01]])
    np.testing.assert_array_equal(rk4_step(circle, states, .1), saddle._rk4_batch_step(states, .1, None))


def test_interrupt_mid_commit_restores_a_consistent_two_section_prefix():
    class InterruptedSections(dict):
        calls = 0
        def items(self):
            self.calls += 1
            for index, entry in enumerate(super().items()):
                if self.calls == 82 and index == 1:
                    raise KeyboardInterrupt("between section commits")
                yield entry
    result = collect(sections=InterruptedSections(specs()))
    assert result.status == "interrupted" and result.completed_steps == 40
    assert not np.isfinite(result.capture_times).any()
    for events in result.events.values():
        assert np.all(events["steps"] <= 40)
    # First section's new downward root in step 41 was NOT committed alone.
    assert len(result.events["historical"]["times"]) == 0
    expected = np.array([[-r, 0., 0.] for r in (1, 2, 3, 4)])
    np.testing.assert_allclose(result.final_states, expected, atol=5e-6)


def test_initial_escape_never_calls_field_with_empty_batch():
    def forbidden(states):
        pytest.fail("no trajectories are active")
    result = collect(rhs=forbidden, initial_states=[[101., 0, 0]])
    assert result.status == "completed" and result.failed.all()
    assert result.failure_steps.tolist() == [0]
    assert len(result.checkpoints) == 2
    assert result.contingency()["failed"] == 1


def test_weak_crossing_orientation_is_excluded_before_capture():
    def weak(states):
        return np.column_stack((-1e-8*np.pi/2*states[:, 1],
                                 np.pi/2*states[:, 0]/1e-8, -np.pi/2*states[:, 1]))
    result = collect(rhs=weak, initial_states=[[1e-8, 0, 1]])
    assert result.status == "completed"
    assert result.events["barrio"]["orientation_unresolved"].all()
    assert result.ambiguous[0, 1] and np.isnan(result.capture_times[0, 1])


def test_exact_step_endpoint_has_one_root_and_no_duplicate_next_step():
    sections = {str(offset): CaptureSection(PoincareSection((1, 0, 0), offset, 1),
                    np.array([[offset, 0, 0]]), (1, 2), (1., 1.), .01, 1) for offset in (1, 2)}
    result = collect(rhs=lambda states: np.tile([1., 0, 0], (len(states), 1)),
                     initial_states=[[0., 0, 0]], sections=sections, dt=.5,
                     horizon=3., checkpoint_times=[3.])
    assert result.status == "completed"
    for name, event in result.events.items():
        assert event["times"] == pytest.approx([float(name)], abs=1e-12)


def test_unequal_section_event_counts_do_not_change_shared_population():
    # Exact curve: x=cos(wt), y=sin(wt), z=sin(2wt), w=pi/2.
    # One downward y return versus two upward z returns per period.
    def doubled_projection(states):
        field = circle(states)
        x, y = states[:, 0], states[:, 1]
        field[:, 2] = np.pi*(x*x-y*y)/(x*x+y*y)
        return field
    sections = specs()
    sections["barrio"] = CaptureSection(PoincareSection((0, 0, 1), 0, 1),
        np.array([[1., 0, 0], [-1., 0, 0]]), (0, 1), (1., 1.), .01, 2)
    result = collect(rhs=doubled_projection, initial_states=[[1., 0, 0]], sections=sections)
    assert result.status == "completed" and not result.ambiguous.any()
    counts = []
    for event in result.events.values():
        window = event["accepted"] & (event["times"] >= 1) & (event["times"] < 9)
        counts.append(int(window.sum()))
        assert event["times"].max() > 10
    assert counts == [2, 4]
    np.testing.assert_allclose(result.capture_times[0], [6., 4.], atol=1e-4)
    assert result.contingency()["both"] == 1

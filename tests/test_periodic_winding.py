"""Exact circles challenge geometry, period multiplicity and actual solvers."""
from copy import deepcopy

import numpy as np
import pytest

from butterfly.poincare import PoincareSection
from butterfly import periodic_winding as g


def circle(method="DOP853", multiplicity=1):
    field = lambda t, q: np.array([-q[1], q[0], 0.])
    period = multiplicity*2*np.pi
    sections = dict(historical=PoincareSection((0., 1., 0.), 0., -1, 0, 0.),
                    barrio=PoincareSection((1., 0., 0.), 0., 1))
    kept = []
    raw, report = g.observe(field, np.array([np.cos(.2), np.sin(.2), 0.]), period, sections,
                            dict(method=method, rtol=1e-12, atol=1e-14, max_step=.01), kept.append)
    metric = g.measure_cycle(raw["times"], raw["states"], report["extrema"], report["events"], period, np.zeros(3), field)
    return raw, report, metric, kept, field


@pytest.mark.parametrize("method", ["DOP853", "Radau"])
@pytest.mark.parametrize("multiplicity", [1, 2])
def test_actual_solver_consumer_known_orbit(method, multiplicity):
    period = 2*np.pi*multiplicity
    raw, report, metric, kept, field = circle(method, multiplicity)
    assert len(kept) == 1 and not report["uncertain_extrema"]
    assert metric["qualified"] is (multiplicity == 1)
    for window in metric["windows"]:
        assert window["counts"] == dict(historical=multiplicity, barrio=multiplicity)
        assert window["geometry"]["midpoint_enriched"]["cut_index"] == multiplicity
        assert abs(window["geometry"]["midpoint_enriched"]["angle_change"]-2*np.pi*multiplicity) < 1e-10
        assert window["conditional_minimal_period"] is (multiplicity == 1)
        if multiplicity == 2:
            assert window["shorter_periods"][0]["scaled_separation"] < 1e-8
    assert metric["repeat"]["passed"]
    for t in np.linspace(0., period*2.5, 57):
        np.testing.assert_allclose(g.dense_value(raw, method, t),
                                   [np.cos(t+.2), np.sin(t+.2), 0.], rtol=0, atol=1e-10)
    for rows in report["events"].values():
        for e in rows:
            np.testing.assert_allclose(g.dense_value(raw, method, e["time"]), e["state"], rtol=0, atol=1e-13)


def test_missing_event_cannot_construct_a_winding():
    raw, report, metric, kept, field = circle()
    report["events"]["historical"] = []
    altered = g.measure_cycle(raw["times"], raw["states"], report["extrema"], report["events"], 2*np.pi, np.zeros(3), field)
    assert not altered["qualified"]
    assert altered["windows"][0]["geometry"]["raw"]["cut_index"] == 1


@pytest.mark.parametrize("change", ["counts", "state", "phase"])
def test_pair_rejects_disagreement(change):
    window = dict(counts=dict(historical=1, barrio=1),
        event_states=dict(historical=[[1., 2., 3.]], barrio=[[2., 3., 4.]]),
        event_phases=dict(historical=[.2], barrio=[.4]))
    other = deepcopy(window)
    if change == "counts":
        other["counts"]["historical"] = 2
    elif change == "state":
        other["event_states"]["historical"][0][2] += 1e-5
    else:
        other["event_phases"]["historical"][0] += .01
    assert not g.compare_windows(window, other)["passed"]


def test_origin_contact_and_undersampling_remain_unqualified():
    from butterfly.projected_winding import polygon_measure
    assert not polygon_measure([[1., 0.], [-1., 0.], [1., 0.]])["qualified"]
    assert not polygon_measure([[1., 0.], [-1., .01], [1., 0.]])["qualified"]


def test_interpolation_refuses_outside_mesh():
    with pytest.raises(ValueError):
        g.interpolate(np.array([0., 1.]), np.zeros((2, 3)), lambda t,q:q, 2.)

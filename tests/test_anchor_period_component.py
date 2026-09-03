import numpy as np

from scripts.select_anchor_period_component import anchor_component, probe_memberships


def test_anchor_component_uses_eight_connectivity() -> None:
    periods = np.asarray([[6, -1, -1], [-1, 6, -1], [-1, -1, 6]])
    assert anchor_component(periods, (1, 1), 6) == [(0, 0), (1, 1), (2, 2)]


def test_anchor_component_does_not_select_an_unanchored_island() -> None:
    periods = np.asarray([[6, 6, -1], [-1, -1, -1], [-1, 6, 6]])
    assert anchor_component(periods, (0, 0), 6) == [(0, 0), (0, 1)]


def test_anchor_component_returns_empty_when_anchor_has_wrong_period() -> None:
    assert anchor_component(np.asarray([[5, 6], [6, 6]]), (0, 0), 6) == []


def test_probe_memberships_report_nearest_grid_and_component() -> None:
    periods = np.asarray([[6, 6, 3], [6, 6, 3]])
    probes = [
        {"id": "on-component", "a": 0.11, "b": 0.2, "c": 6.39},
        {"id": "off-component", "a": 0.2, "b": 0.2, "c": 7.2},
    ]
    results = probe_memberships(
        periods,
        np.asarray([0.1, 0.2]),
        np.asarray([6.0, 6.4, 7.2]),
        probes,
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        b=0.2,
    )
    assert results[0]["grid_index"] == [0, 1]
    assert results[0]["period"] == 6
    assert results[0]["in_anchor_component"] is True
    assert results[1]["grid_index"] == [1, 2]
    assert results[1]["period"] == 3
    assert results[1]["in_anchor_component"] is False

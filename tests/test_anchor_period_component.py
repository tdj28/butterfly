import numpy as np

from scripts.select_anchor_period_component import anchor_component


def test_anchor_component_uses_eight_connectivity() -> None:
    periods = np.asarray([[6, -1, -1], [-1, 6, -1], [-1, -1, 6]])
    assert anchor_component(periods, (1, 1), 6) == [(0, 0), (1, 1), (2, 2)]


def test_anchor_component_does_not_select_an_unanchored_island() -> None:
    periods = np.asarray([[6, 6, -1], [-1, -1, -1], [-1, 6, 6]])
    assert anchor_component(periods, (0, 0), 6) == [(0, 0), (0, 1)]


def test_anchor_component_returns_empty_when_anchor_has_wrong_period() -> None:
    assert anchor_component(np.asarray([[5, 6], [6, 6]]), (0, 0), 6) == []

from __future__ import annotations

import numpy as np

from scripts.qualify_jones_gap_sprinkler_parity import _ensemble


class _Section:
    offset = -0.01


def test_jones_gap_ensemble_places_grid_on_y_section() -> None:
    values = _ensemble(
        _Section(),
        {
            "x_range": [-3.0, -1.0],
            "x_count": 3,
            "z_range": [0.01, 0.02],
            "z_count": 2,
        },
    )
    assert values.shape == (6, 3)
    assert np.all(values[:, 1] == -0.01)
    assert set(values[:, 0]) == {-3.0, -2.0, -1.0}
    assert set(values[:, 2]) == {0.01, 0.02}

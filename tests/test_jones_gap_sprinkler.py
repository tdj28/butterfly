from __future__ import annotations

import numpy as np

from scripts.qualify_jones_gap_sprinkler import _physical_local_result


def test_physical_local_result_maps_normalized_location_and_checks_prediction() -> None:
    result = _physical_local_result(
        np.asarray((-30.0, -20.0, -10.0)),
        {"normalized_location": 0.6},
        {"physical_location": -18.1, "maximum_absolute_error": 0.2},
    )
    assert result["physical_location"] == -18.0
    assert np.isclose(result["absolute_prediction_error"], 0.1)
    assert result["prediction_passed"]


def test_physical_local_result_retains_unresolved_prediction_failure() -> None:
    result = _physical_local_result(
        np.asarray((-30.0, -20.0, -10.0)),
        {"normalized_location": None},
        {"physical_location": -18.1, "maximum_absolute_error": 0.2},
    )
    assert result["physical_location"] is None
    assert not result["prediction_passed"]

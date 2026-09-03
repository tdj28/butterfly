import numpy as np

from scripts.bridge_jones_returning_period12_child import SCHEMA, interpolate_event


def test_returning_child_bridge_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-returning-period12-child-bridge-manifest.v1"


def test_interpolate_event_preserves_endpoints_and_midpoint():
    left = {"a": 1.0, "b": 2.0, "c": 3.0, "initial_state": [1, 2, 3], "period_time": 4.0}
    right = {"a": 3.0, "b": 2.0, "c": 5.0, "initial_state": [3, 4, 5], "period_time": 8.0}
    middle = interpolate_event(left, right, 0.5)
    assert middle["a"] == 2.0
    assert middle["c"] == 4.0
    assert middle["period_time"] == 6.0
    np.testing.assert_allclose(middle["initial_state"], [2, 3, 4])

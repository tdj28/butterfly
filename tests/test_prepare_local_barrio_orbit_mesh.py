import numpy as np
import pytest

from scripts.prepare_local_barrio_orbit_mesh import local_grid


def test_local_grid_is_inclusive_and_contains_required_center():
    a_values, c_values = local_grid(
        {
            "a_range": [0.2154, 0.2157],
            "a_count": 31,
            "c_range": [7.2, 7.52],
            "c_count": 81,
            "required_center": {"a": 0.21555, "c": 7.372},
        }
    )
    assert len(a_values) == 31
    assert len(c_values) == 81
    assert a_values[[0, -1]].tolist() == pytest.approx([0.2154, 0.2157])
    assert c_values[[0, -1]].tolist() == pytest.approx([7.2, 7.52])
    assert np.any(np.isclose(a_values, 0.21555, rtol=0.0, atol=1e-14))
    assert np.any(np.isclose(c_values, 7.372, rtol=0.0, atol=1e-13))


def test_local_grid_rejects_a_missing_required_center():
    with pytest.raises(ValueError, match="absent from the c grid"):
        local_grid(
            {
                "a_range": [0.0, 0.2],
                "a_count": 3,
                "c_range": [1.0, 2.0],
                "c_count": 3,
                "required_center": {"a": 0.1, "c": 1.3},
            }
        )

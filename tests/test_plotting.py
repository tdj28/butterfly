import numpy as np
import pytest

from butterfly.plotting import SPECIAL_CODES, parameter_plane, pixel_edges


def test_parameter_plane_transposes_grid_into_c_by_a_image() -> None:
    rows = []
    for index in range(6):
        a_index, c_index = divmod(index, 3)
        rows.append(
            {
                "point_index": index,
                "a": 0.2 + 0.1 * a_index,
                "b": 0.2,
                "c": 5.0 + c_index,
                "label": "unresolved",
                "fundamental_period": None,
            }
        )
    rows[1]["label"] = "periodic"
    rows[1]["fundamental_period"] = 6
    rows[5]["label"] = "chaotic"
    plane = parameter_plane({"shape": [2, 3], "rows": rows})
    assert plane.values.shape == (3, 2)
    assert plane.values[1, 0] == 6
    assert plane.values[2, 1] == SPECIAL_CODES["chaotic"]
    assert plane.periods_present == (6,)


def test_pixel_edges_pad_regular_axis() -> None:
    assert pixel_edges(np.array([0.2, 0.3, 0.4])) == pytest.approx((0.15, 0.45))


def test_pixel_edges_reject_irregular_axis() -> None:
    with pytest.raises(ValueError, match="regularly spaced"):
        pixel_edges(np.array([0.2, 0.3, 0.5]))

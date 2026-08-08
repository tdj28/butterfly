import numpy as np
import pytest

from butterfly import project_floquet_direction_to_section, select_close_return_candidates


def test_close_return_selector_ranks_scaled_lags_deterministically():
    states = np.asarray(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 0.1],
            [1.0, 0.1],
            [0.0, 0.21],
            [1.0, 0.21],
        ]
    )
    rows = select_close_return_candidates(
        states,
        coordinate_scales=[1.0, 10.0],
        minimum_lag=2,
        maximum_lag=3,
        candidates_per_lag=1,
    )
    assert rows[0].lag == 2
    assert rows[0].start_index == 0
    assert rows[0].normalized_distance == pytest.approx(0.01)
    assert rows[1].lag == 3


def test_close_return_selector_separates_adjacent_candidates():
    states = np.column_stack((np.arange(8.0) % 2.0, np.zeros(8)))
    rows = select_close_return_candidates(
        states,
        coordinate_scales=[1.0, 1.0],
        minimum_lag=2,
        maximum_lag=2,
        candidates_per_lag=3,
        exclusion_radius=1,
    )
    assert [row.start_index for row in rows] == [0, 2, 4]


def test_close_return_selector_rejects_invalid_controls():
    with pytest.raises(ValueError, match="maximum_lag"):
        select_close_return_candidates(
            np.zeros((3, 2)),
            coordinate_scales=[1.0, 1.0],
            minimum_lag=1,
            maximum_lag=3,
        )


def test_floquet_direction_projection_is_scaled_and_section_tangent():
    projected = project_floquet_direction_to_section(
        [2.0, 3.0, 4.0],
        [5.0, 6.0, 7.0],
        [1.0, 0.0, 0.0],
        coordinate_scales=[1.0, 10.0, 0.1],
    )
    assert projected[0] == pytest.approx(0.0, abs=1e-15)
    assert np.linalg.norm(projected / [1.0, 10.0, 0.1]) == pytest.approx(1.0)


def test_floquet_direction_projection_rejects_section_tangency():
    with pytest.raises(ValueError, match="tangent"):
        project_floquet_direction_to_section(
            [1.0, 2.0, 3.0],
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            coordinate_scales=[1.0, 1.0, 1.0],
        )

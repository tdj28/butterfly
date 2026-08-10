import pytest

from scripts.gpu_scan_jones_two_critical_residuals import (
    critical_orbit_assignment,
    cycle_state_count,
    rank_candidate_rows,
    return_coordinate_axis,
    section_kind,
    signed_residual_bracket_cells,
)


def test_critical_assignment_uses_distinct_orbit_phases() -> None:
    result = critical_orbit_assignment(
        [-3.0, -1.02, 1.95, 4.0],
        [(-1.1, -0.9), (1.8, 2.2)],
        (-4.0, 5.0),
    )
    assert result["resolved"]
    assert result["orbit_indices"] == [1, 2]
    assert result["maximum_normalized_interval_distance"] == 0.0
    assert result["normalized_signed_midpoint_residuals"] == pytest.approx(
        [-0.02 / 9.0, -0.05 / 9.0]
    )


def test_critical_assignment_rejects_reusing_one_orbit_point() -> None:
    result = critical_orbit_assignment(
        [0.0, 5.0],
        [(-0.1, 0.1), (-0.2, 0.2)],
        (-1.0, 6.0),
    )
    assert result["orbit_indices"] in ([0, 1], [1, 0])
    assert result["orbit_indices"][0] != result["orbit_indices"][1]


def test_candidate_ranking_is_target_word_blind_and_deterministic() -> None:
    rows = [
        {"id": "b", "eligible": True, "ranking": {"maximum_normalized_midpoint_distance": 0.02, "sum_normalized_midpoint_distance": 0.03, "maximum_zero_slope_residual": 0.1}},
        {"id": "a", "eligible": True, "ranking": {"maximum_normalized_midpoint_distance": 0.02, "sum_normalized_midpoint_distance": 0.03, "maximum_zero_slope_residual": 0.1}},
        {"id": "c", "eligible": False, "ranking": {"maximum_normalized_midpoint_distance": 0.0, "sum_normalized_midpoint_distance": 0.0, "maximum_zero_slope_residual": 0.0}},
    ]
    assert [row["id"] for row in rank_candidate_rows(rows)] == ["a", "b"]


def test_return_coordinate_defaults_to_x_and_accepts_explicit_z() -> None:
    assert return_coordinate_axis({}) == ("x", 0)
    assert return_coordinate_axis({"return_coordinate": {"name": "z", "axis": 2}}) == (
        "z",
        2,
    )


def test_section_defaults_to_legacy_and_accepts_barrio() -> None:
    assert section_kind({}) == ("legacy_negative", 0)
    assert section_kind({"section": {"kind": "barrio_positive_x"}}) == (
        "barrio_positive_x",
        1,
    )


def test_cycle_state_count_defaults_to_six_and_accepts_eight() -> None:
    assert cycle_state_count({}) == 6
    assert cycle_state_count({"cycle_state_count": 8}) == 8


def test_signed_residual_bracket_requires_both_residuals_and_stable_assignment():
    rows = []
    for i, j, residuals in (
        (0, 0, [[-0.2, -0.3], [-0.1, -0.2]]),
        (1, 0, [[0.1, -0.1], [0.2, -0.1]]),
        (0, 1, [[-0.1, 0.2], [-0.2, 0.1]]),
        (1, 1, [[0.2, 0.3], [0.1, 0.2]]),
    ):
        rows.append(
            {
                "id": f"{i}-{j}",
                "grid_index": [i, j],
                "parameters": {"a": float(i), "c": float(j)},
                "eligible": True,
                "signed_midpoint_residuals_by_profile": residuals,
                "assignment_indices_by_profile": [[3, 1], [3, 1]],
            }
        )
    cells = signed_residual_bracket_cells(rows, 2)
    assert len(cells) == 1
    assert cells[0]["a_bounds"] == [0.0, 1.0]
    assert cells[0]["c_bounds"] == [0.0, 1.0]

    rows[-1]["assignment_indices_by_profile"] = [[4, 1], [4, 1]]
    assert signed_residual_bracket_cells(rows, 2) == []

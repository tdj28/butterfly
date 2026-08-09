from scripts.gpu_scan_jones_two_critical_residuals import (
    critical_orbit_assignment,
    rank_candidate_rows,
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

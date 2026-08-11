import pytest

from scripts.select_local_barrio_candidates import select_candidates


def _row(identifier, a, b, c, passed=True, grid_index=(0, 0)):
    return {
        "id": identifier,
        "grid_index": list(grid_index),
        "parameters": {"a": a, "b": b, "c": c},
        "passed": passed,
    }


def test_select_candidates_uses_closed_bounds_and_passed_rows_only():
    rows = [
        _row("upper", 0.3, 0.2, 8.0, grid_index=(2, 2)),
        _row("lower", 0.1, 0.2, 4.0, grid_index=(0, 0)),
        _row("middle", 0.2, 0.2, 6.0, grid_index=(1, 1)),
        _row("failed", 0.2, 0.2, 6.0, passed=False, grid_index=(1, 1)),
        _row("other-b", 0.2, 0.3, 6.0, grid_index=(1, 1)),
    ]
    selected = select_candidates(
        rows, {"a_range": [0.1, 0.3], "b": 0.2, "c_range": [4.0, 8.0]}
    )
    assert [row["id"] for row in selected] == ["lower", "middle", "upper"]


def test_select_candidates_rejects_nonincreasing_ranges():
    with pytest.raises(ValueError, match="increasing"):
        select_candidates(
            [], {"a_range": [0.3, 0.1], "b": 0.2, "c_range": [4.0, 8.0]}
        )

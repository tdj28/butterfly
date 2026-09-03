import pytest

from butterfly.atlas import periodic_components, ranked_recurrence_candidates


def atlas_result() -> dict:
    rows = []
    for index in range(12):
        grid_row, grid_column = divmod(index, 4)
        rows.append(
            {
                "point_index": index,
                "a": 0.22 + 0.01 * grid_row,
                "b": 0.2,
                "c": 5.0 + grid_column,
                "label": "unresolved",
                "fundamental_period": None,
                "candidate_period": 3,
                "candidate_normalized_error": float(20 - index),
            }
        )
    for index in (0, 1, 5):
        rows[index]["label"] = "periodic"
        rows[index]["fundamental_period"] = 3
    rows[11]["label"] = "periodic"
    rows[11]["fundamental_period"] = 4
    return {"shape": [3, 4], "rows": rows}


def test_periodic_components_group_same_period_eight_neighbors() -> None:
    components = periodic_components(atlas_result())
    assert len(components) == 2
    assert components[0].period == 3
    assert components[0].point_indices == (0, 1, 5)
    assert components[0].touches_grid_boundary is True
    assert components[1].period == 4
    assert components[1].point_indices == (11,)


def test_four_connectivity_separates_diagonal_points() -> None:
    result = atlas_result()
    result["rows"][1]["label"] = "unresolved"
    components = periodic_components(result, connectivity=4)
    assert [component.point_indices for component in components if component.period == 3] == [
        (0,),
        (5,),
    ]


def test_candidate_ranking_excludes_periodic_and_tie_breaks() -> None:
    result = atlas_result()
    result["rows"][9]["candidate_normalized_error"] = 1.0
    result["rows"][10]["candidate_normalized_error"] = 1.0
    ranked = ranked_recurrence_candidates(result, limit=2)
    assert [row["point_index"] for row in ranked] == [9, 10]


def test_atlas_rejects_incomplete_grid() -> None:
    result = atlas_result()
    result["rows"].pop()
    with pytest.raises(ValueError, match="exact indexed grid"):
        periodic_components(result)

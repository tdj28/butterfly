from butterfly.candidates import select_low_score_with_neighbors


def grid_result() -> dict:
    return {
        "shape": [3, 3],
        "rows": [
            {"point_index": index, "candidate_normalized_error": float(index + 1)}
            for index in range(9)
        ],
    }


def test_selection_adds_bounded_eight_neighbors() -> None:
    selected = select_low_score_with_neighbors(
        grid_result(), fraction=1 / 9, neighbor_radius=1
    )
    assert selected.core_indices == (0,)
    assert selected.selected_indices == (0, 1, 3, 4)
    assert selected.parent_core_indices[4] == (0,)


def test_selection_tie_breaks_by_point_index() -> None:
    result = grid_result()
    for row in result["rows"]:
        row["candidate_normalized_error"] = 10.0
    result["rows"][0]["candidate_normalized_error"] = 5.0
    result["rows"][1]["candidate_normalized_error"] = 5.0
    result["rows"][2]["candidate_normalized_error"] = 1.0
    selected = select_low_score_with_neighbors(
        result, fraction=2 / 9, neighbor_radius=0
    )
    assert selected.core_indices == (2, 0)
    assert selected.selected_indices == (0, 2)


def test_selection_rejects_incomplete_grid() -> None:
    result = grid_result()
    result["rows"].pop()
    try:
        select_low_score_with_neighbors(result, fraction=0.1, neighbor_radius=1)
    except ValueError as error:
        assert "exact indexed grid" in str(error)
    else:
        raise AssertionError("incomplete grid was accepted")

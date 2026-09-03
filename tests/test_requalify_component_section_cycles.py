from scripts.requalify_component_section_cycles import requalify_candidate


def candidate() -> dict:
    return {
        "section": {"kind": "barrio_positive_x", "crossing_count": 8},
        "section_states": [[0.0, float(index), 0.02] for index in range(8)],
        "checks": {"closure": True, "barrio_crossing_count": False},
        "passed": False,
    }


def test_requalification_changes_only_declared_section_count_check() -> None:
    result = requalify_candidate(
        candidate(),
        expected_count=8,
        section_kind="barrio_positive_x",
    )
    assert result["passed"] is True
    assert result["checks"] == {"closure": True, "barrio_crossing_count": True}
    assert result["requalification"]["orbit_data_changed"] is False


def test_requalification_rejects_the_wrong_count() -> None:
    result = requalify_candidate(
        candidate(),
        expected_count=6,
        section_kind="barrio_positive_x",
    )
    assert result["passed"] is False

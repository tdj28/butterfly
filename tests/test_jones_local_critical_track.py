from __future__ import annotations

from scripts.scan_jones_local_critical_track import match_endpoint_descendant


def _coordinate(local_location=0.62, critical=((0.10, 0.12), (0.60, 0.64))):
    return {
        "domain": [0.0, 1.0],
        "local_critical": {
            "resolved": True,
            "normalized_location": local_location,
        },
        "global_branch_oracle": {
            "resolved": True,
            "branch_count": 3,
            "critical_point_intervals": critical,
        },
    }


def test_endpoint_match_selects_the_frozen_higher_critical() -> None:
    result = match_endpoint_descendant(_coordinate(), 1, 0.15)
    assert result["resolved"]
    assert result["descendant_index"] == 1


def test_endpoint_match_rejects_the_wrong_descendant() -> None:
    result = match_endpoint_descendant(_coordinate(local_location=0.11), 1, 0.15)
    assert not result["resolved"]
    assert result["reason"] == "local track selects the wrong endpoint critical"


def test_endpoint_match_rejects_ambiguous_candidates() -> None:
    result = match_endpoint_descendant(
        _coordinate(local_location=0.5, critical=((0.38, 0.42), (0.58, 0.62))),
        1,
        0.15,
    )
    assert not result["resolved"]
    assert result["reason"] == "endpoint descendant lacks the runner-up margin"


def test_endpoint_match_requires_resolved_inputs() -> None:
    coordinate = _coordinate()
    coordinate["local_critical"]["resolved"] = False
    result = match_endpoint_descendant(coordinate, 1, 0.15)
    assert result == {"resolved": False, "reason": "endpoint inputs are unresolved"}

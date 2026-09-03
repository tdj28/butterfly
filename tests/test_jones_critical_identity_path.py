from __future__ import annotations

from scripts.scan_jones_critical_identity_path import match_persistent_critical


def _coordinate(branch_count, critical, domain=(0.0, 1.0)):
    return {
        "resolved": True,
        "branch_count": branch_count,
        "critical_point_intervals": critical,
        "domain": domain,
    }


RULE = {
    "maximum_normalized_step": 0.12,
    "minimum_runner_up_margin": 0.05,
    "three_branch_critical_symbols_in_increasing_coordinate_order": ["K0", "K1"],
}


def test_identity_rule_selects_a_unique_near_descendant() -> None:
    result = match_persistent_critical(
        _coordinate(2, [[0.39, 0.41]]),
        _coordinate(3, [[0.38, 0.42], [0.72, 0.74]]),
        RULE,
    )
    assert result["resolved"]
    assert result["descendant_index"] == 0
    assert result["descendant_symbol"] == "K0"


def test_identity_rule_rejects_an_ambiguous_split() -> None:
    result = match_persistent_critical(
        _coordinate(2, [[0.49, 0.51]]),
        _coordinate(3, [[0.42, 0.44], [0.56, 0.58]]),
        RULE,
    )
    assert not result["resolved"]
    assert result["descendant_index"] is None
    assert result["reason"] == "nearest descendant lacks the runner-up margin"


def test_identity_rule_rejects_a_large_step() -> None:
    result = match_persistent_critical(
        _coordinate(2, [[0.09, 0.11]]),
        _coordinate(3, [[0.39, 0.41], [0.79, 0.81]]),
        RULE,
    )
    assert not result["resolved"]
    assert result["reason"] == "nearest descendant exceeds the normalized-step gate"


def test_identity_rule_requires_resolved_two_and_three_branch_inputs() -> None:
    unresolved = _coordinate(2, [[0.39, 0.41]])
    unresolved["resolved"] = False
    result = match_persistent_critical(
        unresolved,
        _coordinate(3, [[0.38, 0.42], [0.72, 0.74]]),
        RULE,
    )
    assert result == {"resolved": False, "reason": "bracket coordinate is unresolved"}

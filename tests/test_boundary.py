from __future__ import annotations

import pytest

from butterfly import infer_ordered_transition_bracket


def test_ordered_transition_bracket_preserves_unresolved_gap() -> None:
    result = infer_ordered_transition_bracket(
        (0.145, 0.146, 0.147, 0.148, 0.149),
        (2, 2, None, 3, 3),
    )
    assert result.resolved
    assert result.lower_parameter == 0.146
    assert result.upper_parameter == 0.148
    assert result.unresolved_parameters == (0.147,)


def test_ordered_transition_bracket_rejects_reversal() -> None:
    result = infer_ordered_transition_bracket(
        (0.145, 0.146, 0.147, 0.148),
        (2, 3, None, 2),
    )
    assert not result.resolved
    assert result.lower_parameter is None
    assert result.reason == "resolved labels reverse after the upper regime appears"


def test_ordered_transition_bracket_requires_both_sides() -> None:
    result = infer_ordered_transition_bracket((0.145, 0.146), (2, None))
    assert not result.resolved
    assert result.reason == "both transition regimes were not resolved"


def test_ordered_transition_bracket_requires_strict_parameter_order() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        infer_ordered_transition_bracket((0.145, 0.145), (2, 3))

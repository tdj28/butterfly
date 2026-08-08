"""Finite, unresolved-aware bracketing of ordered topology changes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class OrderedTransitionBracket:
    """A finite sampled bracket, or an explicit reason it is unresolved."""

    resolved: bool
    lower_parameter: float | None
    upper_parameter: float | None
    resolved_points: tuple[tuple[float, int], ...]
    unresolved_parameters: tuple[float, ...]
    reason: str


def infer_ordered_transition_bracket(
    parameters: Sequence[float],
    labels: Sequence[int | None],
    *,
    lower_label: int = 2,
    upper_label: int = 3,
) -> OrderedTransitionBracket:
    """Bracket one ordered transition while preserving unresolved samples.

    ``None`` labels are retained in the result but never coerced.  Resolved
    labels must form a nondecreasing sequence containing only ``lower_label``
    and ``upper_label``.  The returned bounds are the last sampled lower-label
    point and first sampled upper-label point; they need not be adjacent in the
    original grid when intervening samples are unresolved.
    """

    if len(parameters) != len(labels):
        raise ValueError("parameters and labels must have equal length")
    if lower_label == upper_label:
        raise ValueError("transition labels must differ")
    values = tuple(float(value) for value in parameters)
    if any(right <= left for left, right in zip(values, values[1:], strict=False)):
        raise ValueError("parameters must be strictly increasing")
    resolved = tuple(
        (parameter, int(label))
        for parameter, label in zip(values, labels, strict=True)
        if label is not None
    )
    unresolved = tuple(
        parameter
        for parameter, label in zip(values, labels, strict=True)
        if label is None
    )
    unexpected = tuple(
        (parameter, label)
        for parameter, label in resolved
        if label not in (lower_label, upper_label)
    )
    if unexpected:
        return OrderedTransitionBracket(
            False, None, None, resolved, unresolved, "unexpected resolved label"
        )
    seen_upper = False
    for _parameter, label in resolved:
        if label == upper_label:
            seen_upper = True
        elif seen_upper:
            return OrderedTransitionBracket(
                False,
                None,
                None,
                resolved,
                unresolved,
                "resolved labels reverse after the upper regime appears",
            )
    lower_points = [parameter for parameter, label in resolved if label == lower_label]
    upper_points = [parameter for parameter, label in resolved if label == upper_label]
    if not lower_points or not upper_points:
        return OrderedTransitionBracket(
            False,
            None,
            None,
            resolved,
            unresolved,
            "both transition regimes were not resolved",
        )
    lower = max(lower_points)
    upper = min(upper_points)
    if lower >= upper:
        return OrderedTransitionBracket(
            False, None, None, resolved, unresolved, "transition ordering is invalid"
        )
    return OrderedTransitionBracket(
        True,
        lower,
        upper,
        resolved,
        unresolved,
        "finite ordered bracket resolved",
    )

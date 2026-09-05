"""Non-circular symbolic encoding for scalar return-map partitions.

The partition represented here is operational rather than topological: its
critical intervals must already have been inferred from data independent of
the periodic orbit being encoded. Historical labels such as ``C``, ``D``,
``0``, ``1``, and ``2`` are deliberately supplied by the caller instead of
being guessed from a target word.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class OperationalPartition:
    """A frozen scalar partition with uncertainty intervals at its extrema.

    ``branch_symbols`` are ordered by increasing scalar coordinate. The
    section orientation is retained as provenance; changing it requires a new
    partition rather than silently reversing an itinerary.
    """

    coordinate_name: str
    domain: tuple[float, float]
    critical_intervals: tuple[tuple[float, float], ...]
    branch_symbols: tuple[str, ...]
    critical_symbols: tuple[str, ...]
    section_orientation: int

    def __post_init__(self) -> None:
        lower, upper = self.domain
        if not self.coordinate_name:
            raise ValueError("coordinate_name must be nonempty")
        if not isfinite(lower) or not isfinite(upper) or lower >= upper:
            raise ValueError("partition domain must be a finite increasing interval")
        if self.section_orientation not in (-1, 1):
            raise ValueError("section_orientation must be -1 or 1")
        if len(self.branch_symbols) != len(self.critical_intervals) + 1:
            raise ValueError("a partition with n critical intervals needs n+1 branches")
        if len(self.critical_symbols) != len(self.critical_intervals):
            raise ValueError("each critical interval needs one operational symbol")
        symbols = (*self.branch_symbols, *self.critical_symbols)
        if any(not symbol for symbol in symbols) or len(set(symbols)) != len(symbols):
            raise ValueError("partition symbols must be nonempty and unique")

        previous_upper = lower
        for index, (critical_lower, critical_upper) in enumerate(
            self.critical_intervals
        ):
            if (
                not isfinite(critical_lower)
                or not isfinite(critical_upper)
                or critical_lower > critical_upper
            ):
                raise ValueError("critical intervals must be finite and increasing")
            if critical_lower < lower or critical_upper > upper:
                raise ValueError("critical intervals must lie inside the domain")
            if index and critical_lower <= previous_upper:
                raise ValueError("critical intervals must be ordered and disjoint")
            previous_upper = critical_upper


@dataclass(frozen=True, slots=True)
class PartitionPoint:
    """Classification of one scalar return under a frozen partition."""

    value: float
    resolved: bool
    symbol: str | None
    branch_index: int | None
    critical_index: int | None
    zero_slope_residual: float | None
    reason: str


@dataclass(frozen=True, slots=True)
class SymbolicItinerary:
    """A time-ordered orbit word and its rotation-only canonical form."""

    resolved: bool
    raw_symbols: tuple[str | None, ...]
    canonical_symbols: tuple[str, ...] | None
    points: tuple[PartitionPoint, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class CyclicWordComparison:
    """Cyclic equality with reversal reported as a separate diagnostic."""

    same_length: bool
    cyclic_match: bool
    rotation_offset: int | None
    reversal_cyclic_match: bool
    reversal_rotation_offset: int | None


def classify_partition_point(
    value: float,
    partition: OperationalPartition,
    *,
    zero_slope_residual: float | None = None,
    maximum_abs_zero_slope_residual: float = 0.0,
) -> PartitionPoint:
    """Classify one scalar value without fitting or moving the partition."""

    if (
        not isfinite(maximum_abs_zero_slope_residual)
        or maximum_abs_zero_slope_residual < 0.0
    ):
        raise ValueError(
            "maximum_abs_zero_slope_residual must be finite and nonnegative"
        )
    value = float(value)
    if not isfinite(value):
        raise ValueError("partition values must be finite")
    domain_lower, domain_upper = partition.domain
    if value < domain_lower or value > domain_upper:
        return PartitionPoint(
            value,
            False,
            None,
            None,
            None,
            zero_slope_residual,
            "value lies outside the frozen invariant domain",
        )

    for index, (lower, upper) in enumerate(partition.critical_intervals):
        if lower <= value <= upper:
            if zero_slope_residual is None:
                return PartitionPoint(
                    value,
                    False,
                    None,
                    None,
                    index,
                    None,
                    "critical-interval candidate lacks a zero-slope residual",
                )
            residual = float(zero_slope_residual)
            if not isfinite(residual):
                raise ValueError("zero-slope residuals must be finite")
            if abs(residual) > maximum_abs_zero_slope_residual:
                return PartitionPoint(
                    value,
                    False,
                    None,
                    None,
                    index,
                    residual,
                    "critical-interval candidate fails the zero-slope gate",
                )
            return PartitionPoint(
                value,
                True,
                partition.critical_symbols[index],
                None,
                index,
                residual,
                "resolved critical symbol",
            )

    branch_index = sum(
        value > upper for _lower, upper in partition.critical_intervals
    )
    return PartitionPoint(
        value,
        True,
        partition.branch_symbols[branch_index],
        branch_index,
        None,
        zero_slope_residual,
        "resolved branch symbol",
    )


def canonical_cyclic_rotation(symbols: Sequence[str]) -> tuple[str, ...]:
    """Return the lexicographically least cyclic rotation, never a reversal."""

    word = tuple(symbols)
    if not word:
        raise ValueError("a cyclic word must be nonempty")
    return min(word[offset:] + word[:offset] for offset in range(len(word)))


def encode_periodic_itinerary(
    values: Sequence[float],
    partition: OperationalPartition,
    *,
    zero_slope_residuals: Sequence[float | None] | None = None,
    maximum_abs_zero_slope_residual: float = 0.0,
) -> SymbolicItinerary:
    """Encode a periodic orbit held out from construction of ``partition``."""

    scalar_values = tuple(float(value) for value in values)
    if not scalar_values:
        raise ValueError("a periodic itinerary must contain at least one value")
    if zero_slope_residuals is None:
        residuals: tuple[float | None, ...] = (None,) * len(scalar_values)
    else:
        residuals = tuple(zero_slope_residuals)
        if len(residuals) != len(scalar_values):
            raise ValueError("zero_slope_residuals must match the orbit length")
    points = tuple(
        classify_partition_point(
            value,
            partition,
            zero_slope_residual=residual,
            maximum_abs_zero_slope_residual=maximum_abs_zero_slope_residual,
        )
        for value, residual in zip(scalar_values, residuals, strict=True)
    )
    raw = tuple(point.symbol for point in points)
    unresolved = tuple(index for index, point in enumerate(points) if not point.resolved)
    if unresolved:
        return SymbolicItinerary(
            False,
            raw,
            None,
            points,
            "unresolved partition points at indices "
            + ",".join(str(index) for index in unresolved),
        )
    resolved_raw = tuple(symbol for symbol in raw if symbol is not None)
    return SymbolicItinerary(
        True,
        raw,
        canonical_cyclic_rotation(resolved_raw),
        points,
        "resolved under the frozen partition",
    )


def map_symbols(
    symbols: Sequence[str], mapping: Mapping[str, str]
) -> tuple[str, ...]:
    """Apply an explicitly declared symbol mapping with no inferred fallback."""

    word = tuple(symbols)
    missing = sorted(set(word) - set(mapping))
    if missing:
        raise ValueError("symbol mapping is incomplete: " + ",".join(missing))
    mapped = tuple(mapping[symbol] for symbol in word)
    if any(not symbol for symbol in mapped):
        raise ValueError("mapped symbols must be nonempty")
    return mapped


def _rotation_offset(source: tuple[str, ...], target: tuple[str, ...]) -> int | None:
    for offset in range(len(source)):
        if source[offset:] + source[:offset] == target:
            return offset
    return None


def compare_cyclic_words(
    observed: Sequence[str], target: Sequence[str]
) -> CyclicWordComparison:
    """Compare words up to rotation while exposing, not accepting, reversal."""

    observed_word = tuple(observed)
    target_word = tuple(target)
    if not observed_word or not target_word:
        raise ValueError("cyclic words must be nonempty")
    if len(observed_word) != len(target_word):
        return CyclicWordComparison(False, False, None, False, None)
    offset = _rotation_offset(observed_word, target_word)
    reversal_offset = _rotation_offset(tuple(reversed(observed_word)), target_word)
    return CyclicWordComparison(
        True,
        offset is not None,
        offset,
        reversal_offset is not None,
        reversal_offset,
    )


def is_cd_zero_insertion(source: str, target: str) -> bool:
    """Return whether ``target`` inserts one zero immediately after ``CD``."""

    return source.startswith("CD") and target == source[:2] + "0" + source[2:]

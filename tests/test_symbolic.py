from __future__ import annotations

import pytest

from butterfly import (
    OperationalPartition,
    canonical_cyclic_rotation,
    classify_partition_point,
    compare_cyclic_words,
    encode_periodic_itinerary,
    is_cd_zero_insertion,
    map_symbols,
)


def test_one_branch_control_has_no_synthetic_critical_symbol() -> None:
    partition = OperationalPartition(
        coordinate_name="u",
        domain=(0.0, 1.0),
        critical_intervals=(),
        branch_symbols=("B0",),
        critical_symbols=(),
        section_orientation=1,
    )
    result = encode_periodic_itinerary((0.1, 0.8, 0.4), partition)
    assert result.resolved
    assert result.raw_symbols == ("B0", "B0", "B0")
    assert result.canonical_symbols == ("B0", "B0", "B0")


def test_two_branch_control_requires_and_passes_zero_slope_gate() -> None:
    partition = OperationalPartition(
        coordinate_name="u",
        domain=(0.0, 1.0),
        critical_intervals=((0.49, 0.51),),
        branch_symbols=("B0", "B1"),
        critical_symbols=("K0",),
        section_orientation=-1,
    )
    result = encode_periodic_itinerary(
        (0.5, 1.0, 0.0),
        partition,
        zero_slope_residuals=(2e-5, None, None),
        maximum_abs_zero_slope_residual=1e-4,
    )
    assert result.resolved
    assert result.raw_symbols == ("K0", "B1", "B0")
    mapped = map_symbols(
        result.raw_symbols,
        {"K0": "C", "B0": "0", "B1": "1"},
    )
    comparison = compare_cyclic_words(mapped, tuple("C10"))
    assert comparison.cyclic_match
    assert not comparison.reversal_cyclic_match


def test_three_branch_control_preserves_temporal_order_and_critical_identity() -> None:
    partition = OperationalPartition(
        coordinate_name="u",
        domain=(0.0, 1.0),
        critical_intervals=((0.24, 0.26), (0.74, 0.76)),
        branch_symbols=("B0", "B1", "B2"),
        critical_symbols=("K0", "K1"),
        section_orientation=1,
    )
    result = encode_periodic_itinerary(
        (0.25, 0.5, 0.75, 0.9, 0.1),
        partition,
        zero_slope_residuals=(0.0, None, -3e-6, None, None),
        maximum_abs_zero_slope_residual=1e-5,
    )
    assert result.resolved
    assert result.raw_symbols == ("K0", "B1", "K1", "B2", "B0")
    assert result.points[0].critical_index == 0
    assert result.points[2].critical_index == 1
    assert result.points[4].branch_index == 0


@pytest.mark.parametrize("residual", [None, 2e-3])
def test_critical_candidate_is_unresolved_without_a_passing_slope_gate(
    residual: float | None,
) -> None:
    partition = OperationalPartition(
        coordinate_name="u",
        domain=(0.0, 1.0),
        critical_intervals=((0.49, 0.51),),
        branch_symbols=("B0", "B1"),
        critical_symbols=("K0",),
        section_orientation=1,
    )
    point = classify_partition_point(
        0.5,
        partition,
        zero_slope_residual=residual,
        maximum_abs_zero_slope_residual=1e-4,
    )
    assert not point.resolved
    assert point.symbol is None
    assert point.critical_index == 0


def test_outside_domain_is_unresolved_not_extrapolated() -> None:
    partition = OperationalPartition(
        coordinate_name="u",
        domain=(0.0, 1.0),
        critical_intervals=(),
        branch_symbols=("B0",),
        critical_symbols=(),
        section_orientation=1,
    )
    point = classify_partition_point(1.01, partition)
    assert not point.resolved
    assert point.reason == "value lies outside the frozen invariant domain"


def test_rotation_is_allowed_but_reversal_is_reported_separately() -> None:
    assert canonical_cyclic_rotation(tuple("C10")) == ("0", "C", "1")
    rotated = compare_cyclic_words(tuple("10C"), tuple("C10"))
    assert rotated.cyclic_match
    assert rotated.rotation_offset == 2
    reversed_only = compare_cyclic_words(tuple("C01"), tuple("C10"))
    assert not reversed_only.cyclic_match
    assert reversed_only.reversal_cyclic_match


def test_symbol_mapping_must_be_declared_completely() -> None:
    with pytest.raises(ValueError, match="mapping is incomplete"):
        map_symbols(("K0", "B1"), {"K0": "C"})


@pytest.mark.parametrize(
    ("source", "target", "expected"),
    [
        ("CD0", "CD00", True),
        ("CD011", "CD0011", True),
        ("CD0111", "CD00111", True),
        ("C10", "C100", False),
        ("CD01", "CD010", False),
    ],
)
def test_cd_zero_insertion_grammar(source: str, target: str, expected: bool) -> None:
    assert is_cd_zero_insertion(source, target) is expected

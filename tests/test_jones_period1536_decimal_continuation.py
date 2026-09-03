from __future__ import annotations

import sys
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.continue_jones_period1536_decimal_child import (
    half_node_rms,
    normalized_secant,
    selected_source_candidates,
)


def candidate(step: float, value: str) -> dict:
    return {
        "step_length": step,
        "direction": -1,
        "nodes_decimal": [[value, "0", "0"]],
        "period_time_decimal": value,
        "a_decimal": value,
    }


def test_source_candidates_are_selected_in_frozen_step_order() -> None:
    receipt = {"candidates": [candidate(0.25, "2"), candidate(0.125, "1")]}
    manifest = {"source_direction": -1, "source_step_lengths": [0.125, 0.25]}
    assert [row["step_length"] for row in selected_source_candidates(receipt, manifest)] == [0.125, 0.25]


def test_normalized_secant_includes_state_period_and_parameter() -> None:
    with localcontext() as context:
        context.prec = 40
        nodes, period, parameter, norm = normalized_secant(
            candidate(0.125, "1"), candidate(0.25, "2")
        )
        assert norm == Decimal(3).sqrt()
        assert nodes[0][0] == pytest.approx(Decimal(1) / norm)
        assert period == pytest.approx(Decimal(1) / norm)
        assert parameter == pytest.approx(Decimal(1) / norm)


def test_half_node_rms_measures_primitive_doubling_amplitude() -> None:
    nodes = [
        [Decimal("1"), Decimal("2"), Decimal("3")],
        [Decimal("2"), Decimal("4"), Decimal("6")],
    ]
    assert half_node_rms(nodes) == (Decimal(14) / Decimal(3)).sqrt()

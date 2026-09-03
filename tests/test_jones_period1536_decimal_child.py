from __future__ import annotations

import sys
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.switch_jones_period1536_decimal_child import (
    phase_fixed_child_tangent,
    scaling_exponent,
    selected_event_profile,
    transverse_spectrum,
)


def test_phase_fixed_child_tangent_is_normalized_and_transverse() -> None:
    with localcontext() as context:
        context.prec = 40
        nodes = [[Decimal("1"), Decimal("2"), Decimal("3")]]
        tangents = [[Decimal("0.2"), Decimal("0.3"), Decimal("0.4")]]
        mode, phase, _ = phase_fixed_child_tangent(
            nodes, tangents, Decimal("0.2"), Decimal("0.2"), Decimal("7.6")
        )
        assert sum(value * value for row in mode for value in row) == pytest.approx(
            Decimal(1)
        )
        assert abs(sum(a * b for a, b in zip(phase, mode[0]))) < Decimal("1e-35")
        assert mode[1] != mode[0]


def test_transverse_spectrum_removes_neutral_root() -> None:
    transition = [
        Decimal(1), Decimal(0), Decimal(0),
        Decimal(0), Decimal("0.5"), Decimal(0),
        Decimal(0), Decimal(0), Decimal("0.2"),
    ]
    result = transverse_spectrum([transition], [0], 40)
    assert result["dominant_modulus"] == pytest.approx(0.5)
    assert result["maximum_neutral_residual"] < 1e-30


def test_scaling_exponent_recovers_quadratic_opening() -> None:
    rows = [
        {"step_length": 1.0, "half_node_rms": 2.0, "parameter_displacement": sign * 4.0}
        for sign in (-1, 1)
    ] + [
        {"step_length": 2.0, "half_node_rms": 4.0, "parameter_displacement": sign * 16.0}
        for sign in (-1, 1)
    ]
    assert scaling_exponent(rows)["parameter_amplitude_exponent"] == pytest.approx(2.0)


def test_event_profile_supports_sequence_and_single_profile_receipts() -> None:
    profile = {"steps_per_segment": 8192, "a_decimal": "1"}
    assert selected_event_profile({"profile": profile}, 8192) is profile
    assert selected_event_profile({"profiles": [profile]}, 8192) is profile

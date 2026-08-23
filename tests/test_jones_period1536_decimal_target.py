from __future__ import annotations

import sys
from decimal import Decimal, localcontext
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.correct_jones_period1536_decimal_target import (
    periodicity_classification,
    reduced_fixed_parameter_correction,
)


def manifest() -> dict:
    return {
        "acceptance": {
            "minimum_primitive_half_node_rms": 1e-7,
            "maximum_doubled_parent_half_node_rms": 1e-10,
        }
    }


def test_periodicity_classification_is_outcome_neutral() -> None:
    assert periodicity_classification(Decimal("1e-6"), manifest()) == "primitive_period1536"
    assert periodicity_classification(Decimal("1e-12"), manifest()) == "doubled_period768_parent"
    assert periodicity_classification(Decimal("1e-9"), manifest()) == "unresolved"


def test_fixed_parameter_reduction_solves_identity_closure() -> None:
    with localcontext() as context:
        context.prec = 40
        rows = [
            {
                "transition": [
                    Decimal(1), Decimal(0), Decimal(0),
                    Decimal(0), Decimal("0.5"), Decimal(0),
                    Decimal(0), Decimal(0), Decimal("0.25"),
                ],
                "period_state": [Decimal(1), Decimal(0), Decimal(0)],
                "residual": [Decimal("2"), Decimal("3"), Decimal("4")],
            }
        ]
        corrections, period_delta = reduced_fixed_parameter_correction(
            rows,
            [Decimal(1), Decimal(0), Decimal(0)],
            Decimal("5"),
        )
        assert period_delta == Decimal("-2")
        assert corrections[0] == [
            Decimal("-5"),
            Decimal("6"),
            Decimal(16) / Decimal(3),
        ]

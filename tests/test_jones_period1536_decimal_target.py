from __future__ import annotations

import sys
from decimal import Decimal, localcontext
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.correct_jones_period1536_decimal_target import (
    periodicity_classification,
    predecessor_is_admissible,
    reduced_fixed_parameter_correction,
    trial_is_acceptable,
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


def test_backtracking_requires_frozen_residual_reduction() -> None:
    current = Decimal("1e-8")
    tolerance = Decimal("1e-20")
    damping = {"maximum_accepted_ratio": 0.95}
    assert trial_is_acceptable(current, Decimal("9e-9"), tolerance, Decimal(1), damping)
    assert not trial_is_acceptable(
        current, Decimal("9.6e-9"), tolerance, Decimal(1), damping
    )
    assert trial_is_acceptable(
        current, Decimal("1e-21"), tolerance, Decimal(1), damping
    )


def test_armijo_reduction_scales_with_step_fraction() -> None:
    current = Decimal("1e-8")
    damping = {"armijo_coefficient": 0.01}
    assert trial_is_acceptable(
        current, Decimal("0.999e-8"), Decimal("1e-20"), Decimal("0.03125"), damping
    )
    assert not trial_is_acceptable(
        current, Decimal("0.9999e-8"), Decimal("1e-20"), Decimal("0.03125"), damping
    )


def test_predecessor_requirement_distinguishes_failure_and_collapse() -> None:
    schema = "receipt.v1"
    failure = {"schema": schema, "passed": False, "checks": {"correction": False}}
    collapse = {
        "schema": schema,
        "passed": True,
        "checks": {"correction": True},
        "periodicity_classification": "doubled_period768_parent",
    }
    assert predecessor_is_admissible(failure, schema, "unresolved_failure")
    assert predecessor_is_admissible(collapse, schema, "passed_collapse")
    assert not predecessor_is_admissible(collapse, schema, "unresolved_failure")

from __future__ import annotations

import sys
from decimal import Decimal, localcontext
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from correct_jones_period768_decimal_parent import (  # noqa: E402
    matvec,
    newton_correction,
    vector_add,
    vector_scale,
)


def test_decimal_block_elimination_solves_cyclic_newton_equations():
    with localcontext() as context:
        context.prec = 40
        transitions = [
            [
                Decimal("1.1"), Decimal("0.1"), Decimal("0"),
                Decimal("0"), Decimal("0.9"), Decimal("0.2"),
                Decimal("0.1"), Decimal("0"), Decimal("1.05"),
            ],
            [
                Decimal("0.95"), Decimal("0"), Decimal("0.05"),
                Decimal("0.1"), Decimal("1.02"), Decimal("0"),
                Decimal("0"), Decimal("0.03"), Decimal("0.97"),
            ],
        ]
        duration_columns = [
            [Decimal("0.2"), Decimal("-0.1"), Decimal("0.05")],
            [Decimal("0.1"), Decimal("0.04"), Decimal("-0.02")],
        ]
        residuals = [
            [Decimal("0.01"), Decimal("-0.02"), Decimal("0.005")],
            [Decimal("-0.003"), Decimal("0.004"), Decimal("0.006")],
        ]
        phase = [Decimal("0.7"), Decimal("-0.2"), Decimal("0.1")]
        phase_residual = Decimal("0.013")

        corrections, period_correction = newton_correction(
            transitions,
            duration_columns,
            residuals,
            phase,
            phase_residual,
        )

        tolerance = Decimal("1e-35")
        for index in range(2):
            left = vector_add(
                matvec(transitions[index], corrections[index]),
                vector_scale(duration_columns[index], period_correction),
                vector_scale(corrections[(index + 1) % 2], Decimal(-1)),
                residuals[index],
            )
            assert max(abs(value) for value in left) < tolerance
        assert abs(sum(a * b for a, b in zip(phase, corrections[0])) + phase_residual) < tolerance

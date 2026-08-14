from __future__ import annotations

import sys
from decimal import Decimal, localcontext
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from correct_jones_period768_decimal_augmented import (  # noqa: E402
    augmented_newton_correction,
    augmented_rhs,
    matvec,
    vector_add,
    vector_scale,
)


def _matrix(seed):
    return [Decimal(str(value)) for value in seed]


def test_decimal_augmented_rhs_has_expected_sparse_hessian_terms():
    with localcontext() as context:
        context.prec = 40
        zero = Decimal(0)
        one = Decimal(1)
        value = (
            [Decimal("1.2"), Decimal("-0.4"), Decimal("0.7")]
            + [one, zero, zero, zero, one, zero, zero, zero, one]
            + [Decimal("0.3"), Decimal("-0.2"), Decimal("0.1")]
            + [Decimal("0.5"), Decimal("-0.6"), Decimal("0.8")]
            + [zero] * 12
        )
        derivative = augmented_rhs(
            value, Decimal("0.2"), Decimal("0.2"), Decimal("7.6")
        )
        assert len(derivative) == 30
        assert derivative[3:12] == [
            zero, -one, -one,
            one, Decimal("0.2"), zero,
            Decimal("0.7"), zero, Decimal("-6.4"),
        ]
        # J_a w enters the second component; D2f[S_a,w] enters the third.
        assert derivative[28] == Decimal("-0.6")
        assert derivative[29] == Decimal("0.29")


def test_augmented_block_elimination_solves_all_linearized_equations():
    with localcontext() as context:
        context.prec = 50
        rows = [
            {
                "transition": _matrix([1.1, 0.1, 0, 0, 0.9, 0.2, 0.1, 0, 1.05]),
                "parameter_state": _matrix([0.03, -0.02, 0.01]),
                "state_tangent": _matrix([0.02, 0, 0.01, 0, -0.01, 0.03, 0.04, 0, 0.02]),
                "parameter_tangent": _matrix([0.01, 0.02, -0.01]),
                "orbit_time": _matrix([0.2, -0.1, 0.05]),
                "tangent_time": _matrix([-0.03, 0.04, 0.02]),
                "orbit_residual": _matrix([0.01, -0.02, 0.005]),
                "tangent_residual": _matrix([-0.004, 0.003, 0.002]),
            },
            {
                "transition": _matrix([0.95, 0, 0.05, 0.1, 1.02, 0, 0, 0.03, 0.97]),
                "parameter_state": _matrix([-0.02, 0.01, 0.04]),
                "state_tangent": _matrix([0.01, 0.02, 0, -0.02, 0.01, 0.01, 0, 0.03, -0.01]),
                "parameter_tangent": _matrix([0.03, -0.01, 0.02]),
                "orbit_time": _matrix([0.1, 0.04, -0.02]),
                "tangent_time": _matrix([0.02, -0.01, 0.05]),
                "orbit_residual": _matrix([-0.003, 0.004, 0.006]),
                "tangent_residual": _matrix([0.002, -0.005, 0.001]),
            },
        ]
        phase = _matrix([0.7, -0.2, 0.1])
        tangent0 = _matrix([0.2, -0.9, 0.3])
        phase_residual = Decimal("0.013")
        norm_residual = sum(value * value for value in tangent0) - Decimal(1)
        state, tangent, period, parameter = augmented_newton_correction(
            rows, phase, phase_residual, tangent0, norm_residual
        )
        tolerance = Decimal("1e-43")
        for index, row in enumerate(rows):
            next_index = (index + 1) % len(rows)
            state_equation = vector_add(
                matvec(row["transition"], state[index]),
                vector_scale(state[next_index], Decimal(-1)),
                vector_scale(row["orbit_time"], period),
                vector_scale(row["parameter_state"], parameter),
                row["orbit_residual"],
            )
            tangent_equation = vector_add(
                matvec(row["state_tangent"], state[index]),
                matvec(row["transition"], tangent[index]),
                vector_scale(row["tangent_time"], period),
                vector_scale(row["parameter_tangent"], parameter),
                row["tangent_residual"],
                vector_scale(
                    tangent[next_index],
                    Decimal(1) if index + 1 == len(rows) else Decimal(-1),
                ),
            )
            assert max(map(abs, state_equation)) < tolerance
            assert max(map(abs, tangent_equation)) < tolerance
        assert abs(sum(a * b for a, b in zip(phase, state[0])) + phase_residual) < tolerance
        assert abs(
            Decimal(2) * sum(a * b for a, b in zip(tangent0, tangent[0]))
            + norm_residual
        ) < tolerance

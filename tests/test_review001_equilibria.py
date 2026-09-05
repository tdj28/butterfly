"""Algebra-only reviewer checks; no trajectories or optional dependencies."""

from decimal import Decimal, ROUND_DOWN, getcontext, localcontext
import hashlib
import json
from pathlib import Path

import pytest

from scripts.report_review001_equilibria import (
    POINTS, PRECISION, analytic_coefficients, build_report,
    main, matrix_coefficients, solve_saddle_focus_cubic, stable_equilibria,
)


@pytest.fixture(scope="module")
def report():
    return build_report()


def test_exactly_the_four_declared_points_and_both_equilibria(report):
    assert [point["id"] for point in report["points"]] == [point[0] for point in POINTS]
    assert report["points"][1]["parameters_decimal"]["a"] == "0.182643608174"
    for point in report["points"]:
        assert [row["equilibrium"] for row in point["equilibria"]] == ["small", "large"]
        assert float(point["equilibria"][0]["state_decimal80"][2]) < float(point["equilibria"][1]["state_decimal80"][2])


def test_analytic_equilibria_and_package_roots_have_small_residuals(report):
    for point in report["points"]:
        for row in point["equilibria"]:
            assert Decimal(row["rhs_infinity_norm_decimal80"]) < Decimal("1e-72")
            assert Decimal(row["quadratic_residual_decimal80"]) < Decimal("1e-72")
            assert row["rhs_infinity_norm_numpy"] < 2e-12
            assert Decimal(row["maximum_state_difference_numpy_decimal80"]) < Decimal("1e-12")


def test_second_equilibrium_has_opposite_stable_unstable_dimensions(report):
    for point in report["points"]:
        small, large = [row["spectral_convention"] for row in point["equilibria"]]
        assert (small["forward_stable_dimension"], small["forward_unstable_dimension"]) == (1, 2)
        assert (large["forward_stable_dimension"], large["forward_unstable_dimension"]) == (2, 1)
        assert small["standard_one_dimensional_unstable_time_direction"] == "reversed"
        assert large["standard_one_dimensional_unstable_time_direction"] == "forward"


def test_saddle_quantity_sign_and_dimensions_reverse_without_changing_context(report):
    for point in report["points"]:
        for row in point["equilibria"]:
            convention = row["spectral_convention"]
            with localcontext() as context:
                context.prec = PRECISION
                forward = Decimal(convention["forward_signed_sum_real_plus_pair_real"])
                reverse = Decimal(convention["reversed_signed_sum_real_plus_pair_real"])
                assert forward == -reverse
            assert convention["reversed_stable_dimension"] == convention["forward_unstable_dimension"]
            assert convention["standard_spectral_inequality_positive"]
            assert not convention["homoclinic_existence_established"]
    printed_small = report["points"][0]["equilibria"][0]["spectral_convention"]
    assert float(printed_small["forward_signed_sum_real_plus_pair_real"]) == pytest.approx(-10.2140771737, abs=1e-9)


def test_decimal_polynomial_solver_agrees_with_numpy_for_same_matrix(report):
    for point in report["points"]:
        for row in point["equilibria"]:
            assert Decimal(row["maximum_spectral_component_difference_same_binary64_matrix"]) < Decimal("1e-12")
            assert Decimal(row["maximum_spectral_component_difference_numpy_analytic"]) < Decimal("1e-12")
            for key in ("decimal80_analytic_spectrum", "decimal80_exact_binary64_jacobian_spectrum"):
                spectrum = row[key]
                assert Decimal(spectrum["maximum_characteristic_component_residual"]) < Decimal("1e-65")
                assert Decimal(spectrum["quadratic_discriminant"]) < 0
                assert spectrum["bisection"]["converged"]
                assert spectrum["bisection"]["iterations"] <= 320
                assert not spectrum["bisection"]["rigorous_enclosure"]


def test_analytic_coefficients_match_independent_matrix_formula():
    with localcontext() as context:
        context.prec = PRECISION
        a, b, c = map(Decimal, ("0.1798", "0.2", "10.3084"))
        for state in stable_equilibria(a, b, c):
            x, _y, z = state
            matrix = [[Decimal(0), Decimal(-1), Decimal(-1)], [Decimal(1), a, Decimal(0)], [z, Decimal(0), x-c]]
            assert max(abs(left-right) for left, right in zip(
                analytic_coefficients(a, c, state), matrix_coefficients(matrix), strict=True
            )) < Decimal("1e-75")


def test_cubic_solver_known_saddle_focus_and_rejects_three_real_roots():
    with localcontext() as context:
        context.prec = PRECISION
        # (lambda + 10) * ((lambda - 0.1)^2 + 1).
        spectrum = solve_saddle_focus_cubic(map(Decimal, ("9.8", "-0.99", "10.1")))
        assert abs(spectrum["real_eigenvalue"] + 10) < Decimal("1e-70")
        assert abs(spectrum["complex_pair_real"] - Decimal("0.1")) < Decimal("1e-70")
        assert abs(spectrum["complex_pair_imaginary_magnitude"] - 1) < Decimal("1e-70")
        with pytest.raises(ValueError, match="nonreal conjugate pair"):
            solve_saddle_focus_cubic((0, -1, 0))


def test_invalid_parameters_and_nonfinite_coefficients_are_rejected():
    with pytest.raises(ValueError, match="positive parameters"):
        stable_equilibria(Decimal(0), Decimal(1), Decimal(2))
    with pytest.raises(ValueError, match="finite cubic"):
        solve_saddle_focus_cubic((Decimal("NaN"), 0, 1))


def test_deterministic_output_and_decimal_context_preserved(tmp_path, capsys):
    old_precision = getcontext().prec
    first = build_report()
    assert build_report() == first
    assert getcontext().prec == old_precision
    output = tmp_path / "equilibria.json"
    assert main(["--output", str(output)]) == 0
    assert json.loads(output.read_text()) == first
    with pytest.raises(SystemExit):
        main(["--output", str(output)])
    assert "refusing to overwrite" in capsys.readouterr().err
    assert main([]) == 0
    assert json.loads(capsys.readouterr().out) == first
    assert "/Users/" not in output.read_text()


def test_report_uses_declared_rounding_not_callers_context(report):
    with localcontext() as context:
        context.prec = 17
        context.rounding = ROUND_DOWN
        assert build_report() == report
        assert context.prec == 17 and context.rounding == ROUND_DOWN


def test_committed_table_binds_current_algebra_sources_and_declared_points():
    root = Path(__file__).resolve().parents[1]
    table = json.loads((root / "paper/tables/review001-equilibria.json").read_text())
    for key, relative in (
        ("script", "scripts/report_review001_equilibria.py"),
        ("models", "python/butterfly/models.py"),
    ):
        assert table["source_sha256"][key] == hashlib.sha256((root / relative).read_bytes()).hexdigest()
    assert [row["id"] for row in table["points"]] == [row[0] for row in POINTS]
    assert table["precision"]["decimal_digits"] == PRECISION
    assert not table["precision"]["validated_interval_arithmetic"]

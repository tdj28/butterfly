"""Exact polynomial identities and diagnostic guards; no target computations."""

from decimal import Decimal, localcontext
import hashlib
import json

import pytest

from scripts.inspect_homoclinic_interval_arithmetic import (
    PRECISION, bound_json, exact_binary64, hermite_coefficients,
    hermite_evaluate, interval_residual, json_safe, synthetic_controls,
)


def test_archived_float_conversion_preserves_binary_value_not_decimal_label():
    observed = exact_binary64(0.1)
    assert observed == Decimal.from_float(0.1)
    assert observed != Decimal("0.1")
    assert float(observed) == 0.1


def test_hermite_reconstructs_both_endpoint_values_and_derivatives():
    with localcontext() as context:
        context.prec = PRECISION
        y0 = [Decimal("54.01"), Decimal("-1.23")]
        y1 = [Decimal("54.0100000000001"), Decimal("-1.2299999")]
        f0 = [Decimal("0.021"), Decimal("1200.1")]
        f1 = [Decimal("0.02100001"), Decimal("1200.2")]
        width = Decimal("8.6e-12")
        coefficients = hermite_coefficients(y0, y1, f0, f1, width)
        observed_y0, observed_f0 = hermite_evaluate(coefficients, Decimal(0))
        observed_y1, observed_f1 = hermite_evaluate(coefficients, width)
        assert observed_y0 == y0 and observed_f0 == f0
        assert max(abs(left - right) for left, right in zip(observed_y1, y1)) < Decimal("1e-65")
        assert max(abs(left - right) for left, right in zip(observed_f1, f1)) < Decimal("1e-60")


@pytest.mark.parametrize("degree", (1, 2, 3))
def test_exact_polynomial_solution_has_zero_collocation_and_lobatto_residual(degree):
    with localcontext() as context:
        context.prec = PRECISION
        coefficients = [Decimal("54"), Decimal("0.02"), Decimal("1e4"), Decimal("-3e2")][:degree + 1]
        left, right = Decimal("0.99"), Decimal("0.990000000008")

        def truth(position):
            return sum(value * position**power for power, value in enumerate(coefficients))

        def derivative(position, _states):
            return [sum(power * coefficients[power] * position**(power - 1) for power in range(1, len(coefficients)))]

        result = interval_residual(left, right, [truth(left)], [truth(right)], derivative)
        assert result["relative_rms"] < Decimal("1e-60")
        assert result["absolute_collocation_state_balance_defect"][0] < Decimal("1e-65")
        assert result["maximum_endpoint_derivative_reconstruction_error"] < Decimal("1e-60")


def test_midpoint_state_balance_equals_hermite_derivative_defect():
    with localcontext() as context:
        context.prec = PRECISION
        left, right = Decimal("0.8"), Decimal("0.80000003")
        y0, y1 = [Decimal("1.1")], [Decimal("1.100000008")]

        def field(_position, states):
            return [states[0]**2 - Decimal("0.9")]

        width = right - left
        coefficients = hermite_coefficients(y0, y1, field(left, y0), field(right, y1), width)
        state, observed = hermite_evaluate(coefficients, width / 2)
        expected = field((left + right) / 2, state)[0]
        result = interval_residual(left, right, y0, y1, field)
        relative_defect = (observed[0] - expected) / (1 + abs(expected))
        assert abs(result["midpoint_relative_derivative_defect"][0] - relative_defect) < Decimal("1e-65")


def test_stationary_component_control_is_exact_but_quantized_small_interval_is_not():
    controls = synthetic_controls()
    tiny, ordinary = controls
    for row in controls:
        assert row["decimal80_exact_endpoint_data"]["relative_rms"] < Decimal("1e-60")
        assert row["decimal80_rounded_endpoint_data"]["maximum_endpoint_derivative_reconstruction_error"] < Decimal("1e-60")
    assert tiny["decimal80_rounded_endpoint_data"]["relative_rms"] > Decimal("1e-6")
    assert ordinary["decimal80_rounded_endpoint_data"]["relative_rms"] < Decimal("1e-8")
    assert any(value != 0 for value in tiny["endpoint_rounding_errors"])


def test_float_control_and_decimal_control_use_same_nonzero_residual_definition():
    tiny, _ordinary = synthetic_controls()
    high_precision = float(tiny["decimal80_rounded_endpoint_data"]["relative_rms"])
    binary64 = tiny["binary64_rounded_endpoint_data"]["relative_rms"]
    assert binary64 == pytest.approx(high_precision, rel=1e-3)


def test_hash_bound_json_rejects_modified_data(tmp_path):
    path = tmp_path / "diagnostic.json"
    raw = b'{"diagnostic": true}\n'
    path.write_bytes(raw)
    expected = hashlib.sha256(raw).hexdigest()
    assert bound_json(path, expected) == {"diagnostic": True}
    path.write_bytes(b'{"diagnostic": false}\n')
    with pytest.raises(ValueError, match="hash mismatch"):
        bound_json(path, expected)


def test_decimal_results_are_losslessly_serialized_as_strings():
    value = Decimal("0.000123456789012345678901234567890123456789")
    encoded = json.dumps(json_safe({"value": value}), allow_nan=False)
    assert Decimal(json.loads(encoded)["value"]) == value
    with pytest.raises(ValueError, match="nonfinite"):
        json_safe({"value": Decimal("NaN")})


def test_nonpositive_interval_is_rejected():
    with pytest.raises(ValueError, match="positive-width"):
        interval_residual(1.0, 1.0, [2.0], [2.0], lambda _time, _state: [0.0])

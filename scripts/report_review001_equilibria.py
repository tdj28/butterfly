#!/usr/bin/env python3
"""Algebraic equilibrium/spectral check at four declared Rossler parameters.

No trajectory integration, continuation, optimizer, or invariant-manifold
calculation is performed. Decimal arithmetic is not validated interval
arithmetic: its search brackets and residuals are not rigorous enclosures.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
import hashlib
import json
from pathlib import Path
import platform

import numpy as np

from butterfly.models import (
    RosslerParameters, equilibrium_eigenvalues, rossler_equilibria,
    rossler_jacobian, rossler_rhs,
)


ROOT = Path(__file__).resolve().parents[1]
PRECISION = 80
ROOT_RELATIVE_WIDTH = Decimal("1e-72")
MAXIMUM_BISECTIONS = 320
POINTS = (
    ("printed-hub", "0.1798", "0.2", "10.3084"),
    ("initial-homoclinic-candidate", "0.182643608174", "0.2", "10.3084"),
    ("classifier-two-branch-endpoint", "0.1481875", "0.2", "20"),
    ("classifier-three-branch-endpoint", "0.14825", "0.2", "20"),
)


def stable_equilibria(a: Decimal, b: Decimal, c: Decimal):
    """Independent stable formula, restricted to the declared positive cases."""
    if min(a, b, c) <= 0 or c * c <= 4 * a * b:
        raise ValueError("positive parameters and two distinct real roots required")
    radical = (c * c - 4 * a * b).sqrt()
    z_values = (2 * b / (c + radical), (c + radical) / (2 * a))
    return [(a * z, -z, z) for z in z_values]


def analytic_coefficients(a, c, state):
    """lambda^3 + A lambda^2 + B lambda + C from the analytic equations."""
    x, _y, z = state
    r = c - x
    return (r - a, 1 + z - a * r, r - a * z)


def matrix_coefficients(matrix):
    """Characteristic coefficients of a general 3x3 Decimal matrix."""
    j = matrix
    trace = j[0][0] + j[1][1] + j[2][2]
    minors = sum(j[i][i] * j[k][k] - j[i][k] * j[k][i]
                 for i, k in ((0, 1), (0, 2), (1, 2)))
    determinant = (
        j[0][0] * (j[1][1] * j[2][2] - j[1][2] * j[2][1])
        - j[0][1] * (j[1][0] * j[2][2] - j[1][2] * j[2][0])
        + j[0][2] * (j[1][0] * j[2][1] - j[1][1] * j[2][0])
    )
    return (-trace, minors, -determinant)


def cubic_value(value, coefficients):
    a, b, c = coefficients
    return ((value + a) * value + b) * value + c


def solve_saddle_focus_cubic(coefficients):
    """Bounded bisection for the real root, then a quadratic factor.

    A Cauchy radius supplies the initial search bounds. The final negative
    quadratic discriminant checks the assumed one-real/conjugate-pair case.
    Decimal-rounded sign tests do not establish interval-certified bounds.
    """
    coefficients = tuple(Decimal(value) for value in coefficients)
    if not all(value.is_finite() for value in coefficients):
        raise ValueError("finite cubic coefficients required")
    radius = 1 + max(abs(value) for value in coefficients)
    left, right = -radius, radius
    if not cubic_value(left, coefficients) < 0 < cubic_value(right, coefficients):
        raise ValueError("failed to bracket a real cubic root")
    stop = None
    for iterations in range(1, MAXIMUM_BISECTIONS + 1):
        middle = (left + right) / 2
        value = cubic_value(middle, coefficients)
        if value == 0:
            left = right = middle
            stop = "zero residual in Decimal arithmetic"
            break
        if value < 0:
            left = middle
        else:
            right = middle
        if right - left <= ROOT_RELATIVE_WIDTH * max(Decimal(1), abs(middle)):
            stop = "declared relative search-width criterion"
            break
    if stop is None:
        raise ValueError("bounded cubic search did not converge")
    real = (left + right) / 2
    a, b, c = coefficients
    linear = a + real
    constant = b + real * linear
    discriminant = linear * linear - 4 * constant
    if discriminant >= 0:
        raise ValueError("expected exactly one real root and a nonreal conjugate pair")
    pair_real = -linear / 2
    pair_imag = (-discriminant).sqrt() / 2
    if real * pair_real >= 0:
        raise ValueError("expected a hyperbolic saddle focus")
    # Direct polynomial residual at the positive-imaginary root.
    re = (pair_real**3 - 3 * pair_real * pair_imag**2
          + a * (pair_real**2 - pair_imag**2) + b * pair_real + c)
    im = (3 * pair_real**2 * pair_imag - pair_imag**3
          + 2 * a * pair_real * pair_imag + b * pair_imag)
    return {
        "real_eigenvalue": real,
        "complex_pair_real": pair_real,
        "complex_pair_imaginary_magnitude": pair_imag,
        "characteristic_coefficients": coefficients,
        "quadratic_discriminant": discriminant,
        "maximum_characteristic_component_residual": max(
            abs(cubic_value(real, coefficients)), abs(re), abs(im)),
        "bisection": {
            "iterations": iterations, "maximum_iterations": MAXIMUM_BISECTIONS,
            "converged": True, "termination": stop,
            "final_search_width": right - left,
            "relative_width_target": ROOT_RELATIVE_WIDTH,
            "rigorous_enclosure": False,
        },
    }


def spectrum_convention(spectrum):
    real, pair = spectrum["real_eigenvalue"], spectrum["complex_pair_real"]
    stable = int(real < 0) + 2 * int(pair < 0)
    unstable = int(real > 0) + 2 * int(pair > 0)
    forward = real + pair
    # The standard Shilnikov convention here means one real unstable direction
    # and a stable complex pair. Reverse time for the small equilibrium only.
    reversed_for_standard = real < 0
    standard = -forward if reversed_for_standard else forward
    return {
        "forward_stable_dimension": stable,
        "forward_unstable_dimension": unstable,
        "reversed_stable_dimension": unstable,
        "reversed_unstable_dimension": stable,
        "forward_signed_sum_real_plus_pair_real": forward,
        "reversed_signed_sum_real_plus_pair_real": -forward,
        "standard_one_dimensional_unstable_time_direction": (
            "reversed" if reversed_for_standard else "forward"),
        "standard_one_dimensional_unstable_saddle_quantity": standard,
        "standard_spectral_inequality_positive": standard > 0,
        "homoclinic_existence_established": False,
    }


def numpy_spectrum(values):
    real_candidates = [value for value in values if abs(value.imag) <= 1e-12]
    positive_pair = [value for value in values if value.imag > 1e-12]
    negative_pair = [value for value in values if value.imag < -1e-12]
    if len(real_candidates) != 1 or len(positive_pair) != 1 or len(negative_pair) != 1:
        raise ValueError("NumPy did not recover the expected saddle-focus spectrum")
    if abs(positive_pair[0].conjugate() - negative_pair[0]) > 1e-12:
        raise ValueError("NumPy complex roots are not conjugate")
    return {
        "real_eigenvalue": float(real_candidates[0].real),
        "complex_pair_real": float(positive_pair[0].real),
        "complex_pair_imaginary_magnitude": float(positive_pair[0].imag),
    }


def spectrum_disagreement(binary64, decimal):
    return max(abs(Decimal.from_float(value) - decimal[key])
               for key, value in binary64.items())


def inspect_point(name, a_text, b_text, c_text):
    with localcontext() as context:
        context.prec = PRECISION
        context.rounding = ROUND_HALF_EVEN
        a, b, c = map(Decimal, (a_text, b_text, c_text))
        reference_states = stable_equilibria(a, b, c)
        parameters = RosslerParameters(float(a), float(b), float(c))
        states = rossler_equilibria(parameters)
        values = equilibrium_eigenvalues(parameters)
        if states.shape != (2, 3) or values.shape != (2, 3):
            raise ValueError("the package must return both declared equilibria")
        rows = []
        for label, state, reference, eigenvalues in zip(
            ("small", "large"), states, reference_states, values, strict=True
        ):
            spectrum = solve_saddle_focus_cubic(analytic_coefficients(a, c, reference))
            matrix = rossler_jacobian(state, parameters)
            exact_binary64_matrix = [[Decimal.from_float(float(value)) for value in row]
                                     for row in matrix]
            same_matrix = solve_saddle_focus_cubic(matrix_coefficients(exact_binary64_matrix))
            observed = numpy_spectrum(eigenvalues)
            x, y, z = reference
            reference_rhs = (-y - z, x + a * y, b + z * (x - c))
            rows.append({
                "equilibrium": label,
                "state_numpy": state.tolist(), "state_decimal80": reference,
                "maximum_state_difference_numpy_decimal80": max(
                    abs(Decimal.from_float(float(value)) - expected)
                    for value, expected in zip(state, reference, strict=True)),
                "rhs_infinity_norm_numpy": float(np.max(np.abs(rossler_rhs(0.0, state, parameters)))),
                "rhs_infinity_norm_decimal80": max(map(abs, reference_rhs)),
                "quadratic_residual_decimal80": abs(a * z * z - c * z + b),
                "numpy_eigenvalues": observed,
                "decimal80_analytic_spectrum": spectrum,
                "decimal80_exact_binary64_jacobian_spectrum": same_matrix,
                "maximum_spectral_component_difference_numpy_analytic": spectrum_disagreement(observed, spectrum),
                "maximum_spectral_component_difference_same_binary64_matrix": spectrum_disagreement(observed, same_matrix),
                "spectral_convention": spectrum_convention(spectrum),
            })
        return {
            "id": name,
            "parameters_decimal": {"a": a_text, "b": b_text, "c": c_text},
            "equilibria": rows,
        }


def json_safe(value):
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("nonfinite Decimal result")
        return str(value)
    if isinstance(value, dict):
        return {key: json_safe(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(child) for child in value]
    return value


def build_report():
    return json_safe({
        "schema": "butterfly.review001-equilibrium-algebra.v1",
        "scope": "equilibrium and local spectral algebra only; no trajectories, manifold calculation, or proof of a global connection",
        "input_semantics": "declared decimal literals are exact inputs to Decimal; package calculations round them to binary64",
        "comparison_semantics": "the same-binary64-matrix comparison isolates the NumPy eigensolver versus Decimal cubic solver; the analytic comparison also includes parameter, equilibrium, and matrix rounding",
        "precision": {"decimal_digits": PRECISION, "rounding": "ROUND_HALF_EVEN", "validated_interval_arithmetic": False},
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "source_sha256": {
            "script": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "models": hashlib.sha256((ROOT / "python/butterfly/models.py").read_bytes()).hexdigest(),
        },
        "spectral_quantity_definition": "lambda_real + Re(lambda_complex), one member of the conjugate pair, not the trace; reversing time negates the sum and swaps stable/unstable dimensions",
        "standard_shilnikov_convention": "one positive real exponent and a stable conjugate pair; the spectral inequality is necessary context for the cited homoclinic theorem, not evidence that a homoclinic loop exists",
        "limitations": [
            "80-digit working arithmetic is not an 80-digit accuracy or enclosure claim",
            "small residuals and cross-algorithm agreement do not validate a homoclinic parameter",
            "neither equilibrium's global manifold involvement or hub-organizing role is tested",
            "source parameter literals identify audit points, not error-bounded measured coordinates",
        ],
        "points": [inspect_point(*point) for point in POINTS],
    })


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new JSON output path; otherwise print to stdout")
    args = parser.parse_args(argv)
    if args.output is not None and (args.output.exists() or args.output.is_symlink()):
        parser.error("output already exists; refusing to overwrite")
    encoded = json.dumps(build_report(), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output is None:
        print(encoded, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as destination:
            destination.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

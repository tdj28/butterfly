#!/usr/bin/env python3
"""Post-hoc arithmetic inspection of two frozen EXP-476 intervals.

Only local cubic Hermite polynomials, the analytic field, and the original
five-point Lobatto residual definition are evaluated. No integration, BVP
solve, optimizer, mesh refinement, or acceptance reclassification is performed.
Decimal.from_float treats each archived binary64 number as exact input; using
80-digit arithmetic cannot recover digits lost before the receipt was saved.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import platform


ROOT = Path(__file__).resolve().parents[1]
RAW_SHA256 = "c9818275ed3c585934cdeaa85857b04a5e9a6e1a6400f426a5cbf6e06d5b95bc"
MESH_SHA256 = "f27a842cc06b48ff8af19edeea83f6d167922e4a2d829f6fc2ce0ff033e8cb74"
SELECTED_CASES = ("r0.005-tol1e-8", "r0.01-tol1e-8")
PRECISION = 80


def exact_binary64(value):
    """Preserve the exact archived binary value, not its decimal abbreviation."""
    return Decimal.from_float(float(value))


def square_root(value):
    return value.sqrt() if isinstance(value, Decimal) else math.sqrt(value)


def hermite_coefficients(left_state, right_state, left_derivative, right_derivative, width):
    """Ascending-power coefficients in local coordinate x - x_left.

    Operation order follows SciPy's create_spline algebra, with generic float
    or Decimal arithmetic. No interpolation samples or endpoint data change.
    """
    coefficients = []
    for y0, y1, f0, f1 in zip(left_state, right_state, left_derivative, right_derivative):
        slope = (y1 - y0) / width
        auxiliary = (f0 + f1 - 2 * slope) / width
        coefficients.append((y0, f0, (slope - f0) / width - auxiliary, auxiliary / width))
    return coefficients


def hermite_evaluate(coefficients, offset):
    values, derivatives = [], []
    for c0, c1, c2, c3 in coefficients:
        values.append(((c3 * offset + c2) * offset + c1) * offset + c0)
        derivatives.append((3 * c3 * offset + 2 * c2) * offset + c1)
    return values, derivatives


def interval_residual(left, right, left_state, right_state, field):
    """The original collocation state balance and relative Lobatto RMS.

    The midpoint derivative residual is 1.5*state_balance/width, as in
    SciPy's solve_bvp. The other two nonzero quadrature samples are the same
    global-coordinate Lobatto abscissae, evaluated at the selected precision.
    Residuals at the Hermite endpoints are mathematically zero.
    """
    width = right - left
    if width <= 0 or len(left_state) != len(right_state):
        raise ValueError("a positive-width interval and matching endpoint dimensions are required")
    zero, one = width - width, (width - width) + 1
    f_left, f_right = field(left, left_state), field(right, right_state)
    coefficients = hermite_coefficients(left_state, right_state, f_left, f_right, width)
    middle = left + width / 2
    middle_state = [(y0 + y1) / 2 - width / 8 * (f1 - f0)
                    for y0, y1, f0, f1 in zip(left_state, right_state, f_left, f_right)]
    f_middle = field(middle, middle_state)
    balance = [y1 - y0 - width / 6 * (f0 + f1 + 4 * fm)
               for y0, y1, f0, f1, fm in zip(left_state, right_state, f_left, f_right, f_middle)]
    middle_relative = [(3 * defect / (2 * width)) / (one + abs(fm))
                       for defect, fm in zip(balance, f_middle)]
    offset = width / 2 * square_root(one * 3 / 7)
    quadrature_residuals = []
    for point in (middle + offset, middle - offset):
        values, derivative = hermite_evaluate(coefficients, point - left)
        rhs = field(point, values)
        quadrature_residuals.append([(observed - expected) / (one + abs(expected))
                                    for observed, expected in zip(derivative, rhs)])
    component_squared = [
        (one / 2) * ((one * 32 / 45) * rm**2 + (one * 49 / 90) * (r1**2 + r2**2))
        for rm, r1, r2 in zip(middle_relative, *quadrature_residuals)
    ]
    _left_value, reconstructed_left = hermite_evaluate(coefficients, zero)
    _right_value, reconstructed_right = hermite_evaluate(coefficients, width)
    endpoint_error = max(abs(observed - expected)
                         for observed, expected in zip(reconstructed_left + reconstructed_right, f_left + f_right))
    return {
        "width": width,
        "relative_rms": square_root(sum(component_squared)),
        "component_relative_rms": [square_root(value) for value in component_squared],
        "absolute_collocation_state_balance_defect": [abs(value) for value in balance],
        "signed_collocation_state_balance_defect": balance,
        "midpoint_relative_derivative_defect": middle_relative,
        "maximum_endpoint_derivative_reconstruction_error": endpoint_error,
        "left_field_derivative": f_left, "right_field_derivative": f_right,
    }


def rossler_field(a, b, c, duration):
    def field(_position, states):
        x, y, z = states
        return [duration * (-y - z), duration * (x + a * y), duration * (b + z * (x - c))]

    return field


def synthetic_controls():
    """Smooth quadratic solutions, with exact and binary64-rounded samples.

    y(s)=54+10^8*(s-1)^2 has a stationary component at s=1. Its analytic
    derivative supplies the nonautonomous control field. Exact endpoint data
    must give zero residual up to arithmetic precision; rounding endpoints can
    leave a derivative defect despite exact reconstruction of endpoint slopes.
    """
    results = []
    with localcontext() as context:
        context.prec = PRECISION
        base, curvature, center = Decimal(54), Decimal(100000000), Decimal(1)
        for name, left_float, right_float in (
            ("near-stationary-tiny-interval", 1.0000000001, 1.0000000001086218),
            ("well-spaced-interval", 1.0000000001, 1.0001000001),
        ):
            left, right = exact_binary64(left_float), exact_binary64(right_float)

            def truth(position):
                return base + curvature * (position - center)**2

            def field(position, _states):
                return [2 * curvature * (position - center)]

            exact_states = ([truth(left)], [truth(right)])
            rounded_states = tuple([exact_binary64(values[0])] for values in exact_states)
            exact_result = interval_residual(left, right, *exact_states, field)
            rounded_result = interval_residual(left, right, *rounded_states, field)
            float_result = interval_residual(
                left_float, right_float, [float(rounded_states[0][0])], [float(rounded_states[1][0])],
                lambda position, _states: [2.0e8 * (position - 1.0)],
            )
            results.append({
                "name": name, "left": left, "right": right,
                "definition": "y(s)=54+1e8*(s-1)^2; field y'=2e8*(s-1); endpoint data are the only changed ingredient",
                "exact_endpoints": [values[0] for values in exact_states],
                "rounded_binary64_endpoints": [values[0] for values in rounded_states],
                "endpoint_rounding_errors": [rounded[0] - exact[0] for exact, rounded in zip(exact_states, rounded_states)],
                "decimal80_exact_endpoint_data": exact_result,
                "decimal80_rounded_endpoint_data": rounded_result,
                "binary64_rounded_endpoint_data": float_result,
            })
    return results


def inspect_saved_interval(row, mesh_case, fixed):
    peak = mesh_case["worst_intervals"][0]
    index = peak["index"]
    mesh, states = row["normalized_mesh"], row["states"]
    if mesh[index:index + 2] != peak["normalized_span"] or states[index] != peak["left_state"] or states[index + 1] != peak["right_state"]:
        raise ValueError("hash-bound interval diagnostic does not match the saved source interval")
    summary = row["collocation"]
    parameters = [summary["parameter"], fixed["b"], fixed["c"], summary["flight_time"]]
    binary64 = interval_residual(mesh[index], mesh[index + 1], states[index], states[index + 1], rossler_field(*parameters))
    with localcontext() as context:
        context.prec = PRECISION
        decimal80 = interval_residual(
            exact_binary64(mesh[index]), exact_binary64(mesh[index + 1]),
            [exact_binary64(value) for value in states[index]],
            [exact_binary64(value) for value in states[index + 1]],
            rossler_field(*(exact_binary64(value) for value in parameters)),
        )
        ratio = decimal80["relative_rms"] / exact_binary64(peak["relative_rms"])
    return {
        "case": row["case"], "original_status": row["status"], "interval_index": index,
        "selection": "single worst interval by the hash-bound saved-mesh diagnostic; chosen before this arithmetic evaluation",
        "archived_scipy_binary64": peak,
        "local_binary64_arithmetic": binary64,
        "decimal80_arithmetic_on_exact_archived_binary64_inputs": decimal80,
        "decimal80_to_archived_binary64_relative_rms_ratio": ratio,
        "local_binary64_minus_archived_relative_rms": binary64["relative_rms"] - peak["relative_rms"],
    }


def json_safe(value):
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("nonfinite Decimal diagnostic")
        return str(value)
    if isinstance(value, dict):
        return {key: json_safe(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(child) for child in value]
    return value


def bound_json(path, expected_hash):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_hash:
        raise ValueError(f"frozen input hash mismatch: {path.name}")
    return json.loads(raw)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=ROOT / "artifacts/EXP-476/receipt.json")
    parser.add_argument("--mesh-diagnostic", type=Path, default=ROOT / "artifacts/EXP-476/mesh-diagnostic.json")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/EXP-476/arithmetic-diagnostic.json")
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("arithmetic diagnostic output already exists; refusing to overwrite")
    receipt = bound_json(args.receipt, RAW_SHA256)
    mesh_diagnostic = bound_json(args.mesh_diagnostic, MESH_SHA256)
    if receipt["experiment_id"] != "EXP-476" or mesh_diagnostic["receipt_sha256"] != RAW_SHA256:
        raise ValueError("unexpected source experiment or diagnostic binding")
    fixed = {"b": 0.2, "c": 10.3084}
    manifest_path = ROOT / "experiments/manifests/EXP-476-homoclinic-radius-tolerance-grid.json"
    manifest = bound_json(manifest_path, receipt["manifest_sha256"])
    if manifest["fixed_parameters"] != fixed:
        raise ValueError("unexpected fixed parameter convention")
    source_rows = {row["case"]["name"]: row for row in receipt["cases"]}
    diagnostic_rows = {row["case"]["name"]: row for row in mesh_diagnostic["cases"]}
    result = {
        "schema": "butterfly.homoclinic-interval-arithmetic-inspection.v1",
        "experiment_id": "EXP-476", "raw_receipt_sha256": RAW_SHA256,
        "mesh_diagnostic_sha256": MESH_SHA256, "manifest_sha256": receipt["manifest_sha256"],
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": platform.python_version(), "decimal_precision": PRECISION,
        "selection_rule": list(SELECTED_CASES),
        "scope": "post-hoc fixed-interval arithmetic diagnostic only; no target integration, BVP solve, cap change, or qualification",
        "input_semantics": "archived binary64 values converted exactly using Decimal.from_float; higher precision does not recover lost input digits",
        "residual_definition": "unchanged local cubic Hermite field residual normalized componentwise by 1+abs(field), with original five-point Lobatto weights and midpoint state-balance identity",
        "rounding_note": "binary64 and Decimal evaluate the same algebra at their own precision, including field operations and global-coordinate quadrature abscissae; operation ordering may differ slightly from compiled SciPy polynomial evaluation",
        "intervals": [inspect_saved_interval(source_rows[name], diagnostic_rows[name], fixed) for name in SELECTED_CASES],
        "synthetic_controls": synthetic_controls(),
        "limitations": [
            "retained node quantization cannot be reversed by higher-precision reevaluation",
            "synthetic controls isolate one possible arithmetic mechanism, not the target solver's adaptive history",
            "two selected intervals do not establish a global parameter error bound or qualify a failed case",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as destination:
        destination.write(json.dumps(json_safe(result), sort_keys=True, indent=2, allow_nan=False).encode() + b"\n")
    print(json.dumps({"output": str(args.output), "selected_intervals": len(result["intervals"]), "target_integrations": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Validate and compare a frozen finite-radius homoclinic refinement grid.

The comparisons describe observed sensitivity, never a rigorous parameter error
bound.  In particular, technical success and discretization refinement do not
require an endpoint effect to be resolved.  Target integration is intentionally
absent from this module.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
from numbers import Real


GRID_SCHEMA = "butterfly.projected-homoclinic-pilot.v2"
SUMMARY_SCHEMA = "butterfly.projected-homoclinic-grid-sensitivity.v1"

_GATES = (
    "maximum_finest_a_difference",
    "maximum_contraction_ratio",
    "contraction_absolute_slack",
    "endpoint_resolution_fraction",
    "empirical_resolution",
)


def _positive_finite(value, description):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{description} must be finite and positive")
    return float(value)


def _axis(values, description):
    if not isinstance(values, list) or len(values) != 3:
        raise ValueError(f"{description} must contain exactly three values")
    result = [_positive_finite(value, description) for value in values]
    if not result[0] > result[1] > result[2]:
        raise ValueError(f"{description} must be unique and strictly decreasing")
    return result


def _case_key(case):
    if not isinstance(case, Mapping):
        raise ValueError("each case must be a mapping")
    try:
        name = case["name"]
        key = (
            _positive_finite(case["radius"], "case radius"),
            _positive_finite(case["tolerance"], "case tolerance"),
        )
    except KeyError as error:
        raise ValueError(f"case is missing {error.args[0]}") from error
    if not isinstance(name, str) or not name or name != name.strip():
        raise ValueError("case name must be a nonempty string without surrounding whitespace")
    return key, name


def validate_grid_manifest(manifest):
    """Validate v2 grid metadata and return a new list in frozen run order.

    The runner remains responsible for common source, solver, resource, replay,
    and control settings.  This function owns the v2 schema, ``refinement``
    axes/gates, and exact nine-case Cartesian grid.  The manifest must already
    order cases by decreasing radius, then decreasing (loose-to-tight)
    tolerance; analysis of completed rows is independent of their order.
    """
    if not isinstance(manifest, Mapping) or manifest.get("schema") != GRID_SCHEMA:
        raise ValueError("unsupported homoclinic refinement grid manifest")
    refinement = manifest.get("refinement")
    if not isinstance(refinement, Mapping):
        raise ValueError("manifest requires refinement metadata")
    try:
        radii = _axis(refinement["radii"], "refinement radii")
        tolerances = _axis(refinement["tolerances"], "refinement tolerances")
        gates = {key: _positive_finite(refinement[key], f"refinement {key}") for key in _GATES}
    except KeyError as error:
        raise ValueError(f"refinement metadata is missing {error.args[0]}") from error
    if gates["maximum_contraction_ratio"] >= 1:
        raise ValueError("maximum_contraction_ratio must be smaller than one")
    if gates["endpoint_resolution_fraction"] > 1:
        raise ValueError("endpoint_resolution_fraction must be at most one")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or len(cases) != 9:
        raise ValueError("refinement requires all nine Cartesian grid cases")
    actual = [_case_key(case) for case in cases]
    pairs, names = [item[0] for item in actual], [item[1] for item in actual]
    if len(set(names)) != len(names):
        raise ValueError("refinement case names must be unique")
    if len(set(pairs)) != len(pairs):
        raise ValueError("refinement radius/tolerance pairs must be unique")
    expected = [(radius, tolerance) for radius in radii for tolerance in tolerances]
    if set(pairs) != set(expected):
        raise ValueError("cases must equal the declared Cartesian radius/tolerance grid")
    if pairs != expected:
        raise ValueError("cases must run radius-major, loose-to-tight tolerance")
    return [dict(case) for case in cases]


def _nonfinite_paths(value, path="row"):
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from _nonfinite_paths(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            yield from _nonfinite_paths(child, f"{path}[{index}]")
    elif isinstance(value, Real) and not isinstance(value, bool) and not math.isfinite(value):
        yield path


def nonfinite_numeric_paths(value):
    """Return locations of nonfinite numeric values in JSON-shaped data."""
    return list(_nonfinite_paths(value))


def _finite_parameter(row):
    summary = row.get("collocation")
    value = summary.get("parameter") if isinstance(summary, Mapping) else None
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        return None
    return float(value)


def summarize_grid_sensitivity(rows, manifest):
    """Summarize existing runner rows, failing closed on incomplete evidence.

    Each row contains ``case`` metadata, ``collocation.parameter``, and boolean
    ``passed``. Extra row diagnostics are retained by the caller, but any
    nonfinite numeric diagnostic disqualifies the row. Malformed receipt rows
    produce explicit issues, not exceptions or silently dropped evidence.

    ``passed`` combines complete technical success and the per-radius D1/D2
    discretization gates only. Endpoint classifications are a separate result;
    ``below_declared_empirical_resolution`` takes precedence over ``resolved``
    when both the endpoint difference and summed D2 are tiny. All shifts use
    later-minus-earlier (tighter tolerance or smaller radius) sign conventions.
    """
    cases = validate_grid_manifest(manifest)
    refinement = manifest["refinement"]
    radii, tolerances = refinement["radii"], refinement["tolerances"]
    expected = {_case_key(case)[0]: case["name"] for case in cases}
    collected, duplicates, issues = {}, set(), []
    arithmetic_finite = True
    if not isinstance(rows, (list, tuple)):
        rows = []
        issues.append("receipt cases must be a list or tuple")
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            issues.append(f"row {index}: receipt row must be a mapping")
            continue
        try:
            key, name = _case_key(row.get("case"))
        except ValueError as error:
            issues.append(f"row {index}: {error}")
            continue
        if key not in expected:
            issues.append(f"row {index}: unexpected radius/tolerance pair {key}")
            continue
        if name != expected[key]:
            issues.append(f"row {index}: case name does not match frozen pair {key}")
            continue
        if key in collected:
            duplicates.add(key)
            issues.append(f"row {index}: duplicate radius/tolerance pair {key}")
            continue
        parameter = _finite_parameter(row)
        nonfinite = nonfinite_numeric_paths(row)
        if parameter is None:
            issues.append(f"case {name}: collocation parameter is missing or nonfinite")
        if nonfinite:
            issues.append(f"case {name}: nonfinite diagnostics at {', '.join(nonfinite)}")
        if row.get("passed") is not True:
            issues.append(f"case {name}: technical gates did not pass")
        collected[key] = {
            "parameter": parameter,
            "technical_passed": bool(parameter is not None and not nonfinite and row.get("passed") is True),
        }
    missing = [expected[key] for key in expected if key not in collected]
    if missing:
        issues.append(f"missing cases: {', '.join(missing)}")
    complete = len(rows) == 9 and set(collected) == set(expected) and not duplicates
    radius_results = []
    for radius in radii:
        keys = [(radius, tolerance) for tolerance in tolerances]
        parameters = [collected.get(key, {}).get("parameter") for key in keys]
        technical = all(collected.get(key, {}).get("technical_passed", False) and key not in duplicates for key in keys)
        shifts = [None, None]
        if all(parameter is not None for parameter in parameters):
            shifts = [parameters[1] - parameters[0], parameters[2] - parameters[1]]
            if not all(math.isfinite(shift) for shift in shifts):
                issues.append(f"radius {radius}: nonfinite derived tolerance differences")
                shifts, technical = [None, None], False
                arithmetic_finite = False
        differences = [abs(shift) if shift is not None else None for shift in shifts]
        d1, d2 = differences
        limit = refinement["maximum_contraction_ratio"] * d1 + refinement["contraction_absolute_slack"] if d1 is not None else None
        absolute_gate = d2 is not None and d2 <= refinement["maximum_finest_a_difference"]
        contraction_gate = d2 is not None and d2 <= limit
        radius_results.append({
            "radius": radius,
            "tolerances": list(tolerances),
            "parameters": parameters,
            "signed_a_shifts": shifts,
            "D1": d1,
            "D2": d2,
            "contraction_limit": limit,
            "technical_passed": technical,
            "absolute_gate_passed": absolute_gate,
            "contraction_gate_passed": contraction_gate,
            "passed": bool(technical and absolute_gate and contraction_gate),
        })
    endpoint_results = []
    for outer, inner in zip(radius_results, radius_results[1:]):
        signed_shift, difference, summed_d2, limit = None, None, None, None
        classification = "unavailable"
        if outer["parameters"][-1] is not None and inner["parameters"][-1] is not None:
            signed_shift = inner["parameters"][-1] - outer["parameters"][-1]
            if math.isfinite(signed_shift):
                difference = abs(signed_shift)
                limit = refinement["endpoint_resolution_fraction"] * difference
            else:
                signed_shift = None
                issues.append(f"radii {outer['radius']} / {inner['radius']}: nonfinite derived endpoint difference")
                arithmetic_finite = False
        if outer["D2"] is not None and inner["D2"] is not None:
            summed_d2 = outer["D2"] + inner["D2"]
            if not math.isfinite(summed_d2):
                summed_d2 = None
                issues.append(f"radii {outer['radius']} / {inner['radius']}: nonfinite summed D2")
                arithmetic_finite = False
        if outer["technical_passed"] and inner["technical_passed"] and difference is not None and summed_d2 is not None:
            if difference <= refinement["empirical_resolution"] and summed_d2 <= refinement["empirical_resolution"]:
                classification = "below_declared_empirical_resolution"
            elif summed_d2 <= limit:
                classification = "resolved"
            else:
                classification = "unresolved"
        endpoint_results.append({
            "outer_radius": outer["radius"],
            "inner_radius": inner["radius"],
            "tolerance": tolerances[-1],
            "signed_a_shift": signed_shift,
            "a_difference": difference,
            "summed_D2": summed_d2,
            "resolution_limit": limit,
            "classification": classification,
        })
    technical_passed = bool(complete and all(row["technical_passed"] for row in radius_results))
    discretization_passed = bool(complete and all(row["passed"] for row in radius_results))
    evaluable = bool(technical_passed and arithmetic_finite)
    return {
        "schema": SUMMARY_SCHEMA,
        "complete": complete,
        "evaluable": evaluable,
        "technical_passed": technical_passed,
        "discretization_passed": discretization_passed,
        "passed": bool(evaluable and discretization_passed),
        "radius_refinements": radius_results,
        "endpoint_comparisons": endpoint_results,
        "issues": issues,
        "interpretation": "observed finite-radius/discretization sensitivity, not a rigorous parameter error bound; endpoint-effect resolution is separate from technical and discretization success",
    }

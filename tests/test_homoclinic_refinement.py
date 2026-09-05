from copy import deepcopy
import json
import math

import pytest

from butterfly.homoclinic_refinement import (
    GRID_SCHEMA,
    nonfinite_numeric_paths,
    summarize_grid_sensitivity,
    validate_grid_manifest,
)


def grid_manifest():
    radii, tolerances = [0.01, 0.005, 0.0025], [1e-6, 1e-7, 1e-8]
    return {
        "schema": GRID_SCHEMA,
        "refinement": {
            "radii": radii,
            "tolerances": tolerances,
            "maximum_finest_a_difference": 1e-9,
            "maximum_contraction_ratio": 0.3,
            "contraction_absolute_slack": 1e-10,
            "endpoint_resolution_fraction": 0.25,
            "empirical_resolution": 1e-9,
        },
        "cases": [
            {"name": f"r-{radius}-tol-{tolerance}", "radius": radius, "tolerance": tolerance}
            for radius in radii for tolerance in tolerances
        ],
    }


def receipt_rows(manifest, *, finest=(0.18, 0.18000001, 0.18000002), d1=1e-8, d2=2e-10):
    values = {
        (radius, tolerance): value
        for radius, parameter in zip(manifest["refinement"]["radii"], finest)
        for tolerance, value in zip(manifest["refinement"]["tolerances"], [parameter - d2 - d1, parameter - d2, parameter])
    }
    return [
        {"case": dict(case), "passed": True, "collocation": {"parameter": values[(case["radius"], case["tolerance"])]}}
        for case in manifest["cases"]
    ]


def test_validator_accepts_frozen_cartesian_order_without_mutation():
    manifest = grid_manifest()
    before = deepcopy(manifest)
    cases = validate_grid_manifest(manifest)
    assert cases == manifest["cases"]
    assert cases is not manifest["cases"]
    assert all(left is not right for left, right in zip(cases, manifest["cases"]))
    assert manifest == before


@pytest.mark.parametrize("change, message", [
    (lambda manifest: manifest.update(schema="butterfly.projected-homoclinic-pilot.v1"), "unsupported"),
    (lambda manifest: manifest.pop("refinement"), "refinement"),
    (lambda manifest: manifest["cases"].pop(), "nine"),
    (lambda manifest: manifest["cases"].append(dict(manifest["cases"][0])), "nine"),
    (lambda manifest: manifest["cases"][1].update(radius=0.01, tolerance=1e-6), "pairs must be unique"),
    (lambda manifest: manifest["cases"][1].update(name=manifest["cases"][0]["name"]), "names must be unique"),
    (lambda manifest: manifest["cases"][0].update(radius=0.02), "Cartesian"),
    (lambda manifest: manifest["cases"].reverse(), "radius-major"),
    (lambda manifest: manifest["refinement"]["radii"].reverse(), "strictly decreasing"),
    (lambda manifest: manifest["refinement"].update(tolerances=[1e-6, 1e-6, 1e-8]), "strictly decreasing"),
    (lambda manifest: manifest["refinement"].update(radii=[0.01, 0.005]), "exactly three"),
    (lambda manifest: manifest["cases"][0].update(name=" "), "nonempty"),
    (lambda manifest: manifest["cases"][0].pop("radius"), "missing radius"),
    (lambda manifest: manifest["refinement"].pop("empirical_resolution"), "missing empirical_resolution"),
    (lambda manifest: manifest["refinement"].update(maximum_contraction_ratio=1), "smaller than one"),
    (lambda manifest: manifest["refinement"].update(endpoint_resolution_fraction=1.1), "at most one"),
])
def test_validator_rejects_structural_errors(change, message):
    manifest = grid_manifest()
    change(manifest)
    with pytest.raises(ValueError, match=message):
        validate_grid_manifest(manifest)


@pytest.mark.parametrize("value", [0, -1, math.inf, -math.inf, math.nan, True, "1e-8", None])
@pytest.mark.parametrize("location", ["radius", "tolerance", "gate"])
def test_validator_requires_finite_positive_numeric_metadata(value, location):
    manifest = grid_manifest()
    if location == "gate":
        manifest["refinement"]["maximum_finest_a_difference"] = value
    else:
        manifest["cases"][0][location] = value
    with pytest.raises(ValueError, match="finite and positive"):
        validate_grid_manifest(manifest)


def test_summary_groups_by_metadata_not_position_and_keeps_signed_shifts():
    manifest = grid_manifest()
    rows = receipt_rows(manifest, finest=(0.18000002, 0.18000001, 0.18), d1=-1e-8, d2=-2e-10)
    result = summarize_grid_sensitivity(rows, manifest)
    shuffled = rows[::2] + rows[1::2]
    assert summarize_grid_sensitivity(shuffled, manifest) == result
    assert result["complete"] and result["technical_passed"] and result["discretization_passed"] and result["passed"]
    assert not result["issues"]
    for row in result["radius_refinements"]:
        assert row["signed_a_shifts"] == pytest.approx([-1e-8, -2e-10])
        assert row["D1"] == pytest.approx(1e-8)
        assert row["D2"] == pytest.approx(2e-10)
    for row in result["endpoint_comparisons"]:
        assert row["signed_a_shift"] == pytest.approx(-1e-8)
        assert row["a_difference"] == pytest.approx(1e-8)
        assert row["summed_D2"] == pytest.approx(4e-10)
        assert row["classification"] == "resolved"


@pytest.mark.parametrize("change, issue", [
    (lambda rows: rows.pop(), "missing cases"),
    (lambda rows: rows.append(deepcopy(rows[0])), "duplicate"),
    (lambda rows: rows.__setitem__(1, deepcopy(rows[0])), "duplicate"),
    (lambda rows: rows.append({"case": {"name": "extra", "radius": 0.02, "tolerance": 1e-8}, "passed": True, "collocation": {"parameter": 0.18}}), "unexpected"),
    (lambda rows: rows[0]["case"].update(name="renamed"), "name does not match"),
    (lambda rows: rows[0]["case"].update(radius=math.nan), "finite and positive"),
    (lambda rows: rows.__setitem__(0, "not a row"), "mapping"),
    (lambda rows: rows[0].pop("case"), "mapping"),
])
def test_incomplete_or_malformed_receipt_grid_fails_closed(change, issue):
    manifest = grid_manifest()
    rows = receipt_rows(manifest)
    change(rows)
    result = summarize_grid_sensitivity(rows, manifest)
    assert not result["complete"]
    assert not result["technical_passed"]
    assert not result["discretization_passed"]
    assert not result["passed"]
    assert any(issue in message for message in result["issues"])
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("rows", [None, {}, "bad"])
def test_nonsequence_receipt_is_reported_not_raised(rows):
    result = summarize_grid_sensitivity(rows, grid_manifest())
    assert not result["passed"]
    assert "list or tuple" in result["issues"][0]


@pytest.mark.parametrize("passed", [False, None, 1, "true"])
def test_failed_or_nonboolean_pass_status_does_not_hide_finite_parameters(passed):
    manifest = grid_manifest()
    rows = receipt_rows(manifest)
    rows[0]["passed"] = passed
    result = summarize_grid_sensitivity(rows, manifest)
    assert result["complete"]
    assert not result["technical_passed"] and not result["discretization_passed"] and not result["passed"]
    assert result["radius_refinements"][0]["D1"] is not None
    assert result["endpoint_comparisons"][0]["classification"] == "unavailable"
    assert result["radius_refinements"][1]["passed"]


@pytest.mark.parametrize("parameter", [math.nan, math.inf, -math.inf, None, True, "0.18"])
def test_invalid_parameter_has_no_derived_estimate(parameter):
    manifest = grid_manifest()
    rows = receipt_rows(manifest)
    rows[1]["collocation"]["parameter"] = parameter
    result = summarize_grid_sensitivity(rows, manifest)
    assert not result["passed"]
    assert result["radius_refinements"][0]["parameters"][1] is None
    assert result["radius_refinements"][0]["D1"] is None
    assert result["radius_refinements"][0]["D2"] is None
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("diagnostic", [
    {"replay": {"maximum_state_defect": math.nan}},
    {"states": [[0.0, math.inf, 0.0]]},
    {"seed": {"maximum_seed_arc_defect": -math.inf}},
])
def test_nonfinite_extra_diagnostics_fail_closed(diagnostic):
    manifest = grid_manifest()
    rows = receipt_rows(manifest)
    rows[0].update(diagnostic)
    result = summarize_grid_sensitivity(rows, manifest)
    assert not result["technical_passed"] and not result["passed"]
    assert any("nonfinite diagnostics" in issue for issue in result["issues"])
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("finest, d2", [
    ((0.0, 0.0, 0.0), 0.0),
    ((0.0, 2e-10, 4e-10), 2e-10),
])
def test_tiny_endpoint_effect_is_below_resolution_not_resolved(finest, d2):
    manifest = grid_manifest()
    result = summarize_grid_sensitivity(receipt_rows(manifest, finest=finest, d2=d2), manifest)
    assert result["passed"]
    assert all(row["classification"] == "below_declared_empirical_resolution" for row in result["endpoint_comparisons"])


def test_unresolved_endpoint_effect_is_separate_from_discretization_success():
    manifest = grid_manifest()
    rows = receipt_rows(manifest, finest=(0.0, 2e-9, 4e-9), d2=8e-10)
    result = summarize_grid_sensitivity(rows, manifest)
    assert result["technical_passed"] and result["discretization_passed"] and result["passed"]
    assert all(row["classification"] == "unresolved" for row in result["endpoint_comparisons"])


def test_endpoint_classification_does_not_claim_discretization_gate_pass():
    manifest = grid_manifest()
    rows = receipt_rows(manifest, finest=(0.0, 1e-6, 2e-6), d2=2e-9)
    result = summarize_grid_sensitivity(rows, manifest)
    assert result["technical_passed"] and not result["discretization_passed"] and not result["passed"]
    assert all(row["classification"] == "resolved" for row in result["endpoint_comparisons"])


@pytest.mark.parametrize("parameters, expected_absolute, expected_contraction", [
    ([-1e-8, 0.0, 1e-9], True, True),
    ([-1e-8, 0.0, math.nextafter(1e-9, math.inf)], False, True),
    ([0.0, 0.0, 1e-10], True, True),
    ([0.0, 0.0, math.nextafter(1e-10, math.inf)], True, False),
])
def test_discretization_gates_are_inclusive_and_use_both_limits(parameters, expected_absolute, expected_contraction):
    manifest = grid_manifest()
    rows = receipt_rows(manifest)
    for row, parameter in zip(rows[:3], parameters):
        row["collocation"]["parameter"] = parameter
    result = summarize_grid_sensitivity(rows, manifest)
    radius = result["radius_refinements"][0]
    assert radius["absolute_gate_passed"] is expected_absolute
    assert radius["contraction_gate_passed"] is expected_contraction
    assert radius["passed"] is (expected_absolute and expected_contraction)


def test_manifest_declared_resolution_controls_classification():
    manifest = grid_manifest()
    manifest["refinement"]["empirical_resolution"] = 1e-8
    result = summarize_grid_sensitivity(receipt_rows(manifest, finest=(0.0, 2e-9, 4e-9), d2=8e-10), manifest)
    assert all(row["classification"] == "below_declared_empirical_resolution" for row in result["endpoint_comparisons"])


def test_endpoint_quarter_difference_gate_includes_equality():
    manifest = grid_manifest()
    difference, d2 = 2.0**-28, 2.0**-31
    rows = receipt_rows(manifest, finest=(0.0, difference, 2 * difference), d1=2.0**-24, d2=d2)
    result = summarize_grid_sensitivity(rows, manifest)
    for endpoint in result["endpoint_comparisons"]:
        assert endpoint["summed_D2"] == endpoint["resolution_limit"]
        assert endpoint["classification"] == "resolved"


def test_endpoint_empirical_resolution_gate_includes_both_equalities():
    manifest = grid_manifest()
    rows = receipt_rows(manifest, finest=(0.0, 1e-9, 2e-9), d2=0.5e-9)
    endpoint = summarize_grid_sensitivity(rows, manifest)["endpoint_comparisons"][0]
    assert endpoint["a_difference"] == 1e-9
    assert endpoint["summed_D2"] == 1e-9
    assert endpoint["classification"] == "below_declared_empirical_resolution"


def test_arithmetic_overflow_of_finite_parameters_is_not_reported_as_finite_evidence():
    manifest = grid_manifest()
    rows = receipt_rows(manifest)
    rows[0]["collocation"]["parameter"] = -1e308
    rows[1]["collocation"]["parameter"] = 1e308
    result = summarize_grid_sensitivity(rows, manifest)
    assert not result["passed"]
    assert any("nonfinite derived tolerance" in issue for issue in result["issues"])
    json.dumps(result, allow_nan=False)


def test_endpoint_arithmetic_overflow_makes_analysis_nonevaluable():
    manifest = grid_manifest()
    rows = receipt_rows(manifest, finest=(-1e308, 1e308, 1e308), d1=0.0, d2=0.0)
    result = summarize_grid_sensitivity(rows, manifest)
    assert result["technical_passed"] and result["discretization_passed"]
    assert not result["evaluable"] and not result["passed"]
    assert result["endpoint_comparisons"][0]["classification"] == "unavailable"
    assert any("nonfinite derived endpoint" in issue for issue in result["issues"])
    json.dumps(result, allow_nan=False)


def test_recursive_nonfinite_helper_exposes_diagnostic_paths():
    assert nonfinite_numeric_paths({"nested": [0.0, {"bad": math.nan}], "other": math.inf}) == [
        "row.nested[1].bad", "row.other"
    ]
    assert nonfinite_numeric_paths({"finite": 0.0, "label": "NaN is text", "flag": True, "absent": None}) == []

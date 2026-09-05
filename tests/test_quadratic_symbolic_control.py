"""Algebra fixtures and period-2 control only; no held-out target enumeration."""

from fractions import Fraction
import json

import pytest

from scripts import verify_quadratic_symbolic_control as control


def protocol():
    return {
        "schema": control.MANIFEST_SCHEMA,
        "experiment_id": "synthetic-period2-control",
        "periods": [2],
        "parameter_domain": ["0", "2"],
        "root_interval_bits": 20,
        "maximum_sign_refinements": 32,
        "limits": {"maximum_operations": 100_000, "maximum_coefficient_bits": 16_384,
                   "maximum_interval_nodes": 10_000, "maximum_wall_seconds": 30},
    }


def test_pseudo_remainder_preserves_sturm_sign_with_negative_leading_divisor():
    # (x^2-2) mod (-2x+1) = -7/4, so its positive integer multiple is -1.
    assert control.pseudo_remainder((-2, 0, 1), (1, -2), control.Budget()) == (-1,)


def test_exact_division_and_primitive_gcd_on_unrelated_polynomials():
    # x^3-2x^2-x+2 = (x-2)(x^2-1).
    budget = control.Budget()
    assert control.exact_divide((2, -1, -2, 1), (-2, 1), budget) == (-1, 0, 1)
    assert control.polynomial_gcd((2, -1, -2, 1), (-1, 0, 1), budget) == (-1, 0, 1)
    with pytest.raises(control.VerificationFailure, match="not exact"):
        control.exact_divide((1, 0, 1), (-2, 1), budget)


def test_sturm_isolates_positive_and_negative_irrational_roots():
    budget = control.Budget()
    intervals, total = control.isolate_roots((-2, 0, 1), Fraction(-2), Fraction(2), bits=18, budget=budget)
    assert total == len(intervals) == 2
    negative, positive = intervals
    assert negative[1] < 0 < positive[0]
    assert positive[0] ** 2 < 2 < positive[1] ** 2
    assert negative[1] ** 2 < 2 < negative[0] ** 2
    assert all(right - left <= Fraction(1, 1 << 18) for left, right in intervals)


def test_sturm_handles_exact_midpoint_and_domain_endpoint_roots():
    # x(x-1)(x+1) has roots at both domain endpoints and the first midpoint.
    budget = control.Budget()
    poly = (0, -1, 0, 1)
    sequence = control.sturm_sequence(poly, budget)
    assert control.count_open_roots(sequence, Fraction(-1), Fraction(1), budget) == 1
    assert control.count_open_roots(sequence, Fraction(-1), Fraction(0), budget) == 0
    intervals, total = control.isolate_roots(poly, Fraction(-1), Fraction(1), bits=12, budget=budget)
    assert total == 3
    assert intervals == [(Fraction(-1), Fraction(-1)), (Fraction(0), Fraction(0)), (Fraction(1), Fraction(1))]


def test_mixed_rational_and_irrational_roots_are_strictly_separated():
    # (x-1)(x^2-2), with an exact midpoint root beside an irrational root.
    intervals, total = control.isolate_roots((2, -2, -1, 1), Fraction(0), Fraction(2),
                                            bits=10, budget=control.Budget())
    assert total == 2
    assert intervals[0] == (Fraction(1), Fraction(1))
    assert intervals[1][0] > 1


def test_repeated_root_fails_closed_and_root_free_interval_is_complete():
    with pytest.raises(control.VerificationFailure, match="not square-free"):
        control.isolate_roots((1, -2, 1), Fraction(0), Fraction(2), bits=10, budget=control.Budget())
    assert control.isolate_roots((1, 0, 1), Fraction(-2), Fraction(2), bits=10,
                                 budget=control.Budget()) == ([], 0)


def test_exact_interval_arithmetic_handles_sign_crossing():
    budget = control.Budget()
    assert control.interval_square((Fraction(-2), Fraction(3)), budget) == (0, 9)
    assert control.interval_product((Fraction(-2), Fraction(3)), (Fraction(-4), Fraction(5)), budget) == (-12, 15)


def test_period_two_control_has_one_primitive_critical_cycle():
    result = control.verify_control(protocol())
    assert result["passed"]
    row = result["period_results"][0]
    assert row["recurrence_polynomial_coefficients_ascending"] == [1, -1]
    assert row["complete_domain_root_count"] == 1
    cycle = row["cycles"][0]
    assert cycle["parameter_interval"] == ["1", "1"]
    assert cycle["critical_anchored_word"] == "C1"
    assert cycle["primitive_period_certified"]
    assert cycle["noncritical_sign_intervals"] == [{"iterate": 1, "lower": "1", "upper": "1", "sign": 1}]


def test_period_bound_precedes_recurrence_construction():
    for value in (1, 8, True, 2.0):
        with pytest.raises(control.VerificationFailure, match="maximum period"):
            control.critical_polynomials(value, control.Budget())


def test_certified_cycle_refuses_unproven_root_and_nonprimitive_cycle():
    with pytest.raises(control.VerificationFailure, match="not a factor"):
        control.certified_cycle((-2, 1), (Fraction(2), Fraction(2)), 2, control.Budget())
    with pytest.raises(control.VerificationFailure, match="not an exact recurrence root"):
        control.certified_cycle((1, -1), (Fraction(0), Fraction(0)), 2, control.Budget())
    # At mu=1 the third state is zero, so claiming primitive period 4 fails.
    with pytest.raises(control.VerificationFailure, match="lower primitive period"):
        control.certified_cycle((1, -1), (Fraction(1), Fraction(1)), 4, control.Budget())


@pytest.mark.parametrize("field,value", [("periods", [2, 2]), ("periods", [True]),
                                        ("periods", [8]), ("parameter_domain", [0, 2]),
                                        ("root_interval_bits", False), ("maximum_sign_refinements", -1)])
def test_invalid_protocol_fails_before_enumeration(field, value):
    manifest = protocol()
    manifest[field] = value
    with pytest.raises(control.VerificationFailure):
        control.parse_manifest(manifest)


def test_manifest_refuses_extra_inputs_and_nonfinite_limits():
    manifest = protocol()
    manifest["external_comparison_file"] = "forbidden.json"
    with pytest.raises(control.VerificationFailure, match="exactly"):
        control.parse_manifest(manifest)
    for value in (float("nan"), float("inf"), True, "unbounded"):
        manifest = protocol()
        manifest["limits"]["maximum_wall_seconds"] = value
        with pytest.raises(control.VerificationFailure):
            control.parse_manifest(manifest)


def test_operation_bit_interval_and_time_budgets_fail_closed():
    result = control.verify_control(protocol(), budget=control.Budget(maximum_operations=1))
    assert not result["passed"]
    assert result["failure"]["kind"] == "WorkLimit"
    with pytest.raises(control.WorkLimit, match="bit-size"):
        control.Budget(maximum_coefficient_bits=3).check(8)
    budget = control.Budget(maximum_interval_nodes=1)
    budget.visit_interval()
    with pytest.raises(control.WorkLimit, match="interval-node"):
        budget.visit_interval()
    times = iter([0.0, 2.0])
    budget = control.Budget(maximum_wall_seconds=1, clock=lambda: next(times))
    with pytest.raises(control.WorkLimit, match="wall-time"):
        budget.tick()


def test_exclusive_receipt_does_not_overwrite_file_or_dangling_symlink(tmp_path):
    path = tmp_path / "receipt.json"
    control.write_exclusive(path, {"passed": False})
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        control.write_exclusive(path, {"passed": True})
    assert path.read_bytes() == original
    link = tmp_path / "link.json"
    link.symlink_to(tmp_path / "missing.json")
    with pytest.raises(FileExistsError):
        control.write_exclusive(link, {})


def test_cli_retains_dirty_source_failure_without_enumeration(tmp_path, monkeypatch):
    manifest = tmp_path / "protocol.json"
    manifest.write_text(json.dumps(protocol()))
    output = tmp_path / "failed.json"
    monkeypatch.setattr(control, "source_provenance", lambda: {"dirty": True})
    monkeypatch.setattr(control, "verify_control", lambda *_args, **_kwargs: pytest.fail("enumeration must not run"))
    assert control.main(["--manifest", str(manifest), "--output", str(output)]) == 1
    result = json.loads(output.read_text())
    assert not result["passed"]
    assert "clean, committed" in result["failure"]["message"]
    assert str(tmp_path) not in output.read_text()


def test_cli_rejects_existing_output_before_input_read(tmp_path, monkeypatch):
    output = tmp_path / "existing.json"
    output.write_text("retain me")
    monkeypatch.setattr(control, "source_provenance", lambda: pytest.fail("no preflight expected"))
    with pytest.raises(SystemExit):
        control.main(["--manifest", "nonexistent-protocol.json", "--output", str(output)])
    assert output.read_text() == "retain me"


def test_cli_source_change_invalidates_otherwise_passing_period_two_receipt(tmp_path, monkeypatch):
    manifest = tmp_path / "protocol.json"
    manifest.write_text(json.dumps(protocol()))
    output = tmp_path / "changed-source.json"
    sources = iter([{"dirty": False, "commit": "before"}, {"dirty": False, "commit": "after"}])
    monkeypatch.setattr(control, "source_provenance", lambda: next(sources))
    assert control.main(["--manifest", str(manifest), "--output", str(output)]) == 1
    result = json.loads(output.read_text())
    assert not result["passed"]
    assert "source changed" in result["failure"]["message"]
    assert result["period_results"][0]["passed"]  # Partial math is retained, not promoted.

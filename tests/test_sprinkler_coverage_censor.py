from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "qualify_sprinkler_convergence.py"
SPEC = importlib.util.spec_from_file_location("sprinkler_coverage", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


ORACLE_COMMON = {"maximum_conditional_spread_ratio": 0.08}
ACCEPTANCE = {
    "minimum_censored_domain_coverage": 0.65,
    "minimum_fully_resolved_variants": 12,
    "maximum_within_run_normalized_critical_span": 0.03,
}


def _variant(
    *,
    resolved: bool,
    branch_count: int | None,
    critical_points=(0.5,),
    reason="resolved",
    coverage=1.0,
    spread=0.02,
):
    return {
        "resolved": resolved,
        "branch_count": branch_count,
        "critical_points": critical_points,
        "reason": reason,
        "domain_coverage": coverage,
        "conditional_spread_ratio": spread,
    }


def _evaluate(variants):
    return MODULE._coverage_censor_evaluation(
        {"variant_results": variants},
        source_minimum=0.0,
        source_maximum=1.0,
        expected_branch_count=2,
        oracle_common=ORACLE_COMMON,
        acceptance=ACCEPTANCE,
    )


def test_coverage_censor_accepts_twelve_resolved_and_three_nominal_matches():
    resolved = [
        _variant(resolved=True, branch_count=2, critical_points=(0.49 + i / 1000,))
        for i in range(12)
    ]
    censored = [
        _variant(
            resolved=False,
            branch_count=None,
            critical_points=(0.5 + i / 1000,),
            reason="insufficient invariant-domain coverage",
            coverage=0.675,
        )
        for i in range(3)
    ]
    result = _evaluate(resolved + censored)
    assert result["passed"]
    assert result["branch_count"] == 2
    assert result["fully_resolved_variant_indices"] == list(range(12))
    assert result["coverage_censored_variant_indices"] == [12, 13, 14]


def test_coverage_censor_rejects_a_resolved_topology_contradiction():
    variants = [_variant(resolved=True, branch_count=2) for _ in range(14)]
    variants.append(
        _variant(resolved=True, branch_count=3, critical_points=(0.3, 0.7))
    )
    result = _evaluate(variants)
    assert not result["passed"]
    assert result["rejected_variants"][0]["branch_count"] == 3


def test_coverage_censor_rejects_low_coverage_or_nongraphlike_nominal_fit():
    variants = [_variant(resolved=True, branch_count=2) for _ in range(13)]
    variants.extend(
        [
            _variant(
                resolved=False,
                branch_count=None,
                reason="insufficient invariant-domain coverage",
                coverage=0.64,
            ),
            _variant(
                resolved=False,
                branch_count=None,
                reason="insufficient invariant-domain coverage",
                coverage=0.68,
                spread=0.081,
            ),
        ]
    )
    result = _evaluate(variants)
    assert not result["passed"]
    assert len(result["rejected_variants"]) == 2


def test_coverage_censor_rejects_unstable_critical_locations():
    variants = [_variant(resolved=True, branch_count=2) for _ in range(14)]
    variants.append(
        _variant(
            resolved=False,
            branch_count=None,
            critical_points=(0.54,),
            reason="insufficient invariant-domain coverage",
            coverage=0.675,
        )
    )
    result = _evaluate(variants)
    assert not result["passed"]
    assert result["reason"] == "critical-point location is variant-unstable"

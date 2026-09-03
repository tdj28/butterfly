from butterfly.return_map import (
    ReturnMapBranchResult,
    ReturnMapRobustnessResult,
    infer_return_map_branches_coverage_censored,
)


def _variant(
    *,
    resolved=True,
    branch_count=2,
    critical_points=(0.5,),
    reason="resolved",
    coverage=1.0,
    spread=0.02,
):
    return ReturnMapBranchResult(
        resolved=resolved,
        branch_count=branch_count,
        critical_points=critical_points,
        conditional_spread_ratio=spread,
        domain_coverage=coverage,
        bootstrap_consensus=1.0 if resolved else 0.0,
        bootstrap_counts=(),
        reason=reason,
    )


def _robust(variants):
    return ReturnMapRobustnessResult(
        resolved=False,
        branch_count=None,
        critical_point_intervals=(),
        normalized_critical_point_spans=(),
        maximum_normalized_critical_point_span=float("inf"),
        variant_consensus=0.8,
        variant_counts=tuple(
            variant.branch_count if variant.resolved else None
            for variant in variants
        ),
        variant_results=tuple(variants),
        reason="oracle variants disagree",
    )


def _evaluate(variants, expected=2):
    return infer_return_map_branches_coverage_censored(
        _robust(variants),
        source_minimum=0.0,
        source_maximum=1.0,
        expected_branch_count=expected,
    )


def test_accepts_twelve_resolved_and_three_coverage_only_censors():
    variants = [
        _variant(critical_points=(0.49 + index / 1000,))
        for index in range(12)
    ]
    variants.extend(
        _variant(
            resolved=False,
            branch_count=None,
            critical_points=(0.50 + index / 1000,),
            reason="insufficient invariant-domain coverage",
            coverage=0.675,
        )
        for index in range(3)
    )
    result = _evaluate(variants)
    assert result.resolved
    assert result.branch_count == 2
    assert result.fully_resolved_variant_indices == tuple(range(12))
    assert result.coverage_censored_variant_indices == (12, 13, 14)


def test_rejects_resolved_topology_contradiction():
    variants = [_variant() for _ in range(14)]
    variants.append(_variant(branch_count=3, critical_points=(0.3, 0.7)))
    result = _evaluate(variants)
    assert not result.resolved
    assert result.rejected_variant_indices == (14,)


def test_rejects_bootstrap_instability_even_with_nominal_geometry():
    variants = [_variant() for _ in range(12)]
    variants.extend(
        _variant(
            resolved=False,
            branch_count=None,
            reason="bootstrap branch count is unstable",
            coverage=0.7,
        )
        for _ in range(3)
    )
    result = _evaluate(variants)
    assert not result.resolved
    assert result.rejected_variant_indices == (12, 13, 14)


def test_rejects_low_coverage_or_nongraphlike_censor():
    variants = [_variant() for _ in range(13)]
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
                coverage=0.675,
                spread=0.081,
            ),
        ]
    )
    result = _evaluate(variants)
    assert not result.resolved
    assert result.rejected_variant_indices == (13, 14)


def test_rejects_joint_critical_location_instability():
    variants = [_variant() for _ in range(14)]
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
    assert not result.resolved
    assert result.reason == "critical-point location is variant-unstable"

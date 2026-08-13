from __future__ import annotations

from scripts.gpu_audit_jones_scale_ensemble_residuals import combine_candidate


def test_combine_candidate_requires_common_assignment():
    manifest = {
        "profiles": [{"name": "coarse"}, {"name": "fine"}],
        "nested_support": [
            {"name": "nested", "minimum_return_pairs": 1},
            {"name": "full", "minimum_return_pairs": 1},
        ],
        "smoothing_values": [1e-6],
        "ensemble": {"x_count": 2, "z_count": 2},
        "acceptance": {
            "maximum_normalized_critical_location_span": 0.03,
            "maximum_survivor_fraction_difference": 0.03,
            "maximum_direct_absolute_residual": 0.02,
        },
    }
    supports = []
    for name in ("nested", "full"):
        supports.append(
            {
                "name": name,
                "pair_count": 10,
                "source_domain": [0.0, 1.0],
                "smoothing_values": [1e-6],
                "results": [{"resolved": True, "branch_count": 3, "critical_points": [0.2, 0.8]}],
                "assignments": [{
                    "resolved": True,
                    "orbit_indices": [1, 0],
                    "normalized_signed_residuals": [0.01, -0.01],
                    "maximum_absolute_residual": 0.01,
                    "sum_absolute_residual": 0.02,
                }],
            }
        )
    rows = [
        [{"id": "p", "profile": "coarse", "failed_count": 0, "survivor_counts": [3, 3], "supports": supports}],
        [{"id": "p", "profile": "fine", "failed_count": 0, "survivor_counts": [3, 3], "supports": supports}],
    ]
    candidate = {"id": "p", "grid_index": [0, 0], "parameters": {"a": 1, "b": 2, "c": 3}}

    result = combine_candidate(candidate, rows, manifest)

    assert result["eligible"]
    assert result["direct_gate_passed"]
    assert result["common_assignment_indices"] == [1, 0]

    rows[1][0]["supports"][0]["assignments"][0]["orbit_indices"] = [0, 1]
    assert not combine_candidate(candidate, rows, manifest)["eligible"]

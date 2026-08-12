from scripts.select_smoothing_sensitive_candidates import matching_ids


def _row(identifier, votes):
    return {"id": identifier, "robust_partition": {"variant_counts": votes}}


def test_matching_ids_requires_pattern_at_every_profile():
    receipt = {
        "profiles": [
            {"rows": [_row("yes", [3, 3, 3, 2, 3]), _row("mixed", [3, 3, 3, 2, 3])]},
            {"rows": [_row("yes", [3, 3, 3, 2, 3]), _row("mixed", [3, 3, 3, 3, 3])]},
        ]
    }
    selection = {
        "baseline_variant_indices": [0, 1, 2, 4],
        "smoothing_variant_index": 3,
        "baseline_branch_count": 3,
        "smoothing_branch_count": 2,
    }
    assert matching_ids(receipt, selection) == ["yes"]

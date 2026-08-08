from scripts.qualify_censored_pim_saddle_controls import (
    _common_resolved_branch_count,
)


def _row(resolved: bool, branch_count: int | None):
    return {
        "robust_oracle": {
            "resolved": resolved,
            "branch_count": branch_count,
        }
    }


def test_blind_pim_requires_coordinate_agreement() -> None:
    assert (
        _common_resolved_branch_count(
            {"y": _row(True, 2), "z": _row(True, 2)}, [2, 3]
        )
        == 2
    )
    assert (
        _common_resolved_branch_count(
            {"y": _row(True, 2), "z": _row(True, 3)}, [2, 3]
        )
        is None
    )


def test_blind_pim_rejects_unresolved_or_disallowed_count() -> None:
    assert (
        _common_resolved_branch_count(
            {"y": _row(False, None), "z": _row(True, 2)}, [2, 3]
        )
        is None
    )
    assert (
        _common_resolved_branch_count(
            {"y": _row(True, 4), "z": _row(True, 4)}, [2, 3]
        )
        is None
    )

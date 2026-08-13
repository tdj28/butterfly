from __future__ import annotations

import pytest

from scripts.audit_jones_scale_ensemble_residual import (
    point_assignment,
    signed_residual_bracket_cells,
)


def test_point_assignment_uses_distinct_ordered_phases():
    result = point_assignment([0.82, 0.21, 0.50], [0.20, 0.80], [0.0, 1.0])

    assert result["resolved"]
    assert result["orbit_indices"] == [1, 0]
    assert result["normalized_signed_residuals"] == pytest.approx([0.01, 0.02])


def _corner(i, j, residuals):
    return {
        "id": f"p-{i}-{j}",
        "grid_index": [i, j],
        "parameters": {"a": float(i), "b": 0.2, "c": float(j)},
        "eligible": True,
        "common_assignment_indices": [1, 0],
        "reconstructions": {
            "fine/full/s2": {"normalized_signed_residuals": residuals},
            "coarse/nested/s4": {"normalized_signed_residuals": residuals},
        },
    }


def test_signed_residual_bracket_requires_every_reconstruction():
    rows = [
        _corner(0, 0, [-0.1, -0.2]),
        _corner(1, 0, [0.1, -0.1]),
        _corner(0, 1, [-0.2, 0.1]),
        _corner(1, 1, [0.2, 0.2]),
    ]

    cells = signed_residual_bracket_cells(rows)

    assert len(cells) == 1
    assert cells[0]["corner_ids"] == ["p-0-0", "p-1-0", "p-0-1", "p-1-1"]

    rows[2]["reconstructions"]["coarse/nested/s4"]["normalized_signed_residuals"] = [-0.2, -0.1]
    rows[3]["reconstructions"]["coarse/nested/s4"]["normalized_signed_residuals"] = [0.2, -0.3]
    assert signed_residual_bracket_cells(rows) == []

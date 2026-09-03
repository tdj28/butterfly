import numpy as np

from scripts.audit_jones_homoclinic_residual_cells import SCHEMA, winding_number


def test_residual_cell_audit_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-homoclinic-residual-cell-audit-manifest.v1"


def test_counterclockwise_cell_around_origin_has_positive_degree():
    winding, total, error = winding_number(
        np.array([[-1.0, -1.0], [1.0, -1.0], [1.0, 1.0], [-1.0, 1.0]])
    )
    assert winding == 1
    assert np.isclose(total, 2.0 * np.pi)
    assert error < 1e-12


def test_clockwise_cell_around_origin_has_negative_degree():
    winding, total, error = winding_number(
        np.array([[-1.0, -1.0], [-1.0, 1.0], [1.0, 1.0], [1.0, -1.0]])
    )
    assert winding == -1
    assert np.isclose(total, -2.0 * np.pi)
    assert error < 1e-12


def test_component_hulls_can_contain_zero_without_nonzero_degree():
    vectors = np.array(
        [
            [0.000410, -0.002328],
            [0.015887, 0.002389],
            [0.015462, 0.001613],
            [-0.000242, -0.003068],
        ]
    )
    assert all(np.min(vectors[:, axis]) <= 0.0 <= np.max(vectors[:, axis]) for axis in (0, 1))
    winding, _total, error = winding_number(vectors)
    assert winding == 0
    assert error < 1e-12

import numpy as np

from scripts.extend_jones_period6_flip_pseudoarclength import (
    SCHEMA,
    combine_dual_jacobians,
)


def test_flip_pseudoarclength_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period6-flip-pseudoarclength-manifest.v1"


def test_dual_jacobian_inserts_exact_c_column():
    a_jacobian = np.arange(64, dtype=float).reshape(8, 8)
    c_jacobian = 100 + np.arange(64, dtype=float).reshape(8, 8)
    combined = combine_dual_jacobians(a_jacobian, c_jacobian)
    assert combined.shape == (8, 9)
    np.testing.assert_array_equal(combined[:, :5], a_jacobian[:, :5])
    np.testing.assert_array_equal(combined[:, 5], c_jacobian[:, 4])
    np.testing.assert_array_equal(combined[:, 6:], a_jacobian[:, 5:])

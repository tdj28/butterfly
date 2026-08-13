from __future__ import annotations

import numpy as np
from scipy.sparse import csr_matrix

from butterfly import SolverConfig
from scripts import multiple_shooting_core as core


def _affine_segment(state, duration, parameters, solver, continuation_parameter="b"):
    del parameters, solver, continuation_parameter
    state = np.asarray(state, dtype=float)
    return state + duration, 2.0 * np.eye(3), 3.0 * np.ones(3)


def test_sparse_base_system_matches_dense(monkeypatch):
    monkeypatch.setattr(core, "integrate_segment", _affine_segment)
    variables = np.r_[np.arange(6.0), 2.0, 0.24]
    arguments = {
        "segment_count": 2,
        "a": None,
        "c": 5.0,
        "phase": np.asarray((1.0, 0.0, 0.0)),
        "phase_reference": np.zeros(3),
        "solver": SolverConfig(),
        "continuation_parameter": "a",
        "fixed_b": 0.2,
    }

    dense_residual, dense_jacobian = core.base_system(variables, **arguments)
    sparse_residual, sparse_jacobian = core.base_system(
        variables, **arguments, sparse_jacobian=True
    )

    assert isinstance(sparse_jacobian, csr_matrix)
    np.testing.assert_allclose(sparse_residual, dense_residual)
    np.testing.assert_allclose(sparse_jacobian.toarray(), dense_jacobian)

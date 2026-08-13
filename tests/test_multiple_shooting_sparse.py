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


def test_sparse_fixed_parameter_correction_reaches_same_root(monkeypatch):
    target = np.asarray((0.2, -0.4, 0.7, 2.0))

    def linear_system(variables, **arguments):
        sparse = arguments["sparse_jacobian"]
        jacobian = np.c_[np.eye(4), np.zeros(4)]
        if sparse:
            jacobian = csr_matrix(jacobian)
        return np.asarray(variables[:-1]) - target, jacobian

    monkeypatch.setattr(core, "base_system", linear_system)
    arguments = {
        "segment_count": 1,
        "a": None,
        "c": 5.0,
        "phase": np.asarray((1.0, 0.0, 0.0)),
        "phase_reference": np.zeros(3),
        "solver": SolverConfig(),
        "tolerance": 1e-12,
        "max_evaluations": 20,
        "continuation_parameter": "a",
        "fixed_b": 0.2,
    }
    dense, dense_status = core.correct_fixed_parameter(
        np.asarray((0.0, 0.0, 0.0, 1.0)), 0.24, **arguments
    )
    sparse, sparse_status = core.correct_fixed_parameter(
        np.asarray((0.0, 0.0, 0.0, 1.0)),
        0.24,
        **arguments,
        sparse_jacobian=True,
    )

    assert dense_status["success"] and sparse_status["success"]
    np.testing.assert_allclose(dense, target)
    np.testing.assert_allclose(sparse, dense)

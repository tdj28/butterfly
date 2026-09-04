from types import SimpleNamespace

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from butterfly import SolverConfig
from scripts import multiple_shooting_core as core


@pytest.mark.parametrize("sparse_jacobian", [False, True])
@pytest.mark.parametrize(
    ("arclength_error", "expected_success"),
    [(0.0, True), (5e-9, True), (2e-8, False), (float("nan"), False)],
)
def test_arclength_acceptance_requires_all_equations(
    monkeypatch, sparse_jacobian, arclength_error, expected_success
):
    # Matching and phase can be solved while an optimizer terminates away from
    # the requested pseudo-arclength plane. Its success flag alone is not enough.
    predictor = np.asarray((0.0, 0.0, 0.0, 1.0, 0.2))
    tangent = np.asarray((0.0, 0.0, 0.0, 0.0, 1.0))
    terminated_at = predictor.copy()
    terminated_at[-1] += arclength_error

    def closed_and_phase_fixed(variables, **arguments):
        jacobian = np.zeros((4, 5))
        if arguments["sparse_jacobian"]:
            jacobian = csr_matrix(jacobian)
        return np.zeros(4), jacobian

    monkeypatch.setattr(core, "base_system", closed_and_phase_fixed)
    monkeypatch.setattr(
        core,
        "least_squares",
        lambda *args, **kwargs: SimpleNamespace(
            x=terminated_at, success=True, message="xtol termination", nfev=1
        ),
    )
    _, status = core.correct_arclength(
        predictor,
        tangent,
        segment_count=1,
        a=0.2,
        c=5.0,
        phase=np.asarray((1.0, 0.0, 0.0)),
        phase_reference=np.zeros(3),
        solver=SolverConfig(),
        tolerance=1e-11,
        max_evaluations=4,
        sparse_jacobian=sparse_jacobian,
    )
    assert status["matching_residual"] == 0.0
    assert status["phase_residual"] == 0.0
    if np.isfinite(arclength_error):
        assert status["arclength_residual"] == pytest.approx(arclength_error)
    else:
        assert np.isnan(status["arclength_residual"])
    assert status["success"] is expected_success

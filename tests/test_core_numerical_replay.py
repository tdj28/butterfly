import numpy as np
import pytest
from types import SimpleNamespace

from scripts import replay_core_numerics as replay


def test_short_arc_replay_uses_integrations_not_stored_defects(monkeypatch):
    calls = []

    def integrate(state, duration, parameters, solver, continuation_parameter):
        calls.append((state.tolist(), duration))
        return np.asarray(state) + [1, 0, 0], None, None

    monkeypatch.setattr(replay, "integrate_segment", integrate)
    errors = replay.segment_residuals([[0, 0, 0], [1, 0, 0]], [[1, 0, 0], [2, 0.1, 0]], 1, None, None)
    np.testing.assert_allclose(errors, [0, 0.1])
    assert len(calls) == 2


@pytest.mark.parametrize("starts,ends,duration", [
    ([], [], 1), ([[0, 0]], [[0, 0]], 1),
    ([[0, 0, 0]], [[0, 0, 0]], 0),
    ([[0, 0, 0]], [[0, 0, 0]], float("nan")),
    ([[0, 0, 0]], [[0, float("inf"), 0]], 1),
])
def test_short_arc_replay_rejects_invalid_inputs(starts, ends, duration):
    with pytest.raises(ValueError):
        replay.segment_residuals(starts, ends, duration, None, None)


def test_short_arc_replay_rejects_nonfinite_solver_output(monkeypatch):
    monkeypatch.setattr(replay, "integrate_segment", lambda *a, **kw: (np.full(3, np.nan), None, None))
    with pytest.raises(ValueError, match="nonfinite"):
        replay.segment_residuals([[0, 0, 0]], [[1, 0, 0]], 1, None, None)


@pytest.mark.parametrize("state,period", [([1,0,0], 40), ([0,0,0], 41), ([float("nan"),0,0],40)])
def test_distant_or_nonfinite_corrector_cannot_pass_seed_identity(state, period):
    seed = {"initial_state": [0,0,0], "period_time": 40}
    policy = {"maximum_relative_period_difference": 1e-8, "maximum_phase_fixed_state_difference": 1e-6}
    checks = replay.flip_identity_checks(SimpleNamespace(initial_state=state, period_time=period), seed, policy)
    assert not all(checks.values())


def test_narrow_same_phase_seed_neighborhood_passes():
    seed = {"initial_state": [0,0,0], "period_time": 40}
    policy = {"maximum_relative_period_difference": 1e-8, "maximum_phase_fixed_state_difference": 1e-6}
    checks = replay.flip_identity_checks(SimpleNamespace(initial_state=[1e-9,0,0], period_time=40+1e-9), seed, policy)
    assert all(checks.values())

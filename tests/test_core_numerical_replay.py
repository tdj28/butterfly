import numpy as np
import pytest

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

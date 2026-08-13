from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from butterfly import RosslerParameters, SolverConfig

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from multiple_shooting_core import integrate_segment  # noqa: E402


SOLVER = SolverConfig(method="DOP853", rtol=1e-11, atol=1e-13, max_step=0.02)
PARAMETERS = RosslerParameters(a=0.245, b=0.2, c=5.1)


def test_segment_parameter_sensitivities_match_finite_differences() -> None:
    state = np.asarray((0.4, -0.2, 0.3))
    duration = 0.17
    epsilon = 2e-6
    for name in ("a", "b", "c"):
        analytic = integrate_segment(
            state,
            duration,
            PARAMETERS,
            SOLVER,
            continuation_parameter=name,
        )[2]
        plus_values = {
            "a": PARAMETERS.a,
            "b": PARAMETERS.b,
            "c": PARAMETERS.c,
        }
        minus_values = dict(plus_values)
        plus_values[name] += epsilon
        minus_values[name] -= epsilon
        plus = integrate_segment(
            state,
            duration,
            RosslerParameters(**plus_values),
            SOLVER,
            continuation_parameter=name,
        )[0]
        minus = integrate_segment(
            state,
            duration,
            RosslerParameters(**minus_values),
            SOLVER,
            continuation_parameter=name,
        )[0]
        numerical = (plus - minus) / (2.0 * epsilon)
        np.testing.assert_allclose(analytic, numerical, rtol=2e-7, atol=2e-9)

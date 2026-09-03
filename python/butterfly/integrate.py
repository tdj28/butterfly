"""Readable Float64 integration path used as the scientific reference."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import solve_ivp

from .models import RosslerParameters, rossler_rhs


@dataclass(frozen=True, slots=True)
class SolverConfig:
    method: str = "DOP853"
    rtol: float = 1e-10
    atol: float = 1e-12
    max_step: float = 0.05

    def __post_init__(self) -> None:
        if self.rtol <= 0.0 or self.atol <= 0.0 or self.max_step <= 0.0:
            raise ValueError("rtol, atol, and max_step must be positive")


@dataclass(frozen=True, slots=True)
class Trajectory:
    t: NDArray[np.float64]
    y: NDArray[np.float64]
    nfev: int
    success: bool
    message: str


def integrate_trajectory(
    parameters: RosslerParameters,
    initial_state: ArrayLike,
    t_span: tuple[float, float],
    *,
    config: SolverConfig = SolverConfig(),
    t_eval: Sequence[float] | None = None,
) -> Trajectory:
    """Integrate one Rössler trajectory with an adaptive high-order solver."""

    state = np.asarray(initial_state, dtype=np.float64)
    if state.shape != (3,) or not np.all(np.isfinite(state)):
        raise ValueError("initial_state must be three finite values")
    start, stop = map(float, t_span)
    if not np.isfinite(start) or not np.isfinite(stop) or stop <= start:
        raise ValueError("t_span must be finite and strictly increasing")

    result = solve_ivp(
        lambda time, value: rossler_rhs(time, value, parameters),
        (start, stop),
        state,
        method=config.method,
        rtol=config.rtol,
        atol=config.atol,
        max_step=config.max_step,
        t_eval=None if t_eval is None else np.asarray(t_eval, dtype=np.float64),
    )
    return Trajectory(
        t=np.asarray(result.t, dtype=np.float64),
        y=np.asarray(result.y, dtype=np.float64),
        nfev=int(result.nfev),
        success=bool(result.success),
        message=str(result.message),
    )

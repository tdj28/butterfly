"""Explicit, root-interpolated Poincaré sections for the Rössler flow."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import solve_ivp

from .integrate import SolverConfig
from .models import RosslerParameters, rossler_equilibria, rossler_rhs


@dataclass(frozen=True, slots=True)
class PoincareSection:
    """An oriented plane with an optional one-sided coordinate gate."""

    normal: tuple[float, float, float]
    offset: float
    direction: int = 0
    gate_axis: int | None = None
    gate_upper: float | None = None
    name: str = "plane"

    def __post_init__(self) -> None:
        normal = np.asarray(self.normal, dtype=np.float64)
        if normal.shape != (3,) or not np.all(np.isfinite(normal)):
            raise ValueError("section normal must contain three finite values")
        if np.linalg.norm(normal) == 0.0:
            raise ValueError("section normal must be nonzero")
        if self.direction not in (-1, 0, 1):
            raise ValueError("section direction must be -1, 0, or 1")
        if self.gate_axis is not None and self.gate_axis not in (0, 1, 2):
            raise ValueError("gate_axis must be 0, 1, or 2")
        if (self.gate_axis is None) != (self.gate_upper is None):
            raise ValueError("gate_axis and gate_upper must be set together")

    def value(self, state: ArrayLike) -> float:
        return float(np.dot(self.normal, np.asarray(state, dtype=np.float64)) - self.offset)

    def accepts(self, state: ArrayLike) -> bool:
        if self.gate_axis is None:
            return True
        return bool(np.asarray(state, dtype=np.float64)[self.gate_axis] < self.gate_upper)


@dataclass(frozen=True, slots=True)
class PoincareCrossings:
    times: NDArray[np.float64]
    states: NDArray[np.float64]
    section: PoincareSection
    transient: float
    observation_horizon: float
    solver_config: SolverConfig
    integration_success: bool
    integration_message: str


def legacy_rossler_section(parameters: RosslerParameters) -> PoincareSection:
    """Return the plane/half-plane tested by the recovered 2012 C code.

    The historical implementation detected either crossing orientation through
    the small equilibrium's y coordinate, gated by x below that equilibrium.
    Unlike the fixed-step code, this object locates roots by interpolation.
    """

    equilibria = rossler_equilibria(parameters)
    if len(equilibria) == 0:
        raise ValueError("legacy section requires a real equilibrium")
    small = equilibria[0]
    return PoincareSection(
        normal=(0.0, 1.0, 0.0),
        offset=float(small[1]),
        direction=0,
        gate_axis=0,
        gate_upper=float(small[0]),
        name="legacy-small-equilibrium-half-plane",
    )


def collect_crossings(
    parameters: RosslerParameters,
    initial_state: ArrayLike,
    section: PoincareSection,
    *,
    transient: float,
    observation_horizon: float,
    max_crossings: int,
    config: SolverConfig = SolverConfig(),
) -> PoincareCrossings:
    """Integrate, discard a time transient, and collect section crossings."""

    state = np.asarray(initial_state, dtype=np.float64)
    if state.shape != (3,) or not np.all(np.isfinite(state)):
        raise ValueError("initial_state must be three finite values")
    if transient < 0.0 or observation_horizon <= 0.0 or max_crossings <= 0:
        raise ValueError("transient must be nonnegative; horizon/count must be positive")

    def rhs(time: float, value: NDArray[np.float64]) -> NDArray[np.float64]:
        return rossler_rhs(time, value, parameters)

    if transient > 0.0:
        transient_result = solve_ivp(
            rhs,
            (0.0, transient),
            state,
            method=config.method,
            rtol=config.rtol,
            atol=config.atol,
            max_step=config.max_step,
        )
        if not transient_result.success:
            return PoincareCrossings(
                times=np.empty(0, dtype=np.float64),
                states=np.empty((0, 3), dtype=np.float64),
                section=section,
                transient=transient,
                observation_horizon=observation_horizon,
                solver_config=config,
                integration_success=False,
                integration_message=str(transient_result.message),
            )
        state = np.asarray(transient_result.y[:, -1], dtype=np.float64)

    def event(_time: float, value: NDArray[np.float64]) -> float:
        return section.value(value)

    event.direction = section.direction  # type: ignore[attr-defined]
    event.terminal = False  # type: ignore[attr-defined]
    result = solve_ivp(
        rhs,
        (transient, transient + observation_horizon),
        state,
        method=config.method,
        rtol=config.rtol,
        atol=config.atol,
        max_step=config.max_step,
        events=event,
    )
    raw_times = np.asarray(result.t_events[0], dtype=np.float64)
    raw_states = np.asarray(result.y_events[0], dtype=np.float64)
    if raw_states.size == 0:
        raw_states = np.empty((0, 3), dtype=np.float64)
    accepted = np.asarray(
        [section.accepts(crossing) for crossing in raw_states], dtype=bool
    )
    times = raw_times[accepted][:max_crossings]
    states = raw_states[accepted][:max_crossings]
    return PoincareCrossings(
        times=times,
        states=states,
        section=section,
        transient=transient,
        observation_horizon=observation_horizon,
        solver_config=config,
        integration_success=bool(result.success),
        integration_message=str(result.message),
    )

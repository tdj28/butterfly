"""Reference sprinkler sampling for nonattracting chaotic invariant sets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import solve_ivp
from scipy.stats import qmc

from .integrate import SolverConfig
from .models import RosslerParameters, rossler_rhs
from .poincare import PoincareSection


@dataclass(frozen=True, slots=True)
class SprinklerResult:
    """Long-lived ensemble and middle-time crossings from a sprinkler run."""

    capture_times: NDArray[np.float64]
    failed: NDArray[np.bool_]
    survivor_ids: NDArray[np.int64]
    survivor_initial_states: NDArray[np.float64]
    survivor_final_states: NDArray[np.float64]
    checkpoint_times: NDArray[np.float64]
    survivor_counts: NDArray[np.int64]
    midpoint_trajectory_ids: NDArray[np.int64]
    midpoint_times: NDArray[np.float64]
    midpoint_states: NDArray[np.float64]
    all_midpoint_trajectory_ids: NDArray[np.int64]
    all_midpoint_times: NDArray[np.float64]
    all_midpoint_states: NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class SectionReturnResult:
    """One adaptive return from an oriented Poincare section."""

    success: bool
    flight_time: float
    state: NDArray[np.float64]
    message: str


@dataclass(frozen=True, slots=True)
class CaptureLifetimeResult:
    """Escape/capture times used by a PIM-triple refinement."""

    lifetimes: NDArray[np.float64]
    captured: NDArray[np.bool_]
    return_counts: NDArray[np.int64]
    failed: NDArray[np.bool_]


@dataclass(frozen=True, slots=True)
class PIMTriple:
    """Proper-interior-maximum triple on a straight section segment."""

    left: NDArray[np.float64]
    center: NDArray[np.float64]
    right: NDArray[np.float64]
    escape_times: NDArray[np.float64]
    normalized_width: float

    @property
    def points(self) -> NDArray[np.float64]:
        return np.vstack((self.left, self.center, self.right))


@dataclass(frozen=True, slots=True)
class PIMRefinementResult:
    """A resolved PIM triple and its deterministic refinement history."""

    triple: PIMTriple
    refinement_count: int
    lifetime_evaluations: int
    normalized_widths: NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class PIMStraddleResult:
    """Middle-point trajectory restrained by repeated PIM refinement."""

    states: NDArray[np.float64]
    normalized_widths: NDArray[np.float64]
    refinement_events: NDArray[np.int64]
    lifetime_evaluations: int
    final_triple: PIMTriple


@dataclass(frozen=True, slots=True)
class PIMLifetimeBatch:
    """Exact escape times and right-censored lower bounds for PIM points."""

    lifetimes: NDArray[np.float64]
    censored: NDArray[np.bool_]
    failed: NDArray[np.bool_]


@dataclass(frozen=True, slots=True)
class CensorAwarePIMRefinementResult:
    """PIM refinement with certified right-censored block selections."""

    triple: PIMTriple
    refinement_count: int
    lifetime_evaluations: int
    normalized_widths: NDArray[np.float64]
    certified_censor_block_selections: int


@dataclass(frozen=True, slots=True)
class CensorAwarePIMStraddleResult:
    """PIM straddle with right-censored lower-bound provenance."""

    states: NDArray[np.float64]
    normalized_widths: NDArray[np.float64]
    refinement_events: NDArray[np.int64]
    lifetime_evaluations: int
    certified_censor_block_selections: int
    final_triple: PIMTriple


def _normalized_segment_width(
    left: NDArray[np.float64],
    right: NDArray[np.float64],
    coordinate_scales: NDArray[np.float64],
) -> float:
    return float(np.linalg.norm((right - left) / coordinate_scales))


def refine_pim_segment(
    left: ArrayLike,
    right: ArrayLike,
    escape_time: Callable[[NDArray[np.float64]], ArrayLike],
    *,
    coordinate_scales: ArrayLike,
    sample_count: int,
    width_tolerance: float,
    max_refinements: int,
) -> PIMRefinementResult:
    """Refine a segment to a strict proper-interior-maximum triple.

    ``escape_time`` receives a two-dimensional array of evenly spaced points
    and must return one finite escape time per row. At every level, the
    longest-lived strict local maximum is selected; ties are broken by the
    lowest grid index. This deterministic rule is frozen before target runs.
    """

    segment_left = np.asarray(left, dtype=np.float64)
    segment_right = np.asarray(right, dtype=np.float64)
    scales = np.asarray(coordinate_scales, dtype=np.float64)
    if (
        segment_left.ndim != 1
        or segment_right.shape != segment_left.shape
        or scales.shape != segment_left.shape
        or len(segment_left) == 0
    ):
        raise ValueError("PIM endpoints and coordinate scales must share shape (d,)")
    if not np.all(np.isfinite(segment_left)) or not np.all(np.isfinite(segment_right)):
        raise ValueError("PIM endpoints must be finite")
    if np.any(~np.isfinite(scales)) or np.any(scales <= 0.0):
        raise ValueError("PIM coordinate scales must be finite and positive")
    if sample_count < 3 or width_tolerance <= 0.0 or max_refinements < 1:
        raise ValueError("invalid PIM refinement controls")
    if np.array_equal(segment_left, segment_right):
        raise ValueError("PIM segment endpoints must be distinct")

    widths: list[float] = []
    evaluations = 0
    triple: PIMTriple | None = None
    alphas = np.linspace(0.0, 1.0, sample_count, dtype=np.float64)
    for refinement in range(1, max_refinements + 1):
        points = (
            segment_left[None, :]
            + alphas[:, None] * (segment_right - segment_left)[None, :]
        )
        lifetimes = np.asarray(escape_time(points), dtype=np.float64)
        evaluations += len(points)
        if lifetimes.shape != (sample_count,) or np.any(~np.isfinite(lifetimes)):
            raise ValueError("escape_time must return one finite value per point")
        candidates = np.flatnonzero(
            (lifetimes[1:-1] > lifetimes[:-2])
            & (lifetimes[1:-1] > lifetimes[2:])
        ) + 1
        if len(candidates) == 0:
            raise RuntimeError(
                f"no strict interior escape-time maximum at refinement {refinement}"
            )
        best_lifetime = np.max(lifetimes[candidates])
        best = int(candidates[lifetimes[candidates] == best_lifetime][0])
        new_left = points[best - 1].copy()
        center = points[best].copy()
        new_right = points[best + 1].copy()
        width = _normalized_segment_width(new_left, new_right, scales)
        widths.append(width)
        triple = PIMTriple(
            left=new_left,
            center=center,
            right=new_right,
            escape_times=lifetimes[best - 1 : best + 2].copy(),
            normalized_width=width,
        )
        if width <= width_tolerance:
            return PIMRefinementResult(
                triple=triple,
                refinement_count=refinement,
                lifetime_evaluations=evaluations,
                normalized_widths=np.asarray(widths, dtype=np.float64),
            )
        segment_left = new_left
        segment_right = new_right

    assert triple is not None
    raise RuntimeError(
        "PIM refinement did not reach width tolerance: "
        f"{triple.normalized_width:.6g} > {width_tolerance:.6g}"
    )


def refine_censor_aware_pim_segment(
    left: ArrayLike,
    right: ArrayLike,
    escape_time: Callable[[NDArray[np.float64]], PIMLifetimeBatch],
    *,
    coordinate_scales: ArrayLike,
    sample_count: int,
    width_tolerance: float,
    max_refinements: int,
) -> CensorAwarePIMRefinementResult:
    """Refine a PIM segment using exact times and certified lower bounds.

    A contiguous right-censored interior block is admissible only when it is
    bracketed by captured points and its selected lower bound is strictly
    larger than both exact endpoint lifetimes. Blocks touching the segment
    boundary, integration failures, and non-proper refinements are rejected.
    """

    segment_left = np.asarray(left, dtype=np.float64)
    segment_right = np.asarray(right, dtype=np.float64)
    scales = np.asarray(coordinate_scales, dtype=np.float64)
    if (
        segment_left.ndim != 1
        or segment_right.shape != segment_left.shape
        or scales.shape != segment_left.shape
        or len(segment_left) == 0
    ):
        raise ValueError("PIM endpoints and coordinate scales must share shape (d,)")
    if not np.all(np.isfinite(segment_left)) or not np.all(np.isfinite(segment_right)):
        raise ValueError("PIM endpoints must be finite")
    if np.any(~np.isfinite(scales)) or np.any(scales <= 0.0):
        raise ValueError("PIM coordinate scales must be finite and positive")
    if sample_count < 3 or width_tolerance <= 0.0 or max_refinements < 1:
        raise ValueError("invalid PIM refinement controls")
    if np.array_equal(segment_left, segment_right):
        raise ValueError("PIM segment endpoints must be distinct")

    widths: list[float] = []
    evaluations = 0
    censor_selections = 0
    triple: PIMTriple | None = None
    alphas = np.linspace(0.0, 1.0, sample_count, dtype=np.float64)
    for refinement in range(1, max_refinements + 1):
        old_width = _normalized_segment_width(segment_left, segment_right, scales)
        points = (
            segment_left[None, :]
            + alphas[:, None] * (segment_right - segment_left)[None, :]
        )
        batch = escape_time(points)
        lifetimes = np.asarray(batch.lifetimes, dtype=np.float64)
        censored = np.asarray(batch.censored, dtype=bool)
        failed = np.asarray(batch.failed, dtype=bool)
        evaluations += len(points)
        if (
            lifetimes.shape != (sample_count,)
            or censored.shape != (sample_count,)
            or failed.shape != (sample_count,)
            or np.any(~np.isfinite(lifetimes))
        ):
            raise ValueError("invalid censor-aware escape-time batch")
        if np.any(failed):
            raise RuntimeError(
                f"PIM lifetime integration failed at refinement {refinement}"
            )

        candidates: list[tuple[float, int, int, int, bool]] = []
        exact = ~censored
        exact_maxima = np.flatnonzero(
            exact[1:-1]
            & exact[:-2]
            & exact[2:]
            & (lifetimes[1:-1] > lifetimes[:-2])
            & (lifetimes[1:-1] > lifetimes[2:])
        ) + 1
        for center_index in exact_maxima:
            candidates.append(
                (
                    float(lifetimes[center_index]),
                    int(center_index),
                    int(center_index - 1),
                    int(center_index + 1),
                    False,
                )
            )

        padded = np.concatenate(([False], censored, [False])).astype(np.int8)
        starts = np.flatnonzero(np.diff(padded) == 1)
        ends = np.flatnonzero(np.diff(padded) == -1) - 1
        for block_start, block_end in zip(starts, ends, strict=True):
            if block_start == 0 or block_end == sample_count - 1:
                continue
            left_index = int(block_start - 1)
            right_index = int(block_end + 1)
            block_indices = np.arange(block_start, block_end + 1)
            best_bound = np.max(lifetimes[block_indices])
            center_index = int(
                block_indices[lifetimes[block_indices] == best_bound][0]
            )
            if best_bound <= max(lifetimes[left_index], lifetimes[right_index]):
                continue
            new_width = _normalized_segment_width(
                points[left_index], points[right_index], scales
            )
            if new_width >= old_width:
                continue
            candidates.append(
                (
                    float(best_bound),
                    center_index,
                    left_index,
                    right_index,
                    True,
                )
            )

        if not candidates:
            raise RuntimeError(
                "no exact or certified right-censored interior maximum at "
                f"refinement {refinement}"
            )
        score, center_index, left_index, right_index, used_censor = min(
            candidates, key=lambda row: (-row[0], row[1], row[2], row[3])
        )
        del score
        new_left = points[left_index].copy()
        center = points[center_index].copy()
        new_right = points[right_index].copy()
        width = _normalized_segment_width(new_left, new_right, scales)
        widths.append(width)
        censor_selections += int(used_censor)
        triple = PIMTriple(
            left=new_left,
            center=center,
            right=new_right,
            escape_times=np.asarray(
                (
                    lifetimes[left_index],
                    lifetimes[center_index],
                    lifetimes[right_index],
                ),
                dtype=np.float64,
            ),
            normalized_width=width,
        )
        if width <= width_tolerance:
            return CensorAwarePIMRefinementResult(
                triple=triple,
                refinement_count=refinement,
                lifetime_evaluations=evaluations,
                normalized_widths=np.asarray(widths, dtype=np.float64),
                certified_censor_block_selections=censor_selections,
            )
        segment_left = new_left
        segment_right = new_right

    assert triple is not None
    raise RuntimeError(
        "censor-aware PIM refinement did not reach width tolerance: "
        f"{triple.normalized_width:.6g} > {width_tolerance:.6g}"
    )


def advance_censor_aware_pim_straddle(
    initial_triple: PIMTriple,
    return_map: Callable[[NDArray[np.float64]], ArrayLike],
    escape_time: Callable[[NDArray[np.float64]], PIMLifetimeBatch],
    *,
    coordinate_scales: ArrayLike,
    return_count: int,
    sample_count: int,
    width_tolerance: float,
    max_refinements_per_event: int,
) -> CensorAwarePIMStraddleResult:
    """Advance and re-refine a PIM straddle using certified censor bounds."""

    scales = np.asarray(coordinate_scales, dtype=np.float64)
    points = initial_triple.points
    if points.ndim != 2 or points.shape[0] != 3 or scales.shape != points.shape[1:]:
        raise ValueError("PIM triple and coordinate scales have incompatible shapes")
    if np.any(~np.isfinite(scales)) or np.any(scales <= 0.0):
        raise ValueError("PIM coordinate scales must be finite and positive")
    if (
        return_count < 1
        or sample_count < 3
        or width_tolerance <= 0.0
        or max_refinements_per_event < 1
    ):
        raise ValueError("invalid censor-aware PIM straddle controls")

    current = initial_triple
    states = []
    widths = []
    events = []
    evaluations = 0
    censor_selections = 0
    for return_index in range(return_count):
        states.append(current.center.copy())
        widths.append(float(current.normalized_width))
        mapped = np.asarray(return_map(current.points), dtype=np.float64)
        if mapped.shape != current.points.shape or np.any(~np.isfinite(mapped)):
            raise RuntimeError(f"PIM return map failed at return {return_index}")
        mapped_width = _normalized_segment_width(mapped[0], mapped[2], scales)
        if mapped_width > width_tolerance:
            refined = refine_censor_aware_pim_segment(
                mapped[0],
                mapped[2],
                escape_time,
                coordinate_scales=scales,
                sample_count=sample_count,
                width_tolerance=width_tolerance,
                max_refinements=max_refinements_per_event,
            )
            current = refined.triple
            evaluations += refined.lifetime_evaluations
            censor_selections += refined.certified_censor_block_selections
            events.append(return_index + 1)
        else:
            current = PIMTriple(
                left=mapped[0].copy(),
                center=mapped[1].copy(),
                right=mapped[2].copy(),
                escape_times=np.full(3, np.nan),
                normalized_width=mapped_width,
            )
    return CensorAwarePIMStraddleResult(
        states=np.asarray(states, dtype=np.float64),
        normalized_widths=np.asarray(widths, dtype=np.float64),
        refinement_events=np.asarray(events, dtype=np.int64),
        lifetime_evaluations=evaluations,
        certified_censor_block_selections=censor_selections,
        final_triple=current,
    )


def advance_pim_straddle(
    initial_triple: PIMTriple,
    return_map: Callable[[NDArray[np.float64]], ArrayLike],
    escape_time: Callable[[NDArray[np.float64]], ArrayLike],
    *,
    coordinate_scales: ArrayLike,
    return_count: int,
    sample_count: int,
    width_tolerance: float,
    max_refinements_per_event: int,
) -> PIMStraddleResult:
    """Advance a PIM middle-point orbit, refining whenever its bracket expands.

    The mapped endpoints define the next local straight segment. This is the
    standard finite-precision straddle construction: iterate while the bracket
    remains below ``width_tolerance`` and reapply the proper-interior-maximum
    refinement when it grows beyond that scale.
    """

    scales = np.asarray(coordinate_scales, dtype=np.float64)
    points = initial_triple.points
    if points.ndim != 2 or points.shape[0] != 3 or scales.shape != points.shape[1:]:
        raise ValueError("PIM triple and coordinate scales have incompatible shapes")
    if np.any(~np.isfinite(scales)) or np.any(scales <= 0.0):
        raise ValueError("PIM coordinate scales must be finite and positive")
    if return_count < 1:
        raise ValueError("return_count must be positive")

    current = initial_triple
    states: list[NDArray[np.float64]] = []
    widths: list[float] = []
    events: list[int] = []
    evaluations = 0
    for return_index in range(return_count):
        states.append(current.center.copy())
        widths.append(float(current.normalized_width))
        mapped = np.asarray(return_map(current.points), dtype=np.float64)
        if mapped.shape != current.points.shape or np.any(~np.isfinite(mapped)):
            raise RuntimeError(f"PIM return map failed at return {return_index}")
        mapped_width = _normalized_segment_width(mapped[0], mapped[2], scales)
        if mapped_width > width_tolerance:
            refined = refine_pim_segment(
                mapped[0],
                mapped[2],
                escape_time,
                coordinate_scales=scales,
                sample_count=sample_count,
                width_tolerance=width_tolerance,
                max_refinements=max_refinements_per_event,
            )
            current = refined.triple
            evaluations += refined.lifetime_evaluations
            events.append(return_index + 1)
        else:
            current = PIMTriple(
                left=mapped[0].copy(),
                center=mapped[1].copy(),
                right=mapped[2].copy(),
                escape_times=np.full(3, np.nan),
                normalized_width=mapped_width,
            )
    return PIMStraddleResult(
        states=np.asarray(states, dtype=np.float64),
        normalized_widths=np.asarray(widths, dtype=np.float64),
        refinement_events=np.asarray(events, dtype=np.int64),
        lifetime_evaluations=evaluations,
        final_triple=current,
    )


def next_section_return(
    parameters: RosslerParameters,
    initial_state: ArrayLike,
    section: PoincareSection,
    *,
    config: SolverConfig = SolverConfig(),
    departure_time: float = 1e-4,
    maximum_flight_time: float = 50.0,
) -> SectionReturnResult:
    """Advance one section return with adaptive DOP853 event localization.

    A short event-free departure avoids accepting the initial point as a root.
    The state is not projected after integration; SciPy's event state is used.
    """

    state = np.asarray(initial_state, dtype=np.float64)
    if state.shape != (3,) or not np.all(np.isfinite(state)):
        raise ValueError("initial_state must contain three finite values")
    if departure_time <= 0.0 or maximum_flight_time <= departure_time:
        raise ValueError("invalid section-return flight times")
    if abs(section.value(state)) > 1e-8:
        raise ValueError("initial_state must lie on the declared section")
    if section.direction not in (-1, 1):
        raise ValueError("adaptive return requires one declared crossing orientation")

    def rhs(time, value):
        return rossler_rhs(time, value, parameters)

    departure = solve_ivp(
        rhs,
        (0.0, departure_time),
        state,
        method=config.method,
        rtol=config.rtol,
        atol=config.atol,
        max_step=config.max_step,
    )
    if not departure.success:
        return SectionReturnResult(
            success=False,
            flight_time=float("nan"),
            state=np.full(3, np.nan),
            message=str(departure.message),
        )

    def event(_time, value):
        return section.value(value)

    event.direction = section.direction  # type: ignore[attr-defined]
    event.terminal = section.gate_axis is None  # type: ignore[attr-defined]
    result = solve_ivp(
        rhs,
        (departure_time, maximum_flight_time),
        np.asarray(departure.y[:, -1], dtype=np.float64),
        method=config.method,
        rtol=config.rtol,
        atol=config.atol,
        max_step=config.max_step,
        events=event,
    )
    if not result.success or len(result.t_events[0]) == 0:
        return SectionReturnResult(
            success=False,
            flight_time=float("nan"),
            state=np.full(3, np.nan),
            message=str(result.message) if not result.success else "no section return",
        )
    raw_states = np.asarray(result.y_events[0], dtype=np.float64)
    accepted = np.asarray([section.accepts(value) for value in raw_states], dtype=bool)
    if not np.any(accepted):
        return SectionReturnResult(
            success=False,
            flight_time=float("nan"),
            state=np.full(3, np.nan),
            message="no oriented section return passed the declared gate",
        )
    index = int(np.flatnonzero(accepted)[0])
    crossing = raw_states[index]
    return SectionReturnResult(
        success=True,
        flight_time=float(result.t_events[0][index]),
        state=crossing,
        message="section return located",
    )


def section_return_map(
    parameters: RosslerParameters,
    states: ArrayLike,
    section: PoincareSection,
    *,
    config: SolverConfig = SolverConfig(),
    departure_time: float = 1e-4,
    maximum_flight_time: float = 50.0,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.bool_]]:
    """Map section states independently to their next adaptive returns."""

    points = np.asarray(states, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3 or len(points) == 0:
        raise ValueError("states must have nonempty shape (n,3)")
    mapped = np.full_like(points, np.nan)
    times = np.full(len(points), np.nan, dtype=np.float64)
    success = np.zeros(len(points), dtype=bool)
    for index, point in enumerate(points):
        returned = next_section_return(
            parameters,
            point,
            section,
            config=config,
            departure_time=departure_time,
            maximum_flight_time=maximum_flight_time,
        )
        mapped[index] = returned.state
        times[index] = returned.flight_time
        success[index] = returned.success
    return mapped, times, success


def capture_lifetimes_on_section(
    parameters: RosslerParameters,
    initial_states: ArrayLike,
    section: PoincareSection,
    cycle_states: ArrayLike,
    *,
    capture_coordinate_axes: tuple[int, int],
    capture_coordinate_scales: tuple[float, float],
    capture_radius: float,
    required_capture_crossings: int,
    maximum_returns: int,
    config: SolverConfig = SolverConfig(),
    maximum_flight_time: float = 50.0,
) -> CaptureLifetimeResult:
    """Measure adaptive section time until repeated stable-cycle capture."""

    states = np.asarray(initial_states, dtype=np.float64)
    cycle = np.asarray(cycle_states, dtype=np.float64)
    if states.ndim != 2 or states.shape[1] != 3 or len(states) == 0:
        raise ValueError("initial_states must have nonempty shape (n,3)")
    if maximum_returns < required_capture_crossings or required_capture_crossings < 1:
        raise ValueError("maximum_returns must cover the capture streak")
    if capture_radius <= 0.0:
        raise ValueError("capture_radius must be positive")

    current = states.copy()
    lifetimes = np.zeros(len(states), dtype=np.float64)
    captured = np.zeros(len(states), dtype=bool)
    failed = np.zeros(len(states), dtype=bool)
    streaks = np.zeros(len(states), dtype=np.int64)
    return_counts = np.zeros(len(states), dtype=np.int64)
    for _ in range(maximum_returns):
        active = ~(captured | failed)
        if not np.any(active):
            break
        active_indices = np.flatnonzero(active)
        mapped, flight_times, success = section_return_map(
            parameters,
            current[active],
            section,
            config=config,
            maximum_flight_time=maximum_flight_time,
        )
        failed[active_indices[~success]] = True
        valid_indices = active_indices[success]
        if len(valid_indices) == 0:
            continue
        current[valid_indices] = mapped[success]
        lifetimes[valid_indices] += flight_times[success]
        return_counts[valid_indices] += 1
        distances = cycle_crossing_distances(
            mapped[success],
            cycle,
            coordinate_axes=capture_coordinate_axes,
            coordinate_scales=capture_coordinate_scales,
        )
        close = distances <= capture_radius
        streaks[valid_indices] = np.where(close, streaks[valid_indices] + 1, 0)
        captured[valid_indices[streaks[valid_indices] >= required_capture_crossings]] = True
    return CaptureLifetimeResult(
        lifetimes=lifetimes,
        captured=captured,
        return_counts=return_counts,
        failed=failed,
    )


def scrambled_sobol_section_states(
    section: PoincareSection,
    *,
    first_coordinate_range: tuple[float, float],
    second_coordinate_range: tuple[float, float],
    sample_power: int,
    scramble_seed: int,
) -> NDArray[np.float64]:
    """Generate a nested scrambled Sobol ensemble on an oriented x section."""

    if section.normal != (1.0, 0.0, 0.0):
        raise ValueError("Sobol section ensemble currently requires an x plane")
    bounds = np.asarray(
        (first_coordinate_range, second_coordinate_range), dtype=np.float64
    )
    if (
        bounds.shape != (2, 2)
        or not np.all(np.isfinite(bounds))
        or np.any(bounds[:, 0] >= bounds[:, 1])
    ):
        raise ValueError("coordinate ranges must be finite increasing pairs")
    if sample_power < 1 or scramble_seed < 0:
        raise ValueError("sample_power must be positive and seed nonnegative")
    unit = qmc.Sobol(d=2, scramble=True, seed=scramble_seed).random_base2(
        sample_power
    )
    scaled = qmc.scale(unit, bounds[:, 0], bounds[:, 1])
    return np.column_stack(
        (np.full(len(scaled), section.offset), scaled[:, 0], scaled[:, 1])
    )


def survivor_return_pairs(
    result: SprinklerResult, coordinate_axis: int
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Form consecutive return pairs within each surviving trajectory."""

    if coordinate_axis not in (0, 1, 2):
        raise ValueError("coordinate_axis must be 0, 1, or 2")
    order = np.lexsort((result.midpoint_times, result.midpoint_trajectory_ids))
    ordered_ids = result.midpoint_trajectory_ids[order]
    ordered_values = result.midpoint_states[order, coordinate_axis]
    boundaries = np.flatnonzero(np.diff(ordered_ids)) + 1
    sources = []
    targets = []
    for values in np.split(ordered_values, boundaries):
        if len(values) >= 2:
            sources.append(values[:-1])
            targets.append(values[1:])
    if not sources:
        return np.empty(0), np.empty(0)
    return np.concatenate(sources), np.concatenate(targets)


def _rossler_rhs_batch(states, parameters):
    x = states[:, 0]
    y = states[:, 1]
    z = states[:, 2]
    return np.column_stack(
        (
            -y - z,
            x + parameters.a * y,
            parameters.b + z * (x - parameters.c),
        )
    )


def _rk4_batch_step(states, dt, parameters):
    k1 = _rossler_rhs_batch(states, parameters)
    k2 = _rossler_rhs_batch(states + 0.5 * dt * k1, parameters)
    k3 = _rossler_rhs_batch(states + 0.5 * dt * k2, parameters)
    k4 = _rossler_rhs_batch(states + dt * k3, parameters)
    return states + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def _cubic_hermite_crossing(
    previous,
    current,
    previous_derivative,
    current_derivative,
    *,
    dt,
    normal,
    offset,
    direction=1,
    bisection_iterations=40,
):
    """Interpolate an oriented section root inside one flow step."""

    previous = np.asarray(previous, dtype=np.float64)
    current = np.asarray(current, dtype=np.float64)
    previous_derivative = np.asarray(previous_derivative, dtype=np.float64)
    current_derivative = np.asarray(current_derivative, dtype=np.float64)
    normal = np.asarray(normal, dtype=np.float64)
    if (
        previous.ndim != 2
        or previous.shape[1] != 3
        or current.shape != previous.shape
        or previous_derivative.shape != previous.shape
        or current_derivative.shape != previous.shape
    ):
        raise ValueError("Hermite states and derivatives must share shape (n,3)")
    if (
        normal.shape != (3,)
        or direction not in (-1, 1)
        or dt <= 0.0
        or bisection_iterations < 1
    ):
        raise ValueError("invalid Hermite section geometry or iteration count")

    def interpolate(alpha):
        alpha = np.asarray(alpha, dtype=np.float64)
        alpha2 = alpha * alpha
        alpha3 = alpha2 * alpha
        h00 = 2.0 * alpha3 - 3.0 * alpha2 + 1.0
        h10 = alpha3 - 2.0 * alpha2 + alpha
        h01 = -2.0 * alpha3 + 3.0 * alpha2
        h11 = alpha3 - alpha2
        return (
            h00[:, None] * previous
            + (h10 * dt)[:, None] * previous_derivative
            + h01[:, None] * current
            + (h11 * dt)[:, None] * current_derivative
        )

    left = np.zeros(len(previous), dtype=np.float64)
    right = np.ones(len(previous), dtype=np.float64)
    for _ in range(bisection_iterations):
        midpoint = 0.5 * (left + right)
        values = interpolate(midpoint) @ normal - offset
        if direction == 1:
            right = np.where(values >= 0.0, midpoint, right)
            left = np.where(values < 0.0, midpoint, left)
        else:
            right = np.where(values <= 0.0, midpoint, right)
            left = np.where(values > 0.0, midpoint, left)
    alpha = 0.5 * (left + right)
    return alpha, interpolate(alpha)


def cycle_crossing_distances(
    crossing_states: ArrayLike,
    cycle_states: ArrayLike,
    *,
    coordinate_axes: tuple[int, int],
    coordinate_scales: tuple[float, float],
) -> NDArray[np.float64]:
    """Return each crossing's minimum scaled distance to a reference cycle."""

    crossings = np.asarray(crossing_states, dtype=np.float64)
    cycle = np.asarray(cycle_states, dtype=np.float64)
    axes = np.asarray(coordinate_axes, dtype=int)
    scales = np.asarray(coordinate_scales, dtype=np.float64)
    if crossings.ndim != 2 or crossings.shape[1] != 3:
        raise ValueError("crossing_states must have shape (n,3)")
    if cycle.ndim != 2 or cycle.shape[1] != 3 or len(cycle) == 0:
        raise ValueError("cycle_states must have nonempty shape (p,3)")
    if len(set(coordinate_axes)) != 2 or np.any((axes < 0) | (axes > 2)):
        raise ValueError("coordinate_axes must select two distinct state coordinates")
    if np.any(~np.isfinite(scales)) or np.any(scales <= 0.0):
        raise ValueError("coordinate_scales must be finite and positive")
    differences = (
        crossings[:, None, axes] - cycle[None, :, axes]
    ) / scales[None, None, :]
    return np.min(np.linalg.norm(differences, axis=2), axis=1)


def sprinkler_survivors(
    parameters: RosslerParameters,
    initial_states: ArrayLike,
    section: PoincareSection,
    cycle_states: ArrayLike,
    *,
    dt: float,
    horizon: float,
    capture_coordinate_axes: tuple[int, int],
    capture_coordinate_scales: tuple[float, float],
    capture_radius: float,
    required_capture_crossings: int,
    checkpoint_times: ArrayLike,
    midpoint_window: tuple[float, float],
    escape_radius: float = 1e4,
) -> SprinklerResult:
    """Select long-lived trajectories and their middle-time section points.

    The reference implementation supports either orientation of an
    axis-aligned section and applies any declared half-plane gate after root
    interpolation. A trajectory is captured only after a declared number of
    consecutive accepted section returns within a scaled radius of the
    reference invariant set.
    """

    initial = np.asarray(initial_states, dtype=np.float64)
    cycle = np.asarray(cycle_states, dtype=np.float64)
    checkpoints = np.asarray(checkpoint_times, dtype=np.float64)
    if initial.ndim != 2 or initial.shape[1] != 3 or len(initial) == 0:
        raise ValueError("initial_states must have nonempty shape (n,3)")
    if not np.all(np.isfinite(initial)):
        raise ValueError("initial_states must be finite")
    normal = np.asarray(section.normal, dtype=np.float64)
    if np.count_nonzero(normal) != 1 or section.direction not in (-1, 1):
        raise ValueError("sprinkler reference requires an oriented axis-aligned plane")
    if dt <= 0.0 or horizon <= 0.0 or capture_radius <= 0.0:
        raise ValueError("dt, horizon, and capture_radius must be positive")
    if required_capture_crossings < 1 or escape_radius <= 0.0:
        raise ValueError("capture repeats and escape radius must be positive")
    step_count = round(horizon / dt)
    if not np.isclose(step_count * dt, horizon, rtol=0.0, atol=1e-12):
        raise ValueError("horizon must be an integer multiple of dt")
    checkpoint_steps = np.rint(checkpoints / dt).astype(int)
    if (
        np.any(checkpoints <= 0.0)
        or np.any(checkpoints > horizon)
        or np.any(np.diff(checkpoints) <= 0.0)
        or not np.allclose(checkpoint_steps * dt, checkpoints, rtol=0.0, atol=1e-12)
    ):
        raise ValueError("checkpoint_times must be ordered step-aligned times")
    midpoint_start, midpoint_end = map(float, midpoint_window)
    if not (0.0 <= midpoint_start < midpoint_end <= horizon):
        raise ValueError("midpoint_window must lie inside the horizon")

    trajectory_count = len(initial)
    capture_times = np.full(trajectory_count, np.nan, dtype=np.float64)
    failed = np.zeros(trajectory_count, dtype=bool)
    capture_streaks = np.zeros(trajectory_count, dtype=np.int32)
    active_ids = np.arange(trajectory_count, dtype=np.int64)
    active_states = initial.copy()
    checkpoint_counts = []
    checkpoint_index = 0
    record_ids = []
    record_times = []
    record_states = []

    for step in range(1, step_count + 1):
        previous = active_states
        current = _rk4_batch_step(previous, dt, parameters)
        finite = np.all(np.isfinite(current), axis=1)
        bounded = np.linalg.norm(current, axis=1) <= escape_radius
        valid = finite & bounded
        if np.any(~valid):
            failed[active_ids[~valid]] = True

        previous_value = previous @ normal - section.offset
        current_value = current @ normal - section.offset
        if section.direction == 1:
            crossed = valid & (previous_value < 0.0) & (current_value >= 0.0)
        else:
            crossed = valid & (previous_value > 0.0) & (current_value <= 0.0)
        crossed_local = np.flatnonzero(crossed)
        captured_local = np.zeros(len(active_ids), dtype=bool)
        if len(crossed_local):
            previous_crossed = previous[crossed_local]
            current_crossed = current[crossed_local]
            alpha, crossing = _cubic_hermite_crossing(
                previous_crossed,
                current_crossed,
                _rossler_rhs_batch(previous_crossed, parameters),
                _rossler_rhs_batch(current_crossed, parameters),
                dt=dt,
                normal=section.normal,
                offset=section.offset,
                direction=section.direction,
            )
            if section.gate_axis is not None:
                accepted = crossing[:, section.gate_axis] < float(section.gate_upper)
                crossed_local = crossed_local[accepted]
                alpha = alpha[accepted]
                crossing = crossing[accepted]
            if len(crossed_local):
                crossed_ids = active_ids[crossed_local]
                distances = cycle_crossing_distances(
                    crossing,
                    cycle,
                    coordinate_axes=capture_coordinate_axes,
                    coordinate_scales=capture_coordinate_scales,
                )
                close = distances <= capture_radius
                capture_streaks[crossed_ids] = np.where(
                    close, capture_streaks[crossed_ids] + 1, 0
                )
                newly_captured = (
                    capture_streaks[crossed_ids] >= required_capture_crossings
                )
                if np.any(newly_captured):
                    local = crossed_local[newly_captured]
                    captured_local[local] = True
                    capture_times[active_ids[local]] = (
                        step - 1 + alpha[newly_captured]
                    ) * dt
                crossing_times = (step - 1 + alpha) * dt
                in_midpoint = (
                    (crossing_times >= midpoint_start)
                    & (crossing_times <= midpoint_end)
                )
                if np.any(in_midpoint):
                    record_ids.append(crossed_ids[in_midpoint])
                    record_times.append(crossing_times[in_midpoint])
                    record_states.append(crossing[in_midpoint])

        retain = valid & ~captured_local
        active_ids = active_ids[retain]
        active_states = current[retain]
        while (
            checkpoint_index < len(checkpoint_steps)
            and step == checkpoint_steps[checkpoint_index]
        ):
            checkpoint_counts.append(len(active_ids))
            checkpoint_index += 1
        if len(active_ids) == 0:
            while checkpoint_index < len(checkpoint_steps):
                checkpoint_counts.append(0)
                checkpoint_index += 1
            break

    if record_ids:
        all_record_ids = np.concatenate(record_ids)
        all_record_times = np.concatenate(record_times)
        all_record_states = np.concatenate(record_states)
        retained_records = np.isin(all_record_ids, active_ids)
        midpoint_ids = all_record_ids[retained_records]
        midpoint_times = all_record_times[retained_records]
        midpoint_states = all_record_states[retained_records]
    else:
        all_record_ids = np.empty(0, dtype=np.int64)
        all_record_times = np.empty(0, dtype=np.float64)
        all_record_states = np.empty((0, 3), dtype=np.float64)
        midpoint_ids = np.empty(0, dtype=np.int64)
        midpoint_times = np.empty(0, dtype=np.float64)
        midpoint_states = np.empty((0, 3), dtype=np.float64)
    return SprinklerResult(
        capture_times=capture_times,
        failed=failed,
        survivor_ids=active_ids,
        survivor_initial_states=initial[active_ids],
        survivor_final_states=active_states,
        checkpoint_times=checkpoints,
        survivor_counts=np.asarray(checkpoint_counts, dtype=np.int64),
        midpoint_trajectory_ids=midpoint_ids,
        midpoint_times=midpoint_times,
        midpoint_states=midpoint_states,
        all_midpoint_trajectory_ids=all_record_ids,
        all_midpoint_times=all_record_times,
        all_midpoint_states=all_record_states,
    )

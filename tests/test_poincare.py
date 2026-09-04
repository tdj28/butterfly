import numpy as np

from butterfly.integrate import SolverConfig
from butterfly.models import RosslerParameters, rossler_rhs
from butterfly.poincare import (
    PoincareSection,
    barrio_rossler_section,
    collect_crossings,
    legacy_rossler_section,
)


HUB = RosslerParameters(a=0.1798, b=0.2, c=10.3084)
CONFIG = SolverConfig(rtol=1e-10, atol=1e-12, max_step=0.05)


def assert_on_section_at_event_precision(result) -> None:
    # solve_ivp locates events with Brent xtol=rtol=4*eps in time, not
    # section-coordinate units. Convert that scale using the normal velocity,
    # allowing a factor two for interpolation/evaluation roundoff. This tests
    # the interpolated section residual, not forward trajectory accuracy.
    normal = np.asarray(result.section.normal)
    speed = np.asarray([
        abs(np.dot(normal, rossler_rhs(time, state, HUB)))
        for time, state in zip(result.times, result.states, strict=True)
    ])
    eps = np.finfo(float).eps
    time_roundoff = 8 * eps * (1 + np.abs(result.times)) * np.maximum(1.0, speed)
    state_roundoff = 8 * eps * (
        1 + np.abs(result.states) @ np.abs(normal) + abs(result.section.offset)
    )
    residual = np.abs(result.states @ normal - result.section.offset)
    assert np.all(residual <= time_roundoff + state_roundoff)


def test_oriented_crossings_are_interpolated_and_ordered() -> None:
    section = PoincareSection(normal=(0.0, 1.0, 0.0), offset=0.0, direction=1)
    result = collect_crossings(
        HUB,
        (0.0, 4.0, 0.0),
        section,
        transient=20.0,
        observation_horizon=50.0,
        max_crossings=5,
        config=CONFIG,
    )
    assert result.integration_success
    assert result.states.shape == (5, 3)
    assert np.all(np.diff(result.times) > 0.0)
    assert_on_section_at_event_precision(result)
    derivatives = np.asarray(
        [np.dot(section.normal, rossler_rhs(time, state, HUB)) for time, state in zip(result.times, result.states)]
    )
    assert np.all(derivatives > 0.0)


def test_legacy_section_matches_declared_half_plane() -> None:
    section = legacy_rossler_section(HUB)
    result = collect_crossings(
        HUB,
        (0.0, 4.0, 0.0),
        section,
        transient=20.0,
        observation_horizon=80.0,
        max_crossings=6,
        config=CONFIG,
    )
    assert result.integration_success
    assert result.states.shape == (6, 3)
    assert_on_section_at_event_precision(result)
    assert np.all(result.states[:, 0] < section.gate_upper)


def test_barrio_section_matches_declared_oriented_plane() -> None:
    section = barrio_rossler_section(HUB)
    result = collect_crossings(
        HUB,
        (0.0, 4.0, 0.0),
        section,
        transient=20.0,
        observation_horizon=80.0,
        max_crossings=6,
        config=CONFIG,
    )
    assert result.integration_success
    assert result.states.shape == (6, 3)
    assert_on_section_at_event_precision(result)
    derivatives = np.asarray(
        [
            np.dot(section.normal, rossler_rhs(time, state, HUB))
            for time, state in zip(result.times, result.states, strict=True)
        ]
    )
    assert np.all(derivatives > 0.0)


def test_invalid_zero_normal_is_rejected() -> None:
    try:
        PoincareSection(normal=(0.0, 0.0, 0.0), offset=0.0)
    except ValueError as error:
        assert "nonzero" in str(error)
    else:
        raise AssertionError("zero-normal section was accepted")

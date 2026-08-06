import numpy as np

from butterfly.integrate import SolverConfig
from butterfly.models import RosslerParameters, rossler_rhs
from butterfly.poincare import (
    PoincareSection,
    collect_crossings,
    legacy_rossler_section,
)


HUB = RosslerParameters(a=0.1798, b=0.2, c=10.3084)
CONFIG = SolverConfig(rtol=1e-10, atol=1e-12, max_step=0.05)


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
    np.testing.assert_allclose(result.states[:, 1], 0.0, atol=2e-14)
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
    np.testing.assert_allclose(result.states[:, 1], section.offset, atol=2e-14)
    assert np.all(result.states[:, 0] < section.gate_upper)


def test_invalid_zero_normal_is_rejected() -> None:
    try:
        PoincareSection(normal=(0.0, 0.0, 0.0), offset=0.0)
    except ValueError as error:
        assert "nonzero" in str(error)
    else:
        raise AssertionError("zero-normal section was accepted")

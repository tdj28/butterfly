import numpy as np

from butterfly import (
    PoincareSection,
    RosslerParameters,
    cycle_crossing_distances,
    sprinkler_survivors,
)
from butterfly.saddle import _rk4_batch_step


def test_batch_rk4_preserves_duplicate_states() -> None:
    parameters = RosslerParameters(a=0.2, b=0.2, c=20.0)
    states = np.asarray(((0.0, 4.0, 0.0), (0.0, 4.0, 0.0)))
    stepped = _rk4_batch_step(states, 0.01, parameters)
    assert stepped.shape == states.shape
    np.testing.assert_array_equal(stepped[0], stepped[1])
    assert not np.array_equal(stepped[0], states[0])


def test_cycle_crossing_distance_uses_declared_scaling() -> None:
    cycle = np.asarray(((1.0, 2.0, 3.0), (1.0, 4.0, 7.0)))
    crossings = np.asarray(((1.0, 3.0, 5.0), (1.0, 4.0, 7.0)))
    distances = cycle_crossing_distances(
        crossings,
        cycle,
        coordinate_axes=(1, 2),
        coordinate_scales=(2.0, 4.0),
    )
    np.testing.assert_allclose(distances, (np.sqrt(0.5), 0.0))


def test_sprinkler_reports_no_capture_over_short_horizon() -> None:
    parameters = RosslerParameters(a=0.2, b=0.2, c=20.0)
    section = PoincareSection(normal=(1.0, 0.0, 0.0), offset=0.0, direction=1)
    initial = np.asarray(((0.0, -10.0, 0.01), (0.0, -12.0, 0.01)))
    cycle = np.asarray(((0.0, -20.0, 0.01),))
    result = sprinkler_survivors(
        parameters,
        initial,
        section,
        cycle,
        dt=0.01,
        horizon=0.1,
        capture_coordinate_axes=(1, 2),
        capture_coordinate_scales=(10.0, 0.01),
        capture_radius=1e-6,
        required_capture_crossings=2,
        checkpoint_times=(0.05, 0.1),
        midpoint_window=(0.02, 0.08),
    )
    np.testing.assert_array_equal(result.survivor_ids, (0, 1))
    np.testing.assert_array_equal(result.survivor_counts, (2, 2))
    assert not np.any(result.failed)

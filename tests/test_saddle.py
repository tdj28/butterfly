import numpy as np

from butterfly import (
    PoincareSection,
    RosslerParameters,
    cycle_crossing_distances,
    scrambled_sobol_section_states,
    sprinkler_survivors,
    survivor_return_pairs,
)
from butterfly.saddle import _cubic_hermite_crossing, _rk4_batch_step


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


def test_cubic_hermite_crossing_recovers_exact_polynomial_state() -> None:
    previous = np.asarray(((-0.3, 0.0, 2.0),))
    current = np.asarray(((0.7, 1.0, 2.0),))
    previous_derivative = np.asarray(((1.0, 0.0, 0.0),))
    current_derivative = np.asarray(((1.0, 2.0, 0.0),))
    alpha, state = _cubic_hermite_crossing(
        previous,
        current,
        previous_derivative,
        current_derivative,
        dt=1.0,
        normal=(1.0, 0.0, 0.0),
        offset=0.0,
    )
    np.testing.assert_allclose(alpha, (0.3,), atol=1e-12)
    np.testing.assert_allclose(state, ((0.0, 0.09, 2.0),), atol=1e-12)


def test_scrambled_sobol_section_ensemble_is_nested_and_bounded() -> None:
    section = PoincareSection(normal=(1.0, 0.0, 0.0), offset=0.25, direction=1)
    coarse = scrambled_sobol_section_states(
        section,
        first_coordinate_range=(-3.0, -1.0),
        second_coordinate_range=(0.01, 0.02),
        sample_power=3,
        scramble_seed=112,
    )
    fine = scrambled_sobol_section_states(
        section,
        first_coordinate_range=(-3.0, -1.0),
        second_coordinate_range=(0.01, 0.02),
        sample_power=4,
        scramble_seed=112,
    )
    np.testing.assert_array_equal(coarse, fine[: len(coarse)])
    assert np.all(coarse[:, 0] == section.offset)
    assert np.all((-3.0 <= coarse[:, 1]) & (coarse[:, 1] <= -1.0))
    assert np.all((0.01 <= coarse[:, 2]) & (coarse[:, 2] <= 0.02))


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


def test_survivor_return_pairs_do_not_join_trajectories() -> None:
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
        horizon=20.0,
        capture_coordinate_axes=(1, 2),
        capture_coordinate_scales=(10.0, 0.01),
        capture_radius=1e-12,
        required_capture_crossings=100,
        checkpoint_times=(20.0,),
        midpoint_window=(0.0, 20.0),
    )
    source, target = survivor_return_pairs(result, 1)
    expected = sum(
        max(
            np.count_nonzero(result.midpoint_trajectory_ids == trajectory_id) - 1,
            0,
        )
        for trajectory_id in result.survivor_ids
    )
    assert len(source) == expected
    assert len(target) == expected

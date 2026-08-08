import numpy as np

from butterfly import (
    PoincareSection,
    PIMLifetimeBatch,
    RosslerParameters,
    SolverConfig,
    advance_pim_straddle,
    cycle_crossing_distances,
    next_section_return,
    refine_censor_aware_pim_segment,
    refine_pim_segment,
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
    np.testing.assert_array_equal(
        result.all_midpoint_trajectory_ids, result.midpoint_trajectory_ids
    )
    np.testing.assert_array_equal(result.all_midpoint_times, result.midpoint_times)
    np.testing.assert_array_equal(result.all_midpoint_states, result.midpoint_states)


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


def test_pim_refinement_finds_strict_interior_lifetime_peak() -> None:
    def lifetime(points):
        return 10.0 - 1e8 * (points[:, 0] - 0.3712345) ** 2

    result = refine_pim_segment(
        (0.0,),
        (1.0,),
        lifetime,
        coordinate_scales=(1.0,),
        sample_count=17,
        width_tolerance=1e-7,
        max_refinements=8,
    )
    assert result.triple.normalized_width <= 1e-7
    assert abs(result.triple.center[0] - 0.3712345) <= 1e-7
    assert result.triple.escape_times[1] > result.triple.escape_times[0]
    assert result.triple.escape_times[1] > result.triple.escape_times[2]
    assert np.all(np.diff(result.normalized_widths) < 0.0)


def test_pim_straddle_refines_only_after_bracket_expansion() -> None:
    triple = refine_pim_segment(
        (0.0,),
        (1.0,),
        lambda points: 10.0 - 1e8 * (points[:, 0] - 0.3712345) ** 2,
        coordinate_scales=(1.0,),
        sample_count=17,
        width_tolerance=1e-4,
        max_refinements=6,
    ).triple

    result = advance_pim_straddle(
        triple,
        lambda points: 0.3712345 + 2.0 * (points - 0.3712345),
        lambda points: 10.0 - 1e8 * (points[:, 0] - 0.3712345) ** 2,
        coordinate_scales=(1.0,),
        return_count=5,
        sample_count=17,
        width_tolerance=1e-4,
        max_refinements_per_event=3,
    )
    assert result.states.shape == (5, 1)
    assert len(result.refinement_events) >= 1
    assert np.all(result.normalized_widths <= 1e-4)


def test_pim_refinement_rejects_monotone_escape_profile() -> None:
    def lifetime(points):
        return points[:, 0]

    with np.testing.assert_raises_regex(RuntimeError, "no strict interior"):
        refine_pim_segment(
            (0.0,),
            (1.0,),
            lifetime,
            coordinate_scales=(1.0,),
            sample_count=9,
            width_tolerance=1e-6,
            max_refinements=4,
        )


def test_censor_aware_pim_refines_certified_interior_lower_bound() -> None:
    target = 0.3712345

    def lifetime(points):
        exact = 1.0 / (np.abs(points[:, 0] - target) + 0.01)
        center = int(np.argmin(np.abs(points[:, 0] - target)))
        censored = np.zeros(len(points), dtype=bool)
        censored[center] = True
        exact[center] = 200.0
        return PIMLifetimeBatch(
            lifetimes=exact,
            censored=censored,
            failed=np.zeros(len(points), dtype=bool),
        )

    result = refine_censor_aware_pim_segment(
        (0.0,),
        (1.0,),
        lifetime,
        coordinate_scales=(1.0,),
        sample_count=17,
        width_tolerance=1e-6,
        max_refinements=8,
    )
    assert result.triple.normalized_width <= 1e-6
    assert abs(result.triple.center[0] - target) <= 1e-6
    assert result.certified_censor_block_selections == result.refinement_count


def test_censor_aware_pim_rejects_boundary_plateau() -> None:
    def lifetime(points):
        censored = np.zeros(len(points), dtype=bool)
        censored[:3] = True
        return PIMLifetimeBatch(
            lifetimes=np.where(censored, 100.0, 1.0),
            censored=censored,
            failed=np.zeros(len(points), dtype=bool),
        )

    with np.testing.assert_raises_regex(RuntimeError, "no exact or certified"):
        refine_censor_aware_pim_segment(
            (0.0,),
            (1.0,),
            lifetime,
            coordinate_scales=(1.0,),
            sample_count=9,
            width_tolerance=1e-6,
            max_refinements=4,
        )


def test_adaptive_section_return_skips_initial_root() -> None:
    parameters = RosslerParameters(a=0.2, b=0.2, c=20.0)
    section = PoincareSection(normal=(1.0, 0.0, 0.0), offset=0.0, direction=1)
    returned = next_section_return(
        parameters,
        (0.0, -10.0, 0.01),
        section,
        config=SolverConfig(method="DOP853", rtol=1e-10, atol=1e-12, max_step=0.05),
        maximum_flight_time=20.0,
    )
    assert returned.success
    assert returned.flight_time > 1.0
    assert abs(section.value(returned.state)) < 1e-10
    assert -returned.state[1] - returned.state[2] > 0.0

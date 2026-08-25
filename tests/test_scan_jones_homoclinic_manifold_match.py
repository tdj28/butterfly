import numpy as np
from scipy.sparse import csr_matrix

from butterfly import RosslerParameters
from scripts.scan_jones_homoclinic_manifold_match import (
    SCHEMA,
    align_local_geometry,
    parameters_at,
    scan_axis,
    stable_manifold_targets,
    tangent_basis,
)
from scripts.scan_jones_homoclinic_unstable_angles import eigenspaces
from scripts.solve_jones_homoclinic_single_shooting import (
    SCHEMA as SHOOTING_SCHEMA,
    absolute_central_jacobian,
)
from scripts.solve_jones_homoclinic_multiple_shooting import (
    SCHEMA as MULTIPLE_SHOOTING_SCHEMA,
    block_norms,
    interleave_split_nodes,
    node_bounds,
    solution_parameters,
    variable_layout,
)
from scripts.continue_jones_homoclinic_pseudoarclength import (
    SCHEMA as PSEUDOARCLENGTH_SCHEMA,
    arclength_group_norms,
    bounded_sparse_newton,
    directional_c_bounds,
    jacobian_conditioning_accepted,
    local_tangent_from_matching_jacobian,
    native_boolean_checks,
    optimizer_jacobian,
    projected_arclength_tangent,
    receipt_state_vector,
    source_angle_gauge,
    source_curve_values,
    unwrap_angle,
    variable_layout as pseudoarclength_layout,
    weighted_arclength_tangent,
)


def test_manifold_match_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-homoclinic-manifold-match-scan-manifest.v1"
    assert SHOOTING_SCHEMA == "butterfly.jones-homoclinic-single-shooting-manifest.v1"
    assert (
        MULTIPLE_SHOOTING_SCHEMA
        == "butterfly.jones-homoclinic-multiple-shooting-manifest.v1"
    )
    assert (
        PSEUDOARCLENGTH_SCHEMA
        == "butterfly.jones-homoclinic-pseudoarclength-manifest.v1"
    )


def test_homoclinic_multiple_shooting_layout_is_square():
    layout = variable_layout(16)
    assert layout == {
        "node_count": 15,
        "node_size": 45,
        "time_index": 45,
        "a_index": 46,
        "angle_index": 47,
        "variable_count": 48,
    }
    assert 3 * 16 == layout["variable_count"]


def test_homoclinic_pseudoarclength_layout_is_square():
    layout = pseudoarclength_layout(16)
    assert layout["node_size"] == 45
    assert layout["time_index"] == 45
    assert layout["a_index"] == 46
    assert layout["c_index"] == 47
    assert layout["angle_index"] == 48
    assert layout["variable_count"] == 49
    assert 3 * 16 + 1 == layout["variable_count"]


def test_homoclinic_pseudoarclength_angle_unwraps_to_nearest_branch():
    assert np.isclose(unwrap_angle(2.0 * np.pi - 0.1, 0.1), -0.1)
    assert np.isclose(unwrap_angle(-2.0 * np.pi + 0.2, -0.1), 0.2)


def test_homoclinic_pseudoarclength_checks_are_json_native():
    observed = native_boolean_checks(
        {"numpy_true": np.bool_(True), "numpy_false": np.bool_(False)}
    )
    assert observed == {"numpy_true": True, "numpy_false": False}
    assert all(type(value) is bool for value in observed.values())


def test_homoclinic_pseudoarclength_optionally_gates_jacobian_conditioning():
    singular_values = np.array([3.0, 2.0, 1e-9])
    assert jacobian_conditioning_accepted(singular_values, {})
    assert jacobian_conditioning_accepted(
        singular_values, {"minimum_jacobian_singular_value": 5e-10}
    )
    assert not jacobian_conditioning_accepted(
        singular_values, {"minimum_jacobian_singular_value": 2e-9}
    )


def test_homoclinic_pseudoarclength_reads_fixed_c_and_chained_sources():
    legacy = {
        "fixed_parameters": {"b": 0.2, "c": 10.3144},
        "final_variables": {"a": 0.1807, "angle": 2.28, "total_flight_time": 234.5},
    }
    chained = {
        "final_variables": {
            "a": 0.1805,
            "c": 10.3149,
            "angle": 2.281,
            "total_flight_time": 234.48,
        }
    }
    assert source_curve_values(legacy) == (0.1807, 10.3144, 2.28, 234.5)
    assert source_curve_values(chained) == (0.1805, 10.3149, 2.281, 234.48)


def test_homoclinic_pseudoarclength_binds_chained_angle_gauge():
    receipt = {"reference_parameters": {"a": 0.18, "b": 0.2, "c": 10.3}}
    gauge = source_angle_gauge(receipt, {}, fixed_b=0.2)
    assert (gauge.a, gauge.b, gauge.c) == (0.18, 0.2, 10.3)

    recovered = source_angle_gauge(
        {},
        {
            "angle_gauge_reference_parameters": {
                "a": 0.18069045562126884,
                "b": 0.2,
                "c": 10.3144,
            }
        },
        fixed_b=0.2,
    )
    assert recovered == RosslerParameters(
        a=0.18069045562126884, b=0.2, c=10.3144
    )


def test_homoclinic_pseudoarclength_directional_c_bound_enforces_forward_side():
    lower, upper = directional_c_bounds(10.0, 10.00015, 0.001, 1e-6)
    assert np.isclose(lower, 10.000001)
    assert np.isclose(upper, 10.00115)
    assert lower < 10.00015 < upper

    unconstrained = directional_c_bounds(10.0, 10.00015, 0.001, None)
    assert np.allclose(unconstrained, (9.99915, 10.00115))


def test_homoclinic_pseudoarclength_projects_closing_tangent_to_parameters():
    layout = pseudoarclength_layout(2)
    delta = np.arange(1.0, layout["variable_count"] + 1.0)
    scales = np.ones_like(delta)
    tangent = projected_arclength_tangent(delta, scales, layout, ("a", "c"))
    nonzero = np.flatnonzero(tangent)
    assert np.array_equal(nonzero, [layout["a_index"], layout["c_index"]])
    assert np.isclose(np.linalg.norm(tangent), 1.0)
    assert tangent[layout["angle_index"]] == 0.0


def test_homoclinic_pseudoarclength_physical_predictor_holds_nuisance_groups():
    layout = pseudoarclength_layout(2)
    delta = np.arange(1.0, layout["variable_count"] + 1.0)
    scales = np.ones_like(delta)
    tangent = projected_arclength_tangent(delta, scales, layout, ("a", "c"))
    current = np.arange(layout["variable_count"], dtype=np.float64)
    desired_c_increment = 0.25
    step = desired_c_increment / tangent[layout["c_index"]]
    predictor = current + step * tangent * scales

    assert np.allclose(
        predictor[: layout["node_size"]], current[: layout["node_size"]]
    )
    assert predictor[layout["time_index"]] == current[layout["time_index"]]
    assert predictor[layout["angle_index"]] == current[layout["angle_index"]]
    assert np.isclose(
        predictor[layout["c_index"]] - current[layout["c_index"]],
        desired_c_increment,
    )


def test_homoclinic_pseudoarclength_recovers_local_bordered_tangent():
    jacobian = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, -3.0]])
    scales = np.array([2.0, 0.5, 4.0])
    tangent, residual = local_tangent_from_matching_jacobian(
        jacobian, scales, direction_index=2
    )
    physical_tangent = scales * tangent

    assert np.isclose(np.linalg.norm(tangent), 1.0)
    assert tangent[2] > 0.0
    assert np.linalg.norm(jacobian @ physical_tangent) < 1e-12
    assert residual < 1e-12


def test_homoclinic_pseudoarclength_weights_closing_tangent_groups():
    layout = pseudoarclength_layout(2)
    delta = np.ones(layout["variable_count"])
    scales = np.ones_like(delta)
    tangent = weighted_arclength_tangent(
        delta,
        scales,
        layout,
        {
            "nodes": 0.01,
            "total_flight_time": 0.01,
            "a": 1.0,
            "c": 1.0,
            "angle": 0.01,
        },
    )
    groups = arclength_group_norms(tangent, layout)
    assert np.isclose(np.linalg.norm(tangent), 1.0)
    assert np.isclose(groups["a"], groups["c"])
    assert groups["a"] > 50.0 * groups["angle"]
    assert groups["nodes"] < 0.02


def test_homoclinic_pseudoarclength_rejects_negative_tangent_weight():
    layout = pseudoarclength_layout(2)
    with np.testing.assert_raises(ValueError):
        weighted_arclength_tangent(
            np.ones(layout["variable_count"]),
            np.ones(layout["variable_count"]),
            layout,
            {"a": -1.0},
        )


def test_homoclinic_pseudoarclength_exposes_sparse_optimizer_jacobian():
    dense = np.array([[1.0, 0.0], [2.0, 3.0]])
    observed = optimizer_jacobian(dense, "csr")
    assert isinstance(observed, csr_matrix)
    assert np.array_equal(observed.toarray(), dense)
    assert optimizer_jacobian(dense, "dense") is dense


def test_homoclinic_pseudoarclength_recovers_exact_warm_start_vector():
    layout = pseudoarclength_layout(2)
    receipt = {
        "segment_count": 2,
        "final_nodes": [[1.0, 2.0, 3.0]],
        "final_variables": {
            "total_flight_time": 4.0,
            "a": 5.0,
            "c": 6.0,
            "angle": 7.0,
        },
    }
    observed = receipt_state_vector(receipt, layout)
    assert np.array_equal(observed, np.arange(1.0, 8.0))


def test_homoclinic_pseudoarclength_sparse_newton_solves_square_system():
    def compute(point):
        residual = np.array([point[0] - 2.0, 2.0 * (point[1] + 1.0)])
        jacobian = np.array([[1.0, 0.0], [0.0, 2.0]])
        details = {
            "maximum_block_norm": abs(residual[0]),
            "arclength_residual": residual[1],
        }
        return residual, jacobian, details

    result = bounded_sparse_newton(
        compute,
        np.array([0.0, 0.0]),
        np.ones(2),
        np.array([-10.0, -10.0]),
        np.array([10.0, 10.0]),
        maximum_function_evaluations=4,
        maximum_block_residual=1e-12,
        maximum_arclength_residual=1e-12,
        armijo=1e-4,
        backtracking_factor=0.5,
        minimum_step_fraction=1e-6,
        boundary_fraction=0.99,
    )
    assert result.success
    assert result.status == 1
    assert np.allclose(result.x, [2.0, -1.0])
    assert result.newton_history[0]["accepted"]


def test_homoclinic_solution_parameters_support_fixed_a_intersection():
    fixed_c = solution_parameters("a", 0.1826, {"b": 0.2, "c": 10.3084})
    fixed_a = solution_parameters("c", 10.3171, {"a": 0.1798, "b": 0.2})
    assert (fixed_c.a, fixed_c.b, fixed_c.c) == (0.1826, 0.2, 10.3084)
    assert (fixed_a.a, fixed_a.b, fixed_a.c) == (0.1798, 0.2, 10.3171)


def test_homoclinic_node_bounds_are_source_centered():
    seed = np.array([[1.0, 2.0, 3.0], [-1.0, -2.0, -3.0]])
    lower, upper = node_bounds(seed, 0.25)
    assert np.allclose(lower, seed.ravel() - 0.25)
    assert np.allclose(upper, seed.ravel() + 0.25)


def test_homoclinic_matching_block_norms_preserve_segment_order():
    residual = np.array([3.0, 4.0, 0.0, 0.0, 0.0, 12.0])
    assert np.array_equal(block_norms(residual), np.array([5.0, 12.0]))


def test_homoclinic_split_seed_interleaves_midpoints_and_bound_nodes():
    source = np.array([[10.0, 11.0, 12.0], [20.0, 21.0, 22.0]])
    midpoints = np.array(
        [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
    )
    observed = interleave_split_nodes(source, midpoints)
    assert np.array_equal(
        observed,
        np.array(
            [
                [1.0, 2.0, 3.0],
                [10.0, 11.0, 12.0],
                [4.0, 5.0, 6.0],
                [20.0, 21.0, 22.0],
                [7.0, 8.0, 9.0],
            ]
        ),
    )


def test_generic_a_axis_preserves_fixed_b_and_c():
    manifest = {
        "scan_axis": "a",
        "fixed_parameters": {"b": 0.2, "c": 10.3084},
    }
    assert scan_axis(manifest) == "a"
    parameters = parameters_at(manifest, 0.181)
    assert (parameters.a, parameters.b, parameters.c) == (0.181, 0.2, 10.3084)


def test_shooting_norm_gate_converts_to_json_native_boolean():
    gate = np.linalg.norm(np.array([1e-5, 0.0, 0.0])) <= 2e-5
    assert type(gate) is np.bool_
    assert type(bool(gate)) is bool


def test_absolute_central_jacobian_uses_declared_normalized_steps():
    matrix = np.array([[2.0, -1.0, 0.5], [0.0, 3.0, -2.0], [1.0, 1.0, 1.0]])
    observed = absolute_central_jacobian(
        lambda point: matrix @ point,
        np.zeros(3),
        np.array([1e-3, 2e-3, 3e-3]),
    )
    assert np.allclose(observed, matrix)


def test_local_geometry_alignment_preserves_orientations():
    reference = RosslerParameters(0.1798, 0.2, 10.3084)
    _equilibrium, _values, stable, plane = eigenspaces(reference)
    equilibrium2, values2, stable2, plane2 = align_local_geometry(
        RosslerParameters(0.1798, 0.2, 10.3094), stable, plane
    )
    assert equilibrium2.shape == (3,)
    assert values2.shape == (3,)
    assert np.dot(stable, stable2) > 0.99
    assert np.linalg.det(plane2.T @ plane) > 0.99
    assert np.allclose(plane2.T @ plane2, np.eye(2))


def test_stable_targets_reach_matching_sphere():
    parameters = RosslerParameters(0.1798, 0.2, 10.3084)
    equilibrium, _values, stable, _plane = eigenspaces(parameters)
    manifest = {
        "matching_radius": 0.02,
        "stable_manifold": {
            "seed_radius": 1e-8,
            "maximum_backward_time": 10.0,
            "maximum_step": 0.005,
        },
        "solver": {"method": "DOP853", "rtol": 1e-10, "atol": 1e-12},
    }
    targets = stable_manifold_targets(parameters, equilibrium, stable, manifest)
    assert [target["branch_sign"] for target in targets] == [-1, 1]
    assert all(target["status"] == "completed" for target in targets)
    assert all(target["radius_residual"] < 1e-10 for target in targets)


def test_tangent_basis_is_orthonormal_and_tangent():
    equilibrium = np.array([0.1, -0.2, 0.3])
    target = equilibrium + np.array([0.01, -0.015, 0.02])
    basis = tangent_basis(target, equilibrium)
    radial = (target - equilibrium) / np.linalg.norm(target - equilibrium)
    assert np.allclose(basis.T @ basis, np.eye(2))
    assert np.allclose(basis.T @ radial, np.zeros(2))

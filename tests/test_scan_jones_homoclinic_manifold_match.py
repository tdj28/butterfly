import numpy as np

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
from scripts.solve_jones_homoclinic_single_shooting import SCHEMA as SHOOTING_SCHEMA


def test_manifold_match_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-homoclinic-manifold-match-scan-manifest.v1"
    assert SHOOTING_SCHEMA == "butterfly.jones-homoclinic-single-shooting-manifest.v1"


def test_generic_a_axis_preserves_fixed_b_and_c():
    manifest = {
        "scan_axis": "a",
        "fixed_parameters": {"b": 0.2, "c": 10.3084},
    }
    assert scan_axis(manifest) == "a"
    parameters = parameters_at(manifest, 0.181)
    assert (parameters.a, parameters.b, parameters.c) == (0.181, 0.2, 10.3084)


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

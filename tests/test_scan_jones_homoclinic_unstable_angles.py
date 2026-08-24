import numpy as np

from butterfly import RosslerParameters
from scripts.scan_jones_homoclinic_unstable_angles import SCHEMA, eigenspaces
from scripts.refine_jones_homoclinic_unstable_angles import (
    SCHEMA as REFINEMENT_SCHEMA,
    refinement_angles,
)


def test_homoclinic_scan_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-homoclinic-unstable-angle-scan-manifest.v1"


def test_eigenspaces_have_expected_dimensions_and_orthogonality():
    equilibrium, values, stable, plane = eigenspaces(RosslerParameters(0.1798, 0.2, 10.3084))
    assert equilibrium.shape == (3,)
    assert values.shape == (3,)
    assert stable.shape == (3,)
    assert plane.shape == (3, 2)
    assert np.isclose(np.linalg.norm(stable), 1.0)
    assert np.allclose(plane.T @ plane, np.eye(2))


def test_numpy_boolean_is_not_json_native_regression():
    value = np.float64(1.0) > 0.0
    assert type(value) is np.bool_
    assert type(bool(value)) is bool


def test_homoclinic_refinement_schema_is_versioned():
    assert REFINEMENT_SCHEMA == "butterfly.jones-homoclinic-unstable-angle-refinement-manifest.v1"


def test_refinement_grid_covers_window_and_includes_center():
    center = 4.352414822160859
    half_width = 2.0 * np.pi / 96.0
    angles = refinement_angles(center, half_width, 257)
    assert len(angles) == 257
    assert angles[0] == center - half_width
    assert angles[128] == center
    assert angles[-1] == center + half_width

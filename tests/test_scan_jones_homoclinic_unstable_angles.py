import numpy as np

from butterfly import RosslerParameters
from scripts.scan_jones_homoclinic_unstable_angles import SCHEMA, eigenspaces


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

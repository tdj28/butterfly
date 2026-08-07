import numpy as np
import pytest

from butterfly.basins import (
    BasinPlaneManifest,
    fit_uncertainty_exponent,
    initial_condition_grid,
)


def manifest_dict() -> dict:
    return {
        "schema": "butterfly.basin-plane-manifest.v1",
        "experiment_id": "TEST-BASIN",
        "parameters": {"a": 0.245, "b": 0.2, "c": 5.75},
        "plane": {
            "x": {"min": -1.0, "max": 1.0, "count": 2},
            "y": {"min": -2.0, "max": 2.0, "count": 3},
            "z": 0.0,
        },
        "integration": {
            "transient": 10.0,
            "observation_horizon": 20.0,
            "max_crossings": 4,
            "solver": {"method": "DOP853", "rtol": 1e-9, "atol": 1e-11, "max_step": 0.1},
        },
        "classifier": {"max_period": 16, "required_repeats": 4, "atol": 1e-6, "rtol": 1e-7},
    }


def test_basin_grid_is_x_major_y_minor() -> None:
    manifest = BasinPlaneManifest.from_dict(manifest_dict())
    grid = initial_condition_grid(manifest)
    assert [index for index, _ in grid] == list(range(6))
    assert grid[0][1] == (-1.0, -2.0, 0.0)
    assert grid[2][1] == (-1.0, 2.0, 0.0)
    assert grid[-1][1] == (1.0, 2.0, 0.0)


def test_uncertainty_exponent_recovers_known_power_law() -> None:
    epsilons = np.asarray([1.0, 0.5, 0.25, 0.125, 0.0625])
    resolved = np.full(len(epsilons), 100_000)
    uncertain = np.rint(resolved * 0.2 * np.sqrt(epsilons)).astype(int)

    result = fit_uncertainty_exponent(
        epsilons,
        uncertain,
        resolved,
        bootstrap_samples=500,
        bootstrap_seed=17,
    )

    assert result["alpha"] == pytest.approx(0.5, abs=0.002)
    assert result["r_squared"] > 0.999
    assert result["alpha_bootstrap_95_interval"][0] < 0.5
    assert result["alpha_bootstrap_95_interval"][1] > 0.5


def test_uncertainty_exponent_rejects_invalid_counts() -> None:
    with pytest.raises(ValueError, match="between zero and resolved"):
        fit_uncertainty_exponent(
            np.asarray([1.0, 0.5, 0.25]),
            np.asarray([2, 11, 2]),
            np.asarray([10, 10, 10]),
            bootstrap_samples=100,
        )

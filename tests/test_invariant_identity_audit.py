import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_a150_invariant_identity.py"
SPEC = importlib.util.spec_from_file_location("invariant_identity_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _row(y_count, z_count, y_interval, z_interval):
    def coordinate(count, interval, minimum, maximum):
        return {
            "source_minimum": minimum,
            "source_maximum": maximum,
            "robust_oracle": {
                "resolved": count is not None,
                "branch_count": count,
                "critical_point_intervals": [interval] if interval else [],
            },
        }

    return {
        "coordinates": {
            "y": coordinate(y_count, y_interval, -30.0, -10.0),
            "z": coordinate(z_count, z_interval, 0.0093, 0.0098),
        }
    }


def test_common_branch_count_requires_every_dataset_and_coordinate():
    coordinates = [{"name": "y"}, {"name": "z"}]
    rows = [
        _row(2, 2, (-21.1, -21.0), (0.00954, 0.00955)),
        _row(2, 2, (-21.0, -20.9), (0.00953, 0.00954)),
    ]
    assert MODULE._common_branch_count(rows, coordinates, {2, 3}) == 2
    rows[1]["coordinates"]["z"]["robust_oracle"]["branch_count"] = 3
    assert MODULE._common_branch_count(rows, coordinates, {2, 3}) is None


def test_critical_convergence_normalizes_across_datasets():
    coordinates = [{"name": "y"}, {"name": "z"}]
    rows = [
        _row(2, 2, (-21.1, -21.0), (0.00954, 0.00955)),
        _row(2, 2, (-21.0, -20.9), (0.00953, 0.00954)),
    ]
    result = MODULE._critical_convergence(rows, coordinates, 2)
    assert result["y"]["critical_point_intervals"] == [(-21.1, -20.9)]
    assert abs(result["y"]["maximum_normalized_critical_point_span"] - 0.01) < 1e-12
    assert abs(result["z"]["maximum_normalized_critical_point_span"] - 0.04) < 1e-12

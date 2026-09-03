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


def test_oracle_groups_can_treat_coarse_result_as_resolution_control():
    def variant(count, points):
        return {"resolved": True, "branch_count": count, "critical_points": points}

    coordinate = {
        "source_minimum": -30.0,
        "source_maximum": -10.0,
        "robust_oracle": {
            "variant_results": [
                variant(2, [-21.0]),
                variant(3, [-31.0, -21.0]),
                variant(3, [-30.9, -20.9]),
            ]
        },
    }
    rows = [
        {
            "id": "new-data",
            "coordinates": {"y": coordinate, "z": coordinate},
        }
    ]
    groups = [
        {"id": "coarse", "variant_indices": [0], "expected_branch_count": 2},
        {"id": "adequate", "variant_indices": [1, 2], "expected_branch_count": 3},
    ]
    acceptance = {
        "maximum_within_dataset_normalized_critical_span": 0.03,
        "maximum_across_dataset_normalized_critical_span": 0.04,
    }
    result = MODULE._oracle_group_evaluation(
        rows, [{"name": "y"}, {"name": "z"}], groups, acceptance, {}
    )
    assert result["coarse"]["passed"]
    assert result["adequate"]["passed"]

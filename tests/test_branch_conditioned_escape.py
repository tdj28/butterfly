from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace

import numpy as np


SCRIPT = Path(__file__).parents[1] / "scripts" / "qualify_branch_conditioned_escape.py"
SPEC = spec_from_file_location("branch_conditioned_escape", SCRIPT)
MODULE = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_kaplan_meier_rmst_handles_events_and_administrative_censoring():
    rmst, rows = MODULE._kaplan_meier([1.0, 3.0], [True, False], 3.0)

    assert rmst == 2.0
    assert MODULE._survival_at(rows, 0.5) == 1.0
    assert MODULE._survival_at(rows, 2.0) == 0.5


def test_logrank_detects_separated_capture_times():
    statistic, p_value = MODULE._logrank(
        np.arange(1.0, 11.0),
        np.ones(10, dtype=bool),
        np.arange(11.0, 21.0),
        np.ones(10, dtype=bool),
    )

    assert statistic > 10.0
    assert p_value < 0.01


def test_landmark_assignment_is_one_per_trajectory_and_excludes_prior_capture():
    result = SimpleNamespace(
        all_midpoint_trajectory_ids=np.asarray([0, 0, 1, 2, 3]),
        all_midpoint_times=np.asarray([6.0, 9.0, 8.0, 7.0, 7.0]),
        all_midpoint_states=np.asarray(
            [
                [0.0, -3.6, 0.0],
                [0.0, -3.5, 0.0],
                [0.0, -2.9, 0.0],
                [0.0, -2.0, 0.0],
                [0.0, -0.5, 0.0],
            ]
        ),
        capture_times=np.asarray([15.0, 18.0, np.nan, 9.0]),
        failed=np.zeros(4, dtype=bool),
    )

    samples = MODULE._landmark_samples(
        result,
        branch_definition={
            "axis": 1,
            "critical_intervals": [[-3.0, -2.8], [-1.0, -0.8]],
        },
        landmark=10.0,
        window=(5.0, 10.0),
        horizon=20.0,
    )

    np.testing.assert_array_equal(samples["trajectory_id"], [0, 1, 2])
    np.testing.assert_array_equal(samples["assignment_time"], [9.0, 8.0, 7.0])
    np.testing.assert_array_equal(samples["branch"], [0, -1, 1])
    np.testing.assert_array_equal(samples["duration"], [5.0, 8.0, 10.0])
    np.testing.assert_array_equal(samples["event"], [True, True, False])

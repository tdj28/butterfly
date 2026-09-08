import numpy as np
import pytest

from butterfly.transported_tangent import dominant_history
from scripts.audit_exp485_transported_tangent import independently_check_history, descriptive_metrics, audit


def test_independent_product_reconstruction():
    matrices = [np.array([[2., 1.], [.1*i, .001]]) for i in range(8)]
    assert max(independently_check_history(matrices, dominant_history(matrices))) < 1e-12


def test_wrong_endpoint_line_rejected():
    matrices = [np.diag([2., .1])]*8
    rows = dominant_history(matrices)
    rows[-1]["direction"] = [0., 1.]
    with pytest.raises(ValueError, match="direction"):
        independently_check_history(matrices, rows)


def test_wrong_singular_ratio_rejected():
    matrices = [np.diag([2., .1])]*8
    rows = dominant_history(matrices)
    rows[-1]["singular_ratio"] = .5
    with pytest.raises(ValueError, match="ratio"):
        independently_check_history(matrices, rows)


def test_wrong_completed_anchor_rejected(tmp_path):
    (tmp_path/"summary.json").write_text("{}")
    with pytest.raises(ValueError, match="anchor"):
        audit(tmp_path, "0"*64)


def summary_row(index, slope, defined=True):
    return dict(case="test", bin=index, global_seed_id=3, initial_state=[float(index), 0., .1],
        audit=dict(qualified=True, direction=dict(history_angles=dict(a=0., b=0.), solver_angles=[0.],
            projected=dict(DOP853=dict(graph_defined=defined, x_graph_derivative=slope,
                                      coordinate_partial=0.)))))


def test_descriptive_sign_changes_do_not_bridge_missing_slopes():
    rows = [summary_row(0, 1.), summary_row(1, None, False), summary_row(2, -1.)]
    result = descriptive_metrics(rows)["test"]
    assert result["descriptive_adjacent_sign_changes"] == []
    assert result["unreported_x_graph_bins"] == [1]
    assert result["distinct_seeds"] == 1


def test_adjacent_sign_changes_are_recorded_without_interpolation():
    result = descriptive_metrics([summary_row(0, 1.), summary_row(1, -2.)])["test"]
    assert result["descriptive_adjacent_sign_changes"] == [dict(bins=[0, 1], observed_x=[0., 1.], derivatives=[1., -2.])]

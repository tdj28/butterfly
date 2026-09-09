"""Synthetic layout/data guards; no experimental trajectories generated."""
from copy import deepcopy

import matplotlib
import pytest
from scripts import plot_exp503_joint_contact as plot


def synthetic_result():
    p = plot.public.run.load()
    rows = []
    for spec in p["stencil"]:
        value = [.002*spec["sign"]*spec["scale"],-.013+.0004*spec["sign"]*spec["scale"]]
        vectors = [dict(key=v["key"],value=value) for v in p["base_vectors"]]
        rows.append(dict(spec=spec,qualified=True,vectors=vectors))
    return dict(rows=rows,proposal=None)


def test_all_points_retained_and_input_unchanged():
    result = synthetic_result()
    before = deepcopy(result)
    data = plot.derive(result)
    assert result == before and len(data) == 9
    assert all(r["plotted"] and r["variants"] == 256 for r in data)
    assert all(r["minimum"] == r["maximum"] for r in data[1:])


def test_missing_matrix_is_listed_not_averaged_from_survivors():
    result = synthetic_result()
    result["rows"][0]["vectors"].pop()
    result["rows"][0]["qualified"] = False
    data = plot.derive(result)
    assert len(data) == 9 and not data[1]["plotted"] and data[1]["mean"] is None
    assert data[1]["variants"] == 255


def test_complete_nonfinite_matrix_rejected():
    result = synthetic_result()
    result["rows"][0]["vectors"][0]["value"] = [float('nan'),0.]
    with pytest.raises(ValueError,match="finite complete"):
        plot.derive(result)


def test_synthetic_layout_has_both_views_and_scope_text(tmp_path):
    with matplotlib.rc_context():
        figure = plot.draw(plot.derive(synthetic_result()),"SYNTHETIC LAYOUT CONTROL","Not an experimental result")
        assert len(figure.axes) == 2
        assert any("not confidence intervals" in text.get_text() for text in figure.texts)
        figure.savefig(tmp_path/"synthetic-layout.png",dpi=100)
        assert (tmp_path/"synthetic-layout.png").stat().st_size > 10000
        from matplotlib import pyplot as plt
        plt.close(figure)

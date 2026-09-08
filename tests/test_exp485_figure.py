import json

import pytest

from butterfly._paired_startup import sha256
from scripts.plot_exp485_transported_tangent import plot


def test_figure_rejects_wrong_anchor(tmp_path):
    path = tmp_path/"input.json"
    path.write_text("{}")
    with pytest.raises(ValueError, match="anchor"):
        plot(path, "0"*64, tmp_path/"figure")
    assert not (tmp_path/"figure").exists()


def test_figure_rejects_incomplete_grid(tmp_path):
    path = tmp_path/"input.json"
    path.write_text(json.dumps(dict(status="completed-audited", complete_grid_and_decision_replay=True, rows=[])))
    with pytest.raises(ValueError, match="grid"):
        plot(path, sha256(path), tmp_path/"figure")
    assert not (tmp_path/"figure").exists()

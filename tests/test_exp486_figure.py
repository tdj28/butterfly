import json
import math

import pytest

from butterfly._paired_startup import sha256
from scripts.plot_exp486_return_image_folds import plot, verify, FIGURE
from scripts import plot_exp486_return_image_folds as module


def test_known_failed_bracket_breaks_line_without_losing_points():
    values = module.broken_series([0., 1., 2.], [3., 4., 5.], [[0., 1.]])
    assert values[0] == 3. and math.isnan(values[1]) and values[2:] == [4., 5.]


def test_wrong_input_hash_rejected_before_output(tmp_path):
    source = tmp_path/"source.json"
    source.write_text("{}")
    with pytest.raises(ValueError, match="anchor"):
        plot(source, "0"*64, tmp_path/"figure")
    assert not (tmp_path/"figure").exists()


def test_incomplete_grid_rejected_before_output(tmp_path):
    source = tmp_path/"source.json"
    source.write_text(json.dumps(dict(experiment_id="EXP-486", status="completed-audited", complete_grid_and_decision_replay=True,
                                    families=[], rows=[])))
    with pytest.raises(ValueError, match="grid"):
        plot(source, sha256(source), tmp_path/"figure")
    assert not (tmp_path/"figure").exists()


def test_receipt_hash_failure(tmp_path):
    name = f"{FIGURE}.receipt.json"
    (tmp_path/name).write_text("{}")
    (tmp_path/f"{FIGURE}.index.json").write_text(json.dumps(dict(receipts={name: dict(sha256="0"*64, bytes=2)})))
    with pytest.raises(ValueError, match="receipt hash"):
        verify(tmp_path)


def test_missing_pdf_vector_output_fails_contract(tmp_path):
    name = f"{FIGURE}.receipt.json"
    (tmp_path/name).write_text(json.dumps(dict(outputs={})))
    (tmp_path/f"{FIGURE}.index.json").write_text(json.dumps(dict(receipts={name: dict(sha256=sha256(tmp_path/name), bytes=(tmp_path/name).stat().st_size)})))
    with pytest.raises(ValueError, match="output set"):
        verify(tmp_path)


@pytest.mark.parametrize("changed", ["input.json", "plot.py", "audit.py"])
def test_source_and_code_drift_fail_verification(tmp_path, monkeypatch, changed):
    monkeypatch.setattr(module, "ROOT", tmp_path)
    for name in ("input.json", "plot.py", "audit.py"):
        (tmp_path/name).write_text("original bytes")
    receipt = dict(data_source=dict(artifact="input.json", sha256=sha256(tmp_path/"input.json")),
        generator=dict(path="plot.py", sha256=sha256(tmp_path/"plot.py")),
        audit=dict(path="audit.py", sha256=sha256(tmp_path/"audit.py")),
        outputs={f"{FIGURE}.{suffix}": {} for suffix in ("png", "svg", "pdf")})
    name = f"{FIGURE}.receipt.json"
    (tmp_path/name).write_text(json.dumps(receipt))
    (tmp_path/f"{FIGURE}.index.json").write_text(json.dumps(dict(receipts={name:
        dict(sha256=sha256(tmp_path/name), bytes=(tmp_path/name).stat().st_size)})))
    (tmp_path/changed).write_text("changed bytes")
    with pytest.raises(ValueError, match="source/code bytes"):
        verify(tmp_path)

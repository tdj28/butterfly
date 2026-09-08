import json

import pytest

from butterfly._paired_startup import sha256
from scripts.plot_exp486_return_image_folds import plot, verify, FIGURE


def test_wrong_input_hash_rejected_before_output(tmp_path):
    source = tmp_path/"source.json"
    source.write_text("{}")
    with pytest.raises(ValueError, match="anchor"):
        plot(source, "0"*64, tmp_path/"figure")
    assert not (tmp_path/"figure").exists()


def test_incomplete_grid_rejected_before_output(tmp_path):
    source = tmp_path/"source.json"
    source.write_text(json.dumps(dict(status="completed-audited", complete_grid_and_decision_replay=True,
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

import json

import pytest

from scripts import plot_exp489_section_grazing as plot


SOURCE = plot.ROOT/"docs/experiments/receipts/EXP-489-section-grazing-result.json"


def test_all_cases_solvers_and_doses_retained():
    data = plot.derive(json.loads(SOURCE.read_bytes()))
    assert len(data) == 4
    assert sum(len(r["sides"]) for r in data) == 16
    assert sum(s["observed_roots"] for r in data for s in r["sides"]) == 16
    assert sum(s["observed_roots"] == 0 for r in data for s in r["sides"]) == 8


@pytest.mark.parametrize("missing",["case","solver","dose"])
def test_missing_observations_rejected(missing):
    result = json.loads(SOURCE.read_bytes())
    if missing == "case":
        result["cases"].pop()
    elif missing == "solver":
        result["cases"][0]["solvers"].pop()
    else:
        result["cases"][0]["solvers"][0]["sides"].pop()
    with pytest.raises(ValueError):
        plot.derive(result)


def test_render_and_receipt_drift_guard(tmp_path):
    out = tmp_path/"figure"
    plot.plot(SOURCE,plot.sha256(SOURCE),out)
    assert plot.verify(out)
    path = out/(plot.FIGURE+".png")
    with path.open("ab") as stream:
        stream.write(b"tamper")
    with pytest.raises(ValueError,match="output bytes"):
        plot.verify(out)


def test_source_anchor_required(tmp_path):
    with pytest.raises(ValueError,match="source receipt"):
        plot.plot(SOURCE,"0"*64,tmp_path/"unused")

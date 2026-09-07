"""Post-run summary controls; no research artifacts, ODEs or SSH calls."""
import copy

import pytest

from scripts import summarize_exp481_qualification as report


def comparison(passed, error):
    return dict(left="coarse", right="reference", passed=passed,
        capture_membership_agrees=True, sections={"one": dict(left_raw_count=3,
            right_raw_count=3, left_accepted_count=2, right_accepted_count=2,
            maximum_scaled_state_difference=error, maximum_time_difference=1e-8)})


def test_summary_preserves_failures_and_maxima_not_just_the_best_seed():
    rows=[comparison(True,1e-6),comparison(False,1e-2)]
    before=copy.deepcopy(rows)
    result=report.comparison_summary(rows)
    assert rows==before
    assert result==[dict(left="coarse",right="reference",passed=1,total=2,
        maximum_scaled_state_difference=1e-2,maximum_time_difference=1e-8,
        capture_mismatches=0,count_mismatches=0)]


def test_summary_does_not_turn_missing_errors_or_count_mismatch_into_zero():
    row=comparison(False,None)
    row["sections"]["one"]["maximum_time_difference"]=None
    row["sections"]["one"]["right_raw_count"]=4
    row["capture_membership_agrees"]=False
    result=report.comparison_summary([row])[0]
    assert result["maximum_scaled_state_difference"] is None
    assert result["maximum_time_difference"] is None
    assert result["count_mismatches"]==result["capture_mismatches"]==1
    assert result["passed"]==0


def test_changed_run_anchor_fails_before_input_loading(tmp_path,monkeypatch):
    (tmp_path/"receipt.json").write_text("{}")
    monkeypatch.setattr(report,"RUN",tmp_path)
    monkeypatch.setattr(report,"ANCHORS",{"receipt.json":"0"*64})
    def forbidden(*args,**kwargs):
        pytest.fail("inputs loaded after an invalid frozen outcome anchor")
    monkeypatch.setattr(report,"load_package",forbidden)
    with pytest.raises(ValueError,match="anchor"):
        report.audit()

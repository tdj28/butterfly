"""Support display and completed-run report checks, without real research data."""
import numpy as np
import pytest
from scripts import summarize_exp482_maps as report


def test_repeated_pairs_do_not_become_independent_seeds():
    pairs=np.array([[[.1,.2],[.1,.2]],[[.1,.3],[.9,.2]]])
    assert report.support_counts(pairs,np.array([10,11]),[0,1],2).tolist()==[2,1]


def test_support_count_includes_endpoints_without_dropping_upper_bin():
    pairs=np.array([[[0.,.1]],[[1.,.2]]])
    assert report.support_counts(pairs,np.array([2,3]),[0,1],4).tolist()==[1,0,0,1]


def test_wrong_campaign_anchor_stops_before_inputs(tmp_path,monkeypatch):
    (tmp_path/"campaign").mkdir()
    (tmp_path/"campaign/receipt.json").write_text("{}")
    monkeypatch.setattr(report,"RUN",tmp_path)
    def forbidden(*a,**k): pytest.fail("invalid campaign reached input loading")
    monkeypatch.setattr(report,"load_package",forbidden)
    with pytest.raises(ValueError,match="anchor"): report.audit()


def test_summary_preserves_unavailable_metrics_and_does_not_use_diagnostic_rescue():
    failed=dict(bins=40,smoothing=1e-5,resolved=False,reason="unsupported interior gap",coverage=.8)
    diagnostic=dict(failed,resolved=True,reason="resolved finite-resolution scalar map",heldout_q90_error=.01)
    analysis=dict(cases={"case":dict(cohort=dict(retained=[True,False],calibration_seeds=1),analysis=dict(
        joint_primary=dict(resolved=False),critical_matrix=dict(status="not-evaluated"),projections=[
            dict(role="primary",projection=dict(section="historical-negative",axis=0),
                audits={"profile/window-0":dict(calibration_bounds=[-12,0],variants=[failed])}),
            dict(role="diagnostic",projection=dict(section="historical-negative",axis=2),
                audits={"profile/window-0":dict(calibration_bounds=[0,1],variants=[diagnostic])})]))})
    result=report.compact_result(analysis)["case"]
    assert not result["joint_primary"]["resolved"] and len(result["variants"])==2
    assert result["variants"][0]["heldout_q90_error"] is None
    assert result["variants"][1]["heldout_q90_error"]==.01
    assert result["primary_failure_counts"]=={"unsupported interior gap":1}

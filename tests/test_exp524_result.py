"""Recovery claims remain bound to an access-controlled completed receipt."""
import pytest
from scripts import verify_exp524_result as verify


def test_public_calibration_receipt_and_scalar_rederivation():
    if not (verify.audit.ROOT/verify.RECEIPT).is_file():
        pytest.skip('Access-controlled EXP-524 receipt not distributed with source; run on the evidence host.')
    r = verify.verify()
    assert r['audit_passed'] and r['calibration_qualified']
    assert r['complete_points'] == 8 and r['audited_ivps'] == 864
    assert r['maximum_fold_curvature_error'] < .05
    assert r['maximum_gap_curvature_error'] < .05
    assert not r['symbolic_chains_verified'] and not r['incomplete_predictor_scientifically_audited']


def test_substituted_receipt_rejected(tmp_path):
    p = tmp_path/'false.json'; p.write_text('{"passed":true}')
    with pytest.raises(ValueError, match='fixed completed'): verify.verify(p)

"""Post-run verification does not alter the frozen experiment or need public data."""
import pytest
from scripts import verify_exp525_result as verify


def test_failure_record_blocks_interpretation(tmp_path):
    (tmp_path/'failure.json').write_text('{}')
    with pytest.raises(ValueError, match='failure record'):
        verify.verify(tmp_path)


def test_substituted_audit_rejected(tmp_path):
    (tmp_path/'audit.json').write_text('{"passed":true}')
    with pytest.raises(ValueError, match='fixed completed evidence'):
        verify.verify(tmp_path)


def test_private_completed_evidence():
    if not (verify.DEFAULT/'audit.json').is_file():
        pytest.skip('Private research evidence is not distributed with public source.')
    report = verify.verify()
    assert report['authenticated'] and report['new_integrations'] == 0
    assert report['raw_files'] > 0 and not report['symbolic_chains_verified']

"""Artifact-free complete-schema and original-prefix replay controls."""
from copy import deepcopy
import json
from unittest.mock import patch

import numpy as np
import pytest
from scripts import run_exp506_legacy_continuation as run
from tests.test_exp505_legacy_impact import synthetic_manifest


@pytest.mark.parametrize('resolved,word,targets,matches',[
    (True,'010',['001'],['001']),(True,'010',['111'],[]),(False,None,['001'],[])])
def test_complete_word_schema_preserves_raw_result(resolved,word,targets,matches):
    raw = dict(resolved=resolved,raw_word=word,reason='synthetic fixture')
    before = deepcopy(raw)
    result = run.complete_word(raw,targets)
    assert raw == before
    assert all(result[k] == v for k,v in raw.items())
    assert result['cyclic_target_matches'] == matches
    assert result['target_membership_passed'] is (len(matches)==1)
    assert set(result)-set(raw) == {'target_comparisons','cyclic_target_matches','reversal_only_target_matches','target_membership_passed'}


def test_published_historical_word_summary_is_not_a_target_match():
    p = run.ROOT/'docs/experiments/receipts/EXP-186.json'
    receipt = json.loads(p.read_bytes())
    for key in ('dt_0.01_DOP853_Radau','dt_0.005_DOP853_Radau'):
        result = run.complete_word(dict(resolved=True,raw_word=receipt['x_words'][key]),receipt['target_words'])
        assert result['cyclic_target_matches'] == receipt['x_words']['target_matches'] == []
        assert result['reversal_only_target_matches'] == receipt['x_words']['reversal_only_target_matches'] == []


def test_all_255_prefix_fits_replayed_without_any_new_spline(monkeypatch):
    source = np.linspace(0,1,500)
    target = -(source-.5)**2
    manifest = synthetic_manifest()
    manifest['oracle_common']['bootstrap_samples'] = 50
    saved = []
    expected = run.old.oracle(source,target,manifest,'original',saved)
    assert len(saved) == 255
    monkeypatch.setattr(run,'original',lambda:({}, {},dict(fits=saved)))
    def forbidden(*args,**kwargs):
        raise AssertionError('prefix replay must not construct a spline')
    trace = []
    with patch.object(run.old.legacy,'UnivariateSpline',forbidden):
        actual = run.replay_prefix(source,target,manifest,trace)
    assert actual == expected and trace == saved


def test_wrong_prefix_sample_rejected_before_substitution(monkeypatch):
    source = np.linspace(0,1,500)
    manifest = synthetic_manifest()
    saved = []
    run.old.oracle(source,-(source-.5)**2,manifest,'original',saved)
    saved[0]['sample_sha256'] = '0'*64
    monkeypatch.setattr(run,'original',lambda:({}, {},dict(fits=saved)))
    with pytest.raises(ValueError,match='sample/fit'):
        run.replay_prefix(source,-(source-.5)**2,manifest,[])


def test_adapter_restored_after_forced_analysis_failure(monkeypatch):
    originals = (run.old.oracle,run.old.historical._word_row,run.old.historical.UnivariateSpline)
    monkeypatch.setattr(run,'targets',lambda:['001'])
    def fail(*args,**kwargs):
        assert run.old.historical._word_row is not originals[1]
        raise RuntimeError('synthetic failure')
    monkeypatch.setattr(run.old,'analyze',fail)
    with pytest.raises(RuntimeError,match='synthetic'):
        run.analyze()
    assert (run.old.oracle,run.old.historical._word_row,run.old.historical.UnivariateSpline) == originals


def test_public_plan_preserves_old_attempt_and_fit_accounting():
    p = json.loads(run.PLAN.read_bytes())
    assert p['original_attempt_reset'] is False and p['target_integrations'] == 0
    assert p['reused_branch_fits'] == 255
    assert p['original_failure_sha256'] == 'f025767950859ec7846dbaea96a4374fac4137a0989e429332bfcabf2cc7b29c'

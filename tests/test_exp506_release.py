"""Compact public release distinguishes numerical replay from protocol compliance."""
import json
from pathlib import Path

from butterfly._paired_startup import sha256

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT/'docs/experiments/receipts/EXP-506-legacy-turning-impact-result.json'


def test_complete_public_result_has_unchanged_scientific_outputs():
    assert sha256(RESULT) == '4de5d276e8a74b97c31a0bc3eb636da8815c6f685c442b3df2a7325a275a9f32'
    r = json.loads(RESULT.read_bytes())
    assert r['numerical_replay_passed'] is True
    assert len(r['rows']) == 4
    assert r['reused_branch_fits']+r['new_branch_fits'] == r['audit_branch_fit_evaluations'] == 2040
    assert r['audit_word_spline_evaluations'] == 40
    assert all(x['robust_unchanged'] and x['words_unchanged'] for x in r['rows'])
    assert sum(x['removed_root_occurrences'] for x in r['rows']) == 0
    assert sum(x['modes']['original']['retained_root_occurrences'] for x in r['rows']) == 510
    assert all(x['modes']['original']['robust'] == x['modes']['filtered']['robust'] for x in r['rows'])
    assert all(x['modes']['original']['words'] == x['modes']['filtered']['words'] for x in r['rows'])


def test_full_output_cap_deviation_is_not_hidden_by_numerical_pass():
    r = json.loads(RESULT.read_bytes())
    q = r['resource']
    assert r['protocol_compliant'] is False and q['compliant'] is False
    assert q['pre_summary_bytes']+q['summary_bytes'] == q['output_bytes_including_summary'] == 124055116
    assert q['output_limit_bytes'] == 104857600
    assert q['excess_bytes'] == 19197516
    assert r['symbolic_chains_verified'] is False
    assert r['original_attempt_reset'] is False and r['target_integrations'] == 0
    assert r['full_trajectory_audit_repeated'] is False


def test_saved_word_failures_are_preserved_not_relabelled_as_jones_verification():
    r = json.loads(RESULT.read_bytes())
    old = json.loads((ROOT/'docs/experiments/receipts/EXP-186.json').read_bytes())
    assert [row['modes']['original']['robust']['branch_count'] for row in r['rows']] == [2,1,2,1]
    x = [row for row in r['rows'] if row['coordinate'] == 'x']
    assert [row['modes']['original']['words'][0]['raw_word'] for row in x] == [
        old['x_words']['dt_0.01_DOP853_Radau'],old['x_words']['dt_0.005_DOP853_Radau']]
    assert all(not word['target_membership_passed'] for row in r['rows'] for mode in row['modes'].values() for word in mode['words'])

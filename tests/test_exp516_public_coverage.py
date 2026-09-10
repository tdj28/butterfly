from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from scripts import exp516_ordinal_coverage as screen
from scripts import audit_exp516_ordinal_coverage as audit
from scripts import render_exp516_ordinal_coverage as figure

RECEIPT = 'docs/experiments/receipts/EXP-516-event-ordinal-coverage-result.json'
SHA = '45b8dd88ee0cab27d4eba7ec4c4891afdd6948ddaa83c110017ed26ac012a445'


def test_complete_public_matrix_and_unchanged_old_decisions():
    result = audit.audit(screen.ROOT/RECEIPT, SHA)
    assert result['counts'] == dict(profiles=80, accepted_events=740, retained_pairs=660,
        terminal_events_without_successor=80, fixed_ordinal_decisions_preserved=40,
        paired_ordinal_cells=330, missing_ordinal_cells=70, regular_cells=277,
        coverage_cells=0, endpoint_candidate_cells=11, full_state_reference_distances=5280)
    data = figure.plot_data(json.loads((screen.ROOT/RECEIPT).read_bytes()))
    assert sum(len(p['cells']) for p in data) == 400
    assert sum(c['distance'] is None for p in data for c in p['cells']) == 70
    assert not any(c['sampled_coverage'] for p in data for c in p['cells'])


@pytest.mark.parametrize('kind', ['omit-direction', 'omit-node', 'omit-ordinal', 'omit-method',
    'state', 'distance', 'regularity', 'coverage', 'candidate', 'terminal', 'source', 'claim'])
def test_semantic_tamper_even_with_changed_receipt_hash(tmp_path, kind):
    value = json.loads((screen.ROOT/RECEIPT).read_bytes())
    row = value['analysis']['rows'][0]
    comparison = row['ordinals'][7]['nodes'][8]['comparison']
    if kind == 'omit-direction': value['analysis']['rows'].pop()
    elif kind == 'omit-node': row['samples'].pop()
    elif kind == 'omit-ordinal': row['ordinals'].pop()
    elif kind == 'omit-method': comparison['methods'].pop()
    elif kind == 'state': comparison['methods'][0]['input']['state'][2] += .01
    elif kind == 'distance': comparison['joint_distance'] = 0.
    elif kind == 'regularity': comparison['paired_regular'] = not comparison['paired_regular']
    elif kind == 'coverage': comparison['sampled_reference_coverage'] = True
    elif kind == 'candidate': row['ordinals'][0]['cells'][0]['endpoint_candidate'] = True
    elif kind == 'terminal': row['samples'][0]['profiles'][0]['last_event'] = None
    elif kind == 'source': value['sources'][screen.SOURCES[0]] = '0'*64
    elif kind == 'claim': value['analysis']['symbolic_chains_verified'] = True
    path = tmp_path/'changed.json'
    path.write_bytes(screen.encode(value))
    with pytest.raises(ValueError):
        screen.verify(path, screen.sha(path))


def test_actual_isolated_public_replay_from_nine_files(tmp_path):
    names = set(screen.SOURCES) | set(screen.INPUTS) | {RECEIPT, 'scripts/audit_exp516_ordinal_coverage.py'}
    assert len(names) == 9
    for name in names:
        dest = tmp_path/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(screen.ROOT/name, dest)
    reply = subprocess.run([sys.executable, '-I', '-B', str(tmp_path/'scripts/exp516_ordinal_coverage.py'),
        '--verify', str(tmp_path/RECEIPT), '--expected-sha256', SHA], cwd=tmp_path,
        capture_output=True, text=True, check=True, timeout=30)
    assert json.loads(reply.stdout)['passed']
    assert not (tmp_path/'artifacts').exists()
    assert not list(tmp_path.rglob('*.pyc'))
    assert all(screen.sha(tmp_path/n) == screen.sha(screen.ROOT/n) for n in names)


@pytest.mark.parametrize('kind', ['negative', 'nonfinite', 'missing', 'zero'])
def test_figure_never_silently_drops_a_cell(kind):
    value = json.loads((screen.ROOT/RECEIPT).read_bytes())
    value = deepcopy(value)
    row = value['analysis']['rows'][0]['ordinals'][0]
    if kind == 'missing': row['nodes'].pop()
    else: row['nodes'][0]['comparison']['joint_distance'] = {'negative': -1., 'nonfinite': float('nan'), 'zero': 0.}[kind]
    if kind == 'zero':
        data = figure.plot_data(value)
        assert data[0]['cells'][0]['distance'] == 0.
    else:
        with pytest.raises(ValueError): figure.plot_data(value)

"""Analytic event-algebra/screen controls; these synthetic rows are not IVPs."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from scripts import exp516_ordinal_coverage as screen

PARAMETERS = dict(a=.2, b=.2, c=5.)


def event(t, tangent=(1., 0., 0.), q=(-2., 0., .01)):
    f = screen.field(q, PARAMETERS)
    return dict(time=t, state=list(q), raw_tangent=list(tangent), accepted=q[0] < 0 and f[1] < 0,
        angle=abs(f[1])/screen.math.hypot(*f), residual=q[1], normal_velocity=f[1])


def profile(events=None, uncertain=()):
    events = events or [event(1.), event(2.), event(3.)]
    return dict(status='completed', method='DOP853', report=dict(method='DOP853',
        reconstructed=events, uncertain_extrema=list(uncertain), guard=1e-8, horizon=4.))


def observed(**kwargs):
    return screen.observations(profile(**kwargs), PARAMETERS, 0., 0.)


def targets():
    return [dict(image_state=[-2., 0., .01], next_state=[-2., 0., .01]) for _ in range(4)]


def test_exact_phase_correction_and_small_remainder():
    f = [1., -1., 0.]
    assert screen.corrected(f, f) == [0., 0., 0.]
    assert screen.corrected([1., -1., 1e-14], f) == [0., 0., 1e-14]
    assert screen.corrected([1., 0., 0.], f) == [1., 0., 0.]
    with pytest.raises(ValueError):
        screen.corrected([1., 0., 0.], [1., 0., 0.])


def test_every_ordinal_and_terminal_censoring():
    row = observed()
    assert [r['ordinal'] for r in row['pairs']] == [1, 2]
    assert row['last_event']['time'] == 3
    assert row['horizon'] == 4
    assert screen.compare([row, row], 1, targets())['sampled_reference_coverage']
    assert screen.compare([row, row], 2, targets())['sampled_reference_coverage']
    missing = screen.compare([row, observed(events=[event(1.), event(2.)])], 2, targets())
    assert missing['reason'] == 'missing ordinal'
    assert missing['joint_distance'] is None
    assert missing['methods'][0] is not None and missing['methods'][1] is None


def test_rejected_crossings_do_not_increment_ordinal():
    row = observed(events=[event(1.), event(1.5, q=(2., 0., .01)), event(2.)])
    assert len(row['events']) == 2
    assert len(row['pairs']) == 1
    assert row['pairs'][0]['output']['time'] == 2


@pytest.mark.parametrize('kind', ['gain', 'projection', 'uncertain', 'early-invalid'])
def test_invalid_inputs_and_prefix_are_not_qualified(kind):
    p = profile()
    if kind == 'gain':
        p['report']['reconstructed'][0] = event(1., tangent=(1e-8, 0., 0.))
    elif kind == 'projection':
        p['report']['reconstructed'][0] = event(1., tangent=(1e-8, 0., 1.))
    elif kind == 'uncertain':
        p['report']['uncertain_extrema'] = [dict(time=.5)]
    else:
        p['report']['reconstructed'][0] = event(1., q=(-2., 1e-7, .01))
    row = screen.observations(p, PARAMETERS, 0., 0.)
    assert not row['pairs'][0]['regular']
    pair = screen.compare([row, row], 1, targets())
    assert not pair['paired_regular']
    assert pair['joint_distance'] is not None  # Never hide invalid coverage.
    if kind in ('uncertain', 'early-invalid'):
        assert not row['pairs'][1]['regular']


@pytest.mark.parametrize('kind', ['accepted', 'angle', 'velocity', 'residual', 'ordering', 'nonfinite'])
def test_census_algebra_tamper_rejected(kind):
    p = profile()
    e = p['report']['reconstructed'][0]
    if kind == 'accepted': e['accepted'] = False
    elif kind == 'angle': e['angle'] = 0.
    elif kind == 'velocity': e['normal_velocity'] = 0.
    elif kind == 'residual': e['residual'] = 1.
    elif kind == 'ordering': e['time'] = 3.
    elif kind == 'nonfinite': e['raw_tangent'][0] = float('nan')
    with pytest.raises(ValueError):
        screen.observations(p, PARAMETERS, 0., 0.)


@pytest.mark.parametrize('kind', ['time', 'state', 'tangent', 'slope'])
def test_paired_disagreements_retained(kind):
    a = observed()
    b = deepcopy(a)
    if kind == 'time': b['events'][0]['time'] += 1e-3
    elif kind == 'state': b['events'][0]['state'][2] += 1e-3
    elif kind == 'tangent': b['pairs'][0]['input']['tangent'][2] += 1e-3
    elif kind == 'slope': b['pairs'][0]['slope'] += 1e-3
    r = screen.compare([a, b], 1, targets())
    assert not r['paired_regular']
    assert not r['sampled_reference_coverage']


def test_full_state_all_references_and_both_endpoints():
    row = observed()
    for key in ('image_state', 'next_state'):
        refs = targets()
        refs[3][key][2] += .01
        r = screen.compare([row, row], 1, refs)
        assert r['paired_regular']
        assert r['joint_distance'] == 1.
        assert not r['sampled_reference_coverage']


def test_strict_endpoint_nomination_never_claims_continuity():
    a = observed(events=[event(1.), event(2., tangent=(-1., 0., 0.))])
    b = observed(events=[event(1.), event(2.)])
    left, right = [screen.compare([r, r], 1, targets()) for r in (a, b)]
    value = screen.cell(left, right)
    assert value['endpoint_candidate']
    assert not value['interior_continuity_certified']
    assert not value['fold_qualified']
    right['methods'][0]['slope'] = 0.
    assert not screen.cell(left, right)['endpoint_candidate']
    right['ordinal'] = 2
    with pytest.raises(ValueError, match='different ordinals'):
        screen.cell(left, right)


def test_minima_preserve_ties_and_invalid_nodes():
    rows = [dict(node=i, comparison=dict(joint_distance=v, paired_regular=g))
            for i, (v, g) in enumerate([(1., False), (2., True), (2., True), (None, False)])]
    assert screen.minima(rows) == dict(distance=1., nodes=[0])
    assert screen.minima(rows, True) == dict(distance=2., nodes=[1, 2])
    assert screen.minima(rows[-1:]) is None


def test_quota_and_nonfinite_json_fail_before_write(monkeypatch):
    with pytest.raises(ValueError): screen.encode(dict(value=float('nan')))
    monkeypatch.setattr(screen, 'LIMIT', 2)
    with pytest.raises(ValueError, match='cap'): screen.encode(dict(value='over budget'))


def test_actual_isolated_cli_without_raw_or_numerical_libraries(tmp_path):
    for name in set(screen.SOURCES) | set(screen.INPUTS):
        dest = tmp_path/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(screen.ROOT/name, dest)
    path = tmp_path/'scripts/exp516_ordinal_coverage.py'
    reply = subprocess.run([sys.executable, '-I', '-B', str(path)], cwd=tmp_path,
                           capture_output=True, text=True, check=True, timeout=30)
    assert json.loads(reply.stdout) == dict(valid=True, directions=2, profiles=80, new_integrations=0)
    assert not (tmp_path/'artifacts').exists()
    assert not list(tmp_path.rglob('*.pyc'))
    # Import the copied script directly, without the developer repository.
    spec = importlib.util.spec_from_file_location('isolated_screen', path)
    copied = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copied)
    assert copied.ROOT == tmp_path
    assert set(copied.INPUTS) == set(screen.INPUTS)


def test_cli_refuses_unanchored_public_verification(tmp_path):
    reply = subprocess.run([sys.executable, '-I', '-B', str(Path(screen.__file__)),
                            '--verify', str(tmp_path/'absent.json')], capture_output=True, text=True)
    assert reply.returncode == 2
    assert 'published receipt SHA-256' in reply.stderr

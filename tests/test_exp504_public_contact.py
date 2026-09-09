"""Public reconstruction controls using the already audited EXP-503 fixture."""
from copy import deepcopy
import hashlib
import json

import pytest
from scripts import verify_exp504_public_contact as public
from scripts import plot_exp504_contact_path as figure


def count_for(row,old):
    data = (json.dumps(row,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    return dict(old,point_sha256=hashlib.sha256(data).hexdigest())


def test_compact_point_check_replays_the_existing_audited_fixture():
    old = public.run.inputs()
    public.check_point(old['proposal'],public.run.base.load(),old['point_counts'][-1])


@pytest.mark.parametrize('kind',['fold-gate','cycle-gate','boundary-gate','residual','duplicate-fold','wrong-count'])
def test_rehashed_compact_point_corruption_rejected(kind):
    old = public.run.inputs()
    point = deepcopy(old['proposal'])
    if kind == 'fold-gate':
        point['folds'][0]['qualified_in_region'] = False
    elif kind == 'cycle-gate':
        point['cycle']['status'] = 'unqualified'
    elif kind == 'boundary-gate':
        point['boundaries'][0]['comparison']['qualified'] = False
    elif kind == 'residual':
        point['vectors'][0]['value'][1] += .1
    elif kind == 'duplicate-fold':
        point['folds'][-1] = deepcopy(point['folds'][0])
    else:
        point['cycle']['profiles'][0]['metric']['windows'][0]['counts']['historical'] = 7
    count = count_for(point,old['point_counts'][-1])
    with pytest.raises(ValueError):
        public.check_point(point,public.run.base.load(),count)


def test_public_hash_checked_before_receipt_interpretation(tmp_path):
    path = tmp_path/'bad.json'
    public.run.write_json(path,{})
    with pytest.raises(ValueError,match='hash'):
        public.verify(path,'0'*64)


def test_figure_retains_rejected_points_and_start():
    old = public.run.inputs()['proposal']
    saved = dict(result=dict(steps=[dict(point=old,decision=dict(accepted=False,reason='synthetic rejection'))]))
    rows = figure.derive(saved)
    assert len(rows) == 2 and rows[0]['number'] == 0
    assert rows[1]['accepted'] is False
    assert rows[0]['fold_distance'] < 1e-4 < rows[0]['boundary_distance']


def test_figure_labels_use_full_state_not_signed_coordinate_residual():
    saved = dict(result=dict(steps=[]))
    fig = figure.draw(figure.derive(saved),dict(joint_proximity=False))
    assert len(fig.axes) == 2
    assert fig.axes[1].get_yscale() == 'log'
    assert 'Worst distance' in fig.axes[1].get_ylabel()
    import matplotlib.pyplot as plt
    plt.close(fig)

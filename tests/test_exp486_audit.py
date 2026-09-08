import copy
import json

import pytest

from butterfly.poincare import PoincareSection
from butterfly.return_image_curve import image_returns
from scripts import audit_exp486_return_image_folds as audit
from scripts import run_exp486_return_image_folds as run


@pytest.fixture
def trial():
    plan = json.loads(run.PLAN.read_bytes())
    section = PoincareSection((0., 1., 0.), 0., -1)
    value = image_returns(*run.control_field(), [-4., 0., .5], [1., 0., 1.], section,
                          count=5, **run.solver_options(plan))
    return value, section, plan


def check(trial):
    value, section, plan = trial
    return audit.check_trial(value, [-4., 0., .5], [1., 0., 1.], section,
                             "DOP853", 5, plan, run.control_field()[0])


def test_separate_event_algebra(trial):
    assert check(trial) < 1e-12


@pytest.mark.parametrize("field", ["tangent", "valid", "time", "section_residual"])
def test_corrupted_event_rejected(trial, field):
    value, section, plan = copy.deepcopy(trial)
    event = value["events"][1]
    if field == "tangent":
        event[field][0] += .1
    elif field == "valid":
        event[field] = False
    elif field == "time":
        event[field] = 0.
    else:
        event[field] = .1
    with pytest.raises(ValueError):
        check((value, section, plan))


def test_independent_brackets_include_exact_zero_but_not_projection_turn():
    def row(slope, v=1):
        return dict(valid=True, x_graph_slope=slope, input_x_tangent=v)
    assert audit.separate_brackets([row(1), row(0), row(-1)]) == [[0, 2]]
    assert audit.separate_brackets([row(1), row(-1, -1)]) == []

"""An even quadratic term can evade a central first-derivative consistency test."""
from copy import deepcopy
import pytest
from scripts import diagnose_exp521_curvature as diagnostic
from scripts import exp521_critical_response as model
from tests.test_exp521_critical_response import fixture


def test_symmetric_curvature_explains_a_linear_prediction_failure_without_reclassifying_it():
    source, measure = fixture()
    def quadratic(spec):
        p = measure(spec); dc = (spec['parameters']['c']-source['anchor']['c'])/.005
        for v in p['vectors']: v['residual'][2] += 2e-6*dc**2
        return p
    result = model.follow(source, quadratic)
    assert result['response']['qualified'] and not result['decision']['qualified']
    assert all(v['distance'] < 1e-4 for v in result['decision']['folds'])
    rows = diagnostic.calculate(source['vectors'], result['points'], result['correction'], result['proposal'])
    assert len(rows) == 16 and max(r['unexplained_fraction'] for r in rows) < 1e-8
    assert max(r['curvature_relative_disagreement'] for r in rows) < 1e-8
    assert not result['decision']['qualified']


@pytest.mark.parametrize('kind', ['missing', 'order', 'parameter', 'nonfinite'])
def test_diagnostic_does_not_silently_select_a_favorable_stencil(kind):
    source, measure = fixture(); result = model.follow(source, measure)
    points = deepcopy(result['points'])
    if kind == 'missing': points.pop()
    elif kind == 'order': points.reverse()
    elif kind == 'parameter': points[0]['spec']['parameters']['c'] += .01
    else: points[0]['vectors'][0]['residual'][0] = float('nan')
    with pytest.raises(ValueError):
        diagnostic.calculate(source['vectors'], points, result['correction'], result['proposal'])

import numpy as np
import pytest

from scripts.analyze_exp494_shorter_cycles import shorter_metric
from test_periodic_winding import circle


@pytest.mark.parametrize("method",["DOP853","Radau"])
@pytest.mark.parametrize("multiplicity",[1,2])
def test_halving_an_actual_circle_period_has_the_correct_verdict(method,multiplicity):
    raw,observation,_,_,field = circle(method,multiplicity)
    result = shorter_metric(raw,observation,2*np.pi*multiplicity,np.zeros(3),field)
    assert result["qualified"] is (multiplicity == 2)
    if multiplicity == 2:
        assert all(w["counts"] == dict(historical=1,barrio=1) and not w["shorter_periods"] for w in result["windows"])

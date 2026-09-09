import numpy as np
import pytest

from butterfly.poincare import PoincareSection
from butterfly.section_census import collect


@pytest.mark.parametrize("method", ["DOP853", "Radau"])
@pytest.mark.parametrize("offset", [-.0001, .0001, 0.])
def test_hidden_crossing_pair_no_crossing_and_tangency(method, offset):
    rhs = lambda t, q: np.array([1., 2*(t-.5), 0.])
    jac = lambda t, q: np.zeros((3, 3))
    report, raw = collect(rhs, jac, [0., .25+offset, 0.], [1., 0., 0.],
        PoincareSection((0., 1., 0.), 0., -1), method=method, horizon=1., guard=0., max_step=1., first_step=1.)
    assert len(raw["integration_times"]) == 2
    assert not report["ordinary"]
    if offset < 0:
        assert [r["time"] for r in report["reconstructed"]] == pytest.approx([.49, .51], abs=1e-10)
        assert [r["accepted"] for r in report["reconstructed"]] == [True, False]
        assert not report["uncertain_extrema"]
    elif offset > 0:
        assert not report["reconstructed"] and not report["uncertain_extrema"]
    else:
        assert report["uncertain_extrema"]
        # Roundoff can bracket tiny apparent roots at an exact tangency, but
        # uncertainty must remain explicit and must prevent qualification.
        assert not report["numerical_all_root_proof"]

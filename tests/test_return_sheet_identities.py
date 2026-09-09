"""Algebraic checks for the explanatory event-sheet note; no trajectories."""
import numpy as np
import pytest

from butterfly.models import RosslerParameters,rossler_jacobian,rossler_rhs
from butterfly.poincare import legacy_rossler_section


@pytest.mark.parametrize("a",[.21575,.21577])
def test_section_gate_and_grazing_acceleration(a):
    p = RosslerParameters(a=a,b=.2,c=7.212)
    section = legacy_rossler_section(p)
    ys = section.offset
    assert section.gate_upper == pytest.approx(-a*ys,abs=1e-15)
    for z in (.01,1.,13.):
        q = np.array([-a*ys,ys,z])
        f = rossler_rhs(0.,q,p)
        assert f[1] == 0.
        acceleration = rossler_jacobian(q,p)@f
        assert acceleration[1] == pytest.approx(-ys-z,abs=1e-14)
        for displacement in (-.1,.1):
            q[0] = -a*ys+displacement
            assert bool(rossler_rhs(0.,q,p)[1] < 0) == bool(q[0] < section.gate_upper)


@pytest.mark.parametrize("speed",[-.2,-3.,5.])
def test_corrected_tangent_is_tangent_and_matches_fold_numerator(speed):
    f = np.array([2.,speed,-1.])
    v = np.array([3.,.4,7.])
    tau_u = -v[1]/f[1]
    corrected = v+f*tau_u
    assert corrected[1] == pytest.approx(0.,abs=1e-15)
    assert corrected[0] == pytest.approx((f[1]*v[0]-f[0]*v[1])/f[1],rel=1e-14)

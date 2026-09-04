import numpy as np
import pytest
from butterfly.models import RosslerParameters, rossler_rhs
from butterfly.rossler_conventions import (
    OriginFixedRosslerParameters, canonical_to_origin_fixed, origin_fixed_rossler_rhs,
)


@pytest.mark.parametrize("parameters", [RosslerParameters(.2,.2,5.7), RosslerParameters(.182643608174,.2,10.3084), RosslerParameters(0,.2,5)])
def test_parameter_and_vector_field_conversion(parameters):
    mapped = canonical_to_origin_fixed(parameters)
    np.testing.assert_allclose([mapped.canonical.a,mapped.canonical.b,mapped.canonical.c], [parameters.a,parameters.b,parameters.c], rtol=1e-14)
    for point in ([0,0,0], [1,2,3], [-10,4,.01]):
        point = np.asarray(point)
        np.testing.assert_allclose(origin_fixed_rossler_rhs(0,point,mapped), rossler_rhs(0,point+mapped.equilibrium_shift,parameters), atol=1e-13)


def test_equal_named_parameters_are_not_same_slice():
    p = OriginFixedRosslerParameters(.2,.3,4.9).canonical
    assert p.b == pytest.approx(1.47)
    assert p.c == pytest.approx(4.96)
    assert canonical_to_origin_fixed(RosslerParameters(.2,.2,10)).beta != .2


def test_large_equilibrium_is_an_explicit_alternative():
    p = RosslerParameters(.2,.2,5.7)
    mapped = canonical_to_origin_fixed(p, equilibrium_index=1)
    np.testing.assert_allclose(rossler_rhs(0,mapped.equilibrium_shift,p), 0, atol=1e-12)
    assert mapped.beta > 1


def test_absent_equilibrium_and_nonfinite_parameters_rejected():
    with pytest.raises(ValueError):
        canonical_to_origin_fixed(RosslerParameters(1,1,0))
    with pytest.raises(ValueError):
        OriginFixedRosslerParameters(0,float("nan"),1)

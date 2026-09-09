"""I/O-only adapter: identical numeric content, bounded and read-only."""
import numpy as np
import pytest

from scripts.audit_exp494_cached import eager_loader
from scripts import audit_exp494_periodic_winding_transport as frozen
from test_periodic_winding import circle


@pytest.mark.parametrize("method",["DOP853","Radau"])
def test_lazy_and_cached_coefficients_return_identical_states(tmp_path,method):
    raw,report,metric,_,field = circle(method)
    path = tmp_path/"control.npz"
    np.savez_compressed(path,**raw)
    with np.load(path,allow_pickle=False) as lazy, eager_loader(np.load)(path,allow_pickle=False) as cached:
        assert lazy.files == cached.files
        for name in lazy.files:
            np.testing.assert_array_equal(lazy[name],cached[name])
        for t in np.linspace(0.,raw["times"][-1],13):
            np.testing.assert_array_equal(frozen.run.geometry.dense_value(lazy,method,t),
                                          frozen.run.geometry.dense_value(cached,method,t))
        assert cached["times"] is cached["times"]
        with pytest.raises(ValueError):
            cached["times"][0] = 100.


def test_non_npz_loading_keeps_original_semantics(tmp_path):
    path = tmp_path/"array.npy"
    np.save(path,np.arange(3))
    np.testing.assert_array_equal(eager_loader(np.load)(path,allow_pickle=False),np.arange(3))


def test_large_schema_rejected(tmp_path):
    path = tmp_path/"many.npz"
    np.savez(path,**{f"a{i}":np.array(i) for i in range(65)})
    with pytest.raises(ValueError,match="schema"):
        eager_loader(np.load)(path,allow_pickle=False)

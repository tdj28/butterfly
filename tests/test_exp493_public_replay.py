"""The released local-window polygons replay without private research data."""
import numpy as np
import pytest
import json
import shutil

from scripts import export_exp493_projected_inner_turn as release


@pytest.mark.parametrize("turns",[-2,-1,0,1,2])
def test_independent_polygon_ray_count(turns):
    t = np.linspace(.3,.3+2*np.pi*turns,101)
    assert release.ray_index(np.column_stack([np.cos(t),np.sin(t)])) == turns


def test_negative_ray_endpoint_convention():
    assert release.ray_index([[-1.,0.],[-1.,-.1]]) == 1
    assert release.ray_index([[-1.,-.1],[-1.,0.]]) == -1
    assert release.ray_index([[1.,.1],[1.,-.1]]) == 0


def test_all_released_profiles_replay_without_full_horizon_raw_data():
    assert release.verify(release.ROOT/"docs/experiments/receipts")


@pytest.mark.parametrize("change",["archive","compact-verdict"])
def test_release_tampering_fails(tmp_path,change):
    source = release.ROOT/"docs/experiments/receipts"
    for name in (release.ARCHIVE,release.RECEIPT):
        shutil.copyfile(source/name,tmp_path/name)
    if change == "archive":
        (tmp_path/release.ARCHIVE).write_bytes(b"not the bound archive")
    else:
        path = tmp_path/release.RECEIPT
        value = json.loads(path.read_bytes())
        next(r for r in value["intervals"] if r["analysis"] is not None)["analysis"]["qualified"] = False
        path.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        release.verify(tmp_path)

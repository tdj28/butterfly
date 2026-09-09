"""Bounded archival planning and fail-closed extraction controls."""
import hashlib
import json

import pytest

from scripts import release_exp494_periodic_transport as release


def test_shards_preserve_all_members_once_and_in_order():
    rows = [dict(path=str(i),bytes=n) for i,n in enumerate([4,6,3,8,2])]
    chunks = release.partition(rows,10)
    assert [len(c) for c in chunks] == [2,1,2]
    assert [r for c in chunks for r in c] == rows
    assert all(sum(r["bytes"] for r in c) <= 10 for c in chunks)


@pytest.mark.parametrize("size", [-1,11])
def test_oversize_and_negative_members_fail(size):
    with pytest.raises(ValueError):
        release.partition([dict(path="a",bytes=size)],10)


def test_wrong_index_hash_never_creates_output(tmp_path):
    path = tmp_path/"index.json"
    path.write_text("{}")
    with pytest.raises(ValueError,match="hash"):
        release.unpack(path,"0"*64,tmp_path/"out")
    assert not (tmp_path/"out").exists()


@pytest.mark.parametrize("change", ["schema", "experiment", "size", "shard-path"])
def test_invalid_index_never_extracts(tmp_path,change):
    index = dict(schema="butterfly.exp494-full-data.v1",experiment_id="EXP-494",total_members=1,total_bytes=1,
                 shards=[dict(path="part.tar",bytes=1,sha256="0"*64,members=[])])
    if change == "schema":
        index["schema"] = "other"
    elif change == "experiment":
        index["experiment_id"] = "EXP-481"
    elif change == "size":
        index["total_bytes"] = 20*1024**3
    else:
        index["shards"][0]["path"] = "../outside.tar"
    path = tmp_path/"index.json"
    path.write_text(json.dumps(index))
    with pytest.raises(ValueError):
        release.unpack(path,hashlib.sha256(path.read_bytes()).hexdigest(),tmp_path/"out")
    assert not (tmp_path/"out").exists()

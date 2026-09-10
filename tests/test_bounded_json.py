"""The entire final summary, not just prior files, counts against the quota."""
import json
from types import SimpleNamespace

import pytest
from butterfly import bounded_json as bounded


def test_exp506_summary_duplication_regression():
    with pytest.raises(bounded.ArtifactQuotaExceeded):
        bounded.check_size(51851415,72203701,104857600)


def test_complete_canonical_serialization_and_exact_limit(tmp_path):
    value = {'unicode':'λ','nested':[1,True,None]}
    encoded = (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    path = tmp_path/'summary.json'
    result = bounded.write_bounded_json(tmp_path,path,value,limit_bytes=len(encoded))
    assert path.read_bytes() == encoded
    assert result['output_bytes_after'] == len(encoded)


def test_oversized_summary_rejected_without_creating_partial_file(tmp_path):
    bounded.write_json(tmp_path/'point.json',{'prior':'data'})
    before = bounded.directory_bytes(tmp_path)
    path = tmp_path/'summary.json'
    with pytest.raises(bounded.ArtifactQuotaExceeded):
        bounded.write_bounded_json(tmp_path,path,{'duplicate':'x'*100},limit_bytes=before+20)
    assert not path.exists() and bounded.directory_bytes(tmp_path) == before


def test_failure_reserve_is_not_available_to_normal_summary(tmp_path):
    with pytest.raises(bounded.ArtifactQuotaExceeded):
        bounded.write_bounded_json(tmp_path,tmp_path/'summary.json',{},limit_bytes=10,reserve_bytes=8)


def test_free_space_floor_applies_to_full_artifact(tmp_path,monkeypatch):
    monkeypatch.setattr(bounded.shutil,'disk_usage',lambda p:SimpleNamespace(free=100))
    with pytest.raises(bounded.ArtifactQuotaExceeded):
        bounded.write_bounded_json(tmp_path,tmp_path/'summary.json',{'x':'abc'},limit_bytes=1000,minimum_free_bytes=99)
    assert not (tmp_path/'summary.json').exists()


def test_no_overwrite_or_escape(tmp_path):
    path = tmp_path/'summary.json'
    bounded.write_json(path,{'kept':True})
    with pytest.raises(ValueError,match='fresh'):
        bounded.write_bounded_json(tmp_path,path,{},limit_bytes=100)
    with pytest.raises(ValueError,match='fresh'):
        bounded.write_bounded_json(tmp_path,tmp_path.parent/'escape.json',{},limit_bytes=100)
    assert json.loads(path.read_bytes()) == {'kept':True}


def test_nonfinite_or_symlink_output_rejected(tmp_path):
    with pytest.raises(ValueError):
        bounded.write_bounded_json(tmp_path,tmp_path/'bad.json',{'x':float('nan')},limit_bytes=100)
    (tmp_path/'link').symlink_to(tmp_path.parent,target_is_directory=True)
    with pytest.raises(ValueError,match='symlink'):
        bounded.write_bounded_json(tmp_path,tmp_path/'bad.json',{},limit_bytes=100)


@pytest.mark.parametrize('values',[(True,1,10),(-1,1,10),(0,1,-1)])
def test_invalid_quota_values_rejected(values):
    with pytest.raises(ValueError):
        bounded.check_size(*values)

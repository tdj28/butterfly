"""Public evidence replay, with raw coefficient access and integration forbidden."""
from copy import deepcopy
import json
import pytest
from scripts import verify_exp500_public_census as public


@pytest.fixture(scope="module")
def result():
    path = public.run.ROOT/"docs/experiments/receipts/EXP-500-complete-polynomial-census-result.json"
    assert public.run.sha256(path) == "e77a6ef000671836d272f0be6d6aaabc536c791682e88c74cff2fc79c548c54d"
    return json.loads(path.read_bytes())


def test_public_all_event_comparison_replays_without_raw(result,monkeypatch):
    def forbidden(*args,**kwargs): pytest.fail("public comparison must not need private raw or integrate")
    monkeypatch.setattr(public.run.taylor,"integrate",forbidden)
    monkeypatch.setattr(public.run.taylor,"load_stream",forbidden)
    checked = public.validate(result)
    assert checked["qualified"] and checked["inputs"] == 32 and checked["profiles"] == 64
    assert checked["segments"] == 239072 and checked["plane_roots"] == 1024
    assert checked["accepted"] == checked["upward_outside"] == 480 and checked["initial"] == 64
    assert checked["complete_profiles"] == 64 and checked["unresolved_regions"] == checked["join_failures"] == 0


@pytest.mark.parametrize("kind",["input","profile","event","decision","claim"])
def test_incomplete_or_overclaimed_public_result_rejected(result,kind):
    bad = deepcopy(result)
    if kind == "input": bad["rows"].pop()
    elif kind == "profile": bad["rows"][0]["profiles"].pop()
    elif kind == "event": bad["rows"][0]["profiles"][0]["analysis"]["events"].pop()
    elif kind == "decision": bad["rows"][0]["comparison"]["qualified"] = False
    else: bad["exact_flow_all_roots_proved"] = True
    with pytest.raises(ValueError): public.validate(bad)

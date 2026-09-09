"""Replay the published compact result, without private raw trajectories."""
from copy import deepcopy
import json
import pytest
from scripts import verify_exp501_public_contact as v

PATH = v.run.ROOT/"docs/experiments/receipts/EXP-501-limiting-grazing-contact-result.json"
SHA = "c97b64e4770e1b53a66802c9bf6791fe4dbbf22e84d6d12281ccda9ae451b485"


def test_public_contact_result_and_all_condition_counts():
    assert v.run.sha256(PATH) == SHA
    result = v.validate(json.loads(PATH.read_bytes()))
    assert result["candidates"] == 8 and result["qualified_profiles"] == 16
    assert result["target_ivps"] == 38 and result["accepted_prefix_events"] == 72
    assert result["analysis"]["complete"] and result["analysis"]["comparison_cells"] == 384
    assert result["analysis"]["verdict"] == "not-proximate"
    assert not result["analysis"]["symbolic_chains_verified"]


@pytest.mark.parametrize("kind",["missing","claimed-contact","claimed-chain","distance","residual"])
def test_public_tampering_rejected(kind):
    result = deepcopy(json.loads(PATH.read_bytes()))
    if kind == "missing":
        result["rows"].pop()
    elif kind == "claimed-contact":
        result["analysis"]["verdict"] = "proximate"
    elif kind == "claimed-chain":
        result["analysis"]["symbolic_chains_verified"] = True
    elif kind == "distance":
        result["rows"][0]["comparison"]["comparisons"][0]["scaled_distance"] = "0"
    else:
        result["rows"][0]["profiles"][0]["shooting"]["trace"][-1]["residual"][0] = "1e-20"
    with pytest.raises(ValueError):
        v.validate(result)

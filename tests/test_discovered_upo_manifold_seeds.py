from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "validate_discovered_upo_manifold_seeds.py"
SPEC = importlib.util.spec_from_file_location("discovered_upo_seeds", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _receipts():
    discovery = {
        "cases": [
            {
                "id": "left",
                "parameters": {"a": 0.1, "b": 0.2, "c": 20.0},
                "recoveries": [
                    {
                        "accepted": True,
                        "correction": {"initial_state": [1.0, 2.0, 3.0]},
                    }
                ],
            }
        ]
    }
    identity = {
        "cases": [
            {
                "id": "left",
                "parameters": {"a": 0.1, "b": 0.2, "c": 20.0},
                "audits": [
                    {
                        "source_recovery_index": 0,
                        "fundamental_period_time": 12.5,
                    }
                ],
                "families": [
                    {
                        "id": "family-01",
                        "fundamental_lag": 4,
                        "representative_audit_index": 0,
                        "member_audit_indices": [0],
                    }
                ],
            }
        ]
    }
    return discovery, identity


def test_family_adapter_selects_identity_representative():
    discovery, identity = _receipts()
    instances = MODULE._family_instances(discovery, identity, ["left"])
    assert len(instances) == 1
    assert instances[0]["fundamental_lag"] == 4
    assert instances[0]["fundamental_period_time"] == 12.5
    family, case, receipts = MODULE._synthetic_validation_inputs(instances[0])
    assert family["fundamental_lag"] == 4
    assert case == {"id": "left", "a": 0.1}
    row = receipts["discovered-primitive-upos"]["branches"][0]["rows"][0]
    assert row["initial_state"] == [1.0, 2.0, 3.0]


def test_family_adapter_rejects_unaccepted_representative():
    discovery, identity = _receipts()
    discovery["cases"][0]["recoveries"][0]["accepted"] = False
    with pytest.raises(ValueError, match="was not accepted"):
        MODULE._family_instances(discovery, identity, ["left"])


def test_family_adapter_requires_matching_parameters():
    discovery, identity = _receipts()
    identity["cases"][0]["parameters"]["c"] = 19.9
    with pytest.raises(ValueError, match="parameters disagree"):
        MODULE._family_instances(discovery, identity, ["left"])

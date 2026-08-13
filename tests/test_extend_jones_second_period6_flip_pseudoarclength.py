import json
from pathlib import Path

from scripts.extend_jones_second_period6_flip_pseudoarclength import SCHEMA


def test_second_period6_flip_pseudoarclength_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-second-period6-flip-pseudoarclength-manifest.v1"


def test_exp228_exposes_fixed_c_control_guard_at_top_level():
    manifest = json.loads(
        Path(
            "experiments/manifests/EXP-228-second-period6-flip-pseudoarclength.json"
        ).read_text()
    )
    assert manifest["a_guard"] == manifest["continuation"]["a_guard"]

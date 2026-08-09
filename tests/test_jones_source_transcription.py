import json
from pathlib import Path

import pytest

from scripts.audit_jones2012_transcription import (
    audit_transcription,
    small_equilibrium_hopf_a_at_c,
)


SOURCE = Path("experiments/source-transcriptions/jones2012-figures-2-and-6.json")


def test_source_transcription_passes_structural_and_hopf_audit() -> None:
    result = audit_transcription(json.loads(SOURCE.read_text()))
    assert result["passed"]
    assert result["node_count"] == 23
    assert result["matched_transition_count"] == 10
    assert result["visual_only_transition_count"] == 1
    assert result["parameter_landmark_count"] == 10
    assert result["computed_l1_height_hopf_a"] == pytest.approx(
        0.0018649211449047556, abs=2e-15
    )


@pytest.mark.parametrize(
    ("c", "expected_a"),
    [(10.0, 0.001980601948535982), (10.3084, 0.0018649211449047556)],
)
def test_small_equilibrium_hopf_inverse(c: float, expected_a: float) -> None:
    assert small_equilibrium_hopf_a_at_c(c, 0.2) == pytest.approx(
        expected_a, abs=2e-15
    )


def test_audit_rejects_a_non_insertion_transition() -> None:
    document = json.loads(SOURCE.read_text())
    document["figure6"]["matched_p_to_p_plus_1_transitions"][0]["target"] = "CD01"
    with pytest.raises(ValueError, match="zero-insertion rule"):
        audit_transcription(document)

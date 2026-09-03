from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.audit_jones_period3072_segmented_identity import phase_invariant_half_identity


def test_phase_invariant_half_identity_recovers_cyclic_shift() -> None:
    left = np.asarray([[0.0, 0.0, 0.0], [1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    right = np.roll(left, 1, axis=0)
    result = phase_invariant_half_identity(np.vstack((left, right)))
    assert result["rms"] == pytest.approx(0.0)
    assert result["node_shift"] == 2


def test_phase_invariant_half_identity_rejects_odd_node_count() -> None:
    with pytest.raises(ValueError, match="even shape"):
        phase_invariant_half_identity(np.zeros((5, 3)))

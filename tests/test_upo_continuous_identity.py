from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_pim_upo_primitivity.py"
SPEC = importlib.util.spec_from_file_location("upo_identity_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_continuous_phase_alignment_refines_beyond_coarse_grid():
    sample_count = 128
    phases = np.linspace(0.0, 1.0, sample_count, endpoint=False)
    offset = 0.123456789
    left = np.column_stack(
        (np.cos(2.0 * np.pi * phases), np.sin(2.0 * np.pi * phases))
    )

    def shifted_solution(times):
        shifted = np.asarray(times) + offset
        return np.vstack(
            (np.cos(2.0 * np.pi * shifted), np.sin(2.0 * np.pi * shifted))
        )

    rms, phase_shift = MODULE._continuous_phase_invariant_rms(
        left,
        shifted_solution,
        1.0,
        np.ones(2),
        shift_tolerance=1e-12,
    )
    assert rms < 1e-7
    assert min(abs((phase_shift + offset) % 1.0), abs((phase_shift + offset) % 1.0 - 1.0)) < 1e-8

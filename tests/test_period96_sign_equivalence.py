from __future__ import annotations

import numpy as np

from scripts.qualify_jones_period96_sign_equivalence import phase_aligned_identity
from scripts.audit_jones_period96_sign_phase_resolution import (
    continuous_phase_identity,
)


def test_phase_aligned_identity_recovers_shifted_periodic_curve() -> None:
    def orbit(phases):
        angles = 2.0 * np.pi * np.asarray(phases)
        return np.vstack((np.cos(angles), np.sin(angles), np.cos(2.0 * angles)))

    def shifted(phases):
        return orbit((np.asarray(phases) + 0.25) % 1.0)

    result = phase_aligned_identity(
        orbit,
        shifted,
        {
            "phase_samples": 256,
            "coarse_shifts": 32,
            "refinement_stages": 3,
            "refinement_points": 33,
        },
    )

    assert result["rms"] < 1e-12
    assert min(abs(result["phase_shift"] - 0.75), abs(result["phase_shift"] + 0.25)) < 1e-12


def test_continuous_phase_identity_resolves_subgrid_shift() -> None:
    true_shift = 0.500000003

    def orbit(phases):
        angles = 2.0 * np.pi * np.asarray(phases)
        return np.vstack((np.cos(angles), np.sin(angles), np.cos(2.0 * angles)))

    def shifted(phases):
        return orbit((np.asarray(phases) - true_shift) % 1.0)

    result = continuous_phase_identity(
        orbit,
        shifted,
        {
            "phase_samples": 512,
            "expected_phase_shift": 0.5,
            "search_half_width": 1e-5,
            "phase_tolerance": 1e-14,
            "maximum_iterations": 100,
        },
    )

    assert result["success"]
    assert result["rms"] < 1e-10
    assert abs(result["phase_shift"] - true_shift) < 1e-10

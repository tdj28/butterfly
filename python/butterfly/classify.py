"""Conservative recurrence-based classification of Poincaré crossings."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import numpy as np
from numpy.typing import ArrayLike


class OrbitLabel(StrEnum):
    PERIODIC = "periodic"
    CHAOTIC = "chaotic"
    QUASIPERIODIC = "quasiperiodic"
    ESCAPING = "escaping"
    MULTISTABLE = "multistable"
    NUMERICAL_FAILURE = "numerical_failure"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True, slots=True)
class PeriodClassification:
    label: OrbitLabel
    fundamental_period: int | None
    recurrence_error: float | None
    recurrence_tolerance: float | None
    confidence: float
    samples_used: int
    reason: str


def classify_fundamental_period(
    crossings: ArrayLike,
    *,
    max_period: int = 64,
    required_repeats: int = 4,
    atol: float = 1e-7,
    rtol: float = 1e-7,
    escape_radius: float = 1e6,
) -> PeriodClassification:
    """Find the smallest period supported by repeated Poincaré states.

    The function makes only claims supported by recurrence. A bounded sequence
    that fails the periodic test remains unresolved; distinguishing chaos from
    quasiperiodicity requires additional diagnostics such as Lyapunov exponents
    and convergence/spectral tests.
    """

    values = np.asarray(crossings, dtype=np.float64)
    if values.ndim == 1:
        values = values[:, None]
    if values.ndim != 2:
        raise ValueError("crossings must be a one- or two-dimensional sequence")
    if max_period < 1 or required_repeats < 2:
        raise ValueError("max_period must be positive and required_repeats at least 2")
    if atol <= 0.0 or rtol < 0.0 or escape_radius <= 0.0:
        raise ValueError("invalid recurrence or escape tolerance")
    if len(values) == 0:
        return PeriodClassification(
            OrbitLabel.UNRESOLVED,
            None,
            None,
            None,
            0.0,
            0,
            "no section crossings",
        )
    if not np.all(np.isfinite(values)):
        return PeriodClassification(
            OrbitLabel.NUMERICAL_FAILURE,
            None,
            None,
            None,
            1.0,
            len(values),
            "non-finite crossing state",
        )
    if np.max(np.linalg.norm(values, axis=1)) > escape_radius:
        return PeriodClassification(
            OrbitLabel.ESCAPING,
            None,
            None,
            None,
            1.0,
            len(values),
            "crossing norm exceeded escape radius",
        )

    largest_testable = min(max_period, len(values) // (required_repeats + 1))
    if largest_testable < 1:
        return PeriodClassification(
            OrbitLabel.UNRESOLVED,
            None,
            None,
            None,
            0.0,
            len(values),
            "insufficient repeats for period testing",
        )

    for period in range(1, largest_testable + 1):
        samples_used = period * (required_repeats + 1)
        tail = values[-samples_used:]
        differences = tail[period:] - tail[:-period]
        recurrence_error = float(np.max(np.linalg.norm(differences, axis=1)))
        scale = max(float(np.max(np.linalg.norm(tail, axis=1))), 1.0)
        tolerance = float(atol + rtol * scale)
        if recurrence_error <= tolerance:
            confidence = float(1.0 / (1.0 + recurrence_error / tolerance))
            return PeriodClassification(
                OrbitLabel.PERIODIC,
                period,
                recurrence_error,
                tolerance,
                confidence,
                samples_used,
                "smallest repeated return block within declared tolerance",
            )

    return PeriodClassification(
        OrbitLabel.UNRESOLVED,
        None,
        None,
        None,
        0.0,
        len(values),
        "no fundamental period passed; chaos/quasiperiodicity not inferred",
    )

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


@dataclass(frozen=True, slots=True)
class DynamicsThresholds:
    chaos_min: float = 1e-3
    zero_tolerance: float = 5e-3
    contraction_min: float = 1e-3
    z_score: float = 2.0

    def __post_init__(self) -> None:
        if (
            self.chaos_min <= 0.0
            or self.zero_tolerance <= 0.0
            or self.contraction_min <= 0.0
            or self.z_score < 0.0
        ):
            raise ValueError("dynamics thresholds must be positive/nonnegative")


@dataclass(frozen=True, slots=True)
class DynamicsClassification:
    label: OrbitLabel
    fundamental_period: int | None
    confidence: float
    reason: str
    evidence: tuple[str, ...]


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


def classify_with_lyapunov(
    recurrence: PeriodClassification,
    exponents: ArrayLike,
    standard_errors: ArrayLike,
    *,
    thresholds: DynamicsThresholds = DynamicsThresholds(),
) -> DynamicsClassification:
    """Combine recurrence and uncertainty-aware Lyapunov evidence.

    The rules are deliberately sufficient rather than exhaustive. Diagnostics
    that conflict or straddle a decision boundary remain unresolved.
    """

    values = np.asarray(exponents, dtype=np.float64)
    errors = np.asarray(standard_errors, dtype=np.float64)
    if values.shape != (3,) or errors.shape != (3,):
        raise ValueError("three exponents and three standard errors are required")
    if not np.all(np.isfinite(values)) or not np.all(np.isfinite(errors)):
        return DynamicsClassification(
            OrbitLabel.NUMERICAL_FAILURE,
            None,
            1.0,
            "non-finite Lyapunov evidence",
            ("lyapunov-nonfinite",),
        )
    if np.any(errors < 0.0):
        raise ValueError("standard errors must be nonnegative")

    order = np.argsort(values)[::-1]
    values = values[order]
    errors = errors[order]
    lower = values - thresholds.z_score * errors
    upper = values + thresholds.z_score * errors

    if recurrence.label in (OrbitLabel.NUMERICAL_FAILURE, OrbitLabel.ESCAPING):
        return DynamicsClassification(
            recurrence.label,
            None,
            recurrence.confidence,
            recurrence.reason,
            ("recurrence-terminal",),
        )

    positive_largest = lower[0] > thresholds.chaos_min
    flow_zero = lower[1] <= 0.0 <= upper[1] or abs(values[1]) <= thresholds.zero_tolerance
    contracting_third = upper[2] < -thresholds.contraction_min

    if recurrence.label == OrbitLabel.PERIODIC:
        if positive_largest:
            return DynamicsClassification(
                OrbitLabel.UNRESOLVED,
                None,
                0.0,
                "period recurrence conflicts with a decisively positive largest exponent",
                ("period-recurrence", "positive-lyapunov-conflict"),
            )
        return DynamicsClassification(
            OrbitLabel.PERIODIC,
            recurrence.fundamental_period,
            recurrence.confidence,
            "minimal return period passed and Lyapunov evidence does not contradict it",
            ("period-recurrence", "lyapunov-nonconflict"),
        )

    if positive_largest and flow_zero and contracting_third:
        margin = lower[0] - thresholds.chaos_min
        confidence = float(np.clip(margin / (abs(values[0]) + errors[0] + 1e-15), 0.0, 1.0))
        return DynamicsClassification(
            OrbitLabel.CHAOTIC,
            None,
            confidence,
            "positive largest, flow-compatible near-zero middle, and contracting third exponent",
            ("no-period-recurrence", "three-exponent-chaos-signature"),
        )

    two_zero = (
        abs(values[0]) + thresholds.z_score * errors[0] <= thresholds.zero_tolerance
        and abs(values[1]) + thresholds.z_score * errors[1]
        <= thresholds.zero_tolerance
    )
    if two_zero and contracting_third:
        margin = thresholds.zero_tolerance - max(
            abs(values[0]) + thresholds.z_score * errors[0],
            abs(values[1]) + thresholds.z_score * errors[1],
        )
        confidence = float(np.clip(margin / thresholds.zero_tolerance, 0.0, 1.0))
        return DynamicsClassification(
            OrbitLabel.QUASIPERIODIC,
            None,
            confidence,
            "two zero-compatible exponents, one contracting exponent, and no period recurrence",
            ("no-period-recurrence", "three-exponent-torus-signature"),
        )

    return DynamicsClassification(
        OrbitLabel.UNRESOLVED,
        None,
        0.0,
        "recurrence and uncertainty-aware Lyapunov rules did not yield a decisive label",
        ("no-period-recurrence", "lyapunov-boundary-or-unsupported-signature"),
    )


def combine_initial_conditions(
    classifications: list[DynamicsClassification],
) -> DynamicsClassification:
    """Promote distinct resolved attractor signatures to multistability."""

    if not classifications:
        raise ValueError("at least one initial-condition classification is required")
    resolved = [
        classification
        for classification in classifications
        if classification.label
        not in (OrbitLabel.UNRESOLVED, OrbitLabel.NUMERICAL_FAILURE)
    ]
    signatures = {
        (classification.label, classification.fundamental_period)
        for classification in resolved
    }
    if len(signatures) > 1:
        return DynamicsClassification(
            OrbitLabel.MULTISTABLE,
            None,
            min(classification.confidence for classification in resolved),
            "different initial conditions converged to distinct resolved attractor signatures",
            tuple(
                sorted(
                    f"{label.value}:p{period}" for label, period in signatures
                )
            ),
        )
    if len(signatures) == 1:
        representative = resolved[0]
        return DynamicsClassification(
            representative.label,
            representative.fundamental_period,
            min(item.confidence for item in resolved),
            "all resolved initial conditions agree",
            tuple(item.reason for item in resolved),
        )
    return DynamicsClassification(
        OrbitLabel.UNRESOLVED,
        None,
        0.0,
        "no initial condition produced a resolved attractor signature",
        tuple(item.reason for item in classifications),
    )

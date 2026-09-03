"""Initial-condition plane sampling for basin reconnaissance."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .classify import classify_fundamental_period
from .integrate import SolverConfig
from .models import RosslerParameters
from .poincare import collect_crossings, legacy_rossler_section


def fit_uncertainty_exponent(
    epsilons: np.ndarray,
    uncertain_counts: np.ndarray,
    resolved_counts: np.ndarray,
    *,
    bootstrap_samples: int = 5000,
    bootstrap_seed: int = 0,
) -> dict[str, Any]:
    """Fit ``f(epsilon) ~ epsilon**alpha`` with binomial bootstrap intervals.

    A Jeffreys half-count keeps the logarithm defined without silently dropping
    a scale whose observed uncertain count is zero. The bootstrap quantifies
    pair-sampling uncertainty; sensitivity to region, direction, integration
    horizon, and scale range remains a separate scientific check.
    """

    epsilons = np.asarray(epsilons, dtype=float)
    uncertain_counts = np.asarray(uncertain_counts, dtype=np.int64)
    resolved_counts = np.asarray(resolved_counts, dtype=np.int64)
    if not (
        epsilons.ndim == uncertain_counts.ndim == resolved_counts.ndim == 1
        and len(epsilons) == len(uncertain_counts) == len(resolved_counts)
        and len(epsilons) >= 3
    ):
        raise ValueError("uncertainty fit requires at least three aligned scales")
    if np.any(epsilons <= 0.0) or np.any(resolved_counts <= 0):
        raise ValueError("epsilons and resolved counts must be positive")
    if np.any(uncertain_counts < 0) or np.any(uncertain_counts > resolved_counts):
        raise ValueError("uncertain counts must lie between zero and resolved counts")
    if bootstrap_samples < 100:
        raise ValueError("at least 100 bootstrap samples are required")

    fractions = (uncertain_counts + 0.5) / (resolved_counts + 1.0)
    log_epsilon = np.log(epsilons)
    log_fraction = np.log(fractions)
    alpha, intercept = np.polyfit(log_epsilon, log_fraction, 1)
    predicted = intercept + alpha * log_epsilon
    residual_sum = float(np.sum((log_fraction - predicted) ** 2))
    total_sum = float(np.sum((log_fraction - np.mean(log_fraction)) ** 2))
    r_squared = 1.0 if total_sum == 0.0 else 1.0 - residual_sum / total_sum

    rng = np.random.default_rng(bootstrap_seed)
    bootstrap_alphas = np.empty(bootstrap_samples, dtype=float)
    for index in range(bootstrap_samples):
        samples = rng.binomial(resolved_counts, fractions)
        sampled_fractions = (samples + 0.5) / (resolved_counts + 1.0)
        bootstrap_alphas[index] = np.polyfit(
            log_epsilon, np.log(sampled_fractions), 1
        )[0]
    lower, upper = np.quantile(bootstrap_alphas, (0.025, 0.975))
    return {
        "alpha": float(alpha),
        "alpha_bootstrap_95_interval": [float(lower), float(upper)],
        "boundary_dimension_estimate": float(2.0 - alpha),
        "intercept": float(intercept),
        "r_squared": r_squared,
        "epsilons": epsilons.tolist(),
        "uncertain_fractions_jeffreys": fractions.tolist(),
        "bootstrap_samples": bootstrap_samples,
        "bootstrap_seed": bootstrap_seed,
        "fit_space": "ordinary least squares in log(epsilon), log(Jeffreys fraction)",
        "uncertainty_scope": "binomial pair sampling only",
    }


@dataclass(frozen=True, slots=True)
class BasinPlaneManifest:
    experiment_id: str
    parameters: RosslerParameters
    x_min: float
    x_max: float
    x_count: int
    y_min: float
    y_max: float
    y_count: int
    z: float
    transient: float
    observation_horizon: float
    max_crossings: int
    solver: SolverConfig
    max_period: int
    required_repeats: int
    atol: float
    rtol: float

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "BasinPlaneManifest":
        if value.get("schema") != "butterfly.basin-plane-manifest.v1":
            raise ValueError("unsupported basin-plane manifest")
        plane = value["plane"]
        integration = value["integration"]
        classifier = value["classifier"]
        parameters = value["parameters"]
        manifest = cls(
            experiment_id=str(value["experiment_id"]),
            parameters=RosslerParameters(
                a=float(parameters["a"]),
                b=float(parameters["b"]),
                c=float(parameters["c"]),
            ),
            x_min=float(plane["x"]["min"]),
            x_max=float(plane["x"]["max"]),
            x_count=int(plane["x"]["count"]),
            y_min=float(plane["y"]["min"]),
            y_max=float(plane["y"]["max"]),
            y_count=int(plane["y"]["count"]),
            z=float(plane["z"]),
            transient=float(integration["transient"]),
            observation_horizon=float(integration["observation_horizon"]),
            max_crossings=int(integration["max_crossings"]),
            solver=SolverConfig(**integration["solver"]),
            max_period=int(classifier["max_period"]),
            required_repeats=int(classifier["required_repeats"]),
            atol=float(classifier["atol"]),
            rtol=float(classifier["rtol"]),
        )
        manifest.validate()
        return manifest

    def validate(self) -> None:
        if not self.experiment_id:
            raise ValueError("experiment_id is required")
        if self.x_count < 1 or self.y_count < 1:
            raise ValueError("plane grid counts must be positive")
        if self.x_max < self.x_min or self.y_max < self.y_min:
            raise ValueError("plane maxima must not be smaller than minima")
        if self.transient < 0.0 or self.observation_horizon <= 0.0:
            raise ValueError("invalid integration horizon")
        if self.max_crossings < 1 or self.max_period < 1 or self.required_repeats < 2:
            raise ValueError("invalid crossing or recurrence configuration")


def initial_condition_grid(
    manifest: BasinPlaneManifest,
) -> tuple[tuple[int, tuple[float, float, float]], ...]:
    """Return deterministic `x`-major, `y`-minor basin-plane states."""

    return tuple(
        (
            x_index * manifest.y_count + y_index,
            (float(x), float(y), manifest.z),
        )
        for x_index, x in enumerate(
            np.linspace(manifest.x_min, manifest.x_max, manifest.x_count)
        )
        for y_index, y in enumerate(
            np.linspace(manifest.y_min, manifest.y_max, manifest.y_count)
        )
    )


def evaluate_initial_condition(
    manifest: BasinPlaneManifest,
    point_index: int,
    initial_state: tuple[float, float, float],
) -> dict[str, Any]:
    crossings = collect_crossings(
        manifest.parameters,
        initial_state,
        legacy_rossler_section(manifest.parameters),
        transient=manifest.transient,
        observation_horizon=manifest.observation_horizon,
        max_crossings=manifest.max_crossings,
        config=manifest.solver,
    )
    recurrence = classify_fundamental_period(
        crossings.states,
        max_period=manifest.max_period,
        required_repeats=manifest.required_repeats,
        atol=manifest.atol,
        rtol=manifest.rtol,
    )
    return {
        "point_index": point_index,
        "initial_state": list(initial_state),
        "label": recurrence.label.value,
        "fundamental_period": recurrence.fundamental_period,
        "recurrence_error": recurrence.recurrence_error,
        "recurrence_tolerance": recurrence.recurrence_tolerance,
        "crossing_count": len(crossings.times),
        "integration_success": crossings.integration_success,
        "integration_message": crossings.integration_message,
    }

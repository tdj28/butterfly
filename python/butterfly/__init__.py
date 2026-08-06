"""Reference numerical implementation for the Butterfly research program."""

from .classify import OrbitLabel, PeriodClassification, classify_fundamental_period
from .integrate import SolverConfig, Trajectory, integrate_trajectory
from .models import (
    RosslerParameters,
    equilibrium_eigenvalues,
    rossler_equilibria,
    rossler_jacobian,
    rossler_rhs,
)
from .poincare import (
    PoincareCrossings,
    PoincareSection,
    collect_crossings,
    legacy_rossler_section,
)

__all__ = [
    "OrbitLabel",
    "PeriodClassification",
    "RosslerParameters",
    "PoincareCrossings",
    "PoincareSection",
    "SolverConfig",
    "Trajectory",
    "equilibrium_eigenvalues",
    "collect_crossings",
    "classify_fundamental_period",
    "integrate_trajectory",
    "rossler_equilibria",
    "rossler_jacobian",
    "rossler_rhs",
    "legacy_rossler_section",
]

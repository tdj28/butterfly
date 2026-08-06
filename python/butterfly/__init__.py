"""Reference numerical implementation for the Butterfly research program."""

from .integrate import SolverConfig, Trajectory, integrate_trajectory
from .models import (
    RosslerParameters,
    equilibrium_eigenvalues,
    rossler_equilibria,
    rossler_jacobian,
    rossler_rhs,
)

__all__ = [
    "RosslerParameters",
    "SolverConfig",
    "Trajectory",
    "equilibrium_eigenvalues",
    "integrate_trajectory",
    "rossler_equilibria",
    "rossler_jacobian",
    "rossler_rhs",
]

"""Reference numerical implementation for the Butterfly research program."""

from .classify import OrbitLabel, PeriodClassification, classify_fundamental_period
from .integrate import SolverConfig, Trajectory, integrate_trajectory
from .lyapunov import (
    LargestLyapunovResult,
    LyapunovConfig,
    LyapunovResult,
    largest_lyapunov_two_trajectory,
    lyapunov_block_estimates,
    lyapunov_spectrum,
)
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
from .scan import ScanManifest, execute_scan, run_scan

__all__ = [
    "OrbitLabel",
    "LyapunovConfig",
    "LyapunovResult",
    "LargestLyapunovResult",
    "PeriodClassification",
    "RosslerParameters",
    "PoincareCrossings",
    "PoincareSection",
    "SolverConfig",
    "ScanManifest",
    "Trajectory",
    "equilibrium_eigenvalues",
    "execute_scan",
    "collect_crossings",
    "classify_fundamental_period",
    "integrate_trajectory",
    "lyapunov_spectrum",
    "largest_lyapunov_two_trajectory",
    "lyapunov_block_estimates",
    "rossler_equilibria",
    "rossler_jacobian",
    "rossler_rhs",
    "run_scan",
    "legacy_rossler_section",
]

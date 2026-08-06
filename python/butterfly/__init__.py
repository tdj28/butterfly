"""Reference numerical implementation for the Butterfly research program."""

from .atlas import PeriodicComponent, periodic_components, ranked_recurrence_candidates

from .candidates import CandidateSelection, select_low_score_with_neighbors
from .classify import (
    DynamicsClassification,
    DynamicsThresholds,
    OrbitLabel,
    PeriodClassification,
    RecurrenceCandidate,
    classify_fundamental_period,
    classify_with_lyapunov,
    closest_recurrence_candidate,
    combine_initial_conditions,
)
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
from .periodic import MonodromyResult, flow_monodromy
from .scan import ScanManifest, execute_scan, run_scan
from .tiles import (
    TileSpec,
    aggregate_scan_tiles,
    execute_scan_tile,
    verify_completed_aggregate,
    verify_completed_tile,
)

__all__ = [
    "OrbitLabel",
    "PeriodicComponent",
    "CandidateSelection",
    "DynamicsClassification",
    "DynamicsThresholds",
    "LyapunovConfig",
    "LyapunovResult",
    "MonodromyResult",
    "LargestLyapunovResult",
    "PeriodClassification",
    "RecurrenceCandidate",
    "RosslerParameters",
    "PoincareCrossings",
    "PoincareSection",
    "SolverConfig",
    "ScanManifest",
    "Trajectory",
    "TileSpec",
    "aggregate_scan_tiles",
    "equilibrium_eigenvalues",
    "execute_scan",
    "execute_scan_tile",
    "flow_monodromy",
    "collect_crossings",
    "classify_fundamental_period",
    "classify_with_lyapunov",
    "combine_initial_conditions",
    "closest_recurrence_candidate",
    "integrate_trajectory",
    "lyapunov_spectrum",
    "largest_lyapunov_two_trajectory",
    "lyapunov_block_estimates",
    "rossler_equilibria",
    "rossler_jacobian",
    "rossler_rhs",
    "periodic_components",
    "ranked_recurrence_candidates",
    "select_low_score_with_neighbors",
    "run_scan",
    "verify_completed_tile",
    "verify_completed_aggregate",
    "legacy_rossler_section",
]

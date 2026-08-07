"""Reference numerical implementation for the Butterfly research program."""

from .atlas import PeriodicComponent, periodic_components, ranked_recurrence_candidates
from .augmented_flip import (
    augmented_flip_system,
    integrate_flip_segment,
    rossler_hessian_action,
)
from .basins import (
    BasinPlaneManifest,
    evaluate_initial_condition,
    fit_uncertainty_exponent,
    initial_condition_grid,
)

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
from .periodic import (
    MonodromyResult,
    PeriodicOrbitCorrection,
    UnitMultiplierCorrection,
    correct_periodic_orbit,
    correct_unit_multiplier_orbit,
    flow_monodromy,
)
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
    "BasinPlaneManifest",
    "DynamicsClassification",
    "DynamicsThresholds",
    "LyapunovConfig",
    "LyapunovResult",
    "MonodromyResult",
    "PeriodicOrbitCorrection",
    "UnitMultiplierCorrection",
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
    "augmented_flip_system",
    "equilibrium_eigenvalues",
    "evaluate_initial_condition",
    "fit_uncertainty_exponent",
    "execute_scan",
    "execute_scan_tile",
    "flow_monodromy",
    "collect_crossings",
    "classify_fundamental_period",
    "classify_with_lyapunov",
    "combine_initial_conditions",
    "correct_periodic_orbit",
    "correct_unit_multiplier_orbit",
    "closest_recurrence_candidate",
    "integrate_trajectory",
    "initial_condition_grid",
    "integrate_flip_segment",
    "lyapunov_spectrum",
    "largest_lyapunov_two_trajectory",
    "lyapunov_block_estimates",
    "rossler_equilibria",
    "rossler_jacobian",
    "rossler_hessian_action",
    "rossler_rhs",
    "periodic_components",
    "ranked_recurrence_candidates",
    "select_low_score_with_neighbors",
    "run_scan",
    "verify_completed_tile",
    "verify_completed_aggregate",
    "legacy_rossler_section",
]

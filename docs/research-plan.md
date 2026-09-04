# Reproduction and validation plan

Phase outline: 2026-08-07. Current priorities reviewed: 2026-09-04.

Use [next-steps.md](next-steps.md) for the current execution order and
[the public audit](reviews/2026-09-04-public-research-audit.md) for corrected
interpretations. The phases below describe the original program; several
foundation items have since been implemented.

This document covers the Rössler reproduction and claim-validation program. The
broader platform and multi-attractor program is in
[`world-class-roadmap.md`](world-class-roadmap.md).

## Objective

Build a reproducible computational account of the Rössler periodicity hub, then
subject the 2012 paper's distinctive claims to stronger tests than were
available in the original work.

The original referee reports are now an explicit acceptance source. The
binding traceability matrix is in
[`reviews/2026-08-07-jones-peer-review-gap-audit.md`](reviews/2026-08-07-jones-peer-review-gap-audit.md).
In particular, deep periodic-orbit continuation cannot be used to claim that
the two/three-branch, finite-ordering, reinjection, or unfolded-spiral gaps are
closed.

## Phase 0 - Reproducible foundation

- Replace hidden globals and hard-coded resolution with explicit configuration.
- Add a serial reference solver before optimizing MPI or CUDA implementations.
- Define durable result schemas for trajectories, section crossings, orbit
  classifications, continuation branches, and provenance.
- Add automated unit tests for the Rössler vector field, equilibria, RK methods,
  section crossing, and minimal-period detection.
- Preserve the recovered implementation as a historical reference rather than
  silently rewriting it.

Exit criterion: a small deterministic scan can be reproduced from a clean
checkout and yields byte-stable metadata plus numerically consistent results.

## Phase 1 - Reproduce the parameter portraits

- Reproduce the paper's `(a,c)` domain at `b = 0.2` first at modest resolution.
- Implement adaptive integration and interpolated, oriented section crossings.
- Classify periodic, chaotic, quasiperiodic, escaping, multistable, and
  unresolved cases separately.
- Perform integration-horizon, tolerance, precision, resolution, and
  initial-condition sweeps.
- Compute Lyapunov exponents with published tangent equations and QR settings.

Exit criterion: the primary hub and low-period windows persist across two
integrators and documented convergence/basin tests.

## Phase 2 - Reconstruct bifurcation geometry

- Continue equilibria and the Andronov-Hopf curve.
- Locate periodic orbits from the grid and continue their saddle-node and
  period-doubling boundaries with Floquet multipliers.
- Define the return map and an operational two-branch/three-branch criterion.
- Continue the topological-transition curve.
- Reproduce nonattracting chaotic saddles inside representative periodic
  windows and test whether their return-map topology continues the transition
  curve through regular regions.
- Continue both superstability families and test the reported tangency between
  the TBA and `s+` at doubly-superstable points.
- Reproduce the PRL's fixed-period shrimp subdivision separately from Jones's
  inter-period mutant-shrimp connectivity claim.
- Formulate and test the claimed homoclinic boundary-value problem.

Exit criterion: Figures 1-4 can be regenerated from continuation data rather
than inferred solely from rasterized parameter grids, and the TBA can be
followed consistently through both chaotic and regular regions.

## Phase 3 - Test the finite logistic-ordering claim

- Source-audit `L1` and `L2`; where the paper omits equations, publish explicit
  operational paths and test competing interpretations rather than assigning
  false historical precision.
- Build bifurcation diagrams and critical-point caustics along each path.
- Define the symbolic partition and compute critical itineraries, kneading
  sequences, orbit permutations, and entropy estimates.
- Replace “full conjugacy” with the strongest statement actually supported:
  finite combinatorial agreement, semiconjugacy, or conjugacy.

Exit criterion: every comparison through period seven is machine-generated and
independently checked; higher-period tests quantify where agreement persists or
fails.

## Phase 4 - Test the distinctive reinjection hypothesis

- Define the third branch and its reinjection point without relying on a
  hand-chosen projection.
- Evaluate section coordinates, winding/linking data, branch ordering, and
  template invariants as candidate observables.
- Continue representative `p -> p+1` connections and mutant-shrimp tails.
- Test invariance under smooth coordinate changes and section perturbations.
- Compare reinjection measurements directly with homoclinic-sheaf geometry.

Exit criterion: the reinjection hypothesis is either converted into a precise,
robust result or explicitly narrowed/rejected.

## Phase 5 - Rigorous and independent validation

- Use multiprecision arithmetic where convergence is slow or windows are narrow.
- Validate selected periodic orbits and bifurcations with interval methods.
- Reproduce critical results with an independent continuation package.
- Extend the relevant structures in the `b` direction.

Exit criterion: the strongest revised claims have explicit numerical error
bounds and independent computational support.

## Original foundation priorities (historical)

1. Build the serial reference solver and test suite.
2. Reproduce a small period map around the hub.
3. Define a trustworthy Poincaré section and period classifier.
4. Add Lyapunov and orbit-continuation pipelines.
5. Defer the full `5000 x 5000` run until convergence and classification error
   are understood; more pixels are not a substitute for validation.

## Deliverables

- Versioned source and locked environment.
- Machine-readable configuration for every experiment.
- Raw or losslessly compressed numerical arrays.
- Regenerable figures with experiment IDs.
- Claim-ledger updates linked to the supporting experiments.
- A revised manuscript that clearly distinguishes reproduction, new evidence,
  conjecture, and rigorous result.
- A referee-response appendix mapping every original concern to a manuscript
  change, primary citation, experiment/figure receipt, or explicit unresolved
  limitation.

# Execution backlog

This is the live implementation queue. A checkbox closes only when its
acceptance evidence exists in tests, receipts, or a cited experiment record.

## P0 — trustworthy Rössler reproduction

- [x] **P0-001 — Repository and paper claim audit.** Evidence:
  `docs/experiments/EXP-000-repository-audit.md` and `docs/claim-ledger.md`.
- [x] **P0-002 — Reference Rössler model.** Float64 vector field, analytic
  Jacobian, equilibria, and hub eigenstructure are implemented with unit tests.
- [x] **P0-003 — Adaptive CPU integration baseline.** DOP853 path has declared
  tolerances, equilibrium-invariance test, and a short-horizon convergence test.
- [x] **P0-004 — Poincaré section object.** Oriented, interpolated events;
  explicit section definition; section unit tests; legacy-section adapter.
- [ ] **P0-005 — Fundamental-period classifier.** Minimal recurrence period,
  escape/failure/unresolved labels, uncertainty-aware full-spectrum rules for
  chaos/quasiperiodicity, multistability aggregation, conflict detection, and
  synthetic tests exist. EXP-005 passes four frozen published chaotic/periodic
  controls. EXP-010's two finite-time multistability candidates were rejected
  by EXP-012 as long transient capture; real persistent multistable and torus
  controls remain.
- [ ] **P0-006 — Lyapunov spectrum.** Variational equations, QR cadence,
  running convergence diagnostics, equilibrium validation, and trace identity
  exist; a nonlinear two-trajectory largest-exponent cross-check passes, while
  a declared horizon/tolerance/QR sweep and second full-spectrum package remain.
- [ ] **P0-007 — Reproducible scan artifacts.** Frozen manifests, atomic local
  result/receipt writes, hashes, one-command scans, optional full-spectrum
  evidence, immutable tiles, verified resume, and deterministic aggregation now
  exist. Bounded local processes operate only on unique shards; standalone
  schema files and archival promotion remain.
- [ ] **P0-008 — Legacy parity suite.** Recover representative legacy pixels and
  characterize discrepancies caused by fixed-step crossing/classifier logic.
- [ ] **P0-009 — Primary hub reproduction.** Coarse adaptive atlas, convergence
  sweeps, multiple initial conditions, and explicit unresolved regions. EXP-006
  demonstrates that a uniform `5 x 5` grid is decisively but scientifically
  under-resolved. EXP-009 completed a `41 x 41` near-recurrence ranking and
  retained 17 prospective targets. EXP-010 confirmed 135 chaotic targets, two
  unresolved targets, and two apparent multistability candidates. EXP-012
  showed eventual capture into stable period-6 and period-8 windows; saddle
  reconstruction, focused orbit recovery, and local refinement are next.
- [ ] **P0-010 — Bounded global-atlas reconnaissance.** EXP-013 is preregistered
  over `a in [0.22,0.36]`, `c in [5,15]` and completed all 1,189 points without
  numerical failure. Its 82 periodic pixels form 52 coarse components across
  periods 1, 2, 3, 4, 5, 6, 8, and 12; eight touch a search boundary. EXP-014
  qualified 26 consensus-periodic targets, retained nine unresolved cases, and
  produced four finite-time multistability labels. EXP-015 now tests those
  labels and a boundary capture case through transient 19,200: four collapse to
  common periodic capture, while `(a,c)=(0.245,5.75)` retains distinct period-12
  and period-3 cycles. EXP-016 tests both cycles' closure and Floquet stability
  and passes: flow closure is below `7e-12` and leading transverse multipliers
  have moduli `0.3141` and `0.8807`. CLM-019 now requires basin mapping,
  independent orbit correction, and continuation of both overlapping families.
  EXP-017 resolves all 441 basin-plane seeds into periods 12 or 3 and finds a
  `0.47024` discordant-neighbor fraction; uncertainty-exponent scaling is next,
  without prematurely calling the boundary fractal or riddled.

## P1 — GPU qualification and bifurcation geometry

- [x] **P1-001 — Safe Runpod control script.** API key remains outside Git;
  list/catalog/launch/status/terminate commands; duplicate and hourly-cost gates.
- [x] **P1-002 — GPU ensemble kernel.** EXP-018's manifest-bound Triton Float64
  RK4 kernel uses cubic-Hermite section localization and passes Poincare-orbit
  and recurrence-period parity on six stable controls at two timesteps.
- [x] **P1-003 — Cheap NVIDIA qualification.** The final NVIDIA L4 receipt binds
  commit `20bd0b6`, records 717.1 million raw Float64 state-steps/second, matches
  remote/local hashes, and ends with every task-owned pod terminated.
- [ ] **P1-004 — Forced-kill/resume test.** Immutable tile IDs, atomic completion,
  corruption rejection, simulated interrupted-write recovery, and an actual
  mid-computation process kill/restart pass locally. Remote container/storage
  repetition remains required before interruptible production use.
- [ ] **P1-005 — Continuation layer.** Hopf/equilibrium/periodic-orbit branches,
  Floquet multipliers, TBA/TTL curve, topology-change locus, independent cross-check.
  EXP-023 now naturally continues period-3 and period-5 flow orbits in `b` and
  brackets three `-1` and one `+1` multiplier crossings. EXP-024 refines all
  three period-doubling seeds but rejects the `+1` scalar solve because of
  branch switching. EXP-025 through EXP-027 reproduce the same smooth period-5
  `+1` crossing near `b=0.272283` at three pseudo-arclength resolutions with no
  `b` turn, rejecting a saddle-node of the traced branch. EXP-028 solves the
  coupled nontrivial unit-multiplier condition; EXP-029 switches coordinates;
  and EXP-030 phase-invariantly confirms a distinct stable secondary cycle
  alongside the unstable primary above the event. EXP-031 prospectively finds
  square-root branch opening (`0.49896`, `R^2=0.9999992`) and the cubic
  multiplier ratio (`1.9805` median), strongly supporting a supercritical
  pitchfork-like normal form in the phase quotient. Symmetry/validated local
  reduction, equilibrium/Hopf, and TBA remain open. EXP-032 through EXP-034
  resolve thirteen coupled `+1` events on a smooth fixed-`c=5.1` curve over
  `a in [0.235,0.265]`, reaching `b=0.347875`; natural continuation fails below
  `a=0.235`, so full event-system pseudo-arclength and continuation in `c` are
  the next surface-building steps.
- [ ] **P1-006 — Jones path definitions.** Exact `L1`/`L2` parameterizations and
  caustic/window-order reconstruction.

## P2 — topology, validation, and atlas expansion

- [ ] **P2-001 — Return-map topology.** Critical points, branch count, symbolic
  partitions, kneading data, entropy, and coordinate/section sensitivity.
- [ ] **P2-002 — Global bifurcations.** Homoclinic/heteroclinic boundary-value
  problems and bounded focal-point uniqueness claim.
- [ ] **P2-003 — Validated numerics.** Interval validation of selected decisive
  orbits, windows, crossings, and forcing/covering statements.
- [ ] **P2-004 — Two-system qualification.** Add two structurally different
  chaotic flows before scaling the registry.
- [ ] **P2-005 — Dozens-system atlas.** Curated systems, prospective parameter
  planes, negative results retained, uniform provenance and publication pipeline.

## AI gates — structure discovery, not diagram decoration

- [ ] **AI-000 — Numerical-oracle gate.** Complete P0 plus continuation of the
  known two-to-three transition, unstable periodic orbits, and chaotic saddles.
- [ ] **AI-001 — Quotient plausibility.** Test dimensional separation,
  invariant fibers/cones, transverse contraction, section robustness, local
  chart overlap, and parameter gauge alignment. Permit a negative result.
- [ ] **AI-002 — Constrained quotient baselines.** Compare fixed projections,
  principal/local manifold coordinates, constrained splines, and sparse maps
  before an invertible neural model.
- [ ] **AI-003 — Parameterized quotient positive control.** Recover the known
  transition on contiguous held-out regions without hallucinated branches.
- [ ] **AI-004 — Calibrated active search.** Beat or add information beyond
  uniform grids, quadtrees, continuation, GP level sets, and unconstrained ML.
- [ ] **AI-005 — Prospective symbolic grammar.** Commit held-out itinerary
  predictions, then verify them with exact orbit continuation.
- [ ] **AI-006 — New structure and certification.** Require a genuinely new
  prospectively verified branch/symbolic/global-bifurcation result and certify
  a decisive subset with validated numerics.
- [ ] **AI-007 — Optional observation-only study.** Partial/noisy observations,
  delay-coordinate sections, and later circuit data; not a core dependency.

## Checkpoint policy

Commit and push after a coherent, verified milestone—not each file edit. The
current planned checkpoints are: reference core; event/classifier vertical
slice; first tiny atlas; GPU qualification; and each frozen experiment result.

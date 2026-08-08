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
  square-root branch opening (`0.49896`, `R^2=0.9999992`) and ratio-two
  multiplier scaling (`1.9805` median). EXP-032 through EXP-034
  resolve thirteen coupled `+1` events on a smooth fixed-`c=5.1` curve over
  `a in [0.235,0.265]`, reaching `b=0.347875`; natural continuation fails below
  `a=0.235`. EXP-035's full event-system pseudo-arclength crosses that boundary
  with thirty accepted points and finds one reversal in each of the `a` and `b`
  projections. Continuation of this fold-safe set in `c`, plus normal-form
  qualification away from the source, are the next surface-building steps.
  EXP-036 supplies a thirteen-point transverse `c` spine. EXP-037 honestly
  fails at one coarse corner; EXP-038 resolves the same domain at half-step and
  passes all 45 coupled events, establishing the first local `b*(a,c)` surface
  patch. EXP-039 qualifies the separated `c=4.9` point: exponent `0.49867`,
  `R^2=0.9999989`, multiplier ratio `1.9851`, and stability exchange at every
  frozen offset.
  EXP-040 passes the same gates at the event curve's minimum-`b` fold:
  exponent `0.49288`, `R^2=0.9999691`, ratio `1.99691`, and all-point stability
  exchange. EXP-041 resolves the formerly open mechanism at all three points:
  each stored parent closes at half-period, has a fundamental multiplier `-1`,
  and its doubled monodromy produces the observed `+1`. The object is therefore
  a fundamental period-doubling surface, not an unexplained spatial pitchfork.
  EXP-042 directly confirms the off-event outcome at all three points: unstable
  fundamental parents, stable children that fail half-period closure, and
  child/parent period ratios within `0.00036` of two. Local classification is
  closed numerically. EXP-043 then traces five fold-safe fixed-`c` sections: its
  formal gate fails because the `c=4.9` curve itself reverses before a frozen
  minimum-`a` reach, while four sections show the target `b` reversal. EXP-044
  extends the unresolved `c=5.3` section and finds its reversal. EXP-045
  refines all five minima into a smooth local fold line over `c in [4.9,5.3]`,
  with monotone drift and quadratic descriptive fits above `R^2=0.9999992`.
  Independent atlas-boundary overlays, global surface continuation, validated
  samples, equilibrium/Hopf, and TBA remain open.
  EXP-046's independent atlas overlay rejects the inherited period-5/10
  identity and reveals period-3/6 alignment instead. EXP-047 directly confirms
  all tested parents as period 3 and all children as period 6. The surface/fold
  geometry is retained and reclassified; locating the earlier continuation
  family switch is now mandatory.
  EXP-048's long-horizon audit fails methodologically on unstable cycles.
  EXP-049's one-traversal invariant count then shows EXP-023 was never one
  period-5 family: 40/46 rows are double-covered period 3, five are period 5,
  and one is period 4. Rebuild identity-constrained continuation from the last
  verified EXP-022 period-5 seed; do not reuse EXP-023 as a family branch.
  EXP-050 completes that rebuild: 19 identity-safe period-5 points span
  `b=0.173669..0.204808`, wrong-family six-crossing roots are rejected at both
  ends, and a genuine `-1` crossing is bracketed at `[0.1825,0.185]`.
  EXP-051 refines the flip to `b=0.183467590772`. EXP-052/053 switch and
  independently qualify its stable period-10 child, proving a supercritical
  period-5-to-period-10 flip. EXP-054 rejects a step-size-dependent crossing
  count as a transition estimate; EXP-055 instead refines the continuous
  section-boundary grazing at `b=0.181750232321` while the child remains
  strongly stable. Next extend the period-10 child without using raw crossing
  count as an identity gate, then continue both the flip and grazing conditions
  in `(a,b,c)`.
  EXP-056's long extension detects and quarantines a one-row hop to the
  double-covered parent. Its uncontaminated prefix exposes the next child
  event; EXP-057 refines the true period-10 `-1` crossing to
  `b=0.180537208202`. Switch and qualify the period-20 child next.
  EXP-059/060 complete that period-20 qualification. EXP-062/064 then locate
  and independently qualify the supercritical period-20-to-period-40 rung at
  `b=0.179891223762`, including recovery from a perturbed trajectory. Refine
  the bracketed period-40 event, then estimate convergence of the cascade
  parameters without assuming Feigenbaum universality from three intervals.
  EXP-072 validates the frozen period-80 event prediction within `1.398e-7`;
  EXP-073/074 then switch and qualify the stable period-160 child. Refine the
  bracketed 160→320 event, but require a separate period-320 qualification
  before extending the supercritical cascade claim.
  EXP-077 resolves that event at `b=0.179713883301`; its spacing ratio is
  `4.664603`. Next switch and independently qualify period 320. Before going
  materially higher, benchmark multiple-shooting/collocation and remote CPU
  parallelism because single-shooting orbit duration has reached `~2092`.
  EXP-078 confirms the single-shooting branch switch is ill-conditioned.
  EXP-079 passes a 1/2/4/8/16/32-segment audit: 32 segments improve the event
  singular value by `854x` at `1.25e-9` matching residual. Implement the sparse
  multiple-shooting corrector, validate on a known lower-period child, then
  retry period 320. Parallelize segment/tolerance audits on remote CPU; profile
  before allocating GPU spend.
  EXP-090/091 now switch and independently qualify a stable period-640 child.
  EXP-092 freezes the 640→1280 prediction at `b=0.1797121964470`; EXP-093 is
  passed with a signed `-1` bracket `[0.17971219,0.17971220]` whose midpoint
  misses the frozen prediction by `1.447e-9`. Refine the event with a bound
  signed residual before attempting a period-1280 branch switch. EXP-094
  through EXP-096 and the precision-audited EXP-098/099 honestly miss the
  frozen pointwise residual gate despite a final `3.22e-15` sign bracket.
  Implement DEC-003's augmented anti-periodic multiple-shooting solve, validate
  it on EXP-089, and only then decide the period-640 event. EXP-100 freezes the
  32-segment known-event validation with a deliberately perturbed seed. It
  fails at the 30-evaluation cap after `2367 s`: the anti-periodic tangent
  residual reaches `2.14e-9`, but orbit matching remains `1.73e-7` and the
  parameter error is `4.91e-9`. Implement the exact second-variational
  Jacobian, explicitly select the independent flip cluster by proximity to
  `-1`, and repeat the known-event validation before touching period 640.
  EXP-101 freezes that analytic 32-segment rerun with the same perturbed source
  and unchanged scientific gates. It fails at the 20-evaluation cap but reaches
  orbit/tangent residuals `1.78e-9`/`1.77e-10`, corrects the spectrum-label
  bug, and runs `11.4x` faster; its `1.086e-9` reference error still misses the
  `5e-10` gate. EXP-102 freezes one exact-Jacobian resume from the full EXP-101
  orbit and tangent state under unchanged scientific thresholds. It passes at
  `b=0.17971249399303613` with `8.94e-13` reference error, orbit/tangent
  residuals `9.21e-13`/`1.01e-11`, and block/direct agreement `8.88e-15`.
  EXP-103 freezes the validated 64-segment application to EXP-099's period-640
  source inside the audited EXP-093 signed bracket. It passes at
  `b=0.17971219643223899` with prediction error `1.476e-11` and direct flip
  residual `1.90e-10`. Next freeze a period-1280 branch switch, then require
  independent common-parameter identity and Floquet stability before adding an
  eighth supercritical rung. EXP-104 freezes the tangent-informed 128-segment
  switch at two amplitudes and both signs. All four candidates pass, with
  matching residuals below `2.24e-12` and amplitude-scaling distinctness.
  EXP-105 freezes the independent common-parameter identity and 128-block
  Floquet qualification at `b=0.17971215`. It passes with whole-orbit RMS
  `3.94e-8` and stable moduli near `0.426174`, closing the eighth local
  supercritical rung. Return the primary execution frontier to orbit-defined
  flip/grazing surfaces and the reviewer-identified global topology gaps.
- [ ] **P1-006 — Jones path definitions.** Exact `L1`/`L2` parameterizations and
  caustic/window-order reconstruction.

## P2 — topology, validation, and atlas expansion

- [ ] **P2-001 — Return-map topology.** DEC-004 now defines a gated scalar
  return-map oracle with graph-likeness, domain coverage, critical-point
  prominence, bootstrap uncertainty, and explicit unresolved results. Synthetic
  one/two/three-branch and multivalued controls pass. Freeze the first Rössler
  section/coordinate calibration, then add partitions, kneading data, entropy,
  and coordinate/section sensitivity.
- [ ] **P2-002 — Global bifurcations.** Homoclinic/heteroclinic boundary-value
  problems and bounded focal-point uniqueness claim.
- [ ] **P2-003 — Validated numerics.** Interval validation of selected decisive
  orbits, windows, crossings, and forcing/covering statements.
- [ ] **P2-004 — Two-system qualification.** Add two structurally different
  chaotic flows before scaling the registry.
- [ ] **P2-005 — Dozens-system atlas.** Curated systems, prospective parameter
  planes, negative results retained, uniform provenance and publication pipeline.

## Original peer-review closure gates

These gates are binding consequences of the LN13044/Jones referee reports. See
the full [`peer-review gap audit`](reviews/2026-08-07-jones-peer-review-gap-audit.md).
High-period cascade evidence does not substitute for these topology and
exposition requirements.

- [ ] **RVR-001 — Terminology and mathematical objects.** Define the flow,
  section, two-dimensional return map, invariant domain, quotient, and finite
  symbolic comparison separately; enforce the terminology in the manuscript.
- [ ] **RVR-002 — Attribution and novelty.** Primary-source verification of the
  earlier TTL/TBA result, Jones Ref. 6, Holmes, Lefranc, homoclinic foundation,
  and the precise 2012 co-discovery boundary; publish a novelty matrix. The
  referee-named sources are now resolved in `paper/references.bib`, cited in
  the draft, and tracked by `paper/reference-ledger.md`; close reading and the
  full novelty matrix remain open.
- [ ] **RVR-003 — Two/three-branch oracle.** The DEC-004 implementation now
  supplies critical-point prominence, invariant-domain coverage, graph-
  likeness rejection, bootstrap branch classification, and synthetic controls.
  Rössler calibration, transition continuation, and section-perturbation
  robustness remain open. EXP-106 freezes the first calibration on the
  published chaotic `(a,b,c)=(0.2,0.2,20)` control across three nearby section
  offsets, prospectively expecting a robust two-branch relation. It fails that
  expectation because all three sections give three branches with 100/100
  bootstrap agreement and critical-point drift only `~2.2e-6`. Freeze a
  coordinate/orientation/threshold/nearby-parameter sensitivity audit before
  continuing any transition curve. EXP-107 completes that audit: all 105
  negative-oriented `x` cells and all 105 `z` cross-checks resolve as three
  with consensus `1.0`. The strong orientation-invariance diagnostic fails
  because the positive half-plane is not a stable scalar graph. Continue the
  qualified negative-map two/three boundary, but carry the two-dimensional map
  into any topological or reinjection interpretation. EXP-108 first freezes a
  direct control on the distinct Barrio section `x=x_minus`, `dx/dt>0`, using
  the paper's `a=0.11` unimodal and `a=0.2` bimodal chaotic attractors. EXP-108
  passes all 84 primary/cross-coordinate cells. Freeze the first `a`-path
  boundary search now; retain periodic windows as unresolved until a
  chaotic-saddle method is qualified. EXP-109 preregisters that 21-point
  attractor-only path, including both published saddle controls and an ordered
  two/three bracket gate. It passes with an uncertainty band `[0.155,0.16]`,
  five explicit period-4 gaps, and three coverage-unresolved gaps. The binding
  next gate is a saddle method that reproduces the published two-branch saddle
  at `a=0.118` and three-branch saddle at `a=0.149`. EXP-110 preregisters a
  CPU reference sprinkler ensemble with repeated-cycle capture, middle-time
  survivor pairs, two-coordinate branch gates, and an independent DOP853
  capture audit. EXP-110 fails prospectively: its `a=0.118` saddle is robustly
  two-branch, while the shallow extra extremum at `a=0.149` falls below the
  frozen 3-percent prominence threshold; pointwise long-horizon capture labels
  agree only 25/32. Freeze a local-uncertainty critical-point rule and
  ensemble-statistical step/horizon/grid convergence before GPU scaling.
  DEC-006 and EXP-111 now freeze that successor: 15 oracle perturbations across
  five step/horizon/grid ensembles, plus a short-horizon DOP853 audit. EXP-111
  passes all 300 topology cells but fails regular-grid survivor-fraction
  convergence and one linear-interpolation time audit. Replace the grid family
  with independent scrambled Sobol ensembles and linear crossing location with
  cubic Hermite interpolation, then repeat prospectively. DEC-007/EXP-112 now
  freeze three scrambles, three nested sample sizes, step/horizon controls, and
  the unchanged topology/survival/short-horizon acceptance thresholds. EXP-112
  passes all gates and qualifies the finite-time CPU sprinkler at both
  published controls. Next: independent PIM/stagger-and-step corroboration,
  CPU/GPU statistical parity, then saddle-defined TBA continuation.
- [ ] **RVR-004 — Finite logistic ordering.** Recover `L1`/`L2`; verify all
  period-through-seven permutations and kneading data; prospectively locate
  the first higher-period disagreement or establish a declared finite bound.
- [ ] **RVR-005 — Third-branch reinjection.** Define it in the return map or via
  a robust invariant, test coordinate/section sensitivity, and compare its
  predictions with TBA and homoclinic-sheaf alternatives.
- [ ] **RVR-006 — Unfolded spiral.** Replace Fig. 6 with a machine-generated,
  receipt-bound explanation of branch count, critical values, symbolic words,
  and `p -> p+1` transitions over complete spiral turns.
- [ ] **RVR-007 — Exploit/generalize.** Make held-out symbolic/curve predictions
  on Rössler, then freeze the qualified method on two structurally different
  flows before claiming broad generality.
- [ ] **RVR-008 — Manuscript exposition.** Equations and definitions first;
  complete citations; plain-language mechanism; claim/evidence/limitations
  conclusion; independent readability review.

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

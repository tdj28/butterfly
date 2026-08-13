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
  remote/local hashes, and ends with every task-owned pod terminated. EXP-113
  separately qualifies the production chaotic-saddle observable on an RTX
  A5000: both controls retain the CPU two/three topology, the largest survivor
  difference is `1/8192`, DOP853 audits pass, receipt hashes match, spend is
  bounded below `$0.06`, and no pod remains active.
- [ ] **P1-004 — Forced-kill/resume test.** Immutable tile IDs, atomic completion,
  corruption rejection, simulated interrupted-write recovery, and an actual
  mid-computation process kill/restart pass locally. Remote container/storage
  repetition remains required before interruptible production use.
- [ ] **P1-005 — Continuation layer.** Hopf/equilibrium/periodic-orbit branches,
  Floquet multipliers, TBA/TTL curve, topology-change locus, independent cross-check.
  EXP-153 passes an exact 192-point regular small-equilibrium Hopf locus at
  `b=0.2`, with independent eigensystem roots and transverse sign gates. At
  `a=0.1798`, the Hopf endpoint is `c=0.5192306256940273`; period-1 continuation
  toward the reported hub is frozen as the 118-point, Radau-cross-checked
  EXP-154 qualification. EXP-154 passes every scientific gate but fails its
  cardinality gate after duplicating the seed; direction-aware, unchanged-gate
  successor EXP-155 passes. It follows the one-winding family to the reported
  hub coordinate,
  qualifies exponent `0.5017311`, and brackets its first `-1` multiplier
  crossing. EXP-156 passes the coupled exact-`c` flip refinement at
  `c=3.1807265333384103`. EXP-157 switches the doubled-cover nullspace onto a
  nontrivial child, and EXP-158 independently qualifies the two switch signs
  as one primitive stable period-2 orbit at `c=3.1845`, paired with the
  unstable period-1 parent. EXP-159 honestly records natural-parameter identity
  loss; pseudo-arclength EXP-160 then preserves the child and brackets its next
  crossing. EXP-161 solves the exact period-2-to-4 flip at
  `c=4.3100451384813105`; EXP-162/163 switch and independently qualify the
  stable primitive period-4 child at `c=4.318`. EXP-164/165 continue that child
  and solve its exact period-4-to-8 flip at `c=4.636447200967924`; EXP-166/167
  switch and independently qualify a stable primitive period-8 child at
  `c=4.65`. After preserving EXP-168's cardinality failure and EXP-170's
  equal-modulus block-clustering failure, EXP-169/171 locate the exact next
  flip at `c=4.7090113823613065`; EXP-172/173 independently qualify a stable
  primitive period-16 child at `c=4.716`. Before continuing to period 32,
  replace single-shooting branch switching with segmented switching and make
  long recovery checkpointed/parallel. Separately reconstruct the historical
  paths and symbolic partition needed to decide ordering through seven. The
  source audit now establishes that Figure 2 draws horizontal `L1` and vertical
  `L2` examples without printing exact equations; Figure 6 is transcribed into
  23 words and 11 arrows, but its reproducible partition remains absent.
  DEC-014's neutral encoder and synthetic assignment controls now pass.
  EXP-175 qualifies its fresh split-cloud `x` partition, while held-out `z`
  retains one bootstrap-power failure at 50 bins despite six other resolved
  three-branch variants. Frozen unchanged-threshold EXP-176 then passes with
  1000 calibration and 1000 validation pairs: every `x` and `z` variant
  resolves three branches. EXP-177 now qualifies the corresponding two-branch
  dense control in all `x` and `z` variants. EXP-178 prospectively selects the
  higher-coordinate trimodal critical in both observables, but preserves a
  failed `0.010` resolved bracket against the frozen `0.005` gate. The
  unchanged-threshold, higher-power EXP-179 successor also fails: x gives a
  `0.0065` bracket, while the fully cross-coordinate bracket is `0.0075` and
  global branch detection is coordinate-staggered. Fresh-trajectory EXP-180
  then locally tracks the same critical at 20/21 DOP853 points and 4/5 Radau
  controls and selects trimodal index 1 at the endpoint, but retains a
  solver-independent support hole at `a=0.156`: only `14–23.3%` of bins are
  occupied. EXP-181's 64,571-pair survivor cloud hits both frozen physical
  critical predictions and passes all local variants, but its long-time
  fixed-step/DOP853 pointwise capture audit fails at 62.5%. Freeze an EXP-113-
  style successor using survivor-statistic and critical-location parity across
  RK4 step sizes, attractor false-negative controls, and only short-horizon
  DOP853 state/event comparisons. Unchanged-science EXP-183 now passes every
  gate: survivor fractions differ by `0.016724`, both physical criticals agree
  across steps and hit the flank predictions, all attractor controls capture,
  and five-return DOP853 errors are tiny. The local critical identity is
  qualified. EXP-184 now freezes the source-derived neutral-to-Jones mapping
  before any target word is evaluated. Its pre-integration receipt-field
  failure is preserved, and scientifically unchanged EXP-185 passes its full
  two-solver physical-geometry gate. The operational mapping is qualified. A
  landmark-0 sizing diagnostic exposes a noncritical exact orbit and x/z
  projection split. Untouched-landmark EXP-186 then qualifies an exceptionally
  accurate period-6 orbit and step-stable x survivor partition, but fails x/z
  parity and target-word membership: the exact printed coordinate is not a
  reproducible word center. Next freeze a target-word-blind local search for
  the actual period-6 superstable center using periodic-orbit stability and
  criticality; encode its word only after selecting the center. EXP-187 now
  freezes the first half of that search: a signed Floquet saddle-zero atlas,
  three shrinking refinements, and DOP853/Radau ring validation. EXP-187
  preserves a first-step resolution failure while bracketing multiple signed
  zeros inside one coarse cell. EXP-188 freezes that cell at tenfold finer
  resolution with unchanged scientific gates. It resolves 289 cells but fails
  coverage and saddle refinement: 65 zero edges show that the period multiplier
  conflates multiple phase/critical sheets. Freeze a GPU-parallel scan of all
  qualifying zero edges using two independent survivor-derived critical-to-
  orbit residuals; require both critical memberships before encoding. EXP-189
  now freezes the deterministic all-edge interpolation and period-6 correction
  stage. All 65 candidates pass with closure below `1.83e-12`. EXP-190 binds
  the full artifact and executes the two-step GPU reconstruction. All 130 maps
  are robustly two-branch, rejecting the first landmark's Floquet-zero
  neighborhood as a two-critical center location. A post-result diagnostic at
  the other exact period-6 landmark `(0.215,7.6)` finds a three-branch Barrio-
  section z map and one near-critical orbit phase. Prospectively map that
  landmark's complete stable period-6 window at high resolution, correct its
  interior cycles, and solve the two critical residuals without symbolic data.
  EXP-191 now resolves 40,401 points around that second landmark. Its anchor
  belongs to a coherent 981-pixel period-6 component over
  `a in [0.2145,0.21555]`, but the component exits both sampled `c` boundaries.
  Expand the atlas vertically through both exact period-6 landmarks, report
  their nearest-pixel component membership without inferring continuation,
  then correct cycles along any shared band and solve the two direct critical
  residuals. EXP-192 now completes that expansion: both source landmarks are
  period 6, but the first is not in the second landmark's 2,598-pixel anchor
  component. Treat them as distinct stable raster windows. Prepare a
  geometry-only sample of the second component, recover its six section
  phases, and scan the explicitly declared Barrio-section z return map for two
  critical-to-orbit residuals before any word is encoded. Test possible
  unstable continuation between the two windows separately. EXP-194 corrects
  58 stable historical period-6 flow orbits but shows that each has eight,
  rather than six, phases on Barrio's positive-x section. Requalify only that
  section count in EXP-195, then scan both critical residuals against all eight
  Barrio phases. EXP-195 passes 58 immutable candidates. EXP-196 then exactly
  matches CPU/GPU survivor and return-pair counts at both RK4 steps and
  qualifies the three-branch z-map kernel. EXP-197 executes the direct scan
  over all 58: 31 candidates pass cross-step representation gates, but none
  passes both critical-interval and assigned zero-slope gates. Freeze a dense
  local two-residual refinement around the prospectively selected
  `(a,c)=(0.21555,7.372)` point, then independently correct and audit any root.
  EXP-198 executes the prerequisite 2,511-point DOP853/Floquet orbit mesh
  without looking at dense critical residuals. Its center and 685 individual
  points pass, but the 1,000-point coverage gate fails and the center's
  152-point component touches the lower-a boundary. Freeze any GPU use of the
  685 points as an explicitly incomplete diagnostic, retain signed residuals,
  and extend the mesh before making an exhaustive local claim. EXP-199 now
  executes that diagnostic with tighter direct-point gates and a two-step,
  same-phase four-corner signed-bracket rule. Of 126 cross-step-qualified
  points, none passes any direct gate and no cell brackets both residuals: the
  first signed residual crosses zero, while the second remains strictly
  positive. Continue the stable family beyond the fragmented qualified mask,
  following the one-sided second residual rather than densifying the same
  rectangle; keep unstable inter-window continuation as a separate test.
  EXP-200 now freezes the first discriminator: a fourfold-support replay on
  all 168 already-qualified stable orbits in the lower-`c` target rectangle,
  with the same oracle and direct-center gates. Execute it, then either solve
  a new simultaneous bracket or replace support refinement with explicit
  critical-edge continuation if the second branch remains unresolved.
  EXP-200 fails strict recovery with 8/40 cross-step candidates, but 125 points
  are three-branch under all four baseline variants and 104 of those collapse
  to two only under high smoothing at both steps. Freeze a logarithmic
  smoothing ladder with nested 2,048/8,192 support on that complete 104-point
  sensitivity set. Continue the residual only if its critical identity and
  smoothing-transition scale converge. EXP-201 passes that gate with 94/104
  candidates: 86 have exact four-profile transition-index agreement, eight
  differ by one ladder step, and every qualified critical-location span is
  below `0.01680` versus the `0.03` ceiling. Freeze a scale-ensemble signed
  residual from the low-smoothing three-branch regime, then test it before
  extending the corrected-orbit mesh. EXP-202 now freezes that audit over the
  universally three-branch smoothing indices 2--4, requiring one phase
  assignment and both residuals to pass at all 12 scale/support/step views.
  EXP-202 retains all 94 candidates and assignment `[7,5]` but fails: the
  second residual is positive in all 1,128 views (`min=0.019945`). Extend the
  corrected stable family toward lower `c`, preserving the same scale ensemble;
  keep unstable inter-window continuation as a separate prospectively frozen
  experiment. EXP-203 now freezes a 6,283-point DOP853/Floquet extension over
  `a in [0.2155,0.2161]`, `c in [6.88,7.288]`, with no critical reconstruction
  until its orbit-coverage result is sealed. EXP-203 completes but fails
  coverage with 551/1,000 qualified orbits in five bounded components; 4,921
  points first fail correction and 806 first fail stability. Freeze a residual
  replay on the 551 points, and separately continue the stability/fold boundary
  or unstable family rather than extrapolating through the failed region.
  EXP-204 now freezes the first branch: fresh two-step GPU trajectories and 12
  scale/support/step residual views over all 551 candidates, with a 250-point
  coverage gate and strict direct/bracket nomination rules. Independently,
  EXP-205 passes scalar refinement of all seven real `-1` period-6 Floquet
  brackets across `c in [7.192,7.288]`, with `7.63e-11` maximum bracket width
  and exact two-section identity. EXP-206 passes exact-Jacobian coupled
  continuation at all 41 fixed-c points across `c in [7.16,7.32]`, with
  maximum orbit residual `1.10e-11`. EXP-207's strict doubled-period
  nullspace-switching gate fails at `c=7.18,7.24,7.30`: it does not produce the
  frozen eight points in either direction. Each negative direction nevertheless
  yields one accurate, stable 12-historical/16-Barrio-phase candidate separated
  from the doubled parent. EXP-208 independently recorrects all three with
  DOP853 and Radau and passes every primitivity, period-ratio, stability-
  exchange, identity, and section-count gate. EXP-209 passes fixed-`c` child
  continuation at all three slices: opening exponents are
  `0.50258--0.50350`, multiplier-ratio medians are `4.034--4.047`, and all
  cross-solver and two-sided attraction gates pass. EXP-210 now freezes a
  31-by-4 fixed-parameter period-12 surface patch. EXP-210 completes but fails:
  16/124 child corrections collapse to the doubled parent and corrupt the
  surface fits. EXP-211 then passes all 124/124 cells from independent EXP-209
  anchor interpolation with zero fallbacks. Its 31 opening exponents are
  `0.50264--0.50309`, minimum `R^2=0.99999696`, and maximum adjacent-orbit RMS
  is `0.00502`; retain EXP-207's multi-point-arm and EXP-210's root-selection
  failures while continuing the qualified sheet toward endpoints and a future
  independently defined TBA curve. EXP-212 now freezes 100 exact-Jacobian
  pseudo-arclength points in each direction from EXP-206, with broad-`c`
  coverage and remote Radau gates, before extending the children.
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
- [ ] **P1-006 — Jones path definitions.** Source audit is complete. Publish the
  qualified fixed-`a=0.1798` path as `L2`-like; freeze both a visible fixed-`c`
  `L1` segment and a full endpoint-matched `L1` control because the paper prints
  no exact equations. Reconstruct caustics/window ordering under both and retain
  disagreement.

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
  published controls. EXP-113 then passes the Float64 Triton parity gate on an
  RTX A5000: all 30 topology cells agree, one of 8192 survivors differs at one
  final checkpoint, and all critical-location and DOP853 gates pass. Next:
  independent PIM/stagger-and-step corroboration, then saddle-defined TBA
  continuation through the regular gap. DEC-008 and EXP-114 now freeze the
  independent route: strict PIM triples, adaptive DOP853 returns, five declared
  section straddles per control, zero censoring, the unchanged robust branch
  oracle, and direct critical-location comparison against EXP-112. EXP-114
  fails the complete zero-censor gate: all five unimodal and two bimodal lines
  exceed 256 returns. Its three complete bimodal straddles nevertheless yield
  2997 pairs, three branches in both coordinates, oracle consensus `1.0`, and
  CPU/PIM critical spans below `0.01263`. Freeze a right-censor-aware PIM rule
  with nested-horizon stability; do not relabel EXP-114. DEC-009 and EXP-115
  now freeze the order-certified lower-bound rule, three section lines, two
  censor horizons, and all acceptance gates before target execution. EXP-115
  then fails honestly: both 64-return profiles are support-unresolved, while
  both 128-return profiles pass with two/three branches in both coordinates,
  consensus `1.0`, and maximum CPU/PIM span `0.01511`. Freeze a 128-versus-256
  successor before saddle-boundary continuation; retain 64 returns as a
  negative coverage control and do not relabel EXP-115. EXP-116 now freezes
  the hashed 128-return intervals, computes only a new 256-return profile, and
  retains the same two-control/two-coordinate/oracle/CPU gates plus a `0.04`
  128/256 critical-span ceiling. EXP-116 passes: all six lines resolve, all 60
  topology cells return the expected two/three distinction, no integration
  fails, and the maximum 128/256 span is `0.01601`. Freeze saddle-defined
  continuation through the regular gap; do not spend another control-only run.
  EXP-117 now preregisters the first held-out continuation: reuse the complete
  qualified EXP-112 ensemble at all five known period-4 cells on the published
  `c=20,b=0.2` path, leave the three interior branch labels blind, and require
  one ordered two-to-three transition before any refinement or curve fit.
  EXP-117 fails the complete gate but qualifies the blind `a=0.140`
  two-branch saddle, narrowing the resolved saddle bracket to `[0.140,0.149]`.
  `a=0.145` is support-unresolved (72/90 attempted variants resolve as two;
  none as three), and `a=0.120` fails only its too-short cycle-recurrence gate.
  Before scaling the `0.145` ensemble, freeze a multi-burn-in topology and
  Lyapunov audit of EXP-109's adjacent two-branch `a=0.150` aperiodic candidate;
  do not assume a single monotone path across the apparent `0.149/0.150`
  reversal. EXP-118 now freezes that audit: four burn-ins, four additional
  Sobol section seeds at the longest burn-in, both coordinates, the full
  15-variant oracle, and two independent Lyapunov algorithms with no expected
  branch label. EXP-118 fails the strict full gate but removes the alleged
  robust reversal: both Lyapunov cases classify chaotic, 46/48 coarse 20-bin
  cells return two, and 189/192 30--80-bin cells return three, with no opposite
  votes. Freeze new-data resolution convergence with 20 bins as an explicit
  under-resolution control, and repeat the trace identity at tighter solver
  tolerance before returning to the `a=0.145` support hole. EXP-119 now freezes
  five 2400-return datasets with new Sobol seed 119, separate coarse and
  adequate-resolution gates, comparison against the hashed EXP-118 critical
  intervals, and two tighter-tolerance Lyapunov replications. EXP-119 passes:
  30/30 coarse cells reproduce two, 120/120 adequate-resolution cells return
  three, maximum combined critical span is `0.01807`, both Lyapunov cases
  classify chaotic, and trace errors fall to `1.25e-7`. The `0.149/0.150`
  contradiction is closed as under-resolution. Return now to the `a=0.145`
  support hole with a prospectively larger ensemble and the qualified
  resolution-group rule. EXP-120 now freezes eightfold support at every
  corresponding sprinkler run (`2^15,2^16,2^17` nested sizes), two new
  scrambles, the unchanged 15-variant/full-consensus gate, and the prospective
  expectation of two branches supported by all 72 resolved EXP-117 variants.
  EXP-120 fails the full gate after decisively closing support: 105/105 `y`
  cells resolve as two; 84/105 `z` cells resolve as two; and the remaining 21
  are exactly the 80-bin cells, all coverage-censored with one nominal critical
  point and no contradictory topology. Freeze a coverage-censor rule on new
  ensembles and require it to reproduce both published controls before using
  it to qualify `a=0.145`; do not buy more support for an intrinsic projection
  gap. EXP-121 now freezes that rule: at least 12/15 variants must resolve
  normally, every censor must fail only coverage at or above `0.65` while
  retaining the expected nominal critical geometry, and all critical points
  must satisfy the unchanged drift gates. Seven new seed-123--125 ensembles
  test both published controls and `a=0.145`; any noncoverage failure or
  contrary branch count fails the experiment. EXP-121 passes from clean commit
  `8d96f1c`: all 420 control variants resolve normally; `a=0.145` returns 105
  fully resolved `y` variants, 84 fully resolved `z` variants, and 21 admissible
  coverage censors with no rejection. The ordered labels are `2,2,3`, narrowing
  the sampled saddle bracket to `[0.145,0.149]`. Freeze the now-qualified rule
  and begin adaptive saddle continuation inside this bracket, then extend
  outward through additional regular gaps; do not claim a continuous TBA from
  three samples. EXP-122 now freezes the first adaptive midpoint at `a=0.147`
  with no expected label. Candidate counts two and three are tested separately
  under the qualified censor rule, and exactly one count must pass in all seven
  new seed-126--128 ensembles and both coordinates. A pass halves the sampled
  bracket; a failure is retained without choosing the majority label. EXP-122
  passes from clean commit `57e629b`: all 14 blind decisions uniquely select
  two, 207/210 variants resolve normally, and three are admissible coverage
  censors. The sampled bracket halves to `[0.147,0.149]`. Freeze the next blind
  midpoint at `a=0.148` with the same rule and independently chosen ensembles;
  continue bisection only while the invariant-set and numerical gates remain
  qualified. EXP-123 now freezes that blind midpoint on new seeds 129--131 and
  a prospectively reduced `2^13,2^14,2^15` ladder; the unchanged support floors
  make inadequate down-scaling a retained failure. EXP-123 fails despite
  passed support and numerics: six 300-unit runs expose three branches in all
  `y` and adequate-resolution `z` variants, while the 360-unit survivor subset
  returns two in both coordinates. Retain `[0.147,0.149]` and freeze nested
  360--480 survivor-conditioning horizons at `a=0.148`; do not resume spatial
  bisection until branch count and critical geometry stabilize with lifetime.
  EXP-124 now freezes those horizons on new seeds 132--134, centered return
  windows, step halving, and a `2^15,2^16,2^17` ladder. All eight runs must
  blindly choose one common count and retain the original support floors.
  EXP-124 fails that strict gate: 12/16 decisions and 228/240 variants resolve
  as two, none as three, while exactly twelve 80-bin variants are bootstrap-
  unstable in four low-effective-power decisions. The doubled 420-unit sample
  restores two in both coordinates; the 480-unit sample retains only 121
  survivors. Retain the bracket and freeze a censor-aware PIM test at
  `a=0.148`, followed by branch-conditioned lifetime tests; do not convert
  rare-survivor bootstrap failures into an affirmative label. EXP-125 now
  freezes that blind test: the qualified censor-aware PIM method must agree in
  `y` and `z` at both 128- and 256-return ceilings without an encoded expected
  count or sprinkler critical-point reference. EXP-125 passes: all six PIM
  straddles complete, all 60 oracle cells select two, critical spans converge,
  and no lifetime integration fails. The finite sampled bracket narrows to
  `[0.148,0.149]`. Freeze a blind `a=0.1485` midpoint with the same independent
  PIM definition, and quantify escape lifetime conditional on the transient
  third branch before interpreting reinjection. EXP-126 now freezes that
  midpoint with unchanged 128/256 censor ceilings, access lines, oracle matrix,
  and numerical gates; no expected count or prior critical location is encoded.
  EXP-126 passes as three in all 60 oracle cells with all six straddles and
  critical-drift gates passing. The finite bracket is now `[0.148,0.1485]`.
  Add a branch-conditioned escape diagnostic, then freeze `a=0.14825` under the
  identical PIM definition; do not confuse further bisection with independent
  continuation of a TBA curve. EXP-127 now freezes that diagnostic: the full
  EXP-123 `y` critical-point uncertainty bands define the extra and core
  domains before new data, one last pre-landmark crossing assigns each
  trajectory once, seeds 135--137 test a 99% bootstrap RMST contrast and
  log-rank gate, and a seed-135 half-step repeat gates numerical drift. EXP-127
  passes every quality gate but rejects faster capture: all three evidence
  intervals are strictly positive near `+30` units, and the half-step shift is
  only `0.40`. The extra branch has delayed but bounded capture (survival `1`
  at residual 60 and `0` at 180), while the core captures earlier on average
  but retains a rare tail through 270. Freeze the `a=0.14825` PIM midpoint;
  subsequent reinjection work must use the genuine three-branch saddle from
  the upper side, not the `a=0.148` transient domain. EXP-128 now freezes that
  midpoint with the identical blind PIM method and no expected label. A two
  result yields `[0.14825,0.1485]`, a three result yields
  `[0.148,0.14825]`, and any gate failure preserves the current bracket.
  EXP-128 passes as three in all 60 oracle cells with all six straddles,
  cross-horizon critical spans below `0.00910`, and zero failed lifetime
  evaluations. The finite bracket is now `[0.148,0.14825]`. Before spending
  another hour on pure bisection, freeze a signed companion observable and test
  it prospectively. DEC-010 and EXP-129 now freeze the normalized spline slope
  at the lower occupied return-map support. All eight hashed calibration
  profiles reproduce the two/negative and three/positive mapping in both
  coordinates and all variants. The untouched `a=0.148125` midpoint must clear
  a `0.1` magnitude floor at both censor horizons and its slope-predicted class
  must equal the blind critical-point count. EXP-129 passes: all six PIM lines,
  60/60 two-branch oracle cells, and 60/60 negative-slope fits agree, with the
  weakest slope magnitude `0.4994` and no failed lifetime integration. The
  finite bracket is `[0.148125,0.14825]`. EXP-148 later passes the untouched
  midpoint `a=0.1481875` as two-branch at both horizons, narrowing it to
  `[0.1481875,0.14825]`. Leave pure one-dimensional bisection.
  EXP-130 prospectively freezes and executes a transverse `(a,c)` GPU
  discovery pilot with four controls, two fresh Sobol ensembles, half-step
  representatives, and unresolved-aware gates at `c=19.8/19.9`. It correctly
  fails: the published controls pass, but both narrow local PIM controls are
  oracle-dependent despite adequate pairs and zero numerical failures. No
  transverse bracket is claimed. FND-027 therefore rejects brute finite-
  sprinkler continuation and selects adaptive-DOP853 PIM endpoint tests at
  `(c,a)=(19.8,0.145/0.148)` and `(19.9,0.145/0.150)`. EXP-131 executes all
  four adaptive-DOP853 PIM predictions at a 128-return censor ceiling with 12
  resolved access lines and no lifetime failure, but fails the scientific gate.
  It fully passes `c=19.9,a=0.150` as three/positive and prospectively
  falsifies `c=19.8,a=0.148` as three/positive: 24/30 branch variants return
  two and all signed slopes are negative. Freeze a 256-return test under the
  independently qualified EXP-121 censor semantics at `c=19.8,a=0.148/0.150`
  and `c=19.9,a=0.145/0.150`. EXP-132 now freezes exactly that test at a
  256-return ceiling, with the strict oracle retained beside the censor-aware
  decision and bootstrap instability explicitly inadmissible. EXP-132 executes
  cleanly and fails its full gate with three of four endpoints passed. It
  qualifies the finite `c=19.9` bracket `[0.145,0.150]` and the untouched
  `c=19.8,a=0.150` three/positive endpoint. The `c=19.8,a=0.148` endpoint
  remains unresolved because its 12/15 two-branch variants and uniformly
  negative slopes are accompanied by three bootstrap-unstable high-bin
  variants per coordinate. Preserve that failure; continue only the qualified
  endpoints and replace repeated integer bisection with the prospective
  lobe/pruning residual. EXP-150 now freezes unchanged-method PIM-seeded UPO
  recovery at both endpoints of the qualified `c=19.9` bracket before
  inspecting their close returns. Execute it after the active EXP-148 worker
  pool releases, then freeze primitivity/deduplication before tracing any
  transverse lobe. EXP-151 now freezes that downstream audit in advance using
  the improved continuous-phase EXP-135 rule; after EXP-150, only its source
  receipt path/hash and identifiers may be instantiated. EXP-152 adds a tested
  adapter from those dynamic family representatives into every unchanged
  EXP-142 unstable-seed gate. Instantiate only EXP-150/151 hashes after their
  runs; trace no transverse lobe until every retained family passes.
- [ ] **RVR-004 — Finite logistic ordering.** Figure 2/6 source extraction now
  supplies operational path geometry and a hash-bound target of 23 words, ten
  matched arrows, and one visual-only arrow. DEC-014 now freezes independent
  dense-cloud partition inference before any target cycle is labeled. EXP-174
  blindly classifies the ten approximate landmarks without expected labels or
  parameter nudging. It retains a strict transient-profile failure, while all
  late DOP853/Radau comparisons agree: eight periodic labels and two unresolved
  coordinates. Preserve that failure; digitize the box-to-node associations;
  implement the partition controls, verify all period-through-seven
  permutations and kneading data, and prospectively locate the first
  higher-period disagreement or establish a declared finite bound.
- [ ] **MECH-001 — Orbit/manifold condition for the branch opening.** DEC-011
  freezes exact-return, shooting-identity, and Floquet gates for PIM-seeded
  UPOs. EXP-133 now preregisters exploratory recovery on both sides of the
  `c=20` bracket. It passes with 15 accepted recoveries, but exposes repeated
  traversals among the reported lags. EXP-134 now freezes proper-divisor and
  phase-invariant family audits. It confirms two lag-8 double traversals but
  exposes inadequate phase-grid resolution for deduplication. EXP-135 now
  passes continuous phase refinement, qualifying nine primitive families below
  and two above. Continue the shared lag-12 family across the bracket and the
  upper lag-4 family downward with fundamental identity enforced. Then seed stable and unstable manifolds from accepted UPOs and define a continuation residual
  that is distinct from the section-grazing artifact already isolated in
  EXP-055.
  EXP-136 now freezes both lag-12 directions, a midpoint whole-orbit identity
  match, and the upper lag-4 downward continuation on a `1.25e-5` grid. It
  fails strictly: lag 4 passes all 21 points, while both lag-12 paths trip the
  crossing-count gate and every flow-orbit and Floquet gate remains passed. A
  post-hoc boundary audit shows that this is a counting-window artifact: the
  initial phase sits about `1.1e-6` after the section, beyond the frozen
  terminal allowance, and `(0.1 T, 1.1 T]` restores all 12 crossings. Continue
  those closed flow orbits without section count as a stopping gate, record a
  phase-shifted count, then retry whole-orbit family matching. EXP-137 freezes
  both complete flow paths, a separate shifted-count qualification, and a
  decisive same/distinct midpoint classification. Both flow paths and all 42
  shifted counts pass, and the paths classify as distinct, but bitwise Float64
  equality rejects a `2.78e-17` midpoint representation error. EXP-138 freezes
  a `1e-14` parameter-match tolerance and otherwise repeats EXP-137 unchanged.
  It passes: two distinct primitive lag-12 UPO families coexist and persist
  across all 21 points, with 12 shifted-window crossings at all 42 path
  points. Together with lag-4 persistence, this rejects three simple
  orbit-birth/crossing mechanisms. Seed both families' invariant manifolds and
  define a pruning/reinjection connection residual that can change while the
  periodic skeleton remains intact.
  EXP-139 now freezes complete continuation of the eight remaining primitive
  lower-side families, with per-family lag identity measured on shifted
  one-period windows. Seven pass all 21 points; lag-13 family 01 stops at a
  correction closure `1.066e-10`, only `6.6e-12` above the internal numerical
  floor and far below the scientific closure limit. EXP-140 freezes a
  tenfold-tighter DOP853 rerun, passes the original stop, then encounters the
  same floor at the midpoint. EXP-141 now freezes acceptance-aligned control
  flow: optimizer success is explicit, while corrected-seed and independent
  flow closure must still pass the unchanged `1e-8` scientific limit.
  EXP-141 passes all 21 points, completing persistence of all eleven recovered
  primitive UPO families. Build phase-resolved unstable-manifold branches from
  this library, measure their first-return lobe connectivity on both sides,
  and formulate a pruning/reinjection residual with seed-size convergence.
  DEC-012 now freezes section projection and signed Floquet-amplification
  validation. EXP-142 passes all 22 family-endpoint instances and all 132
  signed seed-size trials. Trace capture-truncated first-return lobes for the
  complete library, retain seed-density diagnostics, and select—not yet
  promote—the largest cross-boundary connectivity changes for refinement.
  EXP-143 now freezes a 396-trajectory, capture-truncated lobe atlas with
  independent stable-cycle recovery, nested seed-density coverage, and an
  automatic four-candidate refinement shortlist. It passes and selects lower
  lag-12 negative, lag-7 family 03 positive, lag-5 positive, and lag-13 family
  07 positive. Endpoint occupancy remains highly overlapping; refine capture
  curves over denser amplitudes, multiple orbit phases, and longer horizons
  before defining a connection residual. EXP-144 now freezes that refinement:
  408 traces over three transported orbit phases, a nested 17/9-amplitude grid,
  and 64/96-return administrative horizons. Execute it from the clean pushed
  preregistration commit; promote only candidates with a same-direction,
  at-least-five-return endpoint shift at every phase and both horizons.
  EXP-144 fails that gate while completing every numerical trajectory: none
  of the four candidates is phase-robust and only 13/24 nested-grid summaries
  pass. Retire finite-horizon capture timing as the connection proxy. Define
  the next residual directly from stable/unstable manifold geometry or
  symbolic pruning, with an explicit null control and seed/mesh convergence.
  DEC-013 rejects backward Float64 stable-manifold tracing after a representative
  return proves effectively singular. EXP-145 now freezes a retrospective
  full-section residual: the two-side PIM saddle must exclude the UPO left
  escape lobe, while every three-side PIM access line and both horizons must
  overlap it under nested atlas density. Execute, then require a held-out
  parameter before promoting the residual. EXP-145 passes: all six two-side
  PIM profiles exclude the populated UPO lobe, while all six three-side
  profiles enter it within `2.399e-5`/`6.099e-5` fine/coarse scaled distance.
  Freeze a blind joint PIM/UPO-lobe test at `a=0.1481875`; require its branch
  class and lobe-inclusion class to agree without changing the threshold.
  EXP-146 now freezes the first half: unchanged EXP-142 gates validate all
  eleven continued UPO seeds at that exact untouched midpoint. Execute it,
  then freeze the midpoint lobe atlas before any PIM classification is read.
  EXP-146 passes all eleven instances. EXP-147 now freezes 198 midpoint lobe
  traces with unchanged capture, occupancy, and nested-density controls.
  Execute it before preregistering and running the independent midpoint PIM.
  EXP-147 passes with 989/558 fine/coarse lobe points and no integration
  failure. EXP-148 freezes the untouched midpoint PIM with expected class
  `null`; its clean eight-worker run passes as two-branch on all six
  access-line/horizon reconstructions, narrowing the finite bracket to
  `[0.1481875,0.14825]`. EXP-149 is now instantiated using only the resulting
  receipt and state-archive hashes. The EXP-149 evaluator,
  two↔excluded/three↔included decision, and all thresholds are now committed
  before EXP-148; after that run, only hash/path fields were instantiated.
  EXP-149 passes prospectively: all six blind two-branch PIM clouds contain
  zero states in the frozen UPO left-lobe region, while the independent atlas
  retains 989/558 fine/coarse lobe points. Promote lobe membership to a
  supported local mechanism observable, then define an exact
  manifold-intersection or symbolic-pruning residual.
- [ ] **RVR-005 — Third-branch reinjection.** Define it in the return map or via
  a robust invariant, test coordinate/section sensitivity, and compare its
  predictions with TBA and homoclinic-sheaf alternatives.
- [ ] **RVR-006 — Unfolded spiral.** Replace Fig. 6 with a machine-generated,
  receipt-bound explanation of branch count, critical values, symbolic words,
  and `p -> p+1` transitions over complete spiral turns.
- [ ] **RVR-007 — Exploit/generalize.** Make held-out symbolic/curve predictions
  on Rössler, then freeze the qualified method on two structurally different
  flows before claiming broad generality. The Rössler orbit-level exploitation
  now includes the 41-point EXP-206 flip curve and the 124-point EXP-211 child
  sheet with 31 square-root fits; endpoints, TBA comparison, symbolic held-out
  predictions, and cross-flow transfer remain open.
- [ ] **RVR-008 — Manuscript exposition.** Equations and definitions first;
  complete citations; plain-language mechanism; claim/evidence/limitations
  conclusion; independent readability review. The visual rebuild now
  integrates nineteen figures, a global-to-period-6 shrimp zoom, an eleven-slice
  multi-b atlas, Supplemental Movie S1, and a concise abstract. The remaining
  closure items are the complete unfolded-spiral mechanism figure and an
  independent readability review.

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

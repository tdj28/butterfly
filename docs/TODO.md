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
  EXP-212 fails the symmetric range gate: the upper 100 points reach
  `c=8.40309`, while the lower arm stops after 23 accepted points when only the
  historical count changes 6-to-7. Freeze EXP-213's continuous grazing
  refinement before continuing the invariant event through that boundary.
  EXP-213 converges the continuous root and Radau parity but fails its final
  integer-count gate because the standard collector loses the close crossing
  pair. EXP-214 now freezes extremum-partitioned counting at eight bilateral
  offsets and four Radau controls. EXP-214 passes: extremum-aware counts are
  `7,7,7,7` below and `6,6,6,6` above `c=6.93831802121`, Barrio remains eight,
  and all Radau controls agree. Continue the invariant flip curve through this
  now-qualified representation boundary using orbit/Barrio identity. EXP-215
  freezes 100 such lower-arm points, an extremum-aware seven-phase check, a
  `c<=6.05` reach gate, and remote Radau recorrection.
  EXP-215 fails its 100-point completion gate after six accepted events, but
  those events cross the qualified grazing and reach `c=6.83093` with exact
  `7/7/8` section identity and terminal Radau agreement. The rejected next
  corrector is inaccurate rather than a dynamical endpoint. EXP-216 freezes
  adaptive step-halving from the last two accepted events, without relaxing
  any scientific gate.
  EXP-216 rejects the assumed decreasing-`c` target: the locus turns near
  `c=6.83093` and returns through 21 exact events to `c=6.99993`. Its stop is
  the frozen upper `c` guard. EXP-217 expands only that guard and freezes broad
  returning-arm continuation to `c>=8.25` with the same invariant gates.
  EXP-217 passes all 135 accepted events through `c=8.25273`, with exact
  `7/7/8` identity and terminal Radau parity. The returning arm is separated
  from the original arm by `0.00891` in `a` at `c=7.16` and `0.05778` at
  `c=8.25`. Freeze held-out period-12 branch switching and stability exchange
  on the returning arm before calling the two arms shrimp boundaries.
  EXP-218 aborts before testing the prediction because its inherited symmetric
  auxiliary parent correction fails at the middle event. EXP-219 changes only
  to a successfully audited one-sided parent tangent and preserves the exact
  lower-`a` child prediction and every scientific gate.
  EXP-219 completes but produces zero candidates in both signed directions at
  all three slices; the remote doubled-period singularities are under-resolved.
  EXP-220 freezes exact augmented event recorrection and a four-scale predictor
  ladder while preserving every directional and child-qualification gate.
  EXP-220 fails its three-slice gate but qualifies four primitive stable
  lower-`a` children at the untouched near slice, paired with unstable parents
  and exact `7/8` versus `14/16` identity. The middle candidate is wrong-side
  and unqualified; the far switch yields no root. Freeze identity-safe child
  continuation from the qualified near seed toward the middle slice rather
  than interpreting remote switching failure as nonexistence.
  EXP-221 fails at its first coarse event step by selecting a primitive but
  highly unstable `14/16` root with the wrong period ratio. EXP-222 freezes a
  16-substep bridge from the closest-to-event qualified child over that exact
  interval before any longer child-sheet claim is retried.
  EXP-222 passes all 17 bridge points and three independent controls, proving
  the stable child persists across the coarse root jump. EXP-223 freezes
  adaptive bisection across all 52 event intervals to the middle slice, with a
  maximum accepted child-state step of `0.003` and unchanged science gates.
  EXP-223 rejects the full range after accepting 212 points through 45 exact
  events to `c=7.62518642`: the next narrow bracket collapses onto a
  double-covered parent as that lower-offset parent becomes stable. EXP-224
  freezes exact DOP853/Radau localization of the intervening real-`-1`
  crossing and bilateral primitive-child/double-cover qualification.
  EXP-224 stops administratively before receipt when its Radau child control
  only `5e-5` below the root fails the strict corrector success rule. EXP-225
  changes only the bilateral distance to `1.5e-4`, preserves all science gates,
  and makes qualification exceptions receipt-visible.
  EXP-225 independently localizes the real-`-1` root to `3.96e-9` across
  solvers; its left primitive child and DOP853 right double cover pass. The
  remaining failure is singular redundant-`2T` Radau correction. EXP-226
  freezes independent Radau parent correction, exact `2T` integration, doubled
  section counts, and monodromy squaring without changing any threshold.
  EXP-226 passes every gate: the parent flip crossing lies at
  `(a,c)=(0.24068435298,7.62537829761)` under DOP853, agrees with Radau to
  `3.96e-9` in `c`, has a primitive stable child before it, and a qualified
  stable-parent double cover after it. It was initially interpreted as a
  second boundary.
  EXP-227 first freezes the required local-curve gate: 21 exact fixed-`c`
  events over `c_root±2e-4`, all separated below the source returning arm,
  with endpoint/center Radau controls. Only a pass may seed broad
  pseudo-arclength continuation.
  EXP-227 passes all 21 exact events and three Radau controls while remaining
  `5.60e-7--5.85e-7` lower in `a` than the source arm. EXP-228 freezes 80
  pseudo-arclength events per direction toward `c<=7.46` and `c>=7.78`, with
  that distinctness condition enforced at every accepted point.
  EXP-228 rejects that condition after 30 down-curve and 23 up-curve points:
  exact event gates still pass, but the interpolated separation falls below
  `5e-8` in both directions. Same-`c` diagnostic corrections show that the
  EXP-227 events coincide with the known returning arm and that the apparent
  separation was chord-interpolation error. EXP-229 freezes a full 21-point
  exact-coordinate identity audit. EXP-229 passes all 21 DOP853 comparisons
  and three Radau controls: maximum `a` difference is `1.46e-14`, whereas the
  old interpolated gap is `5.60e-7--5.85e-7`. Retract the distinct-curve and
  paired-boundary interpretations; retain the valid child/stability exchange
  across the known returning flip arm. Require exact same-coordinate
  correction or certified interpolation bounds in every future branch-
  distinctness test.
  EXP-230 freezes the corrected successor: resume the last qualified EXP-223
  exact-event child at index 44, freshly solve the source arm at every direct
  or bisected `c`, retain the exact `-5.730236757e-7` offset, and attempt all
  seven remaining intervals through the middle slice at index 51. Only after
  this path passes should the child surface be expanded transversely to search
  for a genuinely distinct boundary.
  EXP-230 rejects the middle-slice target after five accepted exact-arm points,
  but for a new and informative reason: the primitive period-12 multiplier
  approaches and crosses `-1` near `c=7.6258`. EXP-231 freezes independent
  DOP853/Radau localization plus bilateral stable/unstable controls. A pass
  should seed a period-24 branch switch; do not misclassify this cascade rung
  as a child-sheet endpoint.
  EXP-231 stops before receipt on a Radau `xtol` status whose replayed closure,
  phase, neutral, and multiplier diagnostics all satisfy the existing gates.
  EXP-232 freezes a residual-safe, receipt-visible successor without changing
  the bracket or any scientific threshold.
  EXP-232 passes: roots agree to `3.38e-8` in `c`, retain primitive `14/16`
  child identity, and show `-0.998722` versus `-1.001278` bilateral
  multipliers under both solvers. Freeze multiscale period-24 branch switching
  and independent qualification; this is a cascade rung, not a sheet endpoint.
  EXP-233 freezes the first half: six predictor scales, both nullspace signs,
  and primitive `28/32` period-24 nomination gates. Independently requalify any
  survivors before calling the period-12 flip supercritical.
  EXP-233 stops before receipt on primary-family `xtol`. EXP-234 retains every
  switch and nomination gate while serializing a residual-qualified `xtol`
  exception, exactly as validated in EXP-232.
  EXP-234 still stops because its positive primary offset has raw closure
  `0.00801`, while the center and negative offsets pass near `1e-11`. EXP-235
  freezes the qualified one-sided `[-2e-5,-1e-5,0]` tangent stencil with every
  switch and period-24 gate unchanged.
  EXP-235 completes with zero candidates despite singular value `7.64e-7` and
  tangent dot `2.39e-15`. Its closest positive `0.00025` trial reaches
  residual `1.19e-5` at the 160-evaluation ceiling. EXP-236 freezes a targeted
  480-evaluation retry. That retry converges after 329 evaluations, but its
  half-period closure is `4.03e-9`: it is the period-12 parent traversed twice,
  not a primitive period-24 child. EXP-237 therefore freezes an exact
  segmented augmented solve of the period-12 flip before a segmented child
  switch; do not run another undirected full-period scale ladder. EXP-237
  passes all event and Radau gates. EXP-238 then passes and nominates primitive
  `28/32` period-24 candidates on both mode signs. EXP-239 freezes a separated
  20-step child continuation before two-solver identity, sign-equivalence,
  stability-exchange, and attraction qualification. EXP-239 passes all 20
  steps. EXP-240 proves the separated child is strongly unstable but retains
  an unresolved birth classification; EXP-241 then qualifies the near-event
  parent-unstable/child-stable pairing under both solvers, establishing local
  supercriticality. EXP-242 freezes the complete 21-row Floquet track to
  bracket the child's subsequent real-`-1` crossing. EXP-242 retains all 21
  spectra but fails when nearest-neighbor identity swaps onto the collapsed
  transverse mode. EXP-243 freezes a no-reintegration, eight-orders-separated
  reclassification before any exact next-event solve. EXP-243 passes with one
  bracket; EXP-244 qualifies the exact period-24 flip; EXP-245 nominates
  primitive period-48 children; and EXP-246 independently qualifies the
  near-event parent-unstable/child-stable pairing. EXP-247 freezes eight exact
  period-48 continuation steps toward the next multiplier scan. EXP-247/248
  pass and isolate the next bracket. EXP-249 fails an endpoint-seeded event
  solve; EXP-250's secant seed passes every DOP853 science residual but fails
  optimizer status and a long single-shot Radau replay. EXP-251 freezes an
  unchanged-threshold residual-safe segmented Radau audit, which passes and
  qualifies the period-48 flip. EXP-252 freezes the hash-bound 128-segment
  period-96 child switch and passes all six candidate attempts. EXP-253 freezes
  independent near-event parent/child stability-exchange qualification and
  passes, extending the exact locally supercritical cascade through stable
  period 96 (FND-093). EXP-254 passes every orbit gate except its phase-grid
  sign-identity resolution; EXP-255 completes the continuous calculations but
  fails administrative JSON serialization. EXP-256 freezes the scientifically
  identical corrected successor and passes, proving tangent-sign equivalence.
  EXP-257 passes a short period-96 continuation to a strongly unstable
  endpoint. EXP-258 freezes the exact-row next-flip scan without claiming
  universality and passes with exactly one real-`-1` bracket. EXP-259 freezes
  the exact 128-segment augmented event solve with segmented Radau parity and
  passes. EXP-260 freezes bilateral primitive period-192 child nomination;
  all six candidates pass. EXP-261 independently qualifies an unstable
  period-96 parent and stable primitive period-192 child under DOP853/Radau,
  promoting a fourth local supercritical rung (FND-094). EXP-262 freezes
  continuous whole-orbit phase equivalence of both period-192 switch signs at
  a common parameter and passes. EXP-263 freezes eight exact continuation
  steps and passes at full step size, reaching a strongly unstable period-192
  endpoint with exact `224/256` identity. EXP-264 freezes the magnitude-
  separated nine-row fifth-flip scan and passes with exactly one bracket.
  EXP-265 freezes the exact 256-segment augmented event solve with independent
  segmented Radau parity and fails only its DOP853 direct-product flip gate by
  `6.50e-9`. EXP-266 freezes an immutable-solution, tighter-step DOP853/Radau
  precision audit without relaxing the `1e-7` gate.
  EXP-266 shows both tighter solvers still miss that gate while agreeing with
  each other. EXP-267 freezes a new tighter coupled recorrection and applies
  the same `1e-7` flip threshold to DOP853 and Radau. EXP-267 passes and
  qualifies the fifth event (FND-095); the third finite spacing ratio is
  `4.300`, explicitly rejecting a monotone scaling inference. EXP-268 freezes
  the separate 512-segment period-384 child switch and all six candidates
  pass. EXP-269 freezes the independent period-192-parent/period-384-child
  stability-exchange test and passes under both solvers, extending the
  qualified cascade through stable period 384 (FND-096). Next, resolve both
  period-384 tangent signs at a common coordinate before deeper continuation;
  EXP-270 passes that four-way DOP853/Radau whole-orbit phase audit. EXP-271
  passes eight full continuation steps, retains exact `448/512` identity, and
  reaches preliminary multiplier `-533.597`. EXP-272 passes the
  magnitude-separated nine-row scan with exactly one sixth-flip bracket.
  EXP-273 passes the exact 512-segment two-solver augmented solve and qualifies
  a sixth exact event (FND-097). The fourth finite spacing ratio is `4.836`,
  but the four-ratio sequence remains non-monotone. EXP-274 passes all six
  bilateral 1,024-segment period-768 switch candidates with exact `896/1024`
  identity. EXP-275 passes the independent period-384-parent/period-768-child
  stability exchange, extending the qualified cascade through stable period
  768 (FND-098). EXP-276 freezes whole-orbit equivalence of both tangent signs
  before any deeper continuation. EXP-276 passes nine of ten gates, including
  strong phase identity, but fails modulus spread `0.003450 > 0.002`.
  EXP-277 tightens integration, strengthens identity, and improves the spread
  to `0.002661`, but preserves the same isolated failure. EXP-278 freezes a
  canonical-phase two-solver correction from the negative sign independently
  preselected by EXP-275, retaining the `0.002` gate and exact identity;
  EXP-278 passes all twelve gates with modulus spread `9.78e-8`. EXP-279
  passes eight full steps with exact `896/1024` identity and reaches
  preliminary multiplier `-946.310`. EXP-280 passes the magnitude-separated
  nine-row scan with exactly one seventh-flip bracket. EXP-281's exact
  1,024-segment solve passes every gate except independent Radau flip residual
  (`3.22e-7 > 1e-7`), so no seventh event is promoted. EXP-282 freezes an
  immutable-solution tighter-step precision audit with the unchanged gate.
  EXP-282 preserves the failure (`3.64e-7` Radau residual and `3.67e-7`
  cross-solver difference). EXP-283 freezes a Float64 ULP-scale feasibility
  diagnostic before a new correction formulation is selected. EXP-283 passes:
  the estimated `1.024e-6` multiplier change per Float64 `a` increment and
  `1.836e-7` minimax solver-centering residual both exceed the `1e-7` gate
  (FND-099). EXP-284 passes a 50-decimal-digit segmented integration pilot
  with near-ideal fourth-order convergence. EXP-285 freezes the full parallel
  1,024-segment high-precision multiplier audit. EXP-285 passes nine of ten
  gates but fails raw 4,096/8,192-step convergence; the error ratio `15.988`
  is fourth-order. EXP-286 freezes an untouched 16,384-step profile and
  successive Richardson gates. EXP-286 passes with extrapolated flip residual
  `5.17e-9` and successive-estimate difference `8.97e-9`. EXP-287's independent
  50-digit RK4 3/8-tableau sequence passes every frozen gate and agrees with the
  classical extrapolation within `5.22e-11` on the stored representation; its
  former event promotion (FND-100) is superseded below. EXP-288 then passes all six bilateral sparse
  2,048-segment switches and nominates primitive period-1536 candidates with
  exact `1792/2048` identity. EXP-289 freezes the independent DOP853/Radau
  criticality test without assuming whether the local exchange is
  supercritical or subcritical. EXP-289 preserves a sole resolution failure:
  both solvers classify the child as unstable with `5.74e-6` relative spread,
  but parent moduli `0.9999973/1.0000022` straddle one inside the frozen neutral
  margin. EXP-290 freezes eight sparse continuation steps to move the same
  child away from that parent-resolution frontier before another independent
  audit. EXP-290 passes all eight exact steps, but the branch's sub-precision
  `a` bend is not promoted as a fold. EXP-291 freezes complete 50-digit
  classical-RK4 and RK4 3/8 parent multiplier sequences at the original
  same-coordinate EXP-289 sample; a ten-to-one classification/error margin is
  required before the seventh birth can be called subcritical. EXP-291 passes
  every convergence gate but fails that side test: both tableaux give
  approximately `-1.000000115`, so parent and child are both unstable in the
  stored representation. EXP-292 applies a true 50-digit cyclic
  multiple-shooting correction at three discretization levels, using block
  elimination to solve the full matching problem before any side claim. It
  fails the correction and source-neighborhood gates: all three solves move
  `7.32e-5`--`9.32e-5` from the source while the tracked `-1` root collapses
  toward zero, consistent with convergence to a lower-period double cover.
  FND-101 therefore retracts event seven; six exact supercritical births and a
  stable primitive period-768 child remain qualified. EXP-293 now freezes an
  augmented 50-digit orbit-plus-antiperiodic-tangent pilot that excludes the
  double cover. It reduces the 6,146-variable cyclic Newton system to 8-by-8
  and converges the 1,024-step discrete equations to `2.75e-31/1.23e-30`
  orbit/tangent residuals while retaining `2.58e-5` half-orbit separation.
  It nevertheless fails `a_bounds` after a `-4.50e-9` coordinate shift and
  fails the pointwise tangent-neighborhood gate. Preserve that failure.
  EXP-294 passes six of seven gates: `a` and period converge at
  `15.718/15.706`, the finest and Richardson coordinates both enter the
  original bracket, residuals fall below `1.32e-26`, and primitivity persists.
  Only pointwise identity with the old Float64 tangent field fails, remaining
  `4.162 > 0.1` at every resolution even as the median direction cosine is
  `0.99999987`. Preserve that failure. EXP-295 passes all ten independent
  RK4 3/8 gates: `a` and period converge at `15.721/15.707`, the Richardson
  coordinates agree within `2.05e-14`, finest nodes within `1.24e-10`, and the
  sign-aligned tangent lines to effectively unit cosine. FND-102 supersedes the
  old tangent representation and qualifies event seven at
  `a≈0.24070100823759`; the corrected fifth spacing ratio is `4.244`.
  Criticality of the period-1536 birth remains unresolved. EXP-296 now freezes
  a fresh sparse bilateral period-1536 switch from the passed 4,096-step RK4
  3/8 event representation. All six children pass, but the overall receipt
  preserves a sole source event-matching failure `1.441e-8 > 1e-8`; the
  secondary-null residual is `4.48e-11`. EXP-297 passes its 8,192-step
  augmented refinement with `15.860/15.853` increment ratios and reduces the
  doubled DOP853 source residual to `9.64e-10 < 1e-8`. EXP-298 now freezes a
  fresh two-sign switch from this passed representation at predictor length
  `0.00025`. Both signs pass at a common coordinate only `7.24e-14` above the
  Richardson event, with half-node RMS `6.31e-6`. Their preliminary multipliers
  disagree and are discarded. EXP-299 now freezes DOP853/Radau parent/child
  correction from the positive sign, preselected only by its larger half-period
  closure; either resolved criticality passes and mixed/unresolved fails.
  EXP-299 passes every nonclassification gate. DOP853/Radau independently give
  stable child moduli `0.12419628/0.12419164` with `3.73e-5` relative spread,
  but parent moduli `0.99999149/1.00002167` remain inside the frozen `1e-4`
  neutral margin, so the receipt is preserved as `other-or-unresolved`. Freeze
  an exact sparse continuation of the stable child away from the event, then
  repeat the independent parent/child audit at the terminal coordinate without
  relaxing the classification margin.
  EXP-300 freezes that continuation for 32 exact sparse steps, requiring all
  33 rows and at least `1e-11` terminal separation from the finite 8,192-step
  event coordinate before another criticality audit may be defined.
  EXP-300 accepts only 23/33 rows and therefore fails without relaxation. Its
  exact prefix nevertheless crosses `1e-11` separation at the prospectively
  identifiable first-threshold row (step 16), while the terminal row reaches
  `7.56e-11` and passes all terminal diagnostics. Freeze a new audit that
  selects only the first-threshold row, independently recorrects parent and
  child, and does not treat the failed continuation itself as qualified.
  EXP-301 freezes that audit at the deterministic first-threshold row, step 16
  at `a=0.24070100822533044`. The same two solvers, `1e-4` classification
  margin, `0.02` multiplier-spread ceiling, and exact section identities apply;
  either resolved criticality passes and unresolved fails.
  EXP-301 passes every nonclassification gate but finds both parent and child
  unstable: parent moduli `1.00132578/1.00130325`, child moduli
  `284.80804/284.80915`. Together with EXP-299's independently stable child,
  this brackets a period-1536 stability loss on the accepted EXP-300 prefix.
  Freeze a magnitude-separated block-Floquet scan from the source through step
  16, requiring the exact prefix gates and at least one real-`-1` bracket;
  refine any bracket separately before discussing an eighth event.
  EXP-302 freezes the complete 18-row source-to-step-16 block-Floquet scan. It
  tracks dominant modulus rather than presuming a flip, requires cyclic
  agreement and at least one unit-modulus bracket, and separately reports real
  `-1` and `+1` brackets when admissible.
  EXP-302 passes all 18 rows and isolates exactly one stability-loss bracket
  in the first interval: real multipliers `-0.12419628 -> -4.49514241` over
  `a in [0.24070100823770973,0.24070100823781396]`, width `1.04e-13`.
  Four-shift relative spread stays below `2.35e-6`. Freeze an augmented exact
  period-1536 orbit-plus-antiperiodic-tangent solve on this bracket; do not call
  it an eighth event until the exact event and independent precision gates pass.
  EXP-303 freezes that 2,048-segment augmented orbit-plus-antiperiodic-tangent
  solve with DOP853 and segmented Radau, maximum step `0.01`, the exact bracket
  bounds, and unchanged event/primitive/two-section gates. A pass is event-only;
  period-3072 existence and criticality remain separate.
  EXP-303 is terminated without a scientific verdict after the 12,290-variable
  dense trust-region residual stagnates at `0.251` and two trials diverge to
  `2.91e6/1.84e5`. Preserve the administrative termination. Freeze the same
  bracket as a 50-digit discrete augmented solve using the validated 8-by-8
  cyclic elimination; do not relax any event gate.
  EXP-304 freezes the replacement at 50 decimal digits, 1,024 classical-RK4
  steps per segment, eight workers, and six 8-by-8 Newton updates. It retains
  the untouched bracket, `1e-22` augmented residual gate, and primitive
  half-node separation; a pass remains a single-discretization pilot only.
  EXP-304 converges in 145 seconds to `6.69e-33/2.70e-31` orbit/tangent
  residuals and preserves `7.99e-6` half-node RMS, but its 1,024-step
  coordinate shifts `4.576e-9` outside the bracket and raw tangent displacement
  reaches `54.55`. Preserve the failure. Warm-start 2,048/4,096-step profiles,
  require fourth-order/Richardson bracket recovery, and gate sign-aligned
  tangent lines rather than raw tangent coordinates.
  EXP-305 freezes the classical 1,024/2,048/4,096-step sequence with fourth-
  order `a`/period ratios in `[12,20]`, Richardson bracket recovery, `1e-22`
  augmented residuals, primitive separation, node identity, and minimum
  pointwise tangent-line cosine `0.99`. A pass still requires independent RK4
  3/8 reproduction.
  EXP-305 passes every numerical-convergence, residual, primitivity, node, and
  tangent-line gate. Parameter and period ratios are `15.7178/15.7060`, but
  the Richardson coordinate `a=0.2407010082240912813` lies `1.362e-11` below
  the EXP-302 bracket, so `extrapolated_a_bounds` fails and no eighth event is
  promoted. Preserve the failure. Freeze a target-blind ladder that
  independently recorrects child endpoints and re-evaluates their Floquet
  stability; do not reuse the too-narrow continuation-row bracket as a
  physical bound.
  EXP-306 instead freezes the stronger exact-root test before a costly Float64
  endpoint ladder: an algebraically independent RK4 3/8 augmented sequence at
  1,024/2,048/4,096 steps per segment. The only parameter bound is the full
  successful EXP-300 continuation envelope, selected without stability. A pass
  requires fourth-order convergence and cross-tableau agreement with EXP-305;
  it may qualify the eighth event directly, while period-3072 existence and
  birth direction remain separately locked.
  EXP-306 passes all ten gates. Its Richardson coordinate differs from the
  classical result by `2.05e-14`; period, finest-node, base-tangent, and full
  tangent-line identities all pass. FND-103 promotes the eighth primitive
  numerical real-`-1` event at consensus
  `a=0.24070100822410155263`. The next cascade task is a prospectively frozen
  bilateral period-3072 switch from a sufficiently refined event source;
  stability and birth direction require an independent successor audit.
  EXP-307 freezes the representation safeguard first. It extends the passed
  RK4 3/8 event to 8,192 steps on each of 2,048 segments, requires order-four
  2,048/4,096/8,192 convergence and successive Richardson agreement, and then
  directly applies the unchanged DOP853 event-matching and secondary-null
  gates to the doubled source. Only a pass permits the period-3072 switch.
  EXP-307 passes all ten gates. The 8,192-step residuals are
  `1.25e-31/1.37e-29`, fourth-order ratios are `15.8601/15.8529`, and the
  doubled DOP853 event/secondary-null residuals are `1.36e-9/3.60e-12`.
  Freeze the bilateral 4,096-segment period-3072 switch from this exact source;
  require both tangent signs and doubled exact section identities before
  nominating a child.
  EXP-308 freezes that bilateral switch at the unchanged `0.00025` predictor
  length. Both signs must pass all sparse correction, primitivity, period-ratio,
  displacement, and exact doubled `3584/4096` section gates before any child
  is nominated; preliminary multipliers remain non-evidentiary.
  EXP-308 corrects both signs in two evaluations and passes every shared gate,
  but only the negative sign passes the half-period floor. The positive value
  is `4.41e-8 < 5e-8`; preserve the bilateral failure. EXP-309 freezes the
  deterministic factor-two predictor increase to `0.0005`, with both signs
  and every gate unchanged.
  EXP-309 passes both signs at predictor `0.0005`: matching stays below
  `8.92e-11`, half-node RMS is `9.02e-6`, half-period nonclosures are
  `2.25e-6/3.52e-7`, and exact `3584/4096` identities pass. EXP-310 freezes an
  independent DOP853/Radau parent/child stability audit of the negative sign,
  selected solely by its larger nonclosure; preliminary multipliers remain
  discarded.
  EXP-310 passes every nonclassification gate and finds the period-3072 child
  strongly unstable under both solvers (`18.981764/18.981804`). The parent
  moduli `1.00003875/0.99995754` remain inside the frozen `1e-4` neutral
  margin, so criticality is unresolved rather than promoted. Preserve the
  strong subcritical evidence. EXP-311 freezes four sparse 4,096-segment
  pseudo-arclength steps from the same prospectively selected negative child,
  requiring all five rows and at least `1e-11` terminal separation from the
  finite event coordinate under the existing matching, primitivity, closure,
  period-ratio, and exact `3584/4096` identity gates. EXP-311 accepts all four
  full steps and passes every orbit-level gate, but the branch bends across
  the finite event coordinate and ends only `7.77e-13` away; preserve the
  distance-gate failure. EXP-312 binds the raw EXP-311 receipt, rechecks its
  complete accepted prefix, and freezes eight additional steps from the exact
  final tangent under unchanged orbit gates and the same `1e-11` separation
  target. EXP-312 accepts six rows before the next frozen minimum-step trial
  misses matching; it fails point count and ends `4.744e-12` from the event,
  while all terminal orbit/identity gates pass. EXP-313 now binds the failed
  prefix and freezes the first row beyond `4e-12` (nearly four times the
  finite-to-Richardson event shift) for independent DOP853/Radau audit with
  the `1e-4` margin and all scientific gates unchanged. EXP-313 passes every
  nonclassification gate but finds both parent and child unstable: parent
  moduli are `1.00230292/1.00236720`, while child moduli are
  `22667.8829/22667.8902`. Preserve the unresolved criticality and the evidence
  that the curved daughter crosses to the parent-unstable side. Next localize
  the period-1536 real-`-1` coordinate separately under DOP853 and Radau, then
  switch or sample the period-3072 child on their common coexistence side;
  do not launch another blind farther continuation. EXP-314 now binds the
  EXP-310/313 signed parent residuals, replays their two-point solver-specific
  root estimates, and freezes one outward 2,048-segment parent evaluation per
  solver. Execute EXP-314; both signs must reverse by at least `1e-4` inside
  `7e-13` brackets before any solver-specific child switch is designed.
  EXP-314 passes both brackets at widths `5.954e-13/5.983e-13`; the shared
  EXP-310 coordinate lies between the solver events, explaining the neutral
  split. EXP-315 now freezes two deterministic bisections per solver and
  requires final signed widths at most `1.6e-13`. EXP-315 passes with widths
  `1.48853e-13/1.49575e-13`; the brackets are disjoint by `1.49575e-13`.
  Design the next period-3072 switch in solver-relative event coordinates,
  using each solver's own corrected parent and the same signed offset from its
  bracket. Do not use one shared absolute `a` coordinate to infer criticality.
  EXP-316 now freezes the multiplier-blind EXP-309 negative child and parent
  exactly `5e-13` above each solver's own upper event bound, with the
  preregistered stable-parent/unstable-child prediction and unchanged
  classification, identity, and cross-solver gates. EXP-316 independently
  finds stable parents (`0.99968068/0.99965539`) and strongly unstable children
  (`18.98363/18.98308`), with all solver-agreement and section gates passing,
  but fails the `2e-6` child half-period-nonclosure floor at
  `9.43e-7/1.61e-6`. Preserve the nonpromotion. Post-run node diagnosis shows
  no daughter collapse: half-node RMS remains `9.01896e-6` versus only
  `3.34e-10` cross-solver child RMS. The direct 22,895-time-unit diagnostic is
  below its accumulated integration-error scale. Next freeze an independent
  segmented and tolerance-converged primitive-identity audit; do not relax or
  retrospectively reinterpret the failed EXP-316 gate. EXP-317 now freezes
  tighter DOP853/Radau child corrections, all-phase segmented half identity,
  and a 100-fold separation-to-representation-error requirement. Execute
  EXP-317 next. EXP-317 passes with `8.66425e-6` minimum all-phase half-orbit
  separation, `3.34029e-10` cross-solver RMS, and a `25,938.6` separation/error
  ratio. Combined with EXP-316, promote the eighth local birth as subcritical;
  keep the seventh birth, global period-3072 branch, and ninth event open.
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
  problems and bounded focal-point uniqueness claim. EXP-328 freezes the first
  printed-hub CPU reference scan of 96 unstable-manifold departure angles,
  with event-driven exit, dense return-minimum refinement, and stable-direction
  alignment. EXP-328's serialization failure is preserved; unchanged EXP-329
  passes all 96 rows but finds no jointly close and stable-aligned return.
  EXP-330's pre-integration import failure is preserved; unchanged EXP-331
  passes all 257 receipt-selected local rows. Its closest return improves only
  to `0.0104510073` and remains `0.9992957` transverse. Do not interpret this
  finite rounded-coordinate null scan as rejection. Freeze a two-variable
  angle/`c` nonlinear stable/unstable manifold match, replicate over shrinking
  spheres and an independent integrator, then continue every detected root
  over a declared segment before testing uniqueness. CPU runtime is only 31
  seconds for 257 rows, so no paid GPU is justified for the current stage.
  EXP-332 then passes all nonlinear-target and execution gates on nine `c`
  slices: 223 inward sphere intersections yield no candidate or signed-zero
  cell, but the per-slice minimum chord mismatch decreases monotonically and
  reaches `0.00656684` at the upper boundary with both tangent residuals still
  positive. Run frozen EXP-333's unchanged-method extension through
  `c=10.3224`; if it nominates a root cell, freeze a coupled solve before any
  claim update. EXP-333 passes and nominates 25 direct near matches plus three
  componentwise sign-hull cells over `c=10.3184--10.3204`. Do not yet solve or
  promote: run EXP-334's frozen residual-winding and first-return-continuity
  audit, then refine only nonzero-degree continuous cells. If all three hull
  cells fail degree, retain the direct candidates and freeze a finer
  parameter-angle mesh around their bounded band. EXP-334 passes and rejects
  all three hull cells at winding number zero; only 28 cells had complete
  radius-`0.02` returns. Run frozen EXP-335's radius-`0.025`, 13-by-192 fine
  band with in-scan degree and return-time gates. A continuous nonzero-degree
  cell may seed a coupled solve; direct distance candidates alone may not.
  EXP-335 passes with `39.14%` return coverage and 141 direct near matches but
  again zero degree cells; its `0.00129410` minimum agrees with the smaller
  sphere. Run frozen EXP-336's orthogonal fixed-`c=10.3084` scan over
  `a in [0.1758,0.1838]`. This tests the second rounding direction before
  widening to a full two-parameter curve search. EXP-336 preserves a sole
  return-coverage failure (`9.47%` versus 20%) but finds a much smaller
  `0.00034435` chord at `a=0.1828`; no degree cell exists. Run frozen EXP-337,
  which binds the failure, narrows to `a in [0.1803,0.1838]`, halves spacing,
  and uses radius `0.03` to recover continuous-cell coverage without
  reclassifying EXP-336. EXP-337 passes at `18.89%` coverage and sharpens the
  chord to `0.000162262` at `a=0.18255`, but retains zero degree cells. Run
  frozen EXP-338's smooth three-variable single shooting in angle, `a`, and
  total flight time. If it reaches an interior residual below `1e-8`, freeze a
  segmented multiple-shooting qualification rather than promoting directly.
  EXP-338 loses only final receipt serialization; unchanged EXP-339 passes but
  stalls at `0.000158819` because zero-start relative differences collapse to
  `1.49e-8`. EXP-340's absolute-central correction reduces the mismatch by
  `16.73%` but exhausts 60 evaluations at `0.000135120`; its scaled Jacobian
  condition ratio is about `1.47e5`. Preserve the sole termination-gate
  failure. EXP-341 freezes a receipt-bound 16-arc multiple-shooting successor
  seeded from its interior final trajectory with analytic segment variational
  derivatives and the unchanged global box. It nominates the first root at
  maximum block defect `2.66211e-9`, but is preserved with a sole termination
  failure after continuing to all 60 evaluations. EXP-342 freezes an
  independent 32-arc Radau correction by splitting the matched EXP-341 arcs,
  not by direct long replay, and adds prospective source-root agreement gates.
  It passes at maximum defect `1.08861e-9`, reproducing `a` within `3.13e-11`.
  EXP-343 freezes the radius-`0.025` 32-arc Radau successor from these matched
  nodes with a prospective `2e-6` parameter-persistence gate. It reaches
  `5.49708e-9` and preserves `a` within `1.30e-13`, but fails because the
  ill-conditioned angle/time gauge hits the angle boundary and exceeds its
  nuisance agreement limits. EXP-344 preserves the failure, widens only the
  angle gauge, and freezes a one-evaluation validation of the exact matched
  seed with unchanged `a` and residual gates. It passes at `5.49708e-9`,
  qualifying persistence from radius `0.03` to `0.025`. Freeze the radius
  `0.02` correction with the same wider gauge and parameter-invariance gate.
  EXP-345 reaches `5.60724e-9` and preserves `a` within `4.34e-13`, but again
  hits the nuisance-angle boundary and is preserved as failed. Freeze a wider
  exact-node gauge validation. EXP-346 is frozen with no further optimization;
  it passes at `5.60724e-9`, completing a three-radius root sequence with `a`
  stable to about `1e-12`. Freeze local continuation of the homoclinic curve
  toward fixed `a=0.1798` before any bounded uniqueness statement. EXP-347
  passes the first step at `c=10.3104`, giving `da/dc=-0.325514` and predicting
  the historical-path crossing near `c=10.31714`. EXP-348 freezes a second
  bounded step at `c=10.3144`; it remains interior and follows the secant but
  stalls at `2.51470e-8`, so it is preserved as failed. Freeze a same-`c`
  recovery from its exact nodes before solving the fixed-`a` intersection.
  EXP-349's 64 arcs lower the defect to `1.18448e-8` and preserve `a` within
  `3.13e-14`, but still miss the gate. Preserve the failure and freeze a
  hash-bound 128-arc successor without relaxing thresholds. EXP-350 passes at
  `6.12599e-9`, qualifying the second continuation point at
  `(a,c)=(0.1806904556213,10.3144)`. Its secant slope `-0.325531` agrees with
  EXP-347 and predicts the historical fixed-`a` crossing at
  `c=10.3171353942`. Freeze and run a direct hash-bound boundary-value solve at
  that prospective coordinate; interpolation alone cannot qualify the
  intersection. EXP-351 is frozen as that direct fixed-`a` solve, using the
  analytic `c` variational sensitivity and EXP-350's exact 128-arc nodes.
  EXP-351 lowers the initial defect by more than two orders of magnitude but
  is preserved as failed at `2.09830e-4`; 121/128 blocks already pass and the
  remaining defect localizes near the stable endpoint. EXP-352 freezes a
  hash-bound exact-node warm restart with the same 128 arcs, budget, and
  `1e-8` gate. EXP-352 aborts before receipt generation when an unbounded
  trust-region node trial makes Radau's step size collapse; do not classify it
  as a scientific failure. EXP-353 adds only a prospective `+/-0.5`
  source-centered component guardrail with an explicit node-margin gate.
  EXP-353 completes safely and remains highly interior but stalls at
  `2.09825e-4`, showing that a same-point warm restart is insufficient. Freeze
  EXP-354 from the last qualified fixed-`c` root: correct its 128 nodes at the
  prospectively declared crossing `c=10.3171353942`, measure the residual
  `a-0.1798`, and only then reimpose exact fixed `a`. EXP-354 is preserved as
  failed after reducing the defect to `3.83423e-5`; it remains interior and
  its optimizer optimality `2.85e-6` shows active descent. EXP-355 lowers the
  defect again to `8.30202e-6` and moves to `a=0.1798386481`, with active
  descent and nine failing blocks. EXP-356 halves the defect again to
  `4.10058e-6` and moves to `a=0.1798190580`. EXP-357 freezes the next exact-node
  same-`c` correction without changing any gate. EXP-357 reaches a
  `3.76458e-6` conditioning floor at `a=0.1798174900`, but its nodes are now
  only `1.749e-5` from exact historical `a`. EXP-358 reimposes fixed
  `a=0.1798` from that corrected source and solves `c`, but returns to the same
  `~2.11e-4` stable-end floor near `c=10.3171272` as EXP-351. Preserve the
  failure. Implement pseudo-arclength or collocation continuation with an
  explicit gauge to distinguish a local fold/termination from singular
  fixed-`a` conditioning; do not claim the secant intersection.
  EXP-359 freezes the first such two-parameter pseudo-arclength step, including
  simultaneous analytic `a/c` sensitivities, common-gauge angle alignment,
  deterministic 32-to-128-arc subdivision, and a conservative
  `Delta c=0.0005` predictor. Run it locally before approaching the suspected
  fold. EXP-359 completes numerically but loses its atomic receipt because two
  terminal check values are NumPy booleans. Preserve this as an administrative
  serialization failure; rerun the identical mathematics as EXP-360 after a
  JSON-native boolean regression test. EXP-360 passes all ten gates at
  `(a,c)=(0.1805321204707,10.3148863716751)` with maximum matching defect
  `6.77472e-9` and arclength residual `3.43e-12`. Its local slope
  `-0.325544` preserves the projected historical crossing near
  `c=10.31713529` and shows that the earlier fixed-coordinate floor was not an
  immediate branch termination. Chain the next same-gauge 128-arc
  pseudo-arclength step from EXP-350 and EXP-360, then continue through or
  around any turn until the exact `a=0.1798` section is either qualified or
  excluded on a declared branch segment. EXP-361 freezes that next same-gauge
  step with the unchanged `Delta c=0.0005` predictor and root gates.
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
## EXP-318 — resolve the seventh-birth criticality in 50-digit arithmetic

- [x] Bind the passed EXP-297 augmented event and the preserved EXP-299
  neutral-parent/stable-child source by raw receipt hash.
- [x] Freeze independent classical-RK4 and RK4 3/8 spectra at
  4,096/8,192/16,384 steps on all 1,024 parent segments.
- [x] Require fourth-order/Richardson convergence, cross-tableau agreement,
  at least `1e-7` signed flip signal, and a ten-to-one empirical
  signal-to-error margin.
- [x] Execute EXP-318 from clean committed source and preserve its receipt.
  Both tableaux resolve the parent as stable with an `824.1` signal/error
  ratio, so the stable/stable pair fails only the required exchange gate.
- [x] Preserve the failure and update the ledger/manuscript: the sampled
  candidate cannot be promoted as a supercritical exchange.
- [ ] Recover the immediate period-1536 daughter in the same high-precision
  discrete representation as the exact event; determine whether the stable
  EXP-299 candidate lies beyond a fold/restabilization or on another sheet.
  EXP-319 is frozen at 50 digits with one shared 4,096-step RK4 3/8 map,
  bilateral tangent signs, two predictor scales, quadratic-opening gates, and
  child Floquet stability. It passes with lower-`a` stable daughters and a
  `2.000728` opening exponent, nominating a supercritical birth. EXP-320 now
  passes the identical 8,192-step replication. FND-105 promotes the seventh
  local birth as supercritical. Next trace the separate stable higher-`a`
  period-1536 candidate to a fold, restabilization, or disconnected sheet.
  EXP-321 freezes six 50-digit 4,096-step pseudo-arclength rows from the
  immediate daughter to the target's amplitude scale; no fold or target match
  is required to pass. It passes with six stable lower-`a` rows and no fold.
  Because EXP-299's candidate has only `2.86e-7` direct closure, EXP-322 now
  freezes its fixed-`a` 50-digit correction before any separate-sheet claim.
  It fails unresolved: undamped Newton never improves the initial exact-map
  residual. Preserve that failure and run the frozen residual-decreasing
  backtracking successor EXP-323 without relaxing the `1e-20` gate. EXP-323
  finds descent but its fixed five-percent rule rejects the small `1/32`
  trial. EXP-324 freezes a step-scaled Armijo successor with unchanged science
  gates. EXP-324 passes and collapses the old EXP-299 child seed to the doubled
  parent at `1.20e-23` matching and `7.38e-20` half-node amplitude. Run frozen
  8,192-step EXP-325 before promoting FND-106 across resolutions. EXP-325
  passes from the unchanged seed with `7.22e-30` matching and `6.03e-25`
  half-node RMS, independently collapsing to the doubled parent. FND-106 is
  now qualified; audit EXP-300--302 and any later conclusions that inherited
  EXP-299's primitive-child identity before reusing them. The dependency audit
  retracts EXP-300--302's branch/micro-bracket interpretation while preserving
  the independently converged EXP-306/307 event root and EXP-308--317 local
  calculations. Run frozen EXP-326 to require direct same-map identity between
  the immediate seventh daughter and the eighth-event parent before restoring
  an eight-rung connected-cascade claim. EXP-326 passes continuation, target
  correction, period, primitivity, multiplier, cyclic, and neutral gates but
  preserves one integer-node identity failure caused by a `3.16e-6` phase-
  hyperplane offset. Run frozen EXP-327's exact shared-phase registration;
  do not relax or overwrite EXP-326. EXP-327 passes with `6.35e-18` direct
  same-phase node RMS, `8.57e-26` matching, and `1.02e-21` period difference.
  FND-107 now qualifies the seventh-daughter-to-eighth-event connection.

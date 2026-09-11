# Research updates

Current result: [EXP-522's nonlinear refinement passes](2026-09-10-exp522-nonlinear-refinement-result.md).
All 96 new IVPs pass raw audit; every contact residual improves at least 115×,
with all predictions passing and net progress toward section grazing retained.
EXP-521's failed predictor remains failed. Jones's flow-level symbolic chains
are still unverified. EXP-523 now tests two continuation steps with fresh
derivatives and explicitly preserved physical root identities.
The earlier EXP-520 census and its limits remain in the evidence chain below.

This directory is the chronological project log. It complements the thematic
research plan, claim ledger, experiment records, and execution backlog without
replacing them.

## Update policy

Add or revise the current dated update whenever a coherent checkpoint is
verified. Each update records:

- what changed;
- what evidence passed;
- what the result does and does not establish;
- the relevant source commits and experiment receipts;
- current blockers or gates; and
- the next concrete execution item.

Updates should report observed results rather than activity alone. Scientific
claims continue to live in `docs/claim-ledger.md`, while machine-verifiable run
details live under `docs/experiments/` and `docs/experiments/receipts/`.

## Entries

- [`2026-09-10-exp523-prax-execution.md`](2026-09-10-exp523-prax-execution.md)
  - Frozen two-step computation is running on prax; worker liveness, consumed
  marker and raw writing verified. Complete audit follows automatically.
  This is operational progress, not an EXP-523 scientific result yet.
- [`2026-09-10-exp523-refreshed-path-design.md`](2026-09-10-exp523-refreshed-path-design.md)
  - Two-step continuation with freshly measured a/c responses, a prospectively
  tested quadratic prediction, and at most one normal correction per step.
  Pre-execution local review caught and fixed a cyclic root-identity reset.
- [`2026-09-10-exp522-nonlinear-refinement-result.md`](2026-09-10-exp522-nonlinear-refinement-result.md)
  - All 96 IVPs and 83406 census segments pass raw audit. Fresh fixed-c
  refinement improves every contact residual at least 115× and passes all
  predictions, retaining net gap progress. Failed EXP-521 verdict is unchanged.
- [`2026-09-10-exp521-critical-response-result.md`](2026-09-10-exp521-critical-response-result.md)
  - All 569 IVPs and 416634 periodic census segments pass raw audit. Both
  inner gaps improve and contact proximity passes, but all sixteen linear
  fold predictions fail. Preserve that failure; test nonlinear refinement next.
- [`2026-09-10-exp521-critical-response-design.md`](2026-09-10-exp521-critical-response-design.md)
  - Executable four-point c response and one conditional contact-preserving
  periodic step; all 16 stationary points and both inner maxima tracked.
  Design and tests, not yet a target result or a verified Jones arrow.
- [`2026-09-10-exp520-periodic-stationarity-census.md`](2026-09-10-exp520-periodic-stationarity-census.md)
  - All 417,460 stored segments pass the exact polynomial-root audit; all
  twenty cycle windows and five nearest-object nominations qualify. The
  actual periodic candidate remains below the section by about 0.345:
  restored fold contact is not yet section grazing or a verified Jones arrow.
- [`2026-09-10-exp519-execution.md`](2026-09-10-exp519-execution.md)
  - All four response points and the single correction qualify. Worst corrected
  full-state distance is 8.822e-7 versus 1e-4; the original reserve and every
  numerical threshold remain unchanged. A local contact is recovered, not a chain.
- [`2026-09-10-exp518-recovered-fold-transport.md`](2026-09-10-exp518-recovered-fold-transport.md)
  - All 200 IVPs pass raw audit; all four constructions track through both
  remaining parameter steps. At the endpoint all 16 x-only comparisons pass,
  but all full-state comparisons fail: worst distance is 1.396 times tolerance.
  Fold transport is recovered; fold/cycle contact and Jones's chains are not.
- [`2026-09-10-exp517-earlier-return-folds.md`](2026-09-10-exp517-earlier-return-folds.md)
  - All 108 IVPs pass raw audit. Both solvers recover the same local fold in
  all four history/direction constructions, restoring every full-state reference.
  This is positive local calibration, not a restored eighth-return test or chain.
- [`2026-09-10-exp516-event-ordinal-coverage.md`](2026-09-10-exp516-event-ordinal-coverage.md)
  - All 740 saved accepted events and 660 consecutive pairs audit cleanly;
  all 40 prior decisions remain unchanged. No sampled ordinal restores the
  reference, but two earlier-return sign-change cells warrant direct tests.
- [`2026-09-10-exp515-third-return-precision.md`](2026-09-10-exp515-third-return-precision.md)
  - All twelve IVPs pass raw audit; all eighteen paired sensitivities resolve.
  Tiny third-return derivatives persist at higher precision, while both old
  solvers miss the center values. This does not rescue depth-eight fold coverage.
- [`2026-09-10-exp514-candidate-grazing-boundaries.md`](2026-09-10-exp514-candidate-grazing-boundaries.md)
  - All 120 target IVPs pass raw audit. Every candidate qualifies as a local
  section-grazing boundary with two-sided crossing birth/death and square-root
  scaling. This explains misleading fold brackets, not a verified Jones arrow.
- [`2026-09-10-exp513-candidate-fold-qualification.md`](2026-09-10-exp513-candidate-fold-qualification.md)
  - All 30 IVPs pass raw audit. Every midpoint pair is regular, but all ten
  first Newton proposals leave their boxes. No fold qualifies; safeguarded
  event-aware bracket refinement is next, not a global absence claim.
- [`2026-09-09-exp512-censored-return-extension.md`](2026-09-09-exp512-censored-return-extension.md)
  - All 28 new IVPs pass raw replay and recover every censored ninth return
  with unchanged saved prefixes. The grid now has 38/40 regular pairs and
  five candidate intervals; actual fold/event-sheet qualification is next.
- [`2026-09-09-exp511-direct-curve-coverage.md`](2026-09-09-exp511-direct-curve-coverage.md)
  - All 160 IVPs pass full dense replay. Of 40 paired samples, 31 are regular,
  two collapse and seven lack a ninth return before the fixed horizon. No
  sampled fold bracket qualifies; resolve time-window censoring next.
- [`2026-09-09-exp510-four-substep-fold-transport.md`](2026-09-09-exp510-four-substep-fold-transport.md)
  - All 180 IVPs audit cleanly. The first smaller substep qualifies every
  fold; the second again loses depth-8 input regularity. The controller stops
  correctly. Direct curve coverage/root isolation is next, not looser gates.
- [`2026-09-09-exp509-failed-predictor-replay.md`](2026-09-09-exp509-failed-predictor-replay.md)
  - All 196 original IVPs replay. Depth-8 roots collapse the input curve;
  short-history folds miss proximity. Preserve the failed controller and
  reject the point safely. Smaller-step fold-branch transport is next.
- [`2026-09-09-exp508-constrained-contact-step.md`](2026-09-09-exp508-constrained-contact-step.md)
  - Predictor produced 196 IVPs, then a missing-envelope reporting defect
  stopped the controller. No corrector ran; failure and raw files preserved.
- [`2026-09-09-exp507-fixed-c-fold-restoration.md`](2026-09-09-exp507-fixed-c-fold-restoration.md)
  - All 158 integrations pass raw audit. Fixed-c correction restores fold
  proximity, but the boundary remains about 119 times tolerance. Complete
  output accounting passes; constrained predictor/corrector continuation is next.
- [`2026-09-09-exp506-legacy-word-adapter-continuation.md`](2026-09-09-exp506-legacy-word-adapter-continuation.md)
  - All 2,040 branch fits and 40 word splines reproduce; the turning filter
  changes none of EXP-186's saved outputs. A final-summary quota overrun is
  explicitly flagged, and a tested pre-write quota helper is added for new runs.
- [`2026-09-09-exp505-legacy-turning-point-impact.md`](2026-09-09-exp505-legacy-turning-point-impact.md)
  - New replay adapter failed on omitted word-comparison fields after retaining
  255 branch fits. The attempt is preserved, not reset; EXP-506 continues it.
- [`2026-09-09-exp504-guarded-contact-continuation.md`](2026-09-09-exp504-guarded-contact-continuation.md)
  - All 200 integrations pass raw audit. The first step reduces the boundary
  gap but misses fold proximity by 1.19%; it is rejected and seven slots remain
  unrun. The next controller must restore the fold constraint explicitly.
- [`2026-09-09-exp503-resource-continuation.md`](2026-09-09-exp503-resource-continuation.md)
  - All nine points and 1,580 integrations pass raw audit. The joint correction
  reduces the dominant gap 5.64%, but the boundary still misses by 127 times
  tolerance; a qualified local response supports testing lower-c continuation.
- [`2026-09-09-exp502-joint-contact-search.md`](2026-09-09-exp502-joint-contact-search.md)
  - Seven fixed points completed before the frozen storage threshold stopped
  the eighth. All evidence is retained; failure metadata is public and
  EXP-503 now supplies the complete audited verdict without resetting this failure.
- [`2026-09-09-exp501-limiting-contact.md`](2026-09-09-exp501-limiting-contact.md)
  - All 38 integrations and sixteen limiting-boundary profiles audit cleanly;
  none of 384 cycle-contact comparisons passes. The mismatch persists in the
  limiting trajectory, not merely at finite perturbations.
- [`2026-09-09-exp500-complete-polynomial-census.md`](2026-09-09-exp500-complete-polynomial-census.md)
  - All 239,072 stored-polynomial segments and 1,024 plane roots audited;
  complete classifications and accepted sequences agree at all 32 inputs.
  No exact-flow all-root proof or Jones arrow is inferred.
- [`2026-09-09-exp499-decimal-event-reference.md`](2026-09-09-exp499-decimal-event-reference.md)
  - All 64 decimal trajectories and 480 root evaluations audited; the reference
  agrees at all inputs and exposes an additional limitation of original paired
  solver agreement. Original EXP-498 failures remain unchanged.
- [`2026-09-09-exp498-boundary-transport.md`](2026-09-09-exp498-boundary-transport.md)
  - All 136 integrations audited: six of eight boundary matrices qualify;
  two near-tangent accuracy failures remain, and boundary inputs do not meet
  the cycle-proximity criterion at any of the six events.
- [`2026-09-09-exp497-contact-localization.md`](2026-09-09-exp497-contact-localization.md)
  - All 179 target IVPs audited: the third interior point meets full-state
  fold/cycle proximity in all sixteen variants while retaining primitive 6/8 counts.
- [`2026-09-09-exp496-contact-endpoint.md`](2026-09-09-exp496-contact-endpoint.md)
  - All 124 trajectories audited: the first case has opposite-sign endpoints
  in all four representations; the second retains two input-conditioning failures.
- [`2026-09-09-exp495-fold-cycle-membership.md`](2026-09-09-exp495-fold-cycle-membership.md)
  - Complete 240-cell saved-state comparison: neither primitive base cycle
  meets the measured right-fold proximity criterion, including every fixed
  sensitivity radius. All 26 parent candidates and failures remain; no new IVPs.
- [`2026-09-09-exp494-periodic-winding-transport.md`](2026-09-09-exp494-periodic-winding-transport.md)
  - 806 integrations; 54/64 new parameter nodes qualify. Two apparently
  six-return continuations are detected as double traversals of shorter
  three-return cycles; eight blocked successors remain unrun. No new insertion.
- [`2026-09-09-exp493-projected-inner-turn.md`](2026-09-09-exp493-projected-inner-turn.md)
  - all 128 saved side profiles reproduce the projected turning geometry;
  all 64 opposite-side comparisons add one relative winding. Complete result
  remains fifteen passes and one inherited accuracy failure; no new IVPs.
- [`2026-09-08-exp492-event-boundaries.md`](2026-09-08-exp492-event-boundaries.md)
  - all 248 target IVPs audited; fifteen complete boundary passes and one
  retained paired-state accuracy failure, with all sixteen local mechanisms
  reproduced and all candidate/solver conditions shown.
- [`2026-09-08-exp491-event-sheet-probe.md`](2026-09-08-exp491-event-sheet-probe.md)
  - all 156 trajectories audited: 78/78 sampled points reproduce, but only
  ten intervals pass the time/coordinate screen; sixteen retain event-time
  discontinuity warnings, including two input-sign reversals.
- [`2026-09-08-exp490-direct-folds.md`](2026-09-08-exp490-direct-folds.md)
  - all 26 candidate intervals, 52 solver profiles and 208 retained trajectories;
  ten paired-qualified searches across eight right-region families, with
  duplicated physical locations and all sixteen unresolved intervals retained.
- [`2026-09-08-exp489-section-grazing.md`](2026-09-08-exp489-section-grazing.md)
  - both selected section tangencies reproduce crossing-pair birth/death and
  square-root scaling; this explains event-list jumps, not symbolic chains.
- [`2026-09-08-exp488-event-accuracy.md`](2026-09-08-exp488-event-accuracy.md)
  - complete tolerance matrix retains one passing and one unresolved witness;
  a favorable finest solver pair does not erase the complete failed criterion.

- [`2026-09-07-exp482-successor-preflight.md`](2026-09-07-exp482-successor-preflight.md)
  — distinct successor design/attempt; real source preflight passes 426 tests,
  raw-reference audits and all configurations; cumulative prospective review next.

- [`2026-09-07-exp482-full-workload.md`](2026-09-07-exp482-full-workload.md)
  — full-size analytic and map controls pass; original scan-overhead estimate
  fails; explicitly labeled one-second polling redesign fits projected limits.

- [`2026-09-07-exp482-finer-step-throughput.md`](2026-09-07-exp482-finer-step-throughput.md)
  — finer-step synthetic controls pass; larger CPU batches improve throughput;
  target accuracy and complete successor feasibility remain to be qualified.

- [`2026-09-07-exp481-live-run.md`](2026-09-07-exp481-live-run.md)
  — actual qualification completed: adaptive solvers agree, RK4 steps fail the
  state-accuracy bound; collection prevented, raw replay exact, refinement next.

- [`2026-09-07-exp481-prospective-review.md`](2026-09-07-exp481-prospective-review.md)
  — PR47 merged; prospective review fixes and workload/turning controls passed;
  381 final source-bound tests pass; exact reviewed release ready for execution.

- [`2026-09-07-exp481-phase-authorization.md`](2026-09-07-exp481-phase-authorization.md)
  — real-parent one-use grants, complete three-phase dispatch and fixed target
  attempt marker; analytic control and failure boundaries pass; review next.

- [`2026-09-07-exp481-production-preflight.md`](2026-09-07-exp481-production-preflight.md)
  — actual source-bound test and isolated full-design setup; unchanged numeric
  design separated from release administration; target authorization remains.

- [`2026-09-07-exp481-source-review-gate.md`](2026-09-07-exp481-source-review-gate.md)
  — live Git/source checks, exact canonical review reconstruction and mandatory
  finding/change accounting; runtime authorization remains the next step.

- [`2026-09-07-exp481-fixed-phases.md`](2026-09-07-exp481-fixed-phases.md)
  — complete qualification/collection/replay/analysis path passes in isolated
  circle controls; both cases and every reference row retained; target gate next.

- [`2026-09-07-exp481-sealed-input-audit.md`](2026-09-07-exp481-sealed-input-audit.md)
  — real isolated worker reproduces preserved reference audit exactly; nine-file
  input package and six success/failure controls; no new trajectories.

- [`2026-09-07-exp481-sealed-startup.md`](2026-09-07-exp481-sealed-startup.md)
  — isolated exact-file worker, canonical observed environment and nine real
  startup/failure controls; review-bound target dispatch remains disabled.

- [`2026-09-06-exp481-campaign-aggregation.md`](2026-09-06-exp481-campaign-aggregation.md)
  — fixed 512-batch/128-qualification trial grid and both-case analysis wiring;
  unresolved cases and all six historical reference rows remain explicit.

- [`2026-09-06-exp481-durable-supervisor.md`](2026-09-06-exp481-durable-supervisor.md)
  — adaptive write-once evidence, sampled-resource supervision and actual
  worker/supervisor-loss controls; accepted events and capture labels survive.

- [`2026-09-06-exp481-adaptive-qualification.md`](2026-09-06-exp481-adaptive-qualification.md)
  — adaptive cross-check passes all 24 synthetic comparisons, raw capture
  references verified, and shared-policy RK4 arrays preserved exactly.

- [`2026-09-06-exp481-replay-decisions.md`](2026-09-06-exp481-replay-decisions.md)
  — audited raw-to-cohort replay, complete-grid map/proximity decisions and
  a 2,048-seed synthetic integration-to-analysis control; no new Rössler result.

- [`2026-09-06-exp481-sampling-design.md`](2026-09-06-exp481-sampling-design.md)
  — explicit numeric sampling proposal, fixed seed/pair selection and held-out
  seed-bootstrap map analysis; synthetic monotone/cubic/multivalued controls pass.

- [`2026-09-06-exp481-durable-recording.md`](2026-09-06-exp481-durable-recording.md)
  — write-once paired-section journals, forced process-loss control and
  outcome-free input preflight; numeric sampling and analysis design next.

- [`2026-09-06-exp481-dual-section-collector.md`](2026-09-06-exp481-dual-section-collector.md)
  — shared-trajectory collector and synthetic controls, including unequal
  section counts and capture/interrupt handling; no new research trajectories.

- [`2026-09-06-exp480-both-cycles-qualified.md`](2026-09-06-exp480-both-cycles-qualified.md)
  — both fixed cycles pass paired-section qualification; figure, audited raw
  evidence and prax backup retained; common-population partition work is next.

- [`2026-09-06-exp480-review-and-repairs.md`](2026-09-06-exp480-review-and-repairs.md)
  — real adversarial review, gate-edge repair and anisotropic analytic controls
  completed before target execution.

- [`2026-09-04-review-001-manuscript.md`](2026-09-04-review-001-manuscript.md)
  - responds to the external review with sharper mathematical objects,
  both-equilibrium spectral checks, corrected Sobol uncertainty language,
  prior-work comparisons, and explicit public reproducibility limits;
  preserves the central symbolic question and unperformed closure tests.

- [`2026-09-04-symbolic-mechanism-first.md`](2026-09-04-symbolic-mechanism-first.md)
  - makes the symbolic reinjection explanation the organizing question in the
  title, abstract, early chain figure, results, conclusion, and research priorities;
  preserves the distinction between local ingredients and a verified connection.

- [`2026-09-04-symbolic-chain-restored.md`](2026-09-04-symbolic-chain-restored.md)
  - restores the source-derived 23-word chain and symbolic mechanism to the
  main article, distinguishes reported arrows from new validation, and leaves
  the draft author blank.

- [`2026-09-04-homoclinic-accuracy-grid.md`](2026-09-04-homoclinic-accuracy-grid.md)
  - the nine-case radius/tolerance study, prospective safeguards, and separate
  numerical and accuracy outcomes.

- [`2026-09-04-reproducible-core-and-readable-paper.md`](2026-09-04-reproducible-core-and-readable-paper.md)
  — a readable illustrated main article, preserved technical supplement,
  public core-data replay, later literature, and the independent homoclinic pilot.

- [`2026-09-04-public-research-audit.md`](2026-09-04-public-research-audit.md)
  — fixes numerical acceptance and public-source portability, retracts the
  full-flow Floquet-zero interpretation, qualifies homoclinic/criticality
  uncertainty, and prioritizes reproducibility and independent mechanism tests.

- [`2026-09-02-exp468-seventy-sixth-point-and-new-branch.md`](2026-09-02-exp468-seventy-sixth-point-and-new-branch.md)
  — the project resumes on a new research branch with a figure-rich README;
  EXP-468--473 add qualified Jones homoclinic points 76--81; the 80-point
  figure/manuscript checkpoint passes QA and EXP-474 is frozen prospectively.

- [`2026-08-30-exp467-seventy-five-point-checkpoint.md`](2026-08-30-exp467-seventy-five-point-checkpoint.md)
  — seventy-five receipt-bound roots qualify the nearby Jones homoclinic
  curve; the first sampled turn continues away from the printed section, and
  global nonintersection, uniqueness, and proof remain open.

- [`2026-08-30-exp462-seventy-point-checkpoint.md`](2026-08-30-exp462-seventy-point-checkpoint.md)
  — seventy receipt-bound roots qualify the nearby Jones homoclinic curve;
  the first sampled turn continues away from the printed section, and global
  nonintersection, uniqueness, and proof remain open.

- [`2026-08-30-exp457-sixty-five-point-checkpoint.md`](2026-08-30-exp457-sixty-five-point-checkpoint.md)
  — sixty-five receipt-bound roots qualify the nearby Jones homoclinic curve;
  the first sampled turn moves away from the printed section, and global
  nonintersection, uniqueness, and proof remain open.

- [`2026-08-30-exp452-sixty-point-checkpoint.md`](2026-08-30-exp452-sixty-point-checkpoint.md)
  — the 60-point visual/manuscript checkpoint and five prospectively frozen
  same-gate successors through EXP-457.

- [`2026-08-25-exp342-382-homoclinic-curve.md`](2026-08-25-exp342-382-homoclinic-curve.md)
  — forty-five qualified multiple-shooting roots approach within `1.75e-5` in
  `a` of Jones's historical section, resolve the first local `a` minimum, and
  continue through twenty-eight newly tangent-computed, defect-aware steps on its
  outgoing branch; the exact intersection and uniqueness stay open.

- [`2026-08-23-exp329-331-homoclinic-angle-scans.md`](2026-08-23-exp329-331-homoclinic-angle-scans.md)
  — 96-angle full-circle and 257-angle local scans find no sampled
  stable-aligned return at Jones's rounded hub coordinate, motivating a
  parameter-aware manifold-matching solve.

- [`2026-08-23-exp318-seventh-criticality-frozen.md`](2026-08-23-exp318-seventh-criticality-frozen.md)
  — the two-tableau, 50-digit audit resolves the parent as stable and
  preserves the stable/stable failure that redirects work to child-sheet
  topology.

- [`2026-08-17-exp315-passes-exp316-frozen.md`](2026-08-17-exp315-passes-exp316-frozen.md)
  — both solver-event brackets pass at `1.5e-13` scale and the equal-offset
  period-3072 criticality audit is frozen.

- [`2026-08-13-exp253-passes-exp254-frozen.md`](2026-08-13-exp253-passes-exp254-frozen.md)
  — stable primitive period 96 is qualified and its tangent-sign equivalence
  audit is frozen.

- [`2026-08-13-exp250-science-residuals-exp251-frozen.md`](2026-08-13-exp250-science-residuals-exp251-frozen.md)
  — the secant solve passes all DOP853 event residuals; segmented Radau
  independently qualifies the flip, period-96 children are nominated, and
  their stability-exchange audit is frozen.

- [`2026-08-13-exp249-residual-failure-exp250-frozen.md`](2026-08-13-exp249-residual-failure-exp250-frozen.md)
  — the endpoint-seeded 64-segment event solve stalls above its orbit gate; an
  unchanged-gate secant-seeded successor is frozen.

- [`2026-08-13-exp248-brackets-exp249-frozen.md`](2026-08-13-exp248-brackets-exp249-frozen.md)
  — the exact period-48 branch yields one clean period-96 bracket; its
  64-segment augmented event solve is frozen.

- [`2026-08-13-exp247-passes-exp248-frozen.md`](2026-08-13-exp247-passes-exp248-frozen.md)
  — the exact period-48 branch reaches a strongly unstable endpoint; a
  magnitude-separated nine-row next-flip scan is frozen.

- [`2026-08-13-exp246-period48-qualified-exp247-frozen.md`](2026-08-13-exp246-period48-qualified-exp247-frozen.md)
  — two solvers qualify a stable primitive period-48 child and local
  supercriticality; a short exact continuation is frozen.

- [`2026-08-13-exp245-period48-nominated-exp246-frozen.md`](2026-08-13-exp245-period48-nominated-exp246-frozen.md)
  — exact switching nominates primitive period-48 candidates; independent
  near-event stability exchange is frozen.

- [`2026-08-13-exp244-period24-flip-exp245-frozen.md`](2026-08-13-exp244-period24-flip-exp245-frozen.md)
  — the exact period-24 real-`-1` event passes DOP853/Radau and primitive
  identity gates; its period-48 switch is frozen.

- [`2026-08-13-exp243-brackets-exp244-frozen.md`](2026-08-13-exp243-brackets-exp244-frozen.md)
  — the magnitude-separated reclassification passes with one period-24 flip
  bracket; an exact augmented event solve is frozen.

- [`2026-08-13-exp242-tracker-swap-exp243-frozen.md`](2026-08-13-exp242-tracker-swap-exp243-frozen.md)
  — the frozen eigenvalue tracker swaps onto a collapsed mode; a strictly
  magnitude-separated reclassification of the immutable spectra is frozen.

- [`2026-08-13-exp241-supercritical-exp242-frozen.md`](2026-08-13-exp241-supercritical-exp242-frozen.md)
  — two solvers qualify the returning-arm period-12-to-24 flip as locally
  supercritical; a complete child Floquet scan is frozen.

- [`2026-08-13-exp240-unstable-endpoint-exp241-frozen.md`](2026-08-13-exp240-unstable-endpoint-exp241-frozen.md)
  — two solvers confirm the separated period-24 endpoint is strongly unstable;
  criticality is returned to a frozen near-event parent/child audit.

- [`2026-08-13-exp239-passes-exp240-frozen.md`](2026-08-13-exp239-passes-exp240-frozen.md)
  — a separated primitive period-24 branch passes 20 continuation steps; an
  independent parent/child criticality audit is frozen.

- [`2026-08-13-exp238-period24-nominated-exp239-frozen.md`](2026-08-13-exp238-period24-nominated-exp239-frozen.md)
  — exact segmented switching nominates primitive period-24 candidates on
  both signs; a separated child continuation is frozen next.

- [`2026-08-13-exp237-passes-exp238-frozen.md`](2026-08-13-exp237-passes-exp238-frozen.md)
  — an exact 16-segment period-12 flip and anti-periodic mode pass every gate;
  the first segmented period-24 switch is frozen.

- [`2026-08-13-exp236-collapses-exp237-frozen.md`](2026-08-13-exp236-collapses-exp237-frozen.md)
  — the targeted corrector converges but fails primitivity by collapsing to
  the doubled period-12 parent; an exact segmented event solve is next.

- [`2026-08-12-exp206-period6-flip-curve-frozen.md`](2026-08-12-exp206-period6-flip-curve-frozen.md)
  — exact-Jacobian coupled continuation passes all 41 points and establishes a
  dense sampled period-6 flip-curve segment over `c in [7.16,7.32]`.

- [`2026-08-12-exp205-period6-flip-refinement-frozen.md`](2026-08-12-exp205-period6-flip-refinement-frozen.md)
  — all seven prospectively selected real-minus-one Floquet brackets refine,
  qualifying a sampled period-6 flip edge and its continuation seeds.

- [`2026-08-12-exp204-lower-c-residual-replay-frozen.md`](2026-08-12-exp204-lower-c-residual-replay-frozen.md)
  — a 551-orbit, 12-view GPU residual replay is frozen and awaits the exact
  payload authorization required for its secure worker upload.

- [`2026-08-12-exp203-lower-c-stable-extension-frozen.md`](2026-08-12-exp203-lower-c-stable-extension-frozen.md)
  — the lower-c extension finds 551 qualified stable period-6 orbits in a
  bounded strip but fails its preregistered 1,000-point coverage gate.

- [`2026-08-12-exp202-scale-ensemble-residual-frozen.md`](2026-08-12-exp202-scale-ensemble-residual-frozen.md)
  — all 94 candidates retain a common critical assignment, but the second
  residual stays positive in every one of 1,128 scale/support/step views.

- [`2026-08-12-exp201-smoothing-scale-audit-frozen.md`](2026-08-12-exp201-smoothing-scale-audit-frozen.md)
  — a seven-level smoothing ladder and nested 2,048/8,192 support are frozen
  over the complete 104-point EXP-200 disagreement set and passes at 94 points.

- [`2026-08-11-exp200-lower-c-high-support-scan-frozen.md`](2026-08-11-exp200-lower-c-high-support-scan-frozen.md)
  — quadrupled support rejects sample scarcity but exposes a shallow critical
  that persists under four baseline variants and disappears under the single
  high-smoothing variant.

- [2026-08-09-visual-manuscript-rebuild.md](2026-08-09-visual-manuscript-rebuild.md)
  — the paper now presents nine provenance-tracked figures and Supplemental
  Movie S1; its concise abstract and all 28 rendered pages pass visual QA.

- [`2026-08-09-exp199-incomplete-signed-residual-scan-frozen.md`](2026-08-09-exp199-incomplete-signed-residual-scan-frozen.md)
  — 126 cross-step-qualified maps contain neither a direct center nor a
  simultaneous bracket: the first residual crosses zero while the second
  stays positive throughout the incomplete field.
- [`2026-08-09-exp198-local-orbit-mesh-frozen.md`](2026-08-09-exp198-local-orbit-mesh-frozen.md)
  — the frozen 2,511-point mesh reproduces the center and qualifies 685
  individual orbits but fails its 1,000-point coverage gate.
- [`2026-08-09-exp197-barrio-z-critical-scan-frozen.md`](2026-08-09-exp197-barrio-z-critical-scan-frozen.md)
  — the direct two-step z-critical scan rejects all 58 sampled corrected
  orbits as centers and prospectively localizes the closest residual.
- [`2026-08-09-exp196-gpu-barrio-parity-frozen.md`](2026-08-09-exp196-gpu-barrio-parity-frozen.md)
  — a source-only CPU/GPU parity gate is frozen for the new eight-phase,
  positive-x Barrio-section CUDA path and scalar z return map.
- [`2026-08-09-exp195-eight-phase-requalification-frozen.md`](2026-08-09-exp195-eight-phase-requalification-frozen.md)
  — a one-check successor freezes eight Barrio phases while preserving every
  EXP-194 orbit and all other qualification gates unchanged.
- [`2026-08-09-exp194-local-corrected-cycles-frozen.md`](2026-08-09-exp194-local-corrected-cycles-frozen.md)
  — a no-egress successor freezes DOP853 correction, Floquet stability, and
  Barrio-section phase extraction at 65 geometry-only component pixels.
- [`2026-08-09-exp193-second-component-cycle-sample-frozen.md`](2026-08-09-exp193-second-component-cycle-sample-frozen.md)
  — the 257-pixel GPU extraction was frozen but stopped before integration
  when the required derived-artifact transfer was denied.
- [`2026-08-09-exp192-two-landmark-band-frozen.md`](2026-08-09-exp192-two-landmark-band-frozen.md)
  — the executed 92,736-pixel atlas reproduces both landmarks as period 6 but
  places them in distinct stable raster components.
- [`2026-08-09-exp191-second-period6-window-frozen.md`](2026-08-09-exp191-second-period6-window-frozen.md)
  — the executed 40,401-pixel atlas places the second Jones landmark in a
  coherent 981-pixel period-6 band that exits both sampled `c` boundaries.
- [`2026-08-09-exp190-unimodal-neighborhood-and-new-lead.md`](2026-08-09-exp190-unimodal-neighborhood-and-new-lead.md)
  — all 65 Floquet-zero candidates remain two-branch, while an exploratory
  second-landmark check identifies a prospectively testable three-branch lead.
- [`2026-08-07-exp190-gpu-two-critical-scan-frozen.md`](2026-08-07-exp190-gpu-two-critical-scan-frozen.md)
  — both critical-to-orbit residuals, factor-two GPU parity, and target-word-
  blind ranking are frozen over all 65 prepared period-6 candidates.
- [`2026-08-07-exp189-zero-edge-candidates-frozen.md`](2026-08-07-exp189-zero-edge-candidates-frozen.md)
  — all 65 fine-grid sign-changing edges are frozen for identity-safe period-6
  correction before any GPU critical-residual ranking.
- [`2026-08-07-exp188-floquet-locator-rejected.md`](2026-08-07-exp188-floquet-locator-rejected.md)
  — fine continuation reveals many period-6 zero sheets and no refinement-
  stable saddle; the next locator must resolve both criticals directly.
- [`2026-08-07-exp188-fine-floquet-center-frozen.md`](2026-08-07-exp188-fine-floquet-center-frozen.md)
  — the failed EXP-187 center cell is resampled tenfold more finely with
  unchanged saddle-zero and independent-solver gates.
- [`2026-08-07-exp187-resolution-failure.md`](2026-08-07-exp187-resolution-failure.md)
  — the first Floquet-center mesh violates local orbit-identity gates before
  fitting; opposite multiplier signs motivate a tenfold finer successor.
- [`2026-08-07-exp187-floquet-center-search-frozen.md`](2026-08-07-exp187-floquet-center-search-frozen.md)
  — a word-blind period-6 Floquet saddle-zero search is frozen with coarse,
  refined, and independent-solver topology gates.
- [`2026-08-07-exp186-exact-landmark-word-fails.md`](2026-08-07-exp186-exact-landmark-word-fails.md)
  — the period-6 orbit passes strong solver gates, but x/z projection parity
  and every frozen word target fail; an actual center must be found dynamically.
- [`2026-08-07-landmark0-diagnostic-exp186-frozen.md`](2026-08-07-landmark0-diagnostic-exp186-frozen.md)
  — exact-coordinate pilot exposes an x/z projection split and noncritical
  period-5 orbit; untouched landmark-1 word test frozen with stricter gates.
- [`2026-08-07-exp185-historical-alphabet-qualified.md`](2026-08-07-exp185-historical-alphabet-qualified.md)
  — two solvers, both coordinates, held-out segments, and physical deposition
  geometry qualify the target-word-blind Jones alphabet mapping.
- [`2026-08-07-exp184-launcher-failure-exp185-frozen.md`](2026-08-07-exp184-launcher-failure-exp185-frozen.md)
  — pre-integration nested-receipt launcher failure preserved and
  scientifically unchanged EXP-185 successor frozen.
- [`2026-08-07-exp184-historical-alphabet-frozen.md`](2026-08-07-exp184-historical-alphabet-frozen.md)
  — source-derived `K1/C`, `K0/D`, and geometric numeral mapping frozen before
  any Figure 6 word is evaluated; execution status is superseded by the
  preserved launcher-failure update above.
- [`2026-08-07-exp183-local-critical-identity-qualified.md`](2026-08-07-exp183-local-critical-identity-qualified.md)
  — factor-two survivor parity and short-horizon DOP853 audits close the sole
  support hole and qualify the local unimodal-to-higher-critical identity.
- [`2026-08-07-exp183-gap-statistical-parity-frozen.md`](2026-08-07-exp183-gap-statistical-parity-frozen.md)
  — unchanged scientific successor frozen after EXP-182's pre-manifest import
  failure.
- [`2026-08-07-exp182-launcher-failure.md`](2026-08-07-exp182-launcher-failure.md)
  — direct-entry sibling import failure retained as administrative; no
  trajectory or result was produced.
- [`2026-08-07-exp182-gap-statistical-parity-frozen.md`](2026-08-07-exp182-gap-statistical-parity-frozen.md)
  — two-step survival/critical parity, attractor false-negative controls, and
  five-return DOP853 trajectory audits frozen for the Jones support gap.
- [`2026-08-07-exp181-gap-geometry-parity-failure.md`](2026-08-07-exp181-gap-geometry-parity-failure.md)
  — survivor criticals hit both frozen flank predictions, while the invalid
  long-time pointwise integrator-parity gate is honestly retained as failed.
- [`2026-08-07-exp181-jones-gap-sprinkler-frozen.md`](2026-08-07-exp181-jones-gap-sprinkler-frozen.md)
  — attractor-reference capture, negative gated-section sprinkler, flank
  predictions, and adaptive precision audit frozen at EXP-180's sole gap.
- [`2026-08-07-exp180-local-critical-support-hole.md`](2026-08-07-exp180-local-critical-support-hole.md)
  — 20/21 DOP853 and 4/5 Radau points track the same critical, while one
  solver-independent invariant-support hole keeps the full path failed.
- [`2026-08-07-exp180-local-critical-track-frozen.md`](2026-08-07-exp180-local-critical-track-frozen.md)
  — independent-anchor local critical bootstrap, full DOP853 path, and Radau
  controls frozen separately from global shallow-branch detection.
- [`2026-08-07-exp179-critical-identity-power-failed.md`](2026-08-07-exp179-critical-identity-power-failed.md)
  — doubled support retains a structured, coordinate-staggered global
  branch-count disagreement band and the strict identity failure.
- [`2026-08-07-exp179-critical-identity-power-frozen.md`](2026-08-07-exp179-critical-identity-power-frozen.md)
  — unchanged-threshold, doubled-power scan frozen at `0.0005` spacing inside
  EXP-178's failed critical-identity bracket.
- [`2026-08-07-exp178-critical-identity-direction.md`](2026-08-07-exp178-critical-identity-direction.md)
  — `x` and `z` select the same likely trimodal descendant, while the strict
  resolved-bracket-width failure is retained.
- [`2026-08-07-exp178-critical-identity-frozen.md`](2026-08-07-exp178-critical-identity-frozen.md)
  — cross-coordinate normalized-nearest critical identity rule and unresolved
  gap policy frozen across the historical-section attracting path.
- [`2026-08-07-exp177-two-branch-control-qualified.md`](2026-08-07-exp177-two-branch-control-qualified.md)
  — published unimodal point resolves as a neutral two-branch partition on the
  recovered Jones section in every split-cloud `x` and `z` variant.
- [`2026-08-07-exp177-two-branch-control-frozen.md`](2026-08-07-exp177-two-branch-control-frozen.md)
  — unchanged-threshold two-branch prediction frozen at the published
  unimodal parameter point on the distinct recovered Jones section.
- [`2026-08-07-exp176-neutral-partition-qualified.md`](2026-08-07-exp176-neutral-partition-qualified.md)
  — unchanged-threshold power successor qualifies the neutral three-branch
  Jones-section partition in split calibration/validation `x` and `z` clouds.
- [`2026-08-07-exp175-operational-partition-near-pass.md`](2026-08-07-exp175-operational-partition-near-pass.md)
  — neutral `x` partition passes split-cloud validation; strict `z` cross-check
  retains one 50-bin bootstrap-power failure and drives unchanged-gate EXP-176.
- [`2026-08-07-exp174-figure6-landmarks-frozen.md`](2026-08-07-exp174-figure6-landmarks-frozen.md)
  — blind two-transient, two-initial-state, DOP853/Radau classification is
  frozen and executed for all ten printed Figure 6 landmarks: eight late-time
  periodic labels, two unresolved points, and one preserved transient mismatch.
- [`2026-08-07-jones-path-symbol-source-audit.md`](2026-08-07-jones-path-symbol-source-audit.md)
  — Figure 2 path provenance and Figure 6's 23 words/11 arrows are now
  machine-readable; the missing reproducible partition remains the next gate.
- [`2026-08-07-exp173-period16-qualified.md`](2026-08-07-exp173-period16-qualified.md)
  — four exact fixed-path flips and independent stable-child qualification
  through period 16, plus the measured serial-recovery bottleneck.
- [`2026-08-07-exp156-first-flip-frozen.md`](2026-08-07-exp156-first-flip-frozen.md)
  — exact c-derivative, anti-periodic multiple shooting, cyclic Floquet, and
  independent Radau gates pass for the first period-1 flip.
- [`2026-08-07-exp155-schedule-correction-frozen.md`](2026-08-07-exp155-schedule-correction-frozen.md)
  — preserves EXP-154's administrative failure; the unchanged-gate successor
  passes the one-winding Hopf-to-hub period-1 continuation.
- [`2026-08-07-exp154-period1-path-frozen.md`](2026-08-07-exp154-period1-path-frozen.md)
  — 118-point, winding-safe period-1 continuation and independent Radau gates
  frozen from the Hopf neighborhood to the reported hub.
- [`2026-08-07-exp153-hopf-curve-frozen.md`](2026-08-07-exp153-hopf-curve-frozen.md)
  — exact Rössler Hopf construction passes independent eigensystem and
  transversality gates at all 192 fixed-`b=0.2` points.
- [`2026-08-07-exp001-saddle-focus-correction.md`](2026-08-07-exp001-saddle-focus-correction.md)
  — corrected a stale ledger entry: the reported hub equilibrium is locally
  qualified as a saddle focus, while homoclinic existence remains open.
- [`2026-08-07-exp152-transverse-seed-validator-frozen.md`](2026-08-07-exp152-transverse-seed-validator-frozen.md)
  — tested adapter and unchanged EXP-142 gates frozen for every future
  primitive family at the `c=19.9` bracket endpoints.
- [`2026-08-07-exp151-upo-identity-gates-frozen.md`](2026-08-07-exp151-upo-identity-gates-frozen.md)
  — continuous-phase primitivity and family-identity gates frozen before the
  transverse UPO recovery target is executed.
- [`2026-08-07-exp150-transverse-upo-preregistered.md`](2026-08-07-exp150-transverse-upo-preregistered.md)
  — frozen unchanged-method UPO recovery at both endpoints of the newly
  qualified `c=19.9` saddle-topology bracket.
- [`2026-08-07-exp133-upo-discovery-preregistered.md`](2026-08-07-exp133-upo-discovery-preregistered.md)
  — primitive UPO qualification through continuous phase identity and the
  frozen lag-12/lag-4 continuation test across the local boundary.
- [`2026-08-07-exp132-transverse-pim-preregistered.md`](2026-08-07-exp132-transverse-pim-preregistered.md)
  — frozen 256-return replication that qualifies the `c=19.9` finite bracket
  and `c=19.8,a=0.150` endpoint while retaining the other lower endpoint and
  the full experiment as failed.
- [`2026-08-07-exp131-transverse-pim-preregistered.md`](2026-08-07-exp131-transverse-pim-preregistered.md)
  — frozen adaptive-PIM and signed-slope predictions at four transverse
  endpoints, followed by a clean prospective falsification of the proposed
  `c=19.8,a=0.148` upper endpoint.
- [`2026-08-07-exp130-transverse-pilot-preregistered.md`](2026-08-07-exp130-transverse-pilot-preregistered.md)
  — frozen two-slice GPU discovery design, unresolved-aware topology gates,
  and a run-specific Runpod cost/teardown contract.
- [`2026-08-07-signed-boundary-observable.md`](2026-08-07-signed-boundary-observable.md)
  — prospectively successful signed lower-support prediction at the blind
  `a=0.148125` midpoint and the narrowed finite bracket.
- [`2026-08-07-chaotic-saddle-qualification.md`](2026-08-07-chaotic-saddle-qualification.md)
  — passed CPU and GPU reconstruction of the two published nonattracting
  chaotic-saddle controls, with exact method and claim boundaries.
- [`2026-08-07-paper-workspace-and-referee-citations.md`](2026-08-07-paper-workspace-and-referee-citations.md)
  — compile-ready manuscript, verified referee citations, and automated
  BibTeX/citation traceability gate.
- [`2026-08-07-high-period-cascade-frontier.md`](2026-08-07-high-period-cascade-frontier.md)
  — identity-safe cascade through a stable period-640 child and the frozen
  640-to-1280 event prediction.
- [`2026-08-06-global-atlas-launch.md`](2026-08-06-global-atlas-launch.md)
  — bounded high-`a` atlas design, EXP-013 preregistration, and compute ceiling.
- [`2026-08-06-foundation-and-first-atlas.md`](2026-08-06-foundation-and-first-atlas.md)
  — repository audit through the first Lyapunov-resolved hub pilot.

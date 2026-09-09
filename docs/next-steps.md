# Research priorities after the public audit

Symbolic execution updated 2026-09-09; other priorities reviewed 2026-09-04.
This is the current execution order; the long
[backlog](TODO.md) and frozen manifests retain the historical record.
The [audit](reviews/2026-09-04-public-research-audit.md) explains the corrections
that motivate this sequence. No new GPU jobs were launched for the audit.

The [execution update](updates/2026-09-04-reproducible-core-and-readable-paper.md)
records the first implementation checkpoint. A completed subtask does not
close the broader scientific acceptance criterion below.

The symbolic reinjection explanation is the central scientific objective,
not a final illustration after the numerical work. The next mechanism
experiment should target one `p -> p+1` connection, with its definitions and
inputs made independently reproducible. Full-campaign data release and
completion of every homoclinic refinement are not prerequisites for that
bounded test. Homoclinic accuracy remains required for claims about the global
organizer; no existing acceptance criterion or failed experiment is waived.

## 1. Make the central evidence independently reproducible

- [x] Inventory a first core replay: one atlas panel, one flip, and the initial
  homoclinic candidate, with exact input hashes. Full-campaign dependency
  closure remains open.
- [x] Publish the first versioned [core data bundle](reproducibility.md) with
  checksums, source revision, locked environment, and data license.
- [ ] Expand the public dependency closure to the full campaign, including
  remaining corrected orbits and section/saddle samples. A hash of an
  unavailable file is not a substitute for that file.
- [x] Reproduce one atlas panel, one flip event, and the initial homoclinic
  candidate from a fresh checkout using only the published bundle. Make this
  a documented command and retain discrepancies. The
  [public-download check](reviews/receipts/research-core-v1-public-download.json)
  passes the declared gates; the atlas is a cached-classification redraw.
- [ ] Re-audit all callers of the corrected periodic/phase/arclength gates.
  The [caller audit](reviews/2026-09-04-corrector-caller-audit.md) now fixes
  nine unchecked periodic sites and one shared segmented-arclength gate,
  with failure-injection tests. It does not revalidate the full archive or
  every other corrector implementation.
- [x] Link public code, immutable core/EXP-476 releases, and Movie S1 directly
  from the PDF, with explicit limits on which calculations the public inputs
  can replay. This fixes access information, not full-campaign data closure.
- [ ] Audit return events for transversality throughout the principal orbit,
  branch, and symbolic products. Record normalized crossing angle and invoke
  extremum-aware collection or an unresolved status near tangencies; the
  previously found grazing is not an archive-wide validation.
- [ ] Cross-check a representative low-period flip/child branch in a separate
  continuation formulation, not merely with another integrator inside the
  same shooting/event implementation.

Acceptance: a separate environment can acquire the documented inputs, verify
their hashes, recompute the selected results, and regenerate the figures
within declared numerical tolerances. CPU tests already pass without private
inputs; historical result reproduction is a separate requirement.

## 2. Test the symbolic reinjection mechanism

- [x] Qualify observation of both fixed EXP-479 cycles on both sections:
  [EXP-480](updates/2026-09-06-exp480-both-cycles-qualified.md) passes; six
  historical and eight Barrio events are not a one-to-one alphabet transport.
- [x] Implement raw-retaining common-population selection and joint scalar-map
  analysis, including complete critical-proximity matrices. The
  [EXP-481 synthetic checkpoint](updates/2026-09-06-exp481-replay-decisions.md)
  validates software plumbing, not the nominated Rössler maps.
- [x] Add the adaptive qualification adapter and verify capture-reference rows
  against preserved EXP-480 raw events. The
  [synthetic cross-check](updates/2026-09-06-exp481-adaptive-qualification.md)
  passes; qualification of new nominated trajectories has not run.
- [x] Add durable adaptive snapshots, stage supervision and a pre-import worker
  guard. [Synthetic interruption controls](updates/2026-09-06-exp481-durable-supervisor.md)
  preserve both sections' accepted events/capture labels without false completion.
- [x] Compose the fixed trial grid and both-case analysis, with no best-case
  selection. [Campaign controls](updates/2026-09-06-exp481-campaign-aggregation.md)
  retain all six historical reference rows and unresolved cases.
- [x] Qualify the isolated numerical-worker startup and canonical environment.
  [Nine controls](updates/2026-09-07-exp481-sealed-startup.md) pass; the complete
  source/input/review-bound target dispatcher is not implemented yet.
- [x] Connect the actual isolated input consumer and exact nine-file package.
  [Preserved-reference checks](updates/2026-09-07-exp481-sealed-input-audit.md)
  reproduce the prior result without importing the GPU scout.
- [x] Finish the production controller and numerical phase dispatcher with
  authenticated campaign wiring. EXP-481 failed its numerical qualification;
  the separate finer-step EXP-482 passed all 192 comparisons and completed
  collection, but neither nominated map passed its support gates. Both
  consumed experiments retain their original decisions.
- [x] Diagnose the support failure from saved data. [EXP-483](updates/2026-09-08-exp483-support-diagnosis.md)
  identifies substantial early pair-selector loss and fitted-endpoint exclusion;
  late coverage remains sparse. It does not produce a replacement map verdict.
- [x] Execute and audit the frozen [EXP-484 direct-return pilot](experiments/EXP-484-return-geometry-pilot.md):
  actual early calibration states, two solvers, event-time-corrected section
  derivatives and fixed finite-difference controls. No critical symbols may be
  assigned from coordinate partial derivatives alone.
  All 80 points passed; the entire 240-integration matrix and its decisions
  were audited. See [the completed result](updates/2026-09-08-exp484-direct-geometry.md).
- [x] Complete the fixed [EXP-485 transported-direction pilot](updates/2026-09-08-exp485-transported-tangents.md):
  eight actual predecessors at every EXP-484 point, two solvers, four history
  lengths, complete-grid audit and explicit unresolved/near-vertical cases.
  All 1,280 integrations completed and 80 directions passed. Ten points fail
  the separate x-graph conditioning gate; no critical symbols were assigned.
- [ ] Construct actual finite-return image curves near the two observed
  slope-sign-change regions in each case. Test curve/critical-location agreement
  across history lengths, initial curve directions and solvers before treating
  discrete sign changes as fold brackets. The fixed 16-family
  [EXP-486 pilot](updates/2026-09-08-exp486-continuous-return-curves.md)
  completed 928 integrations: one of four regions qualified, and all
  left-region fold refinements failed solver agreement. Its full-grid audit
  and all-family figure are complete. The
  [EXP-487 event-census witness](experiments/EXP-487-section-census-witness.md)
  completed twelve profiles and confirmed the ordinary-event omission.
  [One witness qualified; one retained an accuracy/reference failure](updates/2026-09-08-exp487-missed-crossing-witness.md).
  [EXP-488 separated refined convergence from the old coarse reference](updates/2026-09-08-exp488-event-accuracy.md):
  all twelve profiles completed; the first witness passes all six fine-pair
  comparisons and the second passes three of six. Its finest solver pair agrees,
  but the complete criterion still fails.
  [EXP-489 directly reproduced a section-grazing boundary near both selected witnesses](updates/2026-09-08-exp489-section-grazing.md):
  26 integrations, both solvers, all signed perturbations, four preceding
  accepted returns and the predicted pair birth/death and square-root scaling.
  [EXP-490 completed all 26 original candidate intervals and 52 solver profiles](updates/2026-09-08-exp490-direct-folds.md),
  retaining 208 trajectories. Ten paired-qualified searches recover nearly
  coincident right-hand fold locations within each case across all eight
  right-region families. Fourteen intervals leave the fixed search boxes;
  two converge but fail the input-projection gate in both solvers. Different
  upstream roots can approach the same physical fold; do not count them as
  extra scalar-map branches. Next construct event-consistent, conditioned
  curve segments with explicit cuts at section grazing and input-projection
  turns, retaining uncovered intervals and the full depth/direction matrix.
  Do not bridge those cuts or select only favorable accuracy profiles.
  [EXP-491 completed the full three-point screen](updates/2026-09-08-exp491-event-sheet-probe.md):
  all 156 trajectories and 78 paired samples qualify numerically, but sixteen
  intervals fail time coherence, including two input-sign reversals. The
  ten screened intervals match EXP-490's ten qualified searches.
  [EXP-492 directly localized all sixteen nominated tangencies](updates/2026-09-08-exp492-event-boundaries.md):
  all 248 integrations completed; both methods pass local geometry, but only
  fifteen candidates pass the complete rule. One paired side-state comparison
  exceeds its frozen bound and remains unqualified. The root states nearly
  coincide within each parameter case; do not count upstream preimages as
  different physical critical objects. Three passing samples still do not
  certify a whole interval, and the ten unselected intervals remain untested
  for hidden boundaries.
  Do not require global smoothness merely to permit symbolic coding: define
  consistent piecewise return domains where appropriate. Test whether an
  extra crossing represents the proposed physical inner return or only a
  change in section-based event count, using geometric trajectories and
  corrected orbit families rather than word matching alone.
  [EXP-493 completes the local saved-trajectory winding check](updates/2026-09-09-exp493-projected-inner-turn.md):
  all 128 profiles and 64 opposite-side comparisons reproduce one extra
  projected winding; the complete result retains the parent 15/16 verdict.
  All local-window polygons are public and replayable without private data.
  Next transport this geometric marker onto corrected periodic cycles and
  qualify its relationship to the critical/branch partition, then continue
  one proposed p-to-p+1 connection. The fixed-parameter initial-condition
  result does not already establish that periodic-family connection.
  EXP-480's two corrected cycles both retain six historical/eight Barrio
  returns; they are not established opposite-period endpoints. Include a
  minimal-period check and actual parameter-family transport before claiming
  a chain connection.
  Then test a conditional local partition
  on held-out returns and corrected cycles, without selecting for target words.
- [ ] Establish the relevant return curve or quotient and its critical geometry
  before assigning target words or continuing a chain arrow. No automatic paid
  review gate applies: major-milestone reviews require human approval per call.
- [ ] Before the next manuscript release, complete the documented
  [legacy turning-point impact audit](experiments/EXP-481-legacy-turning-point-incident.md)
  against preserved historical raw evidence. Its analytic stationary-inflection
  defect is confirmed; impact on earlier Rössler conclusions remains unmeasured.
- [x] Independently enumerate the finite quadratic-map control and compare
  its words/order with the in-scope unimodal source subset under a predeclared
  dictionary. [EXP-478](experiments/EXP-478-quadratic-symbolic-control.md)
  passes this bounded test; third-branch nodes and Rössler arrows are excluded.
- [ ] Execute the separately frozen, raw-retaining
  [EXP-477 center scout](experiments/EXP-477-symbolic-center-pilot.md), then
  qualify any nomination on the historical section before word comparison.
  The [SSH storage amendment](updates/2026-09-05-prax-evidence-storage.md)
  passed its live controls and backed up the frozen source/inputs to `prax`.
  The sole GPU attempt failed configuration validation before source upload
  or targets, then verified cleanup. Before another paid attempt, preserve
  allowlisted provider configuration diagnostics and resolve the exact
  contract/schema mismatch; do not weaken checks or silently retry.
  Recovery corrected the API mapping but a later create returned an ambiguous
  provider error. [EXP-479](experiments/EXP-479-cpu-symbolic-center-pilot.md)
  now provides the local CPU route with unchanged numerical search rules.
- [x] Complete the separately declared CPU scout and full evidence audit.
  [EXP-479 results](updates/2026-09-06-symbolic-scout-results.md): 551 cases,
  384 eligible, two direct nominations, zero corner-range nomination cells.
  Both center nominations remain exploratory. EXP-480 subsequently qualified
  their section-event observations, but partition/criticality and symbolic
  comparison remain incomplete. EXP-477 CUDA did not run.
- [ ] Define the two-dimensional first-return map and the precise scalar
  projection or quotient used for critical-point claims. Quantify when a scalar
  coordinate is not a single-valued map; report conditional spread/support.
  Review 001 adds the explicit quotient condition and an object-by-object
  table; it does not construct or prove the quotient.
- [ ] Replace the retired full-flow Floquet-zero proxy with separate,
  uncertainty-bearing critical-to-orbit membership residuals. Follow critical
  identities across parameter changes and test section/coordinate changes.
- [ ] Freeze one bounded pilot: locate a center without using the desired word,
  encode the independently corrected orbit, and test a proposed `p -> p+1`
  connection at held-out parameters. Stop on unresolved center/partition
  measurements rather than tuning them to produce a source match.
- [ ] Complete the 23-word, period-seven comparison using the frozen source
  target: canonical words, orbit permutations, missing words, and first
  disagreements. A period-doubling cascade alone cannot fill this table.
- [ ] Define a signed manifold-contact or pruning observable for the already
  observed lobe-inclusion change. Test a prediction at held-out parameters
  before identifying it with the topology-transition curve. Results on
  separate slices must not be described as one connected symbolic transition.
- [x] Document both equilibria and time-directed spectral quantities at the
  printed hub, numerical candidate, and classifier endpoints using independent
  algebraic checks. This establishes local spectra, not global involvement.
- [ ] Test competing manifold geometry involving the second equilibrium;
  local eigenvalues neither establish nor exclude its reinjection role.
- [ ] Freeze a randomized-net uncertainty study with independent scrambles
  as the replicate unit. Existing within-net bootstraps/log-rank outputs are
  descriptive; justify replicate count and inferential assumptions before
  attaching calibrated coverage to new effect estimates.
- [ ] Build one computed unfolded-spiral figure that connects parameter path,
  orbit identity, return-map branches, critical values, and symbolic transitions.
  The existing source-derived chain is the hypothesis, not this computed test.

Acceptance: a reader can trace every proposed `p -> p+1` connection to
corrected orbits and an independently specified partition; a changed section
does not silently become a changed invariant-flow claim. Negative or incomplete
word matches are published with the successful matches. The pilot is not
complete until the measured extra return is compared with the predicted
insertion, rather than inferred from generic cascade depth.

## 3. Resolve the homoclinic accuracy question

- [x] Reproduce the initial fixed-c candidate with an independent boundary-value
  formulation. EXP-475 passes analytic positive/negative controls and four
  eigenspace-endpoint collocation cases. AUTO/HomCont was not installed;
  this is a distinct SciPy formulation, not an AUTO validation or proof.
- [x] Implement and prospectively freeze the proposed
  [radius-by-tolerance grid](plans/2026-09-04-homoclinic-refinement.md).
  EXP-476 was executed once from pushed, tagged clean source. Five cases pass,
  the sixth fails at the mesh-refinement cap, and three are skipped.
- [ ] Complete the initial-point accuracy study. [EXP-476](experiments/EXP-476-homoclinic-radius-tolerance-grid.md)
  qualifies tolerance contraction only at radius `0.01`; both endpoint
  comparisons remain unavailable. Inspect and control the floating-point
  sensitivity found on the failed saved mesh before freezing a new strategy.
  Do not retry or retrospectively relax EXP-476.
- [ ] Vary departure/arrival radii, truncation time, mesh, gauge, and precision
  at selected points before and near the apparent turn. Preserve failed solves.
- [ ] Estimate errors in `a` and `c` specifically, rather than interpreting a
  residual threshold or a smallest-singular-value floor as parameter accuracy.
- [ ] If those checks resolve the turn, define a bounded search for intersection
  with the historical section and alternative connections. State the searched
  domain and which branches remain unexamined.

Acceptance: independent formulations agree within a declared parameter
uncertainty that resolves the feature being claimed. A validated local
existence argument would be a further result, not a synonym for agreement.
EXP-474 remains frozen but deferred; adding nearby points with unchanged
uncertainty is lower priority than answering this question.

## 4. Resolve the unusual eighth birth before emphasizing it

- [ ] Continue daughter amplitudes toward the event on both sides using
  independent discretizations and phase-invariant parent comparison.
- [ ] Check daughter amplitude tends to zero and the relevant daughter
  multiplier tends to `+1`. Explain the existing sampled multiplier near 19.
- [ ] Determine criticality from convergent local amplitude/normal-form data,
  accounting for nearby folds and finite-offset sampling.

Acceptance: the local classification survives shrinking offsets and refinement.
Until then, retain the evidence as suggestive rather than claiming that the
sampled stable-parent/unstable-child pair settles the local normal form.

## 5. Establish novelty and a focused paper

- [ ] Perform the missing post-2012 primary-literature review covering
  periodicity hubs, homoclinic organization, return-map reduction, pruning,
  numerical continuation, and validated numerics. The pre-audit bibliography
  had only ten entries, all dated 2012 or earlier.
- [x] Start a targeted post-2012 update: five verified sources, a tested
  equation-convention conversion, and explicit reading-status boundaries.
- [x] Start a claim-level comparison: prior result, Jones/Barrio co-discovery,
  modern reproduction, correction, and potentially new result. Preserve the
  agreed independent co-discovery wording without extending priority claims
  to earlier TTL/TBA work.
- [x] Address Review 001's concrete literature omissions with nine verified
  additions and an explicit source-level manuscript comparison. Preserve
  reading-status limits: this is not a completed systematic survey.
- [x] Focus the main paper on a small connected set of defensible results;
  move the chronological experiment narrative into supplements. Keep the
  figure-rich presentation and explicit negative controls.

Acceptance: every novelty claim survives comparison with the relevant primary
work, and the manuscript's main argument can be followed without reading
hundreds of experiment records.

## 6. Generalize the methods, then scale computation

- [ ] Separate system definitions (vector field, Jacobian, domain, sections)
  from Rössler-specific scripts and result schemas.
- [ ] Qualify the pipeline on two flows with contrasting return geometry;
  choose them from the literature review, including a case where the proposed
  scalar reduction is expected to fail. Do not assume every attractor has the
  same shrimp organization.
- [ ] Add adaptive refinement, uncertainty and basin overlays to the atlas.
  State the bounded parameter domain and unresolved fraction. A finite raster
  cannot establish a complete classification of an unbounded parameter plane.
- [ ] Benchmark GPU throughput on the actual ensemble observables with CPU
  controls, short-run timing, checkpoints, and a cumulative job budget. Keep
  delicate high-precision continuation and validation on the implementation
  that meets the accuracy requirement.
- [ ] Expand to dozens of systems only after the two-system transfer test
  works without per-case hand tuning of acceptance criteria.

Acceptance: the same documented interfaces, evidence schema, and failure
criteria work on the held-out systems. GPU work accelerates validated ensemble
calculations; it does not replace mechanism tests or parameter-error analysis.

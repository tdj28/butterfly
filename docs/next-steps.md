# Research priorities after the public audit

Symbolic execution updated 2026-09-10; other priorities reviewed 2026-09-04.
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
  [EXP-494 completes that bounded transport/minimal-period survey](updates/2026-09-09-exp494-periodic-winding-transport.md):
  all eight older cycle profiles pass, and 54/64 new paired parameter nodes
  qualify after 806 integrations. Two continuations converge to a shorter
  three-return cycle traversed twice; the primitive-period gate rejects them
  despite passing closure and unchanged nominal 6/8 event counts. Eight
  dependent nodes remain unrun. All qualified samples retain winding six.
  Carry the primitive-period guard into every successor; do not silently
  continue a repeated parent as the requested family. Prioritize qualified
  critical-to-orbit membership and an operational branch dictionary on
  primitive candidates before interpreting another parameter sweep as a
  source-chain test. A possible three/six flip is a different question, not
  completion of the required insertion arrow.
  [EXP-495 completes the direct saved-state critical-contact screen](updates/2026-09-09-exp495-fold-cycle-membership.md):
  all 240 eligible pair cells are audited, with all 26 parent candidates
  retained. Neither base is proximate to the measured right-hand fold under
  the primary or any fixed sensitivity radius, even in x alone. These are
  qualified periodic orbits, not qualified critical-contact centers. Next
  solve/refine a contact condition on the primitive family and recompute the
  fold at each new parameter, retaining both solvers, all depth/direction
  representations and failures. Establish the second critical object or
  justified piecewise domain boundary separately; no C/D label follows from
  one right-hand fold or a three/six doubling relation.
  [EXP-496 supplies one qualified endpoint interval](updates/2026-09-09-exp496-contact-endpoint.md):
  all 124 new trajectories are audited. The first case has opposite signed
  residuals across all four representations; the second remains mixed because
  both depth-eight searches lose input conditioning. Next localize inside the
  first interval, re-correcting the primitive cycle and recomputing every fold
  representation at each new parameter. Neither endpoint is proximate; endpoint
  signs alone do not prove an interior contact or continuity.
  [EXP-497 completes that bounded interior localization](updates/2026-09-09-exp497-contact-localization.md):
  after 179 retained target IVPs, the third point meets the unchanged full-state
  proximity rule in all sixteen variants and retains primitive six/eight counts.
  Use this one-fold calibration point to identify the second critical object
  or consistent piecewise boundary, then qualify the branch dictionary. It is
  not yet an exact critical point, C/D assignment, doubly-superstable center or
  source-matched arrow; the second case's inherited failures remain.
  [EXP-498 transports the grazing boundary to that same point](updates/2026-09-09-exp498-boundary-transport.md):
  136 integrations complete, but only six of eight boundary/turn matrices
  qualify. Two near-tangent paired-state errors remain. All 768 predecessor/
  cycle comparisons are retained, and no event index meets the proximity rule.
  Diagnose those errors from retained trajectories, then freeze a successor
  with unchanged accuracy thresholds. Joint contact conditions in a and c,
  not further one-fold tuning alone, are needed to test a two-object center.
  Preserve every representation, the primitive-period guard and the distinction
  between a piecewise domain boundary and a smooth critical point.
  [EXP-499 supplies an all-input decimal reference](updates/2026-09-09-exp499-decimal-event-reference.md):
  all 64 trajectories and 480 nominated roots are audited, and the two decimal
  configurations agree at every input. A third original method/input discrepancy
  demonstrates the limitation of paired Float64 agreement. Next use the retained
  high-precision coefficients for a separately declared complete polynomial
  census and local geometric replay, retaining unresolved isolation and avoiding
  an exact-flow all-root claim. New-parameter high-precision grazing transport
  and joint contact conditions remain separate; do not substitute passing rows
  into the old EXP-498 decision. Shared root-box resolution also limits what
  tiny paired decimal differences say about absolute accuracy.
  [EXP-500 closes the complete stored-polynomial census](updates/2026-09-09-exp500-complete-polynomial-census.md):
  all 239,072 segments and 1,024 plane roots pass the count-certificate audit;
  both configurations agree at every input and reproduce all old accepted
  sequences. There are no unresolved regions or failed join checks. Use these
  qualified event sequences for local geometric replay, then high-precision
  grazing/domain transport and the joint contact conditions. This is not an
  exact-flow all-root proof or a periodic-family insertion: history-dependent
  finite-time counts cannot be relabeled as primitive periods. All older
  accuracy failures remain unchanged.
  [EXP-501 now qualifies the limiting boundary itself](updates/2026-09-09-exp501-limiting-contact.md):
  all 38 integrations, sixteen precision profiles and 72 accepted prefix
  events pass the raw audit. All 384 limiting-predecessor/cycle comparisons
  fail the primary proximity criterion; the best all-variant distance is
  0.01346118, also outside the largest sensitivity radius. Finite perturbations
  do not explain the gap. [EXP-502 reached its storage threshold](updates/2026-09-09-exp502-joint-contact-search.md)
  after seven of eight joint a,c response-stencil points. The
  [EXP-503 continuation](updates/2026-09-09-exp503-resource-continuation.md)
  preserves that failure and reuses all seven complete points to finish the
  same matrix and sole correction. Its full raw audit now passes all nine
  points and 1,580 integrations. All 256 correlated response variants qualify;
  the correction reduces the dominant residual 5.64% while retaining fold
  proximity, but the boundary distance is still 0.012702, about 127 times
  tolerance. Both contact and 20% reduction targets fail. Freeze a bounded,
  event-index-preserving continuation toward lower c with renewed response,
  full-state and primitive-cycle checks. The unbounded linear extrapolation
  (roughly -0.3595 in c) is not a validated root or an authorized numerical
  jump. Plan retained storage before targets; preserve all old evidence and
  consumed attempts, and do not use a favorable subset to certify contact.
  Do not spend another experiment merely refining this fixed anchor or count
  its near-identical upstream boundary representations as different objects.
  [EXP-504's full raw audit](updates/2026-09-09-exp504-guarded-contact-continuation.md)
  passes 200 IVPs, but the first warm step violates fold proximity by 1.19%.
  All numerical and cycle-identity checks pass and the boundary gap decreases;
  the combined model-error norm masked a wrongly predicted fold component.
  The point is rejected and seven later slots remain unrun. This motivates a
  fixed-c fold-restoration test, then a constrained continuation that corrects
  the fold condition before accepting a path point. Preserve this failure and
  every threshold; do not resume EXP-504 or count its diagnostic improvement
  as an accepted path. Then test a conditional local partition
  on held-out returns and corrected cycles, without selecting for target words.
  [EXP-507 completes the fixed-c correction](updates/2026-09-09-exp507-fixed-c-fold-restoration.md):
  all 158 integrations pass raw audit, and full-state fold distance falls to
  0.00000385436 under the unchanged 0.0001 bound. The boundary remains about
  119 times too far away. EXP-508 then produced one lower-c predictor (196 IVPs)
  but its controller crashed on an incomplete contact envelope. No corrector ran.
  [EXP-509](updates/2026-09-09-exp509-failed-predictor-replay.md) prospectively
  repairs unqualified-point reporting and passes the complete 196-IVP raw audit
  without new integrations. Both depth-8 equation roots have near-collapsed
  input curves and same-sign neighboring slopes; the depth-4 folds qualify but
  miss contact tolerance. The 6.735% boundary-gap reduction does not license
  acceptance. [EXP-510](updates/2026-09-09-exp510-four-substep-fold-transport.md)
  implements four smaller fold-only continuation substeps from
  qualified EXP-507 to the same predictor parameters, retaining all four
  representations and both solvers with cross-history full-state agreement.
  Its complete 180-IVP audit passes: all representations qualify at c=7.167,
  but both depth-8 inputs again fail at c=7.162; later substeps are unrun.
  One qualified fold-only substep is not a new joint-contact point. Next sample
  the declared depth-8 image curves directly over a frozen domain at the failed
  parameter, comparing coverage against the qualified depth-4 fold states.
  Retain all regularity failures and every connected root bracket; distinguish
  a solver's wrong root from insufficient finite-curve coverage. Do not infer
  a physical bifurcation or global root absence from this finite failure.
  Do not warm-start from the collapsed roots or lower the gain threshold.
  [EXP-511](updates/2026-09-09-exp511-direct-curve-coverage.md) now completes
  that fixed grid: all 160 IVPs pass full dense replay; 31/40 paired samples
  are regular, two collapse and seven lack a ninth return before the fixed
  horizon. Neither curve supplies a qualifying sampled fold bracket. Next
  extend the horizon for all seven censored samples, with unchanged inputs and
  both solvers, and verify their complete saved eight-return prefixes. Do not
  call this time-window censoring a domain hole or proof of lost physical
  coverage. Any newly exposed bracket still needs event-sheet continuity and
  fold qualification; the other 33 original samples and all failures remain.
  [EXP-512](updates/2026-09-09-exp512-censored-return-extension.md) completes
  that extension: all 28 new IVPs pass dense replay, every saved eight-return
  prefix is unchanged at retained precision, and all seven ninth returns are
  observed. The newly labeled grid has 38/40 regular pairs and five candidate
  intervals: direction 0 [1,2], [15,16], [16,17]; direction 1 [17,18], [18,19].
  Next freeze local fold/event-sheet qualification for all five, both solvers,
  with unchanged gates and full-state comparisons to the four depth-four
  references. Do not count these as five distinct folds or join across a
  grazing discontinuity. Recovered fold representations may support renewed
  constrained joint-contact continuation, not an automatic symbolic claim.
  Preserve all failures and never resume a consumed attempt.
  [EXP-513](updates/2026-09-10-exp513-candidate-fold-qualification.md) now
  implements this all-five test: paired midpoint observations seed bounded
  fold shootings; all nine returns at three offsets and all four full-state
  references must agree. All 30 target IVPs audit cleanly, but both solvers'
  first Newton proposals leave the u box at every candidate. No fold or
  reference restoration qualifies. Next freeze a bracket-preserving,
  event-aware refinement of all five intervals; discriminate a smooth root
  from a grazing/domain cut instead of interpreting these full-step failures
  as global absence or repeating the same unconstrained Newton seed.
  [EXP-514](updates/2026-09-10-exp514-candidate-grazing-boundaries.md) now
  completes all five nominated grazing localizations and the full four-dose,
  two-solver mechanism test. All 120 IVPs pass the raw audit and all five
  candidates qualify. These are clustered upstream representations, not five
  independent physical objects. Reconstruct event-consistent depth-eight input
  coverage near the depth-four fold reference; distinguish finite-image support
  loss from numerical conditioning before another parameter step. Do not rerun
  the now-classified grazing brackets as fold candidates, lower the gain gate,
  or infer global absence of other smooth folds. Primitive-family membership
  and the operational C/D dictionary remain necessary for the symbolic arrow.
  [EXP-515](updates/2026-09-10-exp515-third-return-precision.md) directly tests
  the earlier sensitivity loss at return three: six realized initial inputs,
  two high-precision configurations, all three return ordinals and both old
  solver comparators. Preserve relative-error and root-box uncertainty failures;
  no lowered gain gate or newly recomputed section may manufacture agreement.
  Its complete twelve-IVP raw audit passes and all eighteen decimal-pair
  sensitivities resolve. The two center third-return norms remain near 1e-13;
  all four old center derivative vectors fail relative accuracy, while neighboring
  inputs and earlier returns agree. This supports a real tiny numerical
  derivative and an old precision limitation, not restored depth-eight coverage.
  Next prospectively reconstruct well-conditioned event-consistent image curves
  with held-out validation; do not try to create missing physical support by
  rescaling the old curve or silently dropping the longer-history contrast.
  [EXP-516](updates/2026-09-10-exp516-event-ordinal-coverage.md) first checks the
  cheaper return-renumbering explanation against every retained ordinal:
  all 740 events and 660 pairs audit cleanly, with all 40 old decisions intact.
  No sampled pair restores the reference. Two new endpoint-only cells at
  direction-0 returns 4-to-5 and 7-to-8 bracket the reference x and require
  direct, event-aware fold qualification. Test both with prospective mapped
  initial-direction contrasts and all full-state references; do not call
  earlier-return recovery a pass of the rejected original eighth-return test.
  [EXP-517](updates/2026-09-10-exp517-earlier-return-folds.md) now recovers
  the same local scalar fold in all four new history/direction constructions,
  with both solvers, all full-state references and unchanged gates. All 108
  IVPs pass raw audit; the maximum scaled cross-representation spread is
  1.55605e-13. This is a calibrated local ingredient, not a verified chain.
  Next freeze a prospective transport of these four constructions to the
  two remaining EXP-510 parameter substeps, preserving all failed old
  representations. Require complete event prefixes, input regularity,
  cross-representation agreement and adjacent full-state identity before
  any new endpoint fold/cycle comparison or renewed joint contact.
  The endpoint was exposed in EXP-508/509 with old representations; do not
  describe this outcome-informed successor as fully blind validation.
  [EXP-518](updates/2026-09-10-exp518-recovered-fold-transport.md) completes
  that transport: all 200 IVPs audit and every construction qualifies at both
  remaining steps. Endpoint contact still fails in all 16 full-state variants,
  despite passing x projections (worst 1.39565e-4 versus 1e-4). Next explicitly
  bind the recovered four/seven-return families and qualify their local
  parameter response before a new correction. Preserve the full-state test
  and primitive identity; do not reuse old depth-eight response derivatives.
  A joint fold/grazing correction alone would not supply the missing second
  smooth critical point or verify a Jones word: retain that separate target.
  New executions must use the tested `bounded_json.py` admission for every JSON
  product, including final summaries, and compact references to large fit
  journals. EXP-506's final duplicated summary exposed an output-cap accounting
  defect; its numerical replay passes but its resource protocol does not.
- [ ] Establish the relevant return curve or quotient and its critical geometry
  before assigning target words or continuing a chain arrow. No automatic paid
  review gate applies: major-milestone reviews require human approval per call.
- [ ] Before the next manuscript release, complete the documented
  [legacy turning-point impact audit](experiments/EXP-481-legacy-turning-point-incident.md)
  against preserved historical raw evidence. Its analytic stationary-inflection
  defect is confirmed; impact on earlier Rössler conclusions remains unmeasured.
  The new static inventory identifies 21 source callers and 42 candidate
  manifests, not 42 erroneous results. EXP-186's archived data and original
  source hashes match and provide a concrete first retrospective replay case.
  [EXP-506 now completes that saved-data sensitivity](updates/2026-09-09-exp506-legacy-word-adapter-continuation.md):
  all partitions, bootstrap decisions, critical intervals and words are unchanged
  under the additional turn-geometry filter. This is one checked exposure case,
  not archive-wide clearance or a new validation of the original trajectories.
  Preserve its recorded resource deviation and the prior adapter failure while
  extending the same explicit-scope audit to the remaining candidate studies.
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

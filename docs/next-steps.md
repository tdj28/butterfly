# Research priorities after the public audit

Reviewed 2026-09-04. This is the current execution order; the long
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

Acceptance: a separate environment can acquire the documented inputs, verify
their hashes, recompute the selected results, and regenerate the figures
within declared numerical tolerances. CPU tests already pass without private
inputs; historical result reproduction is a separate requirement.

## 2. Test the symbolic reinjection mechanism

- [ ] Define the two-dimensional first-return map and the precise scalar
  projection or quotient used for critical-point claims. Quantify when a scalar
  coordinate is not a single-valued map; report conditional spread/support.
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

# Butterfly research record

## Purpose

This directory is the living scientific record for a modern, reproducible
re-evaluation of Timothy D. Jones, *Topological origins of a bi-parameter
periodicity hub for the Rössler attractor* (arXiv:1201.4343).

The goal is not to preserve every statement in the 2012 paper. The goal is to
determine, claim by claim, what can be reproduced, what can be strengthened,
what must be narrowed, and what is false or unresolved.

## Documents

- [`../paper/`](../paper/): continuously updated manuscript, authoritative
  BibTeX database, reference ledger, and referee-to-paper traceability checks.
- [`findings/FND-001-apparent-multistability-is-transient-capture.md`](findings/FND-001-apparent-multistability-is-transient-capture.md):
  centralized account of the long chaotic-transient capture finding, its
  implications for Jones and Barrio, and the remaining proof boundary.
- [`findings/FND-002-double-covered-flip-surface.md`](findings/FND-002-double-covered-flip-surface.md):
  decisive reclassification of the apparent `+1` event as a double-covered
  fundamental period-doubling surface and its implications for Jones.
- [`findings/FND-007-shallow-saddle-branch-and-statistical-convergence.md`](findings/FND-007-shallow-saddle-branch-and-statistical-convergence.md):
  retains EXP-110's failed saddle qualification, identifies the shallow added
  branch, and replaces pointwise chaotic identity with statistical convergence.
- [`findings/FND-008-saddle-topology-converges-before-lifetime-density.md`](findings/FND-008-saddle-topology-converges-before-lifetime-density.md):
  records 300/300 stable saddle-topology cells while preserving the failed
  lifetime-density and crossing-time gates.
- [`findings/FND-009-published-chaotic-saddles-qualified.md`](findings/FND-009-published-chaotic-saddles-qualified.md):
  qualifies the published two- and three-branch regular-window saddles across
  Sobol, step, horizon, coordinate, oracle, and DOP853 checks.
- [`findings/FND-010-gpu-saddle-statistical-parity.md`](findings/FND-010-gpu-saddle-statistical-parity.md):
  reproduces those saddle observables on Float64 GPU, records exact CPU/GPU
  discrepancies, cost, hashes, teardown, and the remaining independent-method
  boundary.
- [`findings/FND-011-pim-bimodal-corroboration-and-censor-boundary.md`](findings/FND-011-pim-bimodal-corroboration-and-censor-boundary.md):
  retains independent DOP853/PIM corroboration of the bimodal saddle while
  diagnosing why the complete zero-censor PIM experiment fails.
- [`findings/FND-012-censor-horizon-controls-pim-coverage.md`](findings/FND-012-censor-horizon-controls-pim-coverage.md):
  records independent two-control PIM/DOP853 corroboration at 128 returns while
  preserving the failed 64/128 nested-horizon gate and its support diagnosis.
- [`findings/FND-013-pim-saddle-topology-stable-128-256.md`](findings/FND-013-pim-saddle-topology-stable-128-256.md):
  qualifies independent two-control PIM/DOP853 topology and critical-location
  stability from 128 to 256 returns.
- [`updates/`](updates/): dated progress summaries, evidence, limits, source
  checkpoints, and the next concrete execution item.
- [`TODO.md`](TODO.md): executable, evidence-gated implementation backlog.
- [`claim-ledger.md`](claim-ledger.md): authoritative list of scientific claims,
  their present evidence state, and their acceptance tests.
- [`research-plan.md`](research-plan.md): staged implementation and validation
  roadmap.
- [`world-class-roadmap.md`](world-class-roadmap.md): long-range scientific and
  platform program, including multi-attractor expansion.
- [`ai-research-program.md`](ai-research-program.md): gated topology-aware AI
  program for quotient discovery, active search, symbolic rules, and selective
  certification.
- [`compute/runpod-strategy.md`](compute/runpod-strategy.md): GPU workload,
  provenance, cost-gate, resumability, and teardown design for rented compute.
- [`reviews/2026-08-06-paper-evaluation.md`](reviews/2026-08-06-paper-evaluation.md):
  digest of the external evaluation that initiated this work.
- [`reviews/2026-08-06-jones-barrio-comparison.md`](reviews/2026-08-06-jones-barrio-comparison.md):
  scoped comparison of the shared 2012 result and each paper's distinct
  extensions.
- [`reviews/2026-08-07-jones-peer-review-gap-audit.md`](reviews/2026-08-07-jones-peer-review-gap-audit.md):
  binding traceability matrix from the original referee reports to explicit
  scientific, attribution, figure, and manuscript closure gates.
- [`decisions/DEC-001-independent-codiscovery.md`](decisions/DEC-001-independent-codiscovery.md):
  project wording for the relationship between the Jones and
  Barrio-Blesa-Serrano 2012 results.
- [`decisions/DEC-002-multiple-shooting-high-period.md`](decisions/DEC-002-multiple-shooting-high-period.md):
  evidence-based transition from full-period to segmented shooting after the
  period-320 switch conditioning limit.
- [`decisions/DEC-003-augmented-segmented-flip-solve.md`](decisions/DEC-003-augmented-segmented-flip-solve.md):
  replaces ulp-scale outer scalar refinement with a directly coupled
  anti-periodic tangent/orbit/parameter solve, validated first at period 320.
- [`decisions/DEC-004-return-map-branch-oracle.md`](decisions/DEC-004-return-map-branch-oracle.md):
  defines a coverage-, graph-likeness-, and bootstrap-gated scalar branch
  observable.
- [`decisions/DEC-005-reference-chaotic-saddle-sampler.md`](decisions/DEC-005-reference-chaotic-saddle-sampler.md):
  freezes the CPU survival-ensemble saddle definition and the CPU-to-GPU parity
  gate.
- [`decisions/DEC-006-statistical-saddle-convergence.md`](decisions/DEC-006-statistical-saddle-convergence.md):
  replaces long-horizon point identity with short-horizon numerical and
  long-horizon statistical saddle-convergence gates.
- [`decisions/DEC-007-sobol-hermite-saddle-qualification.md`](decisions/DEC-007-sobol-hermite-saddle-qualification.md):
  removes regular-lattice aliasing and linear section-event error from the
  final CPU saddle-control gate.
- [`experiments/README.md`](experiments/README.md): required structure for every
  computational experiment.
- [`experiments/EXP-000-repository-audit.md`](experiments/EXP-000-repository-audit.md):
  baseline audit of the recovered code.
- [`experiments/EXP-001-reference-core.md`](experiments/EXP-001-reference-core.md):
  tested Rössler equations, equilibria, eigenstructure, and CPU integration path.
- [`experiments/EXP-002-poincare-period-primitives.md`](experiments/EXP-002-poincare-period-primitives.md):
  interpolated section crossings and conservative minimal-period detection.
- [`experiments/EXP-003-tiny-hub-scan.md`](experiments/EXP-003-tiny-hub-scan.md):
  frozen tiny-grid scan and hash-verifiable artifact receipt qualification.
- [`experiments/EXP-004-reference-lyapunov.md`](experiments/EXP-004-reference-lyapunov.md):
  full variational-equation/QR Lyapunov spectrum and convergence boundary.
- [`experiments/EXP-005-published-classifier-controls.md`](experiments/EXP-005-published-classifier-controls.md):
  real chaotic/periodic positive controls from the 2012 PRL.
- [`experiments/EXP-006-resolved-hub-pilot.md`](experiments/EXP-006-resolved-hub-pilot.md):
  first small hub-region atlas with combined recurrence/Lyapunov evidence.
- [`experiments/EXP-007-tiled-resume.md`](experiments/EXP-007-tiled-resume.md):
  immutable tile, verified resume, corruption, and aggregation qualification.
- [`experiments/EXP-008-forced-resume.md`](experiments/EXP-008-forced-resume.md):
  real local worker interruption and verified restart qualification.
- [`experiments/EXP-009-fine-candidate-search.md`](experiments/EXP-009-fine-candidate-search.md):
  tiled `41 x 41` recurrence and near-recurrence candidate discovery run.
- [`experiments/EXP-010-candidate-confirmation.md`](experiments/EXP-010-candidate-confirmation.md):
  frozen candidate confirmation with spectra and two basin probes.
- [`experiments/EXP-011-focused-multistability.md`](experiments/EXP-011-focused-multistability.md):
  tighter multistability replication with independent chaos and Floquet checks.
- [`experiments/EXP-012-transient-capture.md`](experiments/EXP-012-transient-capture.md):
  distinguishes persistent multistability from long transient periodic capture.
- [`experiments/EXP-013-wide-plane-scout.md`](experiments/EXP-013-wide-plane-scout.md):
  completed reconnaissance of the historical high-`a` domain beyond 0.22.
- [`experiments/EXP-014-wide-target-qualification.md`](experiments/EXP-014-wide-target-qualification.md):
  stronger basin and Lyapunov tests for spatially diverse EXP-013 targets.
- [`experiments/EXP-015-high-a-transient-checkpoints.md`](experiments/EXP-015-high-a-transient-checkpoints.md):
  long-transient resolution of apparent high-`a` multistability and capture.
- [`experiments/EXP-016-periodic-coexistence-floquet.md`](experiments/EXP-016-periodic-coexistence-floquet.md):
  closure and Floquet gate for the retained period-12/period-3 coexistence case.
- [`experiments/EXP-017-periodic-coexistence-basin.md`](experiments/EXP-017-periodic-coexistence-basin.md):
  declared initial-condition basin section for the two stable cycles.
- [`experiments/EXP-018-gpu-crossing-parity.md`](experiments/EXP-018-gpu-crossing-parity.md):
  paid Float64 GPU parity gate for Poincare crossings and period labels.
- [`experiments/EXP-019-basin-uncertainty.md`](experiments/EXP-019-basin-uncertainty.md):
  first scale-dependent uncertainty measurement for the period-12/period-3 basins.
- [`experiments/EXP-020-small-scale-basin-uncertainty.md`](experiments/EXP-020-small-scale-basin-uncertainty.md):
  prospective extension of the candidate fractal basin-boundary scaling window.
- [`experiments/EXP-021-multi-b-ac-atlas.md`](experiments/EXP-021-multi-b-ac-atlas.md):
  296,241-point period-atlas sweep and animation across eleven `b` values.
- [`experiments/EXP-022-raster-family-orbits.md`](experiments/EXP-022-raster-family-orbits.md):
  shooting/Floquet confirmation of period-3 and period-5 cross-`b` families.
- [`experiments/EXP-023-periodic-b-continuation.md`](experiments/EXP-023-periodic-b-continuation.md):
  natural continuation and multiplier-crossing brackets for two orbit families.
- [`experiments/EXP-024-floquet-boundary-refinement.md`](experiments/EXP-024-floquet-boundary-refinement.md):
  three refined period-doubling seeds and one honestly rejected scalar solve.
- [`experiments/EXP-025-period5-pseudo-arclength.md`](experiments/EXP-025-period5-pseudo-arclength.md),
  [`EXP-026`](experiments/EXP-026-period5-local-pseudo-arclength.md), and
  [`EXP-027`](experiments/EXP-027-period5-resolved-pseudo-arclength.md):
  three-resolution fold-safe analysis of the period-5 `+1` branch interaction.
- [`experiments/EXP-028-period5-unit-multiplier.md`](experiments/EXP-028-period5-unit-multiplier.md):
  coupled orbit/eigenvector localization of the nontrivial unit-multiplier event.
- [`experiments/EXP-029-period5-branch-switch.md`](experiments/EXP-029-period5-branch-switch.md)
  and [`EXP-030`](experiments/EXP-030-period5-orbit-identity.md): branch switching
  followed by phase-invariant identification of the primary and secondary cycles.
- [`experiments/EXP-031-period5-normal-form-scaling.md`](experiments/EXP-031-period5-normal-form-scaling.md):
  prospective square-root and Floquet scaling test for the local second-iterate
  normal form, subsequently reclassified as a fundamental flip.
- [`experiments/EXP-032-period5-unit-event-a-curve.md`](experiments/EXP-032-period5-unit-event-a-curve.md),
  [`EXP-033`](experiments/EXP-033-expanded-period5-unit-event-a-curve.md), and
  [`EXP-034`](experiments/EXP-034-resolved-period5-unit-event-a-curve.md):
  honest domain/resolution tests and the accepted bounded fixed-`c` event curve.
- [`experiments/EXP-035-event-pseudo-arclength.md`](experiments/EXP-035-event-pseudo-arclength.md):
  full coupled-event pseudo-arclength through the natural-correction boundary,
  revealing folds in both parameter projections.
- [`experiments/EXP-036-period5-unit-event-c-spine.md`](experiments/EXP-036-period5-unit-event-c-spine.md):
  transverse continuation of the event under changes in `c`.
- [`experiments/EXP-037-period5-unit-event-surface-patch.md`](experiments/EXP-037-period5-unit-event-surface-patch.md)
  and [`EXP-038`](experiments/EXP-038-resolved-period5-unit-event-surface-patch.md):
  honest resolution failure followed by the first accepted 45-point local
  event-surface patch.
- [`experiments/EXP-039-separated-normal-form.md`](experiments/EXP-039-separated-normal-form.md):
  separated-point branch identity and prospective normal-form scaling on the
  event surface.
- [`experiments/EXP-040-fold-normal-form.md`](experiments/EXP-040-fold-normal-form.md):
  the same prospective qualification at the event curve's minimum-`b` fold.
- [`experiments/EXP-041-double-cover-audit.md`](experiments/EXP-041-double-cover-audit.md):
  half-period closure, `-1` multiplier, and monodromy-square audit decisively
  reclassifying the surface as a fundamental period-doubling surface.
- [`experiments/EXP-042-period-doubled-offspring-audit.md`](experiments/EXP-042-period-doubled-offspring-audit.md):
  direct off-event confirmation of unstable fundamental parents and stable
  period-doubled children at all three qualified surface points.
- [`experiments/EXP-043-fold-safe-flip-surface-slices.md`](experiments/EXP-043-fold-safe-flip-surface-slices.md),
  [`EXP-044`](experiments/EXP-044-extended-c53-flip-slice.md), and
  [`EXP-045`](experiments/EXP-045-refined-flip-fold-line.md): honest first-gate
  limitation, targeted boundary completion, and a five-point smooth local fold
  line on the period-doubling surface.
- [`experiments/EXP-046-coarse-flip-fold-atlas-overlay.md`](experiments/EXP-046-coarse-flip-fold-atlas-overlay.md)
  and [`EXP-047`](experiments/EXP-047-flip-recurrence-identity.md): failed
  period-5/10 atlas alignment followed by direct reclassification as a
  period-3-to-period-6 flip component.
- [`experiments/EXP-050-identity-constrained-period5-continuation.md`](experiments/EXP-050-identity-constrained-period5-continuation.md):
  clean rebuild of the distinct period-5 branch with recurrence identity
  enforced after every correction.
- [`experiments/EXP-051-refined-true-period5-flip.md`](experiments/EXP-051-refined-true-period5-flip.md)
  through [`EXP-055`](experiments/EXP-055-refined-legacy-section-grazing.md):
  a verified supercritical period-5-to-period-10 flip followed by a distinct
  stable-orbit grazing of the historical section boundary; the sequence is
  summarized in [`FND-003`](findings/FND-003-period5-flip-and-section-grazing.md).
- [`experiments/EXP-079-multiple-shooting-conditioning.md`](experiments/EXP-079-multiple-shooting-conditioning.md):
  32-segment recovery of the high-period flip singularity, establishing the
  numerical basis for the next multiple-shooting corrector.
- [`experiments/EXP-093-scan-period640-predicted-flip.md`](experiments/EXP-093-scan-period640-predicted-flip.md):
  prospective signed-Floquet confirmation of the frozen period-640 flip target
  inside a `1e-8` bracket.
- [`experiments/EXP-097-audit-period640-floquet-precision.md`](experiments/EXP-097-audit-period640-floquet-precision.md):
  solver/representation audit proving block and direct-product agreement while
  identifying integration accuracy as the pointwise event shift.

## Evidence states

Every scientific claim uses one of these states:

1. **Original claim** - stated in the 2012 paper but not yet reproduced here.
2. **Externally supported** - supported by cited literature, with the source
   checked and recorded.
3. **Reproduced** - independently regenerated by code in this repository.
4. **Numerically validated** - reproduced and stable under documented changes
   in solver, precision, tolerance, horizon, initial condition, and resolution.
5. **Rigorously validated** - supported by interval arithmetic,
   computer-assisted proof, or another method with explicit error bounds.
6. **Revised** - a narrower, defensible replacement has been adopted.
7. **Rejected** - evidence contradicts the claim.

"Plausible," "visually clear," and "high resolution" are descriptions, not
evidence states.

## Source-of-truth rules

- The claim ledger is the source of truth for scientific status.
- An experiment record must identify an exact Git commit and configuration.
- Generated datasets and figures must be traceable to an experiment ID.
- Negative and inconclusive results are recorded, not overwritten.
- External-review assertions remain **unverified input** until their primary
  sources have been checked.
- Coordinate-dependent observations must not be called topological invariants.
- Co-discovery language must identify the shared result precisely and must not
  absorb earlier common foundations or paper-specific extensions.
- "Conjugacy" is reserved for a demonstrated conjugacy between precisely
  defined maps and invariant sets. Finite symbolic agreement is reported as
  finite symbolic agreement.

## Naming

- Claims: `CLM-###`
- Findings: `FND-###`
- Experiments: `EXP-###`
- Datasets: `DATA-###`
- Figures: `FIG-###`
- Decisions: `DEC-###`

The identifiers are permanent even if a result is later revised or rejected.

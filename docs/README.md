# Butterfly research record

## Purpose

This directory is the living scientific record for a modern, reproducible
re-evaluation of Timothy D. Jones, *Topological origins of a bi-parameter
periodicity hub for the Rössler attractor* (arXiv:1201.4343).

The goal is not to preserve every statement in the 2012 paper. The goal is to
determine, claim by claim, what can be reproduced, what can be strengthened,
what must be narrowed, and what is false or unresolved.

## Documents

- [`findings/FND-001-apparent-multistability-is-transient-capture.md`](findings/FND-001-apparent-multistability-is-transient-capture.md):
  centralized account of the long chaotic-transient capture finding, its
  implications for Jones and Barrio, and the remaining proof boundary.
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
- [`decisions/DEC-001-independent-codiscovery.md`](decisions/DEC-001-independent-codiscovery.md):
  project wording for the relationship between the Jones and
  Barrio-Blesa-Serrano 2012 results.
- [`findings/FND-001-apparent-multistability-is-transient-capture.md`](findings/FND-001-apparent-multistability-is-transient-capture.md):
  durable interpretation of long chaotic transients versus persistent
  multistability in the Jones-hub and expanded-atlas cases.
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
  prospective square-root and Floquet scaling test for the local pitchfork-like
  normal form.
- [`experiments/EXP-032-period5-unit-event-a-curve.md`](experiments/EXP-032-period5-unit-event-a-curve.md),
  [`EXP-033`](experiments/EXP-033-expanded-period5-unit-event-a-curve.md), and
  [`EXP-034`](experiments/EXP-034-resolved-period5-unit-event-a-curve.md):
  honest domain/resolution tests and the accepted bounded fixed-`c` event curve.

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

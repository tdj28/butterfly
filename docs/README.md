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
- [`findings/FND-014-held-out-saddle-path-and-conditioning-hole.md`](findings/FND-014-held-out-saddle-path-and-conditioning-hole.md):
  qualifies a blind two-branch saddle at `a=0.140`, narrows the finite-sample
  saddle bracket, and retains the unresolved `a=0.145` conditioning hole.
- [`findings/FND-015-a150-chaos-and-resolution-dependent-branch-count.md`](findings/FND-015-a150-chaos-and-resolution-dependent-branch-count.md):
  confirms persistent positive-Lyapunov chaos at `a=0.150` and diagnoses its
  old two-branch label as a coarse-resolution/prominence artifact.
- [`findings/FND-016-a150-three-branch-resolution-qualified.md`](findings/FND-016-a150-three-branch-resolution-qualified.md):
  prospectively qualifies `a=0.150` as chaotic and three-branch at adequate
  resolution while retaining 20 bins as an under-resolution control.
- [`findings/FND-017-a145-support-closed-coordinate-coverage-open.md`](findings/FND-017-a145-support-closed-coordinate-coverage-open.md):
  closes sample scarcity at `a=0.145`, qualifies all `y` cells as two, and
  isolates the remaining `z` failure to fixed-width 80-bin coverage censoring.
- [`findings/FND-018-a145-two-branch-saddle-qualified.md`](findings/FND-018-a145-two-branch-saddle-qualified.md):
  prospectively qualifies the `a=0.145` regular-window saddle as two-branch
  after reproducing both controls, narrowing the sampled bracket to
  `[0.145,0.149]`.
- [`findings/FND-019-blind-a147-saddle-is-two-branch.md`](findings/FND-019-blind-a147-saddle-is-two-branch.md):
  blindly qualifies the midpoint saddle as two-branch across all 14
  run-coordinate decisions, halving the sampled bracket to `[0.147,0.149]`.
- [`findings/FND-020-a148-topology-is-conditioning-sensitive.md`](findings/FND-020-a148-topology-is-conditioning-sensitive.md):
  retains the failed blind `a=0.148` gate and isolates a three-to-two topology
  split between 300- and 360-unit survivor conditioning.
- [`findings/FND-021-a148-long-lived-geometry-is-two-branch-but-power-limited.md`](findings/FND-021-a148-long-lived-geometry-is-two-branch-but-power-limited.md):
  finds two branches in all 228 resolved long-horizon variants through 480
  time units while retaining 12 rare-survivor bootstrap failures and no label.
- [`findings/FND-022-blind-pim-qualifies-a148-two-branch-saddle.md`](findings/FND-022-blind-pim-qualifies-a148-two-branch-saddle.md):
  independently targets the nonattracting saddle and qualifies two branches at
  both 128- and 256-return censor ceilings, narrowing the bracket to
  `[0.148,0.149]`.
- [`findings/FND-023-blind-pim-qualifies-a1485-three-branch-saddle.md`](findings/FND-023-blind-pim-qualifies-a1485-three-branch-saddle.md):
  qualifies the next blind midpoint as three-branch under the identical PIM
  definition, narrowing the finite bracket to `[0.148,0.1485]`.
- [`experiments/EXP-127-a148-branch-conditioned-escape.md`](experiments/EXP-127-a148-branch-conditioned-escape.md):
  prospectively rejects faster capture by the transient extra branch at
  `a=0.148` on untouched ensembles.
- [`findings/FND-024-extra-branch-has-delayed-bounded-capture.md`](findings/FND-024-extra-branch-has-delayed-bounded-capture.md):
  rejects faster mean capture and qualifies a delayed-but-bounded lifetime
  pattern that explains the 300/360-unit conditioning split.
- [`experiments/EXP-128-blind-a14825-censored-pim.md`](experiments/EXP-128-blind-a14825-censored-pim.md):
  qualifies the next blind midpoint as three and narrows the finite bracket to
  `[0.148,0.14825]`.
- [`findings/FND-025-blind-pim-qualifies-a14825-three-branch-saddle.md`](findings/FND-025-blind-pim-qualifies-a14825-three-branch-saddle.md):
  records the second identical-method blind localization and the boundary for
  further classifier bisection versus independent continuation.
- [`decisions/DEC-010-lower-support-slope-observable.md`](decisions/DEC-010-lower-support-slope-observable.md):
  defines the signed companion observable, calibration boundary, and limits on
  any continuity or topology interpretation.
- [`experiments/EXP-129-blind-a148125-pim-boundary-slope.md`](experiments/EXP-129-blind-a148125-pim-boundary-slope.md):
  passes the first held-out slope-sign prediction against a blind two-branch
  PIM midpoint and narrows the bracket to `[0.148125,0.14825]`.
- [`findings/FND-026-signed-boundary-slope-predicts-blind-midpoint.md`](findings/FND-026-signed-boundary-slope-predicts-blind-midpoint.md):
  records the qualified signed companion observable, its direct connection to
  Jones's edge/critical-point statement, and the next manifold-event gate.
- [`experiments/EXP-148-blind-a1481875-censored-pim.md`](experiments/EXP-148-blind-a1481875-censored-pim.md):
  passes the next untouched midpoint as two-branch at both censor horizons and
  narrows the finite bracket to `[0.1481875,0.14825]` before the separately
  frozen lobe-association test is evaluated.
- [`findings/FND-036-phase-resolved-capture-contrast-is-not-robust.md`](findings/FND-036-phase-resolved-capture-contrast-is-not-robust.md):
  rejects the EXP-143 finite-horizon capture contrast under denser seeds,
  three orbit phases, and two horizons while preserving the validated UPO
  skeleton and selecting a direct geometric connection residual.
- [`findings/FND-037-left-lobe-enters-three-branch-pim-saddle.md`](findings/FND-037-left-lobe-enters-three-branch-pim-saddle.md):
  shows retrospectively that a pre-existing UPO unstable lobe is excluded from
  the two-branch PIM saddle but included in the three-branch saddle under
  nested two-dimensional distance controls.
- [`findings/FND-038-one-transverse-bracket-passes-second-remains-open.md`](findings/FND-038-one-transverse-bracket-passes-second-remains-open.md):
  records the mixed EXP-132 result: a qualified finite bracket at `c=19.9`, a
  new three-branch endpoint at `c=19.8,a=0.150`, and the still-unresolved
  bootstrap-sensitive lower endpoint at `c=19.8,a=0.148`.
- [`findings/FND-045-second-cascade-rung-qualified.md`](findings/FND-045-second-cascade-rung-qualified.md):
  carries the primitive period-2 child to its exact next flip and independently
  qualifies the resulting stable primitive period-4 child on the fixed Jones
  path.
- [`findings/FND-046-third-cascade-rung-qualified.md`](findings/FND-046-third-cascade-rung-qualified.md):
  resolves the exact period-4-to-8 flip and independently qualifies a stable
  primitive period-8 child, completing the third fixed-path cascade rung.
- [`findings/FND-047-fourth-cascade-rung-qualified.md`](findings/FND-047-fourth-cascade-rung-qualified.md):
  repairs the equal-modulus block-root audit, resolves the exact period-8-to-16
  flip, and independently qualifies the stable primitive period-16 child.
- [`findings/FND-048-eight-figure6-landmarks-periodic-two-unresolved.md`](findings/FND-048-eight-figure6-landmarks-periodic-two-unresolved.md):
  records the blind exact-coordinate Figure 6 audit: eight solver-qualified
  periodic landmarks, two unresolved coordinates, and one delayed-capture
  failure retained by the strict transient gate.
- [`findings/FND-049-x-partition-passes-z-crosscheck-is-underpowered.md`](findings/FND-049-x-partition-passes-z-crosscheck-is-underpowered.md):
  qualifies the neutral split-cloud `x` partition while retaining the strict
  held-out `z` failure caused by one bootstrap-unstable 50-bin variant.
- [`findings/FND-050-neutral-three-branch-jones-partition-qualified.md`](findings/FND-050-neutral-three-branch-jones-partition-qualified.md):
  qualifies the neutral three-branch Jones-section partition across all seven
  calibration/validation variants independently in `x` and `z`.
- [`findings/FND-051-neutral-two-branch-jones-partition-qualified.md`](findings/FND-051-neutral-two-branch-jones-partition-qualified.md):
  qualifies the matching neutral two-branch control on the same historical
  representation; FND-056 later closes its local critical-identity gate.
- [`findings/FND-052-jones-critical-identity-direction-supported-bracket-open.md`](findings/FND-052-jones-critical-identity-direction-supported-bracket-open.md):
  finds the same unique likely trimodal descendant in `x` and `z` while
  retaining EXP-178's strict resolved-bracket-width failure.
- [`findings/FND-053-global-branch-vote-ill-conditioned-at-critical-birth.md`](findings/FND-053-global-branch-vote-ill-conditioned-at-critical-birth.md):
  shows that doubled support leaves a coordinate-staggered branch-count
  disagreement band, motivating separate local tracking of the old critical.
- [`findings/FND-054-local-critical-persists-except-support-hole.md`](findings/FND-054-local-critical-persists-except-support-hole.md):
  tracks the same local feature around the transition in two solvers and both
  coordinates, retaining one banded-support hole at `a=0.156`.
- [`findings/FND-055-gap-survivors-hit-prediction-but-capture-parity-fails.md`](findings/FND-055-gap-survivors-hit-prediction-but-capture-parity-fails.md):
  fills the gap geometrically with 64,571 survivor pairs per coordinate but
  preserves a failed long-time fixed-step/DOP853 capture-label audit.
- [`findings/FND-056-local-jones-critical-identity-qualified.md`](findings/FND-056-local-jones-critical-identity-qualified.md):
  closes the sole support gap under two RK4 steps and short-horizon DOP853,
  qualifying the unimodal critical as the higher trimodal critical locally.
- [`findings/FND-057-jones-operational-alphabet-qualified.md`](findings/FND-057-jones-operational-alphabet-qualified.md):
  qualifies the source-derived `C,D,0,1,2` mapping across two solvers, both
  coordinates, held-out segments, and physical deposition geometry.
- [`findings/FND-058-exact-figure6-landmark-is-not-a-word-center.md`](findings/FND-058-exact-figure6-landmark-is-not-a-word-center.md):
  preserves a strong period-6 orbit qualification while rejecting the exact
  printed gray-box coordinate as a reproducible Figure 6 word center.
- [`findings/FND-059-floquet-center-search-needs-finer-continuation.md`](findings/FND-059-floquet-center-search-needs-finer-continuation.md):
  preserves the failed coarse identity gate and brackets sub-cell signed-
  multiplier zeros without claiming that a center was found.
- [`findings/FND-060-floquet-zero-surface-does-not-uniquely-locate-center.md`](findings/FND-060-floquet-zero-surface-does-not-uniquely-locate-center.md):
  rejects the refinement-unstable Floquet-only center proxy and selects direct
  two-critical orbit residuals as the next non-circular locator.
- [`findings/FND-061-all-period6-zero-edge-candidates-qualified.md`](findings/FND-061-all-period6-zero-edge-candidates-qualified.md):
  qualifies stable period-6 corrections on all 65 zero edges, preserving the
  complete word-blind input set for GPU critical-residual discovery.
- [`findings/FND-062-period6-floquet-zero-neighborhood-is-unimodal.md`](findings/FND-062-period6-floquet-zero-neighborhood-is-unimodal.md):
  rejects that complete neighborhood as a two-critical center location while
  preserving the global double-superstability question.
- [`findings/FND-063-second-jones-period6-landmark-lies-in-coherent-band.md`](findings/FND-063-second-jones-period6-landmark-lies-in-coherent-band.md):
  places the other exact period-6 landmark inside a coherent 981-pixel band
  whose vertical extent remains truncated and whose orbit identity is open.
- [`findings/FND-064-two-jones-period6-landmarks-occupy-distinct-stable-raster-components.md`](findings/FND-064-two-jones-period6-landmarks-occupy-distinct-stable-raster-components.md):
  reproduces both landmarks as period 6 but places them in distinct resolved
  stable raster components, without excluding unstable continuation.
- [`findings/FND-065-period6-flow-orbits-have-eight-barrio-section-phases.md`](findings/FND-065-period6-flow-orbits-have-eight-barrio-section-phases.md):
  shows across 58 corrected stable orbits that historical period 6 becomes an
  eight-phase cycle on Barrio's published positive-x section.
- [`findings/FND-066-gpu-barrio-section-parity-is-exact.md`](findings/FND-066-gpu-barrio-section-parity-is-exact.md):
  exactly matches CPU/GPU survivor and return-pair counts at two steps and
  qualifies the three-branch Barrio z-map CUDA path.
- [`findings/FND-067-no-sampled-barrio-double-critical-center.md`](findings/FND-067-no-sampled-barrio-double-critical-center.md):
  rejects direct double-critical membership at all 58 sampled corrected
  orbits while localizing the closest residual near `(a,c)=(0.21555,7.372)`.
- [`findings/FND-068-local-orbit-mesh-is-coverage-limited.md`](findings/FND-068-local-orbit-mesh-is-coverage-limited.md):
  records that the dense successor reproduces its center and qualifies 685
  orbits but fails the frozen coverage gate and touches a mesh boundary.
- [`findings/FND-069-no-simultaneous-critical-residual-bracket-in-the-incomplete-dense-field.md`](findings/FND-069-no-simultaneous-critical-residual-bracket-in-the-incomplete-dense-field.md):
  shows that one critical residual crosses zero but the other remains positive
  throughout all 126 cross-step-qualified points, so neither a direct center
  nor a simultaneous bracket exists in the incomplete sampled field.
- [`findings/FND-070-lower-c-critical-is-smoothing-sensitive-not-sample-starved.md`](findings/FND-070-lower-c-critical-is-smoothing-sensitive-not-sample-starved.md):
  shows that quadrupled trajectory support preserves three branches under four
  baseline variants while one high-smoothing variant removes the shallow
  critical, rejecting sample scarcity but not qualifying a topology loss.
- [`findings/FND-071-lower-c-critical-has-a-qualified-finite-data-scale.md`](findings/FND-071-lower-c-critical-has-a-qualified-finite-data-scale.md):
  qualifies the shallow critical's smoothing-transition scale at 94/104 points
  across two RK4 steps and nested 2,048/8,192 trajectory supports, while keeping
  invariant topology and double superstability open.
- [`findings/FND-072-second-critical-residual-remains-positive-across-the-scale-ensemble.md`](findings/FND-072-second-critical-residual-remains-positive-across-the-scale-ensemble.md):
  preserves all 94 scale-qualified candidates but finds the second signed
  residual positive in every low-smoothing/support/step reconstruction,
  rejecting the sampled stable field rather than global double superstability.
- [`findings/FND-073-lower-c-extension-finds-a-bounded-stable-period6-strip.md`](findings/FND-073-lower-c-extension-finds-a-bounded-stable-period6-strip.md):
  records a 551-orbit lower-c stable strip, its correction/stability boundaries,
  and the failed coverage gate that blocks unconstrained residual extrapolation.
- [`findings/FND-074-lower-c-stable-strip-has-a-real-flip-boundary.md`](findings/FND-074-lower-c-stable-strip-has-a-real-flip-boundary.md):
  qualifies seven real-minus-one Floquet events on the stable strip edge and
  promotes them to period-doubling curve and child-branch continuation seeds.
- [`findings/FND-075-period6-flip-edge-continues-as-a-dense-coupled-curve.md`](findings/FND-075-period6-flip-edge-continues-as-a-dense-coupled-curve.md):
  continues the flip event with an exact augmented Jacobian through all 41
  frozen points, replacing the raster edge with a dense bifurcation curve.
- [`findings/FND-076-three-period12-children-qualified.md`](findings/FND-076-three-period12-children-qualified.md):
  independently qualifies primitive stable period-12 children paired with
  unstable period-6 parents at three separated post-flip samples.
- [`findings/FND-077-period6-to12-opening-is-locally-supercritical-at-three-slices.md`](findings/FND-077-period6-to12-opening-is-locally-supercritical-at-three-slices.md):
  replicates square-root opening, flip-multiplier scaling, cross-solver parity,
  and perturbed attraction at three fixed-`c` period-6-to-12 slices.
- [`findings/FND-078-unconstrained-period12-surface-shooting-loses-child-identity.md`](findings/FND-078-unconstrained-period12-surface-shooting-loses-child-identity.md):
  records 16 doubled-parent collapses in a complete 124-cell surface attempt
  and requires explicit nonclosing-child root selection in its successor.
- [`findings/FND-079-period12-child-sheet-qualified-over-dense-flip-patch.md`](findings/FND-079-period12-child-sheet-qualified-over-dense-flip-patch.md):
  qualifies all 124 identity-selected primitive period-12 children, 31
  square-root opening fits, adjacency coherence, and six Radau controls.
- [`experiments/EXP-212-period6-flip-pseudoarclength-extension.md`](experiments/EXP-212-period6-flip-pseudoarclength-extension.md):
  freezes exact dual-parameter pseudo-arclength extension of the parent flip
  curve beyond the qualified child-sheet rectangle.
- [`findings/FND-080-period6-flip-curve-crosses-a-historical-section-boundary.md`](findings/FND-080-period6-flip-curve-crosses-a-historical-section-boundary.md):
  records the complete upper extension and the lower six-to-seven historical
  phase change that nominates a section grazing rather than an orbit endpoint.
- [`findings/FND-081-standard-section-counter-loses-coalescing-crossings.md`](findings/FND-081-standard-section-counter-loses-coalescing-crossings.md):
  preserves EXP-213's failed final count gate despite cross-solver convergence
  of the continuous tangency and motivates extremum-partitioned counting.
- [`findings/FND-082-flip-curve-grazing-is-a-qualified-representation-boundary.md`](findings/FND-082-flip-curve-grazing-is-a-qualified-representation-boundary.md):
  qualifies the seven-to-six historical phase change while Barrio remains
  eight and the exact real-minus-one flow event persists.
- [`experiments/EXP-215-period6-flip-through-grazing.md`](experiments/EXP-215-period6-flip-through-grazing.md):
  records six exact invariant events below the qualified historical-section
  representation boundary and the subsequent fixed-step corrector failure.
- [`findings/FND-083-flip-curve-crosses-qualified-section-grazing.md`](findings/FND-083-flip-curve-crosses-qualified-section-grazing.md):
  qualifies local passage of the real-minus-one flow event through the
  section grazing with terminal Radau control.
- [`experiments/EXP-216-period6-flip-adaptive-below-grazing.md`](experiments/EXP-216-period6-flip-adaptive-below-grazing.md):
  freezes step-halving continuation of the same invariant flip locus toward
  `c=6.05` after EXP-215's fixed-step failure.
- [`findings/FND-084-period6-flip-locus-has-a-lower-c-projection-turn.md`](findings/FND-084-period6-flip-locus-has-a-lower-c-projection-turn.md):
  qualifies the exact locus's sampled lower-`c` turn and returning arm with
  independent terminal recorrection.
- [`experiments/EXP-217-period6-flip-returning-arm.md`](experiments/EXP-217-period6-flip-returning-arm.md):
  freezes broad continuation of the returning arm toward `c=8.25`.
- [`findings/FND-085-period6-flip-locus-has-two-broad-separated-arms.md`](findings/FND-085-period6-flip-locus-has-two-broad-separated-arms.md):
  qualifies 135 returning-arm events and the widening separation from the
  original period-6 flip arm.
- [`experiments/EXP-218-returning-period12-children.md`](experiments/EXP-218-returning-period12-children.md):
  freezes a held-out directional period-12 stability-exchange test on the
  returning arm.
- [`experiments/EXP-219-returning-period12-children-one-sided.md`](experiments/EXP-219-returning-period12-children-one-sided.md):
  preserves that prediction after replacing an administratively fragile
  symmetric parent-tangent estimate.
- [`experiments/EXP-220-returning-period12-children-multiscale.md`](experiments/EXP-220-returning-period12-children-multiscale.md):
  freezes exact event recorrection and a declared four-scale child-switch
  recovery after EXP-219's zero-candidate result.
- [`findings/FND-086-returning-arm-has-local-opposing-side-stability-exchange.md`](findings/FND-086-returning-arm-has-local-opposing-side-stability-exchange.md):
  qualifies four primitive stable lower-`a` children at one untouched
  returning-arm event while preserving the unresolved remote switches.
- [`experiments/EXP-221-returning-period12-child-continuation.md`](experiments/EXP-221-returning-period12-child-continuation.md):
  freezes identity-safe continuation of one qualified child through 52
  returning-arm events toward the unresolved middle slice.
- [`experiments/EXP-222-returning-period12-child-first-bridge.md`](experiments/EXP-222-returning-period12-child-first-bridge.md):
  freezes a 16-substep bridge across EXP-221's first primitive-root jump.
- [`source-audits/2026-08-07-jones-path-and-symbol-transcription.md`](source-audits/2026-08-07-jones-path-and-symbol-transcription.md):
  resolves what Figures 2 and 6 actually specify, records the historical path
  ambiguity, and binds the finite symbol/transition target to machine-readable
  data and a structural audit.
- [`decisions/DEC-014-independent-symbol-partition-before-word-matching.md`](decisions/DEC-014-independent-symbol-partition-before-word-matching.md):
  prevents circular word recovery by requiring dense-cloud critical intervals
  before an independently corrected target cycle is assigned a symbol word.
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

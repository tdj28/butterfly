# Research updates

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

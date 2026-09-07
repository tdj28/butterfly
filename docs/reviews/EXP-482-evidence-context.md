# EXP-482 cumulative evidence context

Summaries below were validated locally; the reviewer has not audited raw data.
No EXP-482 target trajectories exist. The prior review and structured disposition
are reproduced in full below; their execution authorization belonged only to EXP-481.

## N01: observed numerical failure motivating a new study

EXP-481 qualification completed all 128 trials/192 comparisons: 92 passed,
100 failed the fixed scaled event-state bound 1e-4; downstream collection and
analysis never ran. Both nominated cases had 50 failed comparisons. At .01/.005,
maximum RK4 vs DOP853 errors were .005996315/.000389655. DOP853 vs Radau passed
32/32, max 3.199006e-8. Counts, acceptance/capture membership and timing agreed.
Median sectionwise coarse/fine state-error ratio was 15.634, consistent with
fourth-order convergence, not a bound. Exact raw replay reproduced every row.
Preserved phase terminal SHA 51e4cf10dc4c3c2a4706a321fec6314251e9ca59ff2e234c275ed32452ecf2d9.
The consumed EXP-481 attempt is not reopened. Finer Rössler accuracy is unobserved.

## N02: full workload and disclosed resource redesign

Prospectively fixed synthetic workloads generated no Rössler trajectories.
The full t=300 circle uses batch512, actual recorder/replay, six/eight distant
reference rows, and discarded Rössler RHS arithmetic at every circle field call.
Both .0025/.00125 controls passed exact counts (146 raw/73 accepted per seed per
section), no failure/ambiguity/capture, analytic final-state/time error <1e-5.
Measured collection28.643/57.127s; replay .965/1.809s. Actual both-case8192-seed,
200-bootstrap analysis63.423s recovered3branches and the complete six-row near/far
matrix; matched two-sheet primary rejected. No shortened bootstrap extrapolation.
The original .25s-polling conservative gate FAILED: doubled full-tree scan overhead
projected collection50609s >14400. Preserve this failure; worker exit2, cleanup verified.
One-second polling is a post-observation design calculation, not a measured pass.
Same measured-data formula, unchanged headroom and caps: qualification217.093s,
collection7063.630s, analysis/replay304.343s, disk1676665584bytes, RSS644284416bytes.
Collection base=2*32*(28.643151792+57.126544208); projected full scan .111441951s
from slowest of3 local881-file scans scaled to23232files. Charge twice that full
scan at EVERY poll: base/(1-2*scan/poll). Not a hard runtime/retention guarantee;
unknown event frequency/geometry, growing inventories and OS load remain risks.
Less frequent RSS/disk sampling increases possible overshoot latency, while
integration/journals, pre-import deadline/parent guard and write caps are unchanged.
Original workload receipt SHA b8ae5599f85409ee6cd07ae9a3e20fa2083c0a1adbe1fd763dfc873434d78e3d.

## Source-qualified implementation

At ba85d90ba23ec44d4c6f66639d337812374719cf the authentic production source
preflight passed426bound tests/no skips, both raw-reference audits, and all
128qualification/64collection configurations. Includes actual ordinary-controller
three-phase analytic positive/negative grants, both experiment identities,
real Git/provider-packet tampering tests, cubic/two-sheet/inflection/failed-bootstrap
controls. The372-file closure includes both numeric designs and all paired source/tests.
Preflight receipt SHA968f90180975357fea511f382a7bf01cf533dd0d7840f3caf0cadab0e0aad74c.
No target slot consumed. A new reviewed release and fresh reviewed setup are still
required; saved preflight JSON does not authorize a worker. Selecting EXP-482
cannot reuse EXP-481 review or slot; arbitrary experiment IDs are rejected.

## Preserved complete EXP-481 review

# Verdict

The question is worthwhile and appropriately narrower than validating a symbolic partition. This design can assess **operational, finite-resolution adequacy of historical \(x\)** in two nominated cases, followed conditionally by descriptive cycle-event proximity. It cannot establish a globally single-valued return map or validate symbolic dynamics.

The strongest features are the whole-seed holdout, explicit survivor conditioning, fixed cross-window/profile agreement requirements, and prohibition on coordinate rescue. These substantially reduce opportunities for favorable reinterpretation.

Two pre-execution evidence gaps remain: credible completion estimates and qualification of the complete positive turning-region decision path. Neither requires another large experiment. This is a compact review packet; the disclosed local test results are useful evidence, but I have not independently inspected their sources or receipts.

READY AFTER SPECIFIED FIXES

# Blocking findings

## B01 — Resource caps do not establish a feasible completed experiment

- **Severity:** Blocking — missing feasibility evidence, not a demonstrated resource failure.
- **Plan section:** Resources; “CPU wall bounds are not demonstrated completion-time estimates.”
- **Why it matters:** The planned collection entails approximately **1.47 billion seed-level RK4 steps**, or 5.90 billion seed-level right-hand-side evaluations, before qualification and analysis. Batching may make this practical, but the four-hour cap and two-hour analysis bound are not completion estimates. With campaign-wide stopping and no retry, an avoidable cap hit produces an invalid campaign rather than an interpretable scientific result.
- **Concrete minimum fix:** Before target execution, provide a compact benchmark-based estimate for collection, analysis, storage, and peak memory using the actual execution paths. Use a short bounded throughput benchmark and representative synthetic analysis workloads; no new target trajectory pilot is necessary. Include checkpointing, journal writes, bootstrap work, and safety headroom. Confirm that phase deadlines fit the overall deadline. If they do not, revise resources or the fixed sample before outcomes exist—not during the campaign.
- **Claim affected:** The ability to deliver any completed, interpretable result within the declared campaign.

## B02 — The disclosed controls do not yet qualify the complete positive turning-region path

- **Severity:** Blocking — missing qualification evidence.
- **Plan section:** Local qualification evidence; analytic-circle controller run; cubic, multivalued, and stationary-inflection tests.
- **Why it matters:** The end-to-end circle run establishes a valuable **zero-turn identity-map path**. The disclosed cubic tests may establish the remaining behavior, but their scope is unspecified. The main scientific conclusion additionally depends on recovering nonzero turning regions, matching their order across variants, handling bootstrap failures, and applying the distance/slope membership rule correctly. Passing local extrema tests alone would not qualify that combined path.
- **Concrete minimum fix:** Attest whether existing tests already exercise that full path. If not, add one bounded, schema-faithful synthetic fixture with known prominent turns and known near/far reference events, processed by the same analysis and reporting code. Use the declared clustered sampling structure and representative support. Require the expected branch count and event classifications across the prescribed variants. Add a matched clearly multivalued or unresolved-support fixture that must not receive positive support. Freeze these expected outcomes before running the controls. Supply only a compact pass/fail summary.
- **Claim affected:** Interpretability of both positive turning-region proximity and failures to find stable turns.

# Important non-blocking findings

## I01 — “Independently estimated” needs a reference-conditioning qualification

- **Severity:** Important — claim-boundary clarification.
- **Plan section:** Claim; capture reference; “near independently estimated turning regions.”
- **Why it matters:** The map uses fresh trajectories rather than the cycle events as fitting observations, which is a genuine strength. However, cohort eligibility depends on capture relative to that same nominated cycle, and also on the other section. Thus the fitted map describes a **reference-conditioned survivor population**, not a population selected independently of the reference. The q90 and support rules further delimit what “adequate” means.
- **Concrete minimum fix:** Describe turning regions as “estimated from separate fresh trajectories in the reference-conditioned retained cohort.” In every positive summary, state the accepted-error quantile, unsupported fraction, and covered domain. Do not interpret the result as ruling out rare sheets or extrapolate through support gaps. No new sampling arm is needed for the stated conditional claim.
- **Claim affected:** Independence and population scope of the positive conclusion.

## I02 — The historical inflection bug needs a dependency disposition, not an unrestricted audit

- **Severity:** Important — unresolved provenance dependency.
- **Plan section:** “The old helper mislabels stationary inflections”; “Historical impact audit remains open.”
- **Why it matters:** The new analyzer’s rejection of this counterexample is reassuring. An error in historical symbolic interpretation need not invalidate this prospective study. An error affecting the identity, ordering, or numerical qualification of the actual reference events would.
- **Concrete minimum fix:** Produce a short dependency disposition: did the old helper affect only interpretation or nomination, or did it affect supplied reference states, event ordering, capture definitions, or current thresholds? Interpretation-only effects can remain a separately tracked historical issue. Effects on executable inputs must be corrected and requalified before freeze. Retain the nominated cases rather than silently replacing unfavorable ones.
- **Claim affected:** Provenance of the nominated cycles and correctness of cycle-event proximity comparisons.

## I03 — Gate failure needs a prespecified scientific interpretation

- **Severity:** Important — reporting and estimand clarification.
- **Plan section:** Joint primary gate; support floors; “complete unresolved results remain reportable.”
- **Why it matters:** A completed campaign can fail because of inadequate support, unstable inferred turns, excessive supported-row prediction error, or a stable map with no nearby cycle event. These are different conclusions. The disclosed minimum seed counts and bootstrap envelopes do not make all such failures evidence against the historical projection.
- **Concrete minimum fix:** Freeze a short outcome table separating:
  1. technical invalidity;
  2. insufficient information/support;
  3. observed failure of the operational adequacy or stability criteria;
  4. adequate map but no stable prominent turns or no qualifying cycle-event proximity;
  5. joint support for the bounded positive claim.

  Report the failed components rather than only a composite pass/fail. Keep all event-region classifications descriptive; make no familywise-confidence claim.
- **Claim affected:** Interpretation of null, mixed, and unresolved outcomes.

# What should remain unchanged

- **The narrow scientific boundary.** No claims about invariance, exact criticality, homoclinic existence, symbolic letters/arrows, or parameter-plane topology.
- **Whole-seed splitting and resampling.** Seeds—not pairs, windows, variants, or nearby parameter cases—are the independent sampling units for within-case uncertainty.
- **Equal seed contributions and true consecutive pairs.** No bridging unresolved events, duplication, interpolation, or refill.
- **Calibration-only fitting, normalization, and affine baseline.** Keep identical supported holdout rows for comparison. An affine map can be an adequate scalar map; failure to beat it is not automatically a failure of scalar adequacy.
- **The fixed conjunction across cases, windows, profiles, and variants.** Do not pool cases or choose the best setting after inspection.
- **All six historical cycle events and no phase picking.**
- **Diagnostic coordinates cannot rescue historical \(x\).**
- **The distinction between early numerical qualification and long-time convergence.** Short adaptive checks do not establish long-time shadowing or complete root detection.
- **Existing analytic controls, retained failed bootstrap replicates, and honest operational-cap semantics.**

# Minimal revised design

1. **Keep the proposed scientific sample and primary analysis.** Do not add cases, coordinate searches, or a new experimental arm.

2. **Complete the two small pre-execution gates.**
   - Establish completion headroom using bounded execution-path benchmarks (**B01**).
   - Establish end-to-end recovery and rejection behavior for turning-region decisions, reusing existing tests where sufficient (**B02**).

3. **Freeze the exact claim language.** The primary result is finite-resolution historical-\(x\) adequacy on supported observations from the explicitly reference-conditioned, retained finite-time cohort. Turning-region proximity is a conditional second-stage description, not independent validation of the cycle or a partition (**I01**).

4. **Close only the relevant historical dependency.** Verify the reference events and capture inputs are unaffected by the old inflection error, or requalify those inputs. Do not make completion of an unrelated historical reinterpretation project a prerequisite (**I02**).

5. **Freeze the outcome table and compact reporting template** (**I03**). Report, separately for each case:
   - original and retained seed counts, split sizes, and exclusion reasons;
   - profile-retention disagreement;
   - support and unsupported fractions;
   - spline and affine holdout q90 errors on identical rows;
   - branch counts, bootstrap consensus, and cross-map turning-region spans;
   - the event-region distance/slope matrix only when its enabling gate passes.

The sample floors should remain labeled information floors, not power guarantees. Synthetic controls can establish that the procedure can recognize specified alternatives; they cannot promise sufficient target retention or target precision.

# Freeze checklist

- [ ] **B01:** Compact runtime/storage/memory estimate demonstrates headroom within consistent phase and campaign deadlines.
- [ ] **B02:** Full positive-turn and adverse-control paths pass prespecified expectations; source-bound coverage is summarized, not dumped.
- [ ] **I01:** Positive-claim wording includes reference conditioning, finite-time retention, quantile tolerance, and support limitations.
- [ ] **I02:** Historical-helper dependency is explicitly disposed of; any affected executable inputs are requalified.
- [ ] **I03:** Positive, adverse, mixed, unresolved, and invalid outcomes have fixed reporting rules.
- [ ] **Local source/schema verification:** Confirm the exact section equations, crossing directions, acceptance gates, capture-sequence rule, spline objective, support construction, turn matching, quantile convention, and normalization of cross-map distances.
- [ ] **Local leakage verification:** Eligibility uses only the prespecified collection rules; holdout responses cannot alter fitting, support definitions, variants, thresholds, or reference-event selection.
- [ ] **Local execution verification:** Confirm hash-bound inputs, seed/split identity, deadline guards, incomplete-campaign handling, and a reproducible environment receipt.
- [ ] No target outcomes have informed these revisions; any change to sample size, thresholds, controls, or resource limits is recorded before target execution.

## Preserved complete structured EXP-481 adjudication

```json
{"approved_for_execution":true,"changes":[{"after":{"bytes":11909,"sha256":"25534382c79c1b612a4f0e088fa21124eead187217010f6c9eb9201fe6ca1756"},"before":{"bytes":11306,"sha256":"44d8d624d02ff40ee9c1a9bc8ce06d202335994863e24981d64b05fde8df2ae8"},"findings":["I01"],"path":"python/butterfly/paired_campaign.py"},{"after":{"bytes":14311,"sha256":"6b9f84a9cd4b6c5b1df074f41dab2953d470e7f70242f91495e0aebfc70b361f"},"before":{"bytes":6356,"sha256":"68cb44b072a6a131c953b51f19a59c17806ab8e6dcdb3a276003ec56bcfec672"},"findings":["B01","B02"],"path":"scripts/qualify_paired_phases.py"},{"after":{"bytes":9116,"sha256":"84cefc0adbc74a365b08ce43b490b505720875e6063e827bdd786b8479574808"},"before":{"bytes":7866,"sha256":"3c716d445c038a1e7adcea85afdcb0c954d52472cc3db8cf3da9fd79dbb956ec"},"findings":["B01","B02","I01"],"path":"tests/test_paired_campaign.py"},{"after":{"bytes":4923,"sha256":"c5f0efe86cdc52d3a6d440213aaaf70c081b135a691c66874c79a4ecd6320b7f"},"before":{"bytes":4066,"sha256":"ea8f3e99a094187b952d6dcb38e13cad3425930ddf8eaf6ef6ebe4d2b2a0db5b"},"findings":["B02"],"path":"tests/test_seed_return_map.py"}],"code_freeze_commit":"68585e2bf853fcd2778b6efdf4b2e652bb6749db","experiment_id":"EXP-481","explanation":{"bytes":10585,"path":"docs/reviews/EXP-481-adjudication.md","sha256":"341d594526d3f60bdf653207196383b20e64d1de499b03b8809af8eb3813c3aa"},"final_inventory_sha256":"97b4867426f502d9b6efb4fc573f1616bd25c04b3a87cc01bba2fa9b8e5de7ff","findings":[{"authorizes_change":true,"decision":"accept","id":"B01","rationale":"Caps alone did not demonstrate feasible completion.","resolution":"Frozen guarded synthetic journal/replay, all-profile qualification and full-population analysis benchmark passes all doubled resource estimates; no target limits or sampling changed."},{"authorizes_change":true,"decision":"accepted_modified","id":"B02","rationale":"Existing campaign cubic tests already covered the combined path, but disclosure and adverse coverage needed strengthening.","resolution":"Full all-six-row matrix asserted; two-sheet campaign rejects positive support; failed bootstrap draws stay in denominator. 86 focused tests and full-population synthetic benchmark pass."},{"authorizes_change":true,"decision":"accept","id":"I01","rationale":"Fresh trajectories are separate fitting observations but capture-conditioned on the reference cycle.","resolution":"Machine result explicitly states reference-conditioned retained finite-time scope and reports q90, unsupported and coverage thresholds alongside all observed per-variant metrics; no rare-sheet or support-gap inference."},{"authorizes_change":false,"decision":"accept","id":"I02","rationale":"The known defect can affect nomination or interpretation, not the current raw event-construction path.","resolution":"EXP480 producer source matches its frozen execution version; variational correction and geometric raw roots do not call the old helper. Both raw six/eight-event audits pass again. Keep both conditional nominations; broader historical impact remains separately open."},{"authorizes_change":false,"decision":"accept","id":"I03","rationale":"Different failure mechanisms require different scientific interpretations.","resolution":"The bound adjudication document freezes a casewise five-category outcome table and full reporting template. Existing complete result preserves component reasons and all metrics; no new gate or outcome-selected threshold."}],"qualification":{"bytes":3530,"path":"docs/experiments/receipts/EXP-481-review-fixes.json","sha256":"4e2ba5aa6475cc7f3f14906c772c53c5d8acb0d75f4da51a33bac3df317e946b"},"review_sha256":"28ee5ad3cb9784693139b2b335b3a534b934afed353858e9d077828f8d19c6f9","reviewed_inventory_sha256":"3fe22cbe673dab7bf07ee2f49b3950101aaf879cab23832dd7360ccd471299e6","reviewed_packet_commit":"c8f4bc322f4e81aa94821bd1c2bc0435cc403542","schema":"butterfly.paired-review-adjudication.v1","self_sha256":"c2121c4338fa4ed9faa23ceec391a30fb8b8022a74f37e727cee3e3bbff66d40","verdict":"READY AFTER SPECIFIED FIXES"}
```

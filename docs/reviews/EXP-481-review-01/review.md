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

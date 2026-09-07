# Verdict

This is a useful **bounded numerical qualification step**, provided its result determines whether to proceed to a separately frozen historical-section sampling study. It will not independently test Jones’s chains, discover the already-known return counts, or establish that either nomination admits a valid scalar partition.

The design is unusually disciplined about exploratory selection, common-trajectory comparisons, failure retention, and preventing premature symbolic interpretation. Two repairs are needed before execution: make half-plane acceptance robust to numerical uncertainty, and establish that the numerical gates are meaningful at the declared scales. Neither requires additional target nominations or a large control campaign.

This review assesses the supplied compact design and disclosed verification summaries. It does not independently verify omitted source, manifests, tests, or historical raw evidence. Execution remains unauthorized pending adjudication and rebinding.

READY AFTER SPECIFIED FIXES

# Blocking findings

## B01 — Half-plane membership is not protected against numerical ambiguity

- **Severity:** Blocking; definite design omission.
- **Plan section / excerpt:** Artifact 3: “no explicit half-plane-edge margin.” The historical section accepts downward crossings of `y=y_small` only when `x<x_small`.
- **Why it matters:** Transversality to the plane does not establish robust membership in its gated half-plane. A crossing can be well resolved in time yet arbitrarily close to `x=x_small`. All four profiles could agree on acceptance without resolving that boundary reliably, particularly because they share a correction formulation. Ambiguity at a rejected crossing can also change the accepted count, so checking accepted events alone would not suffice.
- **Concrete minimum fix:** At every downward historical-plane root, including roots rejected by the half-plane gate, record signed gate distance. Freeze an uncertainty margin in the same units, tied conservatively to the event-state accuracy budget. Treat roots within that margin as **gate-unresolved**, not as evidence of stable accepted counts. Add synthetic tests on both sides of, and within, the margin. If orientation filtering has any uncovered low-normal-velocity regime, apply the same unresolved treatment there.
- **Claim affected:** Numerically robust historical-section membership and ordered accepted return sets.

## B02 — The numerical acceptance budget lacks a demonstrated calibration

- **Severity:** Blocking; missing justification and control evidence, not evidence that the proposed numbers are wrong.
- **Plan section / excerpt:** Artifact 2’s proposed gates; Artifact 3’s metric using `[15,15,0.01]`, physical-coordinate crossing angle, and analytic-circle controls.
- **Why it matters:** The scaled event-state threshold implies, among other bounds, an absolute z discrepancy no larger than `1e-8`. That may be reasonable, but solver tolerances alone do not establish it. Near weakly transverse crossings, state error can produce much larger event-time error. The packet also does not specify enough about closure and extremum normalization to assess whether all gates form a coherent accuracy budget. The reported circle tests establish useful implementation behavior, but do not demonstrate the complete correction-to-event pipeline at the proposed anisotropy.
- **Concrete minimum fix:**
  1. Supply a compact gate table defining units, normalization, rationale, and the outcome assigned to each failure. Explicitly connect event-state uncertainty, normal velocity, phase uncertainty, and boundary margins.
  2. Before target execution, qualify the pipeline on an analytic periodic problem with known events and anisotropic coordinates. Exercise shooting correction as well as both event integrators, unless existing controls already do so.
  3. Include a small number of predetermined adverse cases: weak transversality, a near-plane extremum, closely spaced crossings, and the B01 gate edge. Demonstrate the declared acceptance or unresolved behavior; do not claim universal missed-root detection.
  
  Retain the proposed thresholds if this supports them. Otherwise revise and refreeze them without inspecting target outcomes. A broad tolerance sweep or a new Rössler control study is unnecessary.
- **Claim affected:** Interpretation of a pass as meaningful numerical agreement, and of a failure as something other than an arbitrary scaling artifact.

# Important non-blocking findings

## I01 — “Event transport” should not imply a verified merged chronology

- **Severity:** Important, non-blocking if the claim is narrowed.
- **Plan section / excerpt:** Artifacts 1–2: “common-trajectory event chronology”; Artifact 3: no merged cross-section chronology separation test.
- **Why it matters:** Per-section ordered agreement does not necessarily establish an unambiguous interleaving of the two sections when an event from each occurs nearly simultaneously. There is also no event-to-event transport map being validated. This omission is harmless for per-section reproducibility but matters for a stronger transport or correspondence claim.
- **Concrete minimum fix:** Describe the endpoint as **paired-section event reproducibility on the same corrected trajectory**. State that neither a cross-section bijection nor robust merged interleaving is established. Only if interleaving is needed for the next decision should the pilot add a merged-order comparison with a predefined temporal uncertainty exclusion.
- **Claim affected:** Cross-section correspondence and transport, rather than the narrower within-section checks.

## I02 — Freeze a compact outcome and decision contract

- **Severity:** Important, non-blocking; decision rules are partly present but not fully synthesized.
- **Plan section / excerpt:** Retain both nominations and all profiles; failures retained; no automatic retry; “final pass.”
- **Why it matters:** Agreement failures, unresolved geometry, solver failures, and provenance invalidation have different meanings. They must not become interchangeable “negative results.” Likewise, eight numerical profiles are not eight independent scientific observations, and the two nearby selected nominations cannot estimate a population success rate.
- **Concrete minimum fix:** Freeze per-nomination and overall outcome rules:
  - **Qualified:** All required profiles and gates pass.
  - **Numerically unresolved / not qualified:** Required numerical or geometric checks fail, or a profile is unavailable.
  - **Invalid execution:** Binding, source, raw-integrity, or other execution-integrity requirements fail.
  
  Retain detailed reasons beneath these labels. Define an overall pass as both nominations qualifying; report mixed outcomes without promoting only the favorable nomination into a general success claim. No significance testing or power calculation is needed for this fixed-case engineering qualification.
- **Claim affected:** Interpretation of positive, negative, mixed, incomplete, and invalid outcomes.

## I03 — The cooperative budget is not a runtime ceiling

- **Severity:** Important, non-blocking.
- **Plan section / excerpt:** “1,800 seconds cooperative wall budget,” checked at profile boundaries and after final audits.
- **Why it matters:** A long correction or integration can exceed that budget before control returns. Four profiles per nomination are a proportionate design, but the stated duration must not be represented as a hard resource bound.
- **Concrete minimum fix:** Declare an actual outer job limit or an explicit operator-abort policy, with interruption producing an incomplete receipt and no retry. Record a conservative storage expectation and qualification of the numerical dependencies on the target host. No new paid worker is necessary.
- **Claim affected:** Feasibility and completeness of the planned run, not the mathematical validity of completed comparisons.

## I04 — The successor needs a common sampling estimand, not just common trajectories

- **Severity:** Important, non-blocking for this pilot; required before successor execution.
- **Plan section / excerpt:** Artifact 2, worklist items 2–4: common retained population, capture definitions, scalar-map tests, and neutral critical identities.
- **Why it matters:** Common trajectories remove one major section-comparison confound, but event-weighted clouds can still weight those trajectories differently when sections have unequal return counts. A settled attracting cycle also cannot supply the independent support needed to qualify a partition or scalar map.
- **Concrete minimum fix:** In the successor’s separate freeze, define the independent sampling unit, trajectory- versus event-weighting, seed distribution, transient and finite-horizon rules, and capture conditioning. Freeze the primary scalar-map adequacy endpoint, support requirements, holdout scheme, and coordinate choice before target survivor outcomes. Use a bounded sample-size justification for that endpoint—not a symbolic-word success target.
- **Claim affected:** Whether later differences reflect section geometry, capture selection, or weighting, and whether later critical-membership claims have adequate support.

# What should remain unchanged

- **Both disclosed nominations remain fixed.** Their exploratory selection and proximity to the nomination threshold must remain visible; neither is an exact center certificate or an independent discovery replicate.
- **Both sections are observed on each same corrected trajectory.** This is the strongest protection against comparing incompatible orbit realizations.
- **DOP853 and Radau, each at two declared profiles, remain fixed.** Their agreement is valuable numerical triangulation, while the shared shooting formulation remains an explicit independence limitation.
- **Fixed half-open windows and no rotation/window search remain.** These prevent alignment choices from manufacturing agreement.
- **Raw plane roots precede orientation and gate filtering.** Rejected roots, failures, and partial runs should remain locally retained.
- **No partition, critical lettering, word matching, or continuation is performed.** Neither six-versus-eight counts nor a pilot pass licenses a symbolic node or arrow claim.
- **The non-certification language remains explicit.** These checks neither prove all roots were found nor certify a primitive period.
- **Pre-outcome execution locking and exact review/runtime binding remain.** Do not trade these safeguards for an informal approval.
- **The external review packet remains compact.** The omitted archive belongs in local verification and reproduction, not in this design review.

# Minimal revised design

1. **Freeze the actual question.**  
   For each of the two fixed nominations, do independently recorrected numerical profiles reproduce stable, well-resolved ordered accepted events on both declared sections over the fixed windows? The endpoint is a casewise qualification result and its predefined diagnostic vector, not a population estimand or symbolic confirmation.

2. **Keep the existing eight-profile design.**  
   Two nominations × two solvers × two profiles; unchanged seeds, correction formulation, integration horizon, expected counts, windows, and no automatic retry. No additional target reconnaissance is needed.

3. **Repair only the missing numerical qualification.**  
   Add the half-plane uncertainty exclusion. Define the existing gate metrics precisely and qualify their joint accuracy budget using compact analytic controls, including an end-to-end correction check and predetermined adverse event geometries. Absence of detected extrema is not, by itself, proof that none exist.

4. **Use the narrower chronology claim.**  
   Compare the ordered event sets within each section as planned. Do not add merged chronology machinery unless that is necessary for the immediate successor decision.

5. **Predeclare interpretation and stopping.**

   | Outcome | Permitted conclusion / action |
   |---|---|
   | Both nominations qualify | The numerical event-observation setup is adequate to attempt a separately reviewed common-population partition study. |
   | One qualifies | Case-specific mixed feasibility; retain both outcomes and authorize no automatic survivor promotion. |
   | A completed run shows unstable membership, poor conditioning, or inconsistent events | Current setup is not qualified; diagnose numerics or event geometry without interpreting this as a symbolic falsification. |
   | Required profile fails or run is interrupted | Qualification is incomplete; preserve evidence and do not infer absence of the orbit or chain. |
   | Integrity gate fails | Execution is invalid for qualification; retain the receipt and evidence. |

6. **Require a new freeze for any repair after target outcomes.**  
   No silent threshold relaxation, window movement, retry, seed change, or coordinate substitution. A redesigned follow-up must disclose what the pilot revealed.

# Freeze checklist

- [ ] B01 resolved: gate-distance metric, uncertainty margin, treatment of rejected roots, and edge tests are fixed.
- [ ] B02 resolved: compact numerical gate definitions and justification supplied; relevant analytic control results disclosed.
- [ ] Endpoint language explicitly excludes partition validity, critical membership, symbolic transport, primitive-period certification, and all-root certification.
- [ ] Per-nomination, overall, mixed, incomplete, and invalid outcome rules are fixed.
- [ ] Local source checks verify profile-specific correction, section equations and equilibrium selection, window endpoints, event matching, gate application, and failure aggregation.
- [ ] Local schema/execution checks verify units and normalizations, finite-data rejection, input bindings, raw retention, interruption handling, and final integrity invalidation.
- [ ] Target-host dependency qualification, resource stopping policy, storage expectation, and bounded reproduction instructions are recorded.
- [ ] Any design/runtime changes receive fresh bindings; the actual review and adjudication are retained; the approved source is pushed before execution.
- [ ] Successor sampling, weighting, capture, scalar-map, holdout, and critical-membership decisions remain separately frozen before their outcomes are generated.

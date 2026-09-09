# EXP-502: testing both contacts together

**Search in progress: first point audited, full result pending.** EXP-501 showed that
the limiting boundary misses the primitive cycle at the right-fold proximity
anchor. EXP-502 varies both a and c to test whether the two contact residuals
can be reduced together. The bounded search uses eight fixed stencil points
and permits one joint correction only if every representation passes.

The [prospective protocol](../experiments/EXP-502-joint-contact-search.md)
and [local design audit](../experiments/EXP-502-local-design-audit.md) state
all selections, tolerances and failure rules. The index choice is informed
by EXP-501, not an independent confirmatory selection. Matching two projected
x coordinates is not sufficient: both full-state contacts and primitive
six/eight counts must pass. No result alone supplies C/D labels or a Jones
period-insertion arrow.

## Validation before targets

- Fifteen focused tests pass, including missing/failed variants, singular and
  ill-conditioned Jacobians, scale disagreement, clipping, forbidden index
  rotation, guard retention/counts, budget refusal, authenticated inputs and
  isolated copied-source startup (`preflight-focused-03.xml`).
- The saved analytic rehearsal passes twelve fold profiles, four periodic
  profiles, four decimal profiles and six response controls, with no target
  integrations (`artifacts/EXP-502/preflight-controls-01`).
- The earlier full suite passed 2,331 tests with one Linux-only skip
  (`preflight-suite-01.xml`); that run preceded the final startup-path
  correction and two additional focused tests. The final revision passes
  **2,333 tests with one Linux-only skip** in 165.27 seconds
  (`artifacts/EXP-502/preflight-suite-02.xml`).
- A strengthened startup assertion caught a macOS `/var` versus
  `/private/var` path-normalization defect. The failed receipt remains
  `preflight-focused-02.xml` (14 pass, one fail); the assertion was retained
  and the copied root normalized. No target attempt was consumed.
- Manuscript references and the symbolic control table pass. No paid review,
  API call, credential read, GPU rental or raw upload was used.

## Integration-count clarification

The inherited section census makes a short guard integration followed by its
main integration, but archives only the main mesh. Earlier wrappers counted
archived products. EXP-502 retains the guard separately, counts every target
ODE call before it starts, and audits guard-to-main continuity. It also
reports the older product-count convention separately. Historical receipts
are unchanged; this finding does not by itself establish revised counts for
every earlier experiment or change any measured trajectory verdict.

## Execution record

The tested source was committed and pushed as
`69efcd337ea1601256ed60779f1ca6a73712c9cd`; the manifest SHA-256 is
`20c9fc885f2eeaf8df6225e487f67ee5d531b64ccaa4e0fe2e7e32bb28091038`.
Both public Linux CI jobs (Python 3.12 and 3.13) passed for that exact head:
[source-freeze checks](https://github.com/tdj28/butterfly/actions/runs/34397501855).
The runner was launched against that live public revision, with output at
`artifacts/EXP-502/target-69efcd3`. It repeats the analytic controls before
consuming the exclusive attempt marker. The first individually audited point
is recorded below; the whole response matrix remains pending. This file records
the complete run,
raw audit, failures and next scientific decision rather than marking the
research objective complete at preparation.

Latest execution checkpoint: all four a-direction stencil points have
completed, with 708 recorded target integrations. The c-direction points
continue. Only the first point has undergone the standalone audit below;
the complete eight-point response has not yet been interpreted.

### First fixed point: standalone raw audit completed

While the remaining points execute, the first point was audited through the
same frozen `check_point` function, after hashing its complete file inventory
and binding every frozen source. This early check does **not** replace the
final whole-experiment audit or permit a proposal from a partial stencil.

At (a,b,c)=(0.21548015990653546,0.2,7.212), all four fold representations, all
eight boundary representations, primitive-cycle qualification and cycle-index
correspondence pass. There is no joint proximity: the maximum fold-pair
distance is 0.0028628081 and the boundary/event-1 distance is 0.0139366085,
both outside 1e-4. Decreasing a alone at this dose worsens both distances
relative to the EXP-497/501 anchor. It does not settle the two-parameter test.

The audit counts 182 actual target integrations versus 158 products under the
old convention; the difference is the 24 now-retained guard integrations.
Receipt: `artifacts/EXP-502/first-point-audit-01.json`. Point SHA-256:
`b4ca4bbbe98b4a0e42a99e5c2bb39212809c679daef8a561cba7b7a19ec32e72`.
All remaining fixed points still run regardless of this result.

The retained size of the first two points motivates a separately documented
[resource continuation](2026-09-09-exp503-resource-continuation.md), prepared
while this run continues unchanged. It may execute only after an archived
resource failure and reuses every completed fixed point. The original cap,
attempt marker, source files and scientific thresholds are not being changed.

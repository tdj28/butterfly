# EXP-502: testing both contacts together

**Execution preparation, not a new scientific result.** EXP-501 showed that
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

Ready for the public source freeze after final-revision validation. No EXP-502 target
outcomes have yet been interpreted. This file will record the complete run,
raw audit, failures and next scientific decision rather than marking the
research objective complete at preparation.

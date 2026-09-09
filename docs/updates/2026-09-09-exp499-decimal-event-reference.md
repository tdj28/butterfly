# EXP-499: resolving the near-tangent accuracy question

EXP-498 is complete and merged through PR68 (`44b76c5`). Its two failed
section-state comparisons remain failed. The saved-data phase diagnostic
motivates a distinct, higher-precision reference, not a correction to those
original verdicts.

## The next decisive check

Use all 32 realized side inputs, all eight candidates and all 240 previously
accepted event nominations. Integrate each input in 40-digit/degree-24 and
50-digit/degree-32 decimal arithmetic, with fixed steps .02/.01. This is 64
new local CPU trajectories and 480 event-root evaluations. NumPy longdouble
on this Mac has only Float64 precision; changing that dtype would not supply
the needed reference.

The reference configurations must agree within 1e-12 in time and 1e-9 in
scaled full state. Then compare **both** original methods to **both** references
under the original 1e-7 time/1e-6 state thresholds. Failed, empty and missing
cases cannot be hidden by choosing one favorable reference.

Full decimal Taylor coefficients are streamed to local compressed archives
as steps complete. The auditor checks the coefficient equations with a
separate scalar calculation, mesh continuity, root states, complete inputs,
all comparisons, and source/raw hashes without integrating again.

## Local design audit and scope

- The method is not a rigorous enclosure. A small retained tail and agreement
  between configurations do not bound the unknown exact-flow error.
- Both configurations share one Taylor implementation. Independent scalar
  coefficient checks and known analytic solutions address some shared bugs;
  they do not amount to independent-team replication.
- Boxes come from the existing accepted-event census. This experiment can
  refine those nominations or fail to find them, not discover all missing
  crossings outside the boxes. Full-census qualification remains separate.
- Exact realized binary64 inputs and parameters are promoted with
  `Decimal.from_float`; no new section, equilibrium or nominal displacement
  is substituted.
- Only the state equation is integrated. The original variational state
  influenced adaptive error control but does not change the mathematical
  state ODE; its removal here is explicit, not an unnoticed solver setting.
- No reference result repairs EXP-498, proves C/D or identifies a second
  smooth critical point. The one-fold anchor still is not a verified center.

During result-free implementation, the final-time calculation was made
explicit to prevent Decimal rounding from causing a tiny nonadvancing final
step. Coefficient streaming replaced end-only storage so failures preserve
their partial trajectory. Both changes precede new target outcomes. The first
analytic control directory is retained; the second exercises the final
streaming consumer. No target run has been repeated.

The first isolated startup rehearsal failed before any target outcome: two
public transitive receipts (EXP-486 and EXP-491) were checked upstream but
absent from the copied input list. The failed temporary source tree and
`artifacts/EXP-499/sealed-startup-01-failure.json` remain. The unfrozen
successor now explicitly hashes both receipts; the parent source/plans are
unchanged. A read-set regression and actual isolated-checkout test guard the
complete input and import closure.

Before freeze, the initial storage reserve was set to 11 GiB because retained
preflight copies leave just over 12 GiB free. The 2 GiB output cap and 8 GiB
free-space floor are unchanged, leaving at least 1 GiB additional headroom.
No scientific accuracy threshold, sample or failure rule changed.

## Evidence and execution status

All 22 focused tests pass, including the complete read-set and isolated-source
startup checks. The final full suite passes **2,246 tests with one existing
Linux-only skip** in 149.01 seconds, retained in
`artifacts/EXP-499/preflight-tests-02.xml`. The preceding 2,244-test run is also
retained; the two added tests cover the packaging gap it did not detect.
All six analytic control profiles pass:
two precision configurations for a transverse rotation crossing, a near-tangent
rotation pair, and a nonlinear system with exact exponential solution.
The streaming controls are retained in
`artifacts/EXP-499/preflight-controls-03`. Their raw coefficient and root
identities also pass with integration disabled, recorded in
`artifacts/EXP-499/preflight-controls-audit-01.json`. All 92 imported/bound
source paths are present. The staged credential scan passes on 2,736 files.

The [protocol](../experiments/EXP-499-decimal-event-reference.md),
[plan](../../experiments/manifests/EXP-499-decimal-event-reference.json),
[runner](../../scripts/run_exp499_decimal_reference.py) and
[auditor](../../scripts/audit_exp499_decimal_reference.py) define the bounded
successor. Local preflight is complete; the next action is the public source
freeze and single bounded execution. Maximum workload: 64 target IVPs, 7,200 seconds, 2 GiB
output, 11 GiB initial disk reserve and 8 GiB free-space floor.

Paid review: **not run**, under the human-approval policy. No GPU rental,
credential access or raw upload is needed. Existing raw-publication boundaries
remain unchanged; compact evidence does not imply a full public raw release.

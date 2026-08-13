# EXP-202 — Low-smoothing scale-ensemble residual audit

Status: completed; failed with 94 eligible, zero direct candidates, and zero
strict two-residual bracket cells

## Question

Does the EXP-201-qualified shallow critical nominate a direct doubly-critical
period-6 orbit or a complete same-phase signed-residual bracket in the sampled
lower-`c` field when the arbitrary high-smoothing veto is replaced by a
low-smoothing ensemble?

## Frozen design

The input is exactly the 94 EXP-201-qualified candidates. The audit uses
smoothing indices 2, 3, and 4 (`4.6416e-6`, `1e-5`, and `2.1544e-5`), the
maximal contiguous three-level set for which every one of the 416
candidate/support/step reconstructions is resolved as three-branch. No orbit,
trajectory, critical point, or parameter is recomputed.

For each candidate, two criticals are assigned to distinct period-6 orbit
phases independently in all 12 scale/support/step reconstructions. Eligibility
requires a common ordered phase assignment and a maximum normalized critical-
location span of `0.03`. At least 70 candidates must remain eligible.

A direct nomination requires both assigned signed residuals to remain within
`0.02` in every reconstruction. A bracket nomination requires a complete
four-corner lattice cell with the same ordered phase assignment and both
residuals bracketing zero separately in every one of the 12 reconstructions.
The experiment passes if either nomination exists after the coverage gate.

Manifest:
[`../../experiments/manifests/EXP-202-low-smoothing-scale-ensemble-residual.json`](../../experiments/manifests/EXP-202-low-smoothing-scale-ensemble-residual.json).

## Claim boundary

A pass nominates a point or cell for fresh-trajectory zero-slope,
DOP853/Radau, and coordinate/section confirmation. It does not itself establish
double superstability. A failure rejects only the sampled, coverage-incomplete
stable field under this declared scale ensemble; it does not exclude a center
beyond the field or on an unstable continuation.

## Result

All 94 candidates remain eligible and use the same ordered phases `[7,5]` in
all 12 reconstructions. No point passes the `0.02` direct gate and none of the
40 complete lattice cells brackets both residuals in every reconstruction.

The first residual spans zero across the field, from `-0.004116` to `0.002440`,
but no complete cell brackets it view-by-view. The second residual is strictly
positive in all 1,128 evaluations: minimum `0.019945`, median `0.030794`, and
maximum `0.043328`. The closest candidate is `(a,c)=(0.21565,7.284)` with
worst residual `0.028711`, or 1.436 times the direct gate.

This scale-aware negative result validates the EXP-199 obstruction without
using the smoothing level that caused EXP-200's disagreement. Extend the
corrected stable family toward lower `c`, where the second residual is
smallest, before rerunning this ensemble. Keep unstable inter-window
continuation separate.

Raw receipt: `artifacts/EXP-202/receipt.json`, 705,390 bytes, SHA-256
`11ca103e800c084431bf1283982fd8d1e55866f8a0d35f36b49ebd80e6402136`.
Compact receipt: [`receipts/EXP-202.json`](receipts/EXP-202.json).

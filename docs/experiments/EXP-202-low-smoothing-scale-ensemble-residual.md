# EXP-202 — Low-smoothing scale-ensemble residual audit

Status: prospectively frozen before residual evaluation

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

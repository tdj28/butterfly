# EXP-180 retains one solver-independent support hole

Date: 2026-08-07

EXP-180 executed from pushed clean commit
`ad7a1993534a15a2e54780f08feae89f6dd79220`. The raw receipt is frozen at
SHA-256 `54267eba6b911022efd8d493b2fbb2704ef35ab275aeb6ee286e6b444ac3a949`.

Twenty of 21 DOP853 points and four of five Radau controls resolve the same
local critical in all variants and both coordinates. At the trimodal endpoint,
all four solver-coordinate decisions select critical index 1 with large
runner-up margins. The strict experiment remains failed because `a=0.156`
occupies only `14–23.3%` of bins under both solvers, so no variant clears the
unchanged `70%` domain-support floor.

The next test must fill that support hole with a qualified transient or
nonattracting invariant-set construction. Nominal spline extrapolation and
interpolation across the gap are not accepted.

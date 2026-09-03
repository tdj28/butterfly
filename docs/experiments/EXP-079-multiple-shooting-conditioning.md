# EXP-079 — Multiple-shooting conditioning audit

Status: executed; passed

At the verified 160→320 event, represent the doubled parent with 1, 2, 4, 8,
16, and 32 cyclic shooting segments. Build the block matching Jacobian with
node-state, total-duration, parameter-sensitivity, and phase columns. Record
matching residuals, segment transition conditioning, and singular spectra.

Pass if the 32-segment smallest singular value is `<=1e-7`, matching residual
is `<=1e-8`, and it is at least threefold smaller than the equivalent
one-segment value. Passing validates the conditioning premise for implementing
a segmented branch-switch corrector; it does not itself find period 320.

The clean run at `15941395b7e632739c216e7f06af4f4cc8dddf80` passed.
The one-segment smallest singular value is `7.7488e-7`; values for 2, 4, 8,
16, and 32 segments fall to `1.1285e-7`, `8.6161e-9`, `2.6284e-9`,
`1.8954e-9`, and `9.0708e-10`. The 32-segment reduction factor is `854.26`,
with matching residual `1.247e-9`. Receipt SHA-256:
`ebfae4383f9e0dd667b3d76664492fbcf6e025126e20d71026d3be0cdd372c45`.

Accept the conditioning premise. Implement a sparse segmented corrector and
validate it against a lower-period known child before retrying the period-320
switch. Large individual transition matrices remain ill-conditioned, so the
block system must be solved without explicitly composing monodromies.

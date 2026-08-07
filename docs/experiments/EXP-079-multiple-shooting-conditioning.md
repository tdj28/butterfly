# EXP-079 — Multiple-shooting conditioning audit

Status: preregistered after EXP-078; pending clean execution

At the verified 160→320 event, represent the doubled parent with 1, 2, 4, 8,
16, and 32 cyclic shooting segments. Build the block matching Jacobian with
node-state, total-duration, parameter-sensitivity, and phase columns. Record
matching residuals, segment transition conditioning, and singular spectra.

Pass if the 32-segment smallest singular value is `<=1e-7`, matching residual
is `<=1e-8`, and it is at least threefold smaller than the equivalent
one-segment value. Passing validates the conditioning premise for implementing
a segmented branch-switch corrector; it does not itself find period 320.

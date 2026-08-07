# EXP-102 — Receipt-bound analytic augmented flip resume

Status: preregistered; not executed

Bind the failed full EXP-101 receipt as both source and baseline. Resume from
its exact 32 orbit nodes, period, corrected `b`, and 32 transported tangent
nodes with zero parameter offset. Re-anchor only the phase gauge at the stored
first node. Keep the same bounds `[0.17971245,0.17971255]`, baseline DOP853
integrator, exact Rössler second-variational Jacobian, EXP-089 reference, and
explicit proximity-to-`-1` spectrum selection.

Permit 20 additional exact residual/Jacobian evaluations at tolerance `1e-11`.
All scientific gates are unchanged: solver success; reference error `<=5e-10`;
orbit, phase, tangent, and normalization residuals each `<=1e-8`; direct flip
residual `<=1e-6` with imaginary part `<=1e-8`; and block/direct difference
and cyclic spread each `<=1e-8`.

Passing completes DEC-003's mandatory known-event validation and permits a
separately preregistered 64-segment application to the period-640 source.
Failure closes this unscaled trust-region path and requires a frozen scaling or
nonlinear-solver comparison. It does not alter EXP-099 or establish an eighth
event or period-1280 child.

# EXP-102 — Receipt-bound analytic augmented flip resume

Status: executed; passed

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

The clean run at `812b26bcec8d230632b064c566fdf0e0da5e66d1` passed. It
terminated successfully by `xtol` after 20 evaluations and `254.05 s`, at
`b=0.17971249399303613`. The error from EXP-089 is `-8.94e-13`; orbit,
tangent, phase, and normalization residuals are `9.21e-13`, `1.01e-11`,
`1.62e-18`, and `1.11e-16`. Four direct products give
`-0.99999997682431`, block/direct difference `8.88e-15`, and cyclic spread
`1.67e-15`. Full receipt SHA-256:
`040085a791de6940be4ab4111d8a45f69bb7e8d50cf14b7611e047d181472410`.

DEC-003's mandatory known-event validation is complete. The same analytic
formulation may now be applied in a separately frozen 64-segment experiment to
the bracketed period-640 event. EXP-102 does not retroactively pass any scalar
refinement and does not establish the eighth event or a period-1280 child.

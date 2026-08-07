# EXP-105 — Independently qualify the period-1280 child

Status: executed; passed

Bind the passed full EXP-104 receipt and select both signs at frozen predictor
length `0.001`. Correct each 128-segment candidate independently to the common
parameter `b=0.17971215`, on the child side of the eighth event and just beyond
both source candidates. Use the EXP-103 tight integrator and analytic fixed-
parameter multiple shooting.

At the common parameter, compute a 128-block cyclic Floquet spectrum for each
sign. Independently reconstruct both full dense orbits, search 256 coarse phase
shifts, and apply five deterministic 129-point refinement stages. Pass only if
both correctors succeed with matching residual `<=1e-8`, half-node RMS remains
`>=1e-5`, both dominant nontrivial moduli are `<=0.999`, their difference is
`<=1e-4`, phase-aligned whole-orbit RMS is `<=1e-5`, maximum segment endpoint
error is `<=1e-8`, and the two periods agree within `1e-8`.

Passing establishes that both switch signs represent one stable period-1280
child and closes the eighth local supercritical rung. It remains finite local
cascade evidence, not a proof of universality or a complete explanation of the
parameter plane. Failure retains the distinct EXP-104 candidates but forbids
the stability and supercriticality claims.

The clean run at `42dee43051bb7d88bf6a8fff55839a0beaafd716` passed. Both signs
correct in four evaluations with matching residuals below `2.18e-12`, identical
period `8367.041654978086`, and half-node RMS `1.086e-4`. Deterministic phase
matching finds shift `0.49999999917054` and whole-orbit RMS `3.94e-8`; maximum
segment endpoint error is `2.70e-12`. The independent 128-block dominant
moduli are `0.4261745532` and `0.4261741560`, differing by `3.97e-7` and both
well inside the unit circle. Full receipt SHA-256:
`e63a38618e1539d79942180539024b9c9ff4e1e10c2716da79d8890522013eaf`.

The two switch signs are one stable period-1280 child. Together with EXP-103
and EXP-104, this closes the eighth local supercritical rung. The result
strengthens the finite cascade and three prospective predictions; it does not
by itself establish universality or explain the global shrimp/hub plane.

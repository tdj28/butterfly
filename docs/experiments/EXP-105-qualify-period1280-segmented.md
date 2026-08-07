# EXP-105 — Independently qualify the period-1280 child

Status: preregistered; not executed

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

# EXP-100 — Validate the augmented segmented flip solve

Status: preregistered; not executed

Implement DEC-003's square orbit--parameter--anti-periodic-tangent system and
validate it at the already resolved EXP-089 period-320 event. Bind the full
EXP-089 receipt, perturb its source `b` upward by `5e-9`, and keep the frozen
search bounds `[0.17971245,0.17971255]`.

With 32 shooting segments, solve `194` unknowns: 96 orbit-node coordinates,
total period, `b`, and 96 tangent-node coordinates. Enforce 96 orbit matching
equations, one phase equation, 96 tangent transport/anti-periodic boundary
equations, and one tangent normalization. Use a local-dependency sparse finite-
difference Jacobian and the established baseline integrator.

Pass only if the solver reports success, recovers the EXP-089 reference event
within `5e-10`, and has orbit, phase, tangent-transport, and normalization
residuals each `<=1e-8`. An independent block-cyclic spectrum must give a real
`-1` residual `<=1e-6`; block and four cyclic direct-product results must agree
and remain basepoint-stable within `1e-8`.

Passing validates the augmented formulation at period 320. It does not change
the EXP-099 status or establish the period-640 event. Only a separately frozen
64-segment application may do that.

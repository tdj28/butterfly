# EXP-100 — Validate the augmented segmented flip solve

Status: executed; failed at the frozen evaluation cap

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

The clean run at `e7a046a956060504497d64358e35097c7bc47dfe` exhausted all
30 function evaluations after `2367.32 s`. It reduced the tangent-transport
residual from `3.09e-4` to `2.14e-9`, but stopped with orbit matching
`1.73e-7`, parameter error `4.91e-9`, and first-order optimality `1.52e-8`.
Those values fail the unchanged `1e-8`, `5e-10`, and solver-success gates.
Full receipt SHA-256:
`a95552c2699ad3df43c5861e17d15bc54e7a25553571babefa7b1194bbbf0eb8`.

The independent direct monodromy calculation nevertheless gives the intended
signed multiplier `-0.99999998557114`, with cyclic-basepoint spread
`2.00e-15`. The augmented anti-periodic equations are therefore moving toward
the correct eigendirection, but the finite-difference corrector is neither
converged nor fast enough to validate the method.

EXP-100 also exposes a diagnostic bug at the double unit collision: the
generic block-spectrum cluster labels call the near `-1` cluster neutral and
the near `+1` cluster nontrivial. That makes the recorded block/product
difference and independent block multiplier residual approximately `2`, even
though the block clusters themselves contain both `+0.9999998806` and
`-0.9999999856` and the direct products consistently identify the latter.
This does not change the failed outcome, which already fails solver, orbit,
and reference gates. The next experiment must use an exact second-variational
Jacobian and validate the flip cluster by proximity to `-1`, not by the generic
neutral/nontrivial labels.

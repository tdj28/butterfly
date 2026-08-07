# EXP-076 — Resolve the period-160 flip

Status: preregistered after EXP-075; pending clean execution

Repeat only the final EXP-075 bracket with `rtol=2e-13`, `atol=2e-15`,
`max_step=0.025`, and bisection tolerance `1e-14`. Require bracket width
`<=2e-14`, multiplier residual `<=5e-9`, real multiplier, closure `<=1e-9`,
and half-period closure `>=5e-4`.

Passing locates the 160→320 candidate and permits its spacing ratio to be
reported. It does not establish the period-320 child or asymptotic
universality.

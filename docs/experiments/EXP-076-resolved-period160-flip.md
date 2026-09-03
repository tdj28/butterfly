# EXP-076 — Resolve the period-160 flip

Status: executed; failed before receipt

Repeat only the final EXP-075 bracket with `rtol=2e-13`, `atol=2e-15`,
`max_step=0.025`, and bisection tolerance `1e-14`. Require bracket width
`<=2e-14`, multiplier residual `<=5e-9`, real multiplier, closure `<=1e-9`,
and half-period closure `>=5e-4`.

Passing locates the 160→320 candidate and permits its spacing ratio to be
reported. It does not establish the period-320 child or asymptotic
universality.

The clean run at `6e1bf07` stopped before writing a receipt because both
endpoints had the same multiplier sign under the tighter solver. The inherited
`1.05e-13` bracket was narrower than the solver-induced root shift. This is a
precision-consistency failure, not evidence against the event.

A post-failure five-point audit with the same tighter solver directly brackets
the root on `[0.17971388325058413,0.17971388330058413]`, with endpoint
residuals `-1.6620e-5` and `+2.2256e-8`. EXP-077 freezes that measured bracket
and retains all EXP-076 acceptance gates.

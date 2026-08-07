# EXP-062 — Resolve the period-20 flip residual

Status: preregistered after EXP-061; pending clean execution

Repeat only the final EXP-061 bracket using half the solver tolerances,
`max_step=0.01`, bisection tolerance `1e-11`, and multiplier residual gate
`5e-8`. Require bracket width `<=2e-11`, closure `<=1e-9`, real multiplier,
and half-period closure `>=0.05`.

Passing resolves the numerical near miss and locates the period-20-to-period-40
flip candidate. Period-40 existence and criticality remain separate tests.

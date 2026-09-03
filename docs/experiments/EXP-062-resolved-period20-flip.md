# EXP-062 — Resolve the period-20 flip residual

Status: executed; passed

Repeat only the final EXP-061 bracket using half the solver tolerances,
`max_step=0.01`, bisection tolerance `1e-11`, and multiplier residual gate
`5e-8`. Require bracket width `<=2e-11`, closure `<=1e-9`, real multiplier,
and half-period closure `>=0.05`.

Passing resolves the numerical near miss and locates the period-20-to-period-40
flip candidate. Period-40 existence and criticality remain separate tests.

The clean run at `17f5c894440719a5857c54430191a778be830e96` passed.
It locates the period-20 `-1` event at `b=0.17989122376161149` in an
`8.23e-12` bracket. The best multiplier is `-1.00000000307`, closure is
`9.23e-14`, and half-period closure is `0.126248`. Receipt SHA-256:
`39ff26d290174285d6b77c0a9ff0437da0c2500473f2e47cc23805f17b9082d2`.

Accept a true period-20 flip candidate and switch its period-40 shooting
branch. Child existence, identity, and stability exchange remain open.

# EXP-061 — Refine the period-20 flip

Status: executed; failed residual gate by 5.6 percent

Refine the verified period-20 child's real Floquet crossing through `-1`
inside the frozen EXP-059 bracket
`b=[0.179867537983,0.180005617536]`. Use the reusable doubled-child refinement
and require half-period closure `>=0.05` at every accepted event estimate.

Pass with bracket width `<=1e-9`, multiplier residual `<=1e-7`, imaginary part
`<=1e-8`, closure `<=1e-9`, and the half-period identity gate. Passing locates
a candidate period-20-to-period-40 flip. It does not establish the period-40
child or criticality until a separate switch and fixed-parameter qualification.

The clean run at `3273a7b06fdc02776d9b8dd688755f8f98ec0363` failed one
numerical gate. It narrowed the event to a `6.58e-11` bracket around
`b=0.1798912237575`, with closure `2.62e-13` and half-period closure `0.12625`,
but the best multiplier residual `1.056e-7` slightly exceeds the frozen
`1e-7` threshold. Receipt SHA-256:
`d4d779eaf8f65fc26fa925c947a4b51efb71916e6cf1f6375671ff0ae9324cfe`.

Retain the run as failed. EXP-062 freezes its final bracket, tightens the
parameter tolerance to `1e-11`, and requires the stricter multiplier residual
`5e-8`; it does not relax identity or closure gates.

# EXP-061 — Refine the period-20 flip

Status: preregistered after EXP-060; pending clean execution

Refine the verified period-20 child's real Floquet crossing through `-1`
inside the frozen EXP-059 bracket
`b=[0.179867537983,0.180005617536]`. Use the reusable doubled-child refinement
and require half-period closure `>=0.05` at every accepted event estimate.

Pass with bracket width `<=1e-9`, multiplier residual `<=1e-7`, imaginary part
`<=1e-8`, closure `<=1e-9`, and the half-period identity gate. Passing locates
a candidate period-20-to-period-40 flip. It does not establish the period-40
child or criticality until a separate switch and fixed-parameter qualification.

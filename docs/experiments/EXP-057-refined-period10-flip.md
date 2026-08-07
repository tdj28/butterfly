# EXP-057 — Refine the first period-10 flip

Status: preregistered after EXP-056; pending clean execution

Refine the stable period-10 child's first real Floquet crossing through `-1`
inside the frozen EXP-052 bracket
`b=[0.180320828520,0.180788459850]`. Correct the full child orbit at every
bisection point and require half-period closure `>=0.5`, avoiding both the
section-count ambiguity exposed by EXP-054/055 and the double-covered-parent
hop exposed by EXP-056.

Pass with bracket width `<=1e-9`, multiplier residual `<=1e-7`, imaginary part
`<=1e-8`, closure `<=1e-9`, and the half-period identity gate. Passing locates
a candidate period-10-to-period-20 flip; branch switching is still required to
establish the child and determine criticality.

# EXP-057 — Refine the first period-10 flip

Status: executed; passed

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

The clean run at `6c7d971564a837632b8975ab61d9d454a56ed3dc` passed.
It locates the period-10 `-1` event at `b=0.18053720820244146` in a
`5.57e-11` bracket. The best multiplier is `-0.9999999846`, closure is
`1.28e-12`, and half-period closure is `0.889644`, decisively excluding a
double-covered period-5 parent. Receipt SHA-256:
`350458bf4ccc23bfd8804e2ee2e1ae986be62744c9a08452501b23dca388a7a8`.

Accept a true period-10 flip candidate and switch its period-20 shooting
branch. Criticality and the child stability remain open until that switch is
independently qualified.

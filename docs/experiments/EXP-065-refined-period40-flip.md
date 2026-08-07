# EXP-065 — Refine the period-40 flip

Status: executed; passed

Refine the independently qualified period-40 child's real Floquet crossing
through `-1` inside the frozen EXP-063 positive-arm bracket
`b=[0.179702297291,0.179822410665]`. Require bracket width `<=2e-11`,
multiplier residual `<=5e-8`, real multiplier, closure `<=1e-9`, and
half-period closure `>=0.01`.

Passing locates a candidate period-40-to-period-80 flip and supplies a fourth
cascade parameter. Period-80 existence and criticality remain separate tests;
no universality estimate is accepted solely from the first few spacings.

The clean run at `470dcc2f8cc22a9e981bc3d1a4da01662076ae65` passed.
It locates the period-40 `-1` event at `b=0.17975062136766212` in a
`7.16e-12` bracket. The best multiplier is `-1.00000002748`, closure is
`3.48e-14`, and half-period closure is `0.0399174`. Receipt SHA-256:
`fd6ec4742f18461a89458dc635d41569f6dbce3676570d5c6cf7a9251e487d1d`.

Accept a period-40-to-period-80 flip candidate. Analyze the four verified
event parameters prospectively, then use the resulting next-event prediction
to guide—but not pre-validate—the period-80 branch search.

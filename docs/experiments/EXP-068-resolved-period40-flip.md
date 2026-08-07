# EXP-068 — Resolve the period-40 event for branch switching

Status: preregistered after EXP-067; pending clean execution

Re-refine only the frozen EXP-065 final bracket using `rtol=2e-13`,
`atol=2e-15`, `max_step=0.01`, and bisection tolerance `1e-12`. Require bracket
width `<=2e-12`, multiplier residual `<=1e-8`, closure `<=1e-9`, real
multiplier, and half-period closure `>=0.01`.

Passing supersedes EXP-065 only as the numerical source point for another
period-80 switch. It does not alter the earlier event sequence or EXP-066
prediction analysis beyond a negligible last-coordinate refinement.

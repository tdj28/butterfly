# EXP-068 — Resolve the period-40 event for branch switching

Status: executed; passed

Re-refine only the frozen EXP-065 final bracket using `rtol=2e-13`,
`atol=2e-15`, `max_step=0.01`, and bisection tolerance `1e-12`. Require bracket
width `<=2e-12`, multiplier residual `<=1e-8`, closure `<=1e-9`, real
multiplier, and half-period closure `>=0.01`.

Passing supersedes EXP-065 only as the numerical source point for another
period-80 switch. It does not alter the earlier event sequence or EXP-066
prediction analysis beyond a negligible last-coordinate refinement.

The clean run at `e6e355d4de86860da7f7e71405d0c2881aa0b2e9` passed.
It locates the event at `b=0.17975062136631975` in an `8.95e-13` bracket.
The best multiplier is `-1.00000000242`, closure is `7.32e-13`, and
half-period closure is `0.0399174`. Receipt SHA-256:
`0c4698f47921ddc89a61d7d01f566d010d3b0ee52b58a8b9c9d9a33d1542579b`.

Accept this as the resolved numerical source point for the next period-80
switch. The shift from EXP-065's estimate is `1.34e-12`, immaterial to the
reported cascade ratios at their shown precision.

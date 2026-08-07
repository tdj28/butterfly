# EXP-051 — Refined identity-safe period-5 flip

Status: preregistered after EXP-050; pending clean execution

Bisect the true period-5 branch's signed real multiplier through `-1` inside
`b in [0.1825,0.185]`. Every midpoint must retain exactly five section
crossings. Pass requires bracket width `<=1e-9`, multiplier residual `<=1e-7`,
closure `<=1e-9`, and identity 5 at the best point.

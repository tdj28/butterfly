# EXP-051 — Refined identity-safe period-5 flip

Status: executed; passed

Bisect the true period-5 branch's signed real multiplier through `-1` inside
`b in [0.1825,0.185]`. Every midpoint must retain exactly five section
crossings. Pass requires bracket width `<=1e-9`, multiplier residual `<=1e-7`,
closure `<=1e-9`, and identity 5 at the best point.

The clean run at `13cef6b12c7bd818a841803a117d5bac2bd7b1bf` passed.
The refined event is `b=0.18346759077`, bracket width `7.45e-11`, best
multiplier `-0.99999999493`, closure `6.25e-14`, and crossing identity 5.
Receipt SHA-256:
`9c5b805435a3eaa53af2ba44ea2b0ac80366ea524028fe73b393aa9ae2d38cb5`.
Accept the true period-5 flip and switch its doubled-period shooting branch.

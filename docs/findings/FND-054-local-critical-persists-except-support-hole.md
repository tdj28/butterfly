# FND-054 — The likely Jones critical persists except at one support hole

Status: strong directional support; uninterrupted identity not qualified

On fresh trajectories, EXP-180 locally bootstraps the pre-existing critical at
20 of 21 DOP853 path points and four of five independent Radau controls. Both
solvers and both coordinates land on increasing-coordinate trimodal critical
index 1 at `a=0.160`, with endpoint distances below `0.006` and runner-up
margins above `0.316`.

The sole `a=0.156` failure occurs identically in both solvers and coordinates.
Nominal critical locations remain tightly grouped, but the banded attracting
support occupies only `14–23.3%` of oracle bins, below the frozen `70%` floor.
The result therefore supports the same local identity on both sides of the
gap, but does not authorize interpolation through it or historical symbol
assignment. An invariant-set reconstruction with adequate support is required.

Evidence: [`../experiments/EXP-180-jones-local-critical-track.md`](../experiments/EXP-180-jones-local-critical-track.md).

# EXP-111 — Statistical convergence of the published saddle controls

Status: preregistered under DEC-006; not yet executed

EXP-110 is retained as failed. This successor tests the two diagnosed
obstructions without rewriting the earlier manifest.

At each published period-4 control, run five frozen sprinkler ensembles:

- the original 8192-seed, `dt=0.01`, horizon-300 baseline;
- the same ensemble at half the step;
- conditioning to time 360 with a later midpoint window;
- a half-cell-shifted grid at the original resolution; and
- a half-cell-shifted `96 x 48` grid.

The branch candidate floor is `0.001` of the global target range, but no branch
passes merely because it exceeds that value. Every coordinate/run must retain
the expected count across all 15 combinations of five bin counts and three
smoothing values. Every cell performs 50 deterministic bootstraps. Within-run
normalized critical-location span must be at most `0.03`; the span across all
five ensembles must be at most `0.04`.

Long-horizon survivor fractions may differ from baseline by no more than 0.05
at common checkpoints. Each run must leave at least 100 final survivors,
provide at least 1000 within-trajectory pairs per coordinate, remain numerically
finite, and recover two branches at `a=0.118` and three at `a=0.149` in `y` and
`z`.

Five fixed seeds per control also undergo a pointwise 40-time-unit RK4/DOP853
audit before long chaotic separation. At least five returns must match with
maximum scaled section-state error `0.001` and time error `2e-5`. The tolerance
was calibrated before preregistration on the separate chaotic-attractor control
`a=0.11`, where the largest observed errors were `0.000612` and `9.48e-6`.

A pass qualifies the CPU sprinkler reconstruction at the two published
controls. It still requires an independent saddle method and CPU/GPU
statistical parity before the TBA can be continued across the parameter plane.

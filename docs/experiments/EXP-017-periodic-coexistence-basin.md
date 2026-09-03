# EXP-017 — Period-12/period-3 basin-plane reconnaissance

Status: passed coarse reconnaissance; boundary scaling pending
Manifest: `experiments/manifests/EXP-017-periodic-coexistence-basin.json`
Claim target: CLM-019

## Purpose

Map a declared two-dimensional initial-condition cross-section for the
coexisting stable period-12 and period-3 cycles established by EXP-015 and
EXP-016 at `(a,b,c)=(0.245,0.2,5.75)`.

## Method and acceptance gate

The discovery plane is `z_0=0` with `x_0,y_0 in [-10,10]` on a `21 x 21`
grid. Every initial condition is integrated after transient 4,800, then up to
192 section crossings are collected over 1,600 time units. The recurrence
classifier tests periods through 32 with eight repeats. Independent processes,
not Python threads, execute the grid.

The experiment passes operationally if all 441 initial conditions return an
explicit result without numerical failure. It supports a nontrivial basin
cross-section if both periods 3 and 12 occur away from only their original seed
points. Unresolved pixels are retained and later receive longer transient
checkpoints; they are not labeled chaotic.

This coarse plane cannot measure a fractal basin boundary or exclude other
basins in three-dimensional state space. Its purpose is to choose a focused
adaptive basin domain and boundary-refinement strategy.

## Result

The clean run from commit `be279486f47c881dfbe9c84447eb48f9a32934e1`
completed all 441 initial conditions with eight local processes in 284.9
seconds. Every seed resolved periodically: 282 to period 12 and 159 to period 3.
There were no unresolved or numerical-failure pixels.

The coarse categorical grid is highly intermingled:

- 395 of 840 four-neighbor edges, or `0.47024`, change attractor; and
- 432 of 441 points have at least one differently classified point in their
  local `3 x 3` neighborhood.

This rejects a simple single smooth division at the sampled scale. It motivates
an uncertainty-exponent/resolution study and targeted basin-boundary dynamics.
It does not yet establish a fractal, riddled, or Wada basin boundary; those
terms require scale-dependent evidence and, for Wada, a third basin.

Result SHA-256:
`0037fd278b2da2e77565d28b4b15cba14e86f385a6c5998aceec615648cec69a`.
The checked-in receipt is [`receipts/EXP-017.json`](receipts/EXP-017.json).

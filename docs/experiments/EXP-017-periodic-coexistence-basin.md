# EXP-017 — Period-12/period-3 basin-plane reconnaissance

Status: preregistered; execution pending
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

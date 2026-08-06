# EXP-016 — Period-12/period-3 coexistence and Floquet gate

Status: preregistered; execution pending
Manifest: `experiments/manifests/EXP-016-periodic-coexistence-floquet.json`

## Purpose

Test the sole EXP-015 persistent-multistability candidate at
`(a,b,c)=(0.245,0.2,5.75)` by recovering both long-lived cycles and computing
flow closure and Floquet multipliers. The two initial states remained on period
12 and period 3 respectively through transient 19,200.

## Method and acceptance gate

Both basin probes are reintegrated after transient 9,600 with tighter DOP853
tolerances (`rtol=1e-11`, `atol=1e-13`, `max_step=0.025`). Up to 384 section
crossings are collected over 3,000 time units. Period classification requires
12 repeats at stricter recurrence tolerances.

Each recovered cycle must have the expected distinct period, flow closure error
at most `1e-7`, a neutral autonomous-flow multiplier within `1e-5` of one, and
all nontrivial Floquet multipliers strictly inside the unit circle.

Passing supports two stable coexisting periodic attractors for the sampled
basins. Basin-boundary mapping, exact shooting/collocation correction,
continuation of both families, and interval validation remain required for a
world-class persistent-multistability claim.

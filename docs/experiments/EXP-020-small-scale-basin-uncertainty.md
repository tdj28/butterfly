# EXP-020 — Prospective small-scale basin uncertainty

Status: preregistered; pending frozen GPU execution
Manifest: `experiments/manifests/EXP-020-small-scale-basin-uncertainty.json`
Claim target: CLM-019

## Purpose

Test prospectively whether the small-scale exponent suggested by EXP-019
persists when the scale window is extended four dyadic levels. EXP-019 showed a
coarse saturation plateau and a post-result four-scale slope near 0.373. This
experiment freezes the entire new window before execution and fits all seven
declared scales, avoiding post-hoc window selection.

## Frozen method and gate

The parameters, initial-condition plane, pair geometry, Float64 GPU integrator,
transient, observation horizon, and recurrence classifier are unchanged from
EXP-019. The seven epsilons run from 0.125 to 0.001953125. Two new deterministic
seeds and 4,096 pairs per seed give 8,192 pairs per scale and 57,344 pairs in
total. The execution gate again requires at least 98% of pairs at every scale
to resolve into period 3 or period 12.

The primary numerical result is the all-seven-scale log-log slope, its 5,000-
sample pair-bootstrap interval, and `R^2`. Consistency with the EXP-019
small-scale candidate requires a well-fit positive exponent in roughly the
previous `[0.35,0.40]` band. Failure of that comparison is retained and would
mean the previous four-scale window was pre-asymptotic or unstable.

## Limits

Even a stable result applies only to the declared plane and basin pair. A final
fractal-boundary claim still requires CPU subset parity, integration-horizon
sensitivity, added spatial regions or conditioning rules, and assessment of
direction/seed dependence.

# EXP-026 — Resolved local pseudo-arclength through the period-5 +1 crossing

Status: preregistered; pending clean local execution
Manifest: `experiments/manifests/EXP-026-period5-local-pseudo-arclength.json`
Claim target: EXP-024/025 period-5 `+1` branch interaction

## Purpose and method

Repeat EXP-025 with a constant arclength step one quarter of the original seed
secant norm. The corrected implementation holds that step length fixed rather
than recursively shrinking it. The same exact state-transition and `b`-
sensitivity Jacobian traces the fixed-`(a,c)=(0.245,5.1)` period-5 orbit from
the `b=0.265,0.270` seeds through the local guard window `[0.24,0.31]`.

The run freezes 100 attempted steps and requires at least 30 corrected points
with maximum closure `<=1e-9`. The primary observations are whether `b` reverses
and where the significant real multiplier crosses `+1` along this continuously
traced branch.

## Limits

A smooth `+1` crossing without a `b` turn rejects a saddle-node interpretation
for this branch but does not identify the second interacting branch or the
generic bifurcation type. That requires a coupled eigenvector/boundary system
and local two-branch analysis.

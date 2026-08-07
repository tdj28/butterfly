# EXP-026 — Resolved local pseudo-arclength through the period-5 +1 crossing

Status: executed; closure passed; frozen point-count gate failed
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

## Result

The clean run at commit `cbc1229b48a67fa15a55152639a15596b23b8b97`
produced 24 corrected points before crossing the `b=0.31` guard, short of the
frozen minimum 30, so the overall gate failed. Maximum closure was
`6.35e-11`, and there were no `b`-direction reversals.

The denser branch trace brackets the smooth real `+1` crossing between
`b=0.27135355` (multiplier `0.920922`) and `b=0.27274971` (multiplier
`1.040261`), with a descriptive linear estimate `b=0.27227869`. The multiplier
then increases monotonically through the sampled local path, reaching `4.9257`
by `b=0.31066`.

The receipt SHA-256 is
`9e15e1cd8ec4dba0b170a093554609ab4be791dee6ce895c5df36b8b6eb3e416`.

## Decision

The no-turn result is reproduced at quarter step, and the branch interaction
is localized far from the rejected EXP-024 scalar center. The completed gate
remains failed because 24 is less than 30. EXP-027 freezes one-eighth seed-
secant spacing and a `b=0.30` guard, which should supply at least 40 points while
independently resolving the same crossing.

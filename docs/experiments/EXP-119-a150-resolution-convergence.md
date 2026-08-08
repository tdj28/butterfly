# EXP-119 — `a=0.150` resolution convergence and tighter trace audit

Status: preregistered; not executed

## Diagnosis under test

EXP-118 found a repeatable split: 20-bin variants under-resolve the shallow
extremum as two branches, while every resolved 30--80-bin variant returns
three. EXP-119 tests that resolution model on new data rather than relaxing
the failed predecessor.

## Frozen new data

At `a=0.150,b=0.2,c=20`, collect 2400 returns after a 10000-time-unit burn-in
from the original state and four new scrambled-Sobol section states using seed
119. This doubles the prior sequence length and changes every Sobol target.
All five datasets must integrate successfully, remain nonperiodic through
period 64, and supply at least 2000 pairs in both coordinates.

The three 20-bin variants are an explicit under-resolution control and must
return two in `y` and `z`. The twelve 30--80-bin variants are the declared
adequate-resolution group and must return three. Every cell must pass its
50-bootstrap oracle. Within-dataset critical drift must be at most `0.03`; the
combined new/frozen-EXP-118 drift must be at most `0.04`. The predecessor raw
receipt hash and its adequate-resolution intervals are embedded in the
manifest.

## Tighter Lyapunov gate

Repeat the two initial-state variational and independent two-trajectory
Lyapunov calculations with DOP853 tightened from `(rtol,atol,max_step) =
(1e-10,1e-12,0.05)` to `(1e-11,1e-13,0.025)`. Both must classify chaotic,
agree on the largest exponent within `0.03`, and now satisfy the unchanged
`1e-6` divergence-trace identity threshold.

## Claim boundary

Passing qualifies the `a=0.150` chaotic invariant set as three-branch at the
declared adequate resolutions and explains the former two label as measured
under-resolution. It does not locate the TBA, close the `a=0.145` support hole,
prove template equivalence, or supply a global curve.

Immutable manifest:
`experiments/manifests/EXP-119-a150-resolution-convergence.json`.

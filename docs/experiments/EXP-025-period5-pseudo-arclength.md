# EXP-025 — Fold-safe period-5 pseudo-arclength continuation

Status: executed; resolution gate failed; no b turn observed
Manifest: `experiments/manifests/EXP-025-period5-pseudo-arclength.json`
Claim target: failed EXP-024 `+1` refinement and P1-005

## Purpose and method

Trace the fixed-`(a,c)=(0.245,5.1)` period-5 flow orbit through the region where
natural `b` continuation and scalar `+1` bisection switched branches. The
extended unknown is `(x0,T,b)`. Three closure equations, one phase condition,
and one secant pseudo-arclength condition form a five-equation corrector.

The exact Jacobian integrates both the state-transition matrix and parameter
sensitivity `d x / d b`, whose forcing is `(0,0,1)` for the Rössler vector
field. EXP-023 points at `b=0.265` and `0.270` seed the oriented secant. Sixty
steps use the preceding secant length, with a guard range `b in [0.20,0.35]`.

The execution gate requires at least 20 corrected points and maximum closure
`<=1e-8`. A reversal of the `b` component is evidence that pseudo-arclength
passed a fold that natural continuation cannot parameterize uniquely.

## Limits

This experiment traces one orbit branch and recomputes Floquet multipliers. It
does not impose a coupled `+1` eigencondition, prove genericity, or continue the
fold surface in `(a,b,c)`. Any turning point remains a numerical fold candidate
until a dedicated boundary solve is performed.

## Result

The clean run at commit `8cb6fb5` failed the frozen minimum-point gate: the
full-space secant step reached the upper `b` guard after 11 points rather than
the required 20. All nine corrected predictions succeeded, and maximum closure
was `2.73e-11`, but no `b`-direction reversal occurred.

The traced branch is smooth and informative. Its significant real multiplier
rises from `0.8094` at the `b=0.270` seed to `1.3025` at `b=0.27567`, then to
`8.537` by `b=0.35069`. Thus this branch crosses `+1` without turning in `b`.
The scalar EXP-024 solve switched between orbit branches; its rejected
`b=0.27809` center is not a saddle-node on this traced branch.

The receipt SHA-256 is
`6fcf27036a371987e23a2b189e7ce3e782eb0f1033ab39e9bbab8d50257352e1`.

## Decision

Reject the fold interpretation for the pseudo-arclength branch observed here.
Retain “+1 branch interaction/stability crossing” until the intersecting orbit
branch is identified and a coupled eigencondition is solved. EXP-026 freezes a
constant quarter-size arclength step so the crossing is densely resolved and
the no-turn result is tested over a controlled local window.

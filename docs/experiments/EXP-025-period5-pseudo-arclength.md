# EXP-025 — Fold-safe period-5 pseudo-arclength continuation

Status: preregistered; pending clean local execution
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

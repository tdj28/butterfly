# EXP-019 — Period-12/period-3 basin uncertainty exponent

Status: preregistered; implementation pending frozen GPU execution
Manifest: `experiments/manifests/EXP-019-basin-uncertainty.json`
Claim target: CLM-019

## Hypothesis

The visually mixed period-12/period-3 basin section in EXP-017 has a
scale-dependent uncertain fraction. If
`f(epsilon) proportional to epsilon^alpha`, a smooth boundary in the declared
two-dimensional plane is compatible with `alpha` near 1, a fractal boundary
with `0 < alpha < 1`, and riddled-like uncertainty with `alpha` near 0.

This experiment measures `alpha`; it does not presuppose any of those labels.

## Frozen method

At `(a,b,c)=(0.245,0.2,5.75)`, sample deterministic pairs in
`(x,y,z) in [-10,10] x [-10,10] x {0}`. Pair endpoints are separated by exactly
epsilon along a uniformly sampled direction, with centers restricted so both
endpoints remain inside the plane. Seven dyadic scales from 2 through 0.03125,
4,096 pairs per scale, and two independent seeds yield 8,192 pairs per scale.

The EXP-018-qualified Float64 GPU path uses RK4 at `dt=0.005`, cubic-Hermite
Poincare event localization, transient 4,800, observation horizon 1,600, and
the unchanged `1e-6` recurrence classifier. A pair is resolved only when both
endpoints classify as period 3 or period 12. It is uncertain only when those
two resolved periods differ.

The log-log slope uses a declared Jeffreys half-count so zero observed
uncertain pairs do not cause post-hoc scale deletion. A deterministic 5,000-
sample binomial bootstrap reports the 95% pair-sampling interval. The execution
gate requires at least 98% resolved pairs at every scale.

## Interpretation limits

A passing execution gate makes the exponent reportable, not final. A fractal
or riddled claim additionally requires stability under added smaller scales,
sampling regions, direction rules, random seeds, integration horizons, and an
independent CPU subset. The bootstrap interval covers pair sampling only and
does not represent those systematic uncertainties.

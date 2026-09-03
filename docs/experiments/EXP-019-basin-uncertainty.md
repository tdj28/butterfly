# EXP-019 — Period-12/period-3 basin uncertainty exponent

Status: executed; resolution gate passed; smaller-scale confirmation required
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

## Result

The frozen L4 run at commit
`dda142644ac1eef659726840545f829395dfd86e` completed 114,688 trajectories in
130.85 seconds. Every one of the 57,344 pairs resolved into period 3 or period
12, so the 98% execution gate passed at all seven scales. The retrieved receipt
SHA-256 matched the remote value:
`0ece074434092be87e40010852b9e69eb66b46e2ec2f503bc67699c2124bb0b9`.
The host was terminated and the account pod list verified empty.

The uncertain fractions from largest to smallest epsilon were `0.4484`,
`0.4534`, `0.4597`, `0.3983`, `0.3175`, `0.2399`, and `0.1846`. The
preregistered fit over all seven scales gives `alpha=0.2218`, pair-bootstrap
95% interval `[0.2126,0.2315]`, but only `R^2=0.8545`. The poor fit matters:
the first three scales are in a saturation plateau and a single power law does
not describe the complete declared range.

A disclosed post-result sensitivity calculation over the four smallest scales
gives `alpha=0.3733`, interval `[0.3499,0.3980]`, and `R^2=0.9983`, implying a
slice-boundary dimension estimate near `1.6267`. This is strong evidence against
a smooth boundary in the sampled scale window and is not compatible with
calling the observed plane merely a coarse smooth separator. It is not yet a
final fractal-dimension estimate because that four-scale window was identified
after seeing the saturation pattern.

## Decision

Retain “fractal basin-boundary candidate” as the supported description. Freeze
smaller scales prospectively and require exponent stability, an independent
CPU subset, added seeds/regions, and horizon sensitivity before promoting the
result to a quantitative fractal-boundary claim. The positive small-scale slope
does not support a riddled-basin label at current resolution.

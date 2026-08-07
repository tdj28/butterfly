# EXP-039 — Separated-point normal-form qualification at c=4.9

Status: preregistered; pending clean local execution
Manifest: `experiments/manifests/EXP-039-separated-normal-form.json`
Claim target: persistence of EXP-031's pitchfork-like mechanism on EXP-038

## Hypothesis and method

At the prospectively selected surface point
`(a,b*,c)=(0.245,0.2975539193,4.9)`, the nontrivial-unit event has the same
supercritical pitchfork-like quotient normal form found at `c=5.1`.

Correct the primary periodic family at fixed `b` on both sides of the event,
construct the two-dimensional null space of the extended shooting Jacobian,
and switch along the null direction orthogonal to the observed primary tangent.
Continue both coordinate signs for 24 pseudo-arclength steps. At five frozen
positive `b-b*` offsets, independently correct primary and secondary cycles,
compare full trajectories modulo phase, compute Floquet stability, and fit the
branch-separation power law.

## Acceptance and limits

Each switched direction must supply at least twelve points. At the largest
offset, the two switched representations must match below phase-aligned RMS
`1e-5`, while primary-secondary RMS must exceed `1e-2`. All closures must be
below `1e-8`; primary must be unstable and secondary stable at every offset.
The separation exponent must lie in `[0.4,0.6]` with `R^2 >= 0.98`, and the
median multiplier-deviation ratio must lie in `[1.5,2.5]`.

Passing shows that the pitchfork-like mechanism persists at a separated point
on the local event surface. It does not establish uniformity across the whole
surface, identify an exact symmetry, or replace validated local reduction.

# EXP-039 — Separated-point normal-form qualification at c=4.9

Status: executed; passed
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

## Result

The clean run at commit `d1fbb62de3f2005534750908d68f875b6aed1123`
passed all gates. Both switched directions produced all 24 requested points.
At the largest frozen offset, the two coordinate representations align to
phase-invariant RMS `2.27e-7`. Stability exchange holds at all five offsets;
maximum corrected closure is `9.89e-14`.

The branch-separation exponent is `0.49867276` with
`R^2=0.99999893`. The multiplier-deviation ratio has median `1.98510` and range
`[1.94074,1.99627]`, approaching two toward the event. The complete receipt
SHA-256 is
`f47e364131dd5b977b6bfdfa3e5218ce490d135fa42f0fc493cff9ef45746560`.

The comparison with EXP-031 is
`artifacts/EXP-039/EXP-031-039-normal-form-comparison.png` (SHA-256
`d1cd5f32e3ebbf279c058ca89e3224f1ccf9cda165bfc14a2160e3beaf684c24`).

## Decision

Accept that the supercritical pitchfork-like quotient normal form persists at
two separated points of the event surface, `c=5.1` and `c=4.9`, at fixed
`a=0.245`. The near-identical exponents and multiplier ratios make an isolated
degeneracy explanation implausible.

This remains a numerical local-normal-form classification, not an exact
symmetry theorem. Surface-wide uniformity, changes near folds, and independent
validated calculations remain open.

# EXP-158 — Primitive stable period-2 child qualification

Status: passed independent identity, stability, primitivity, and attraction gates

## Question

At a common post-flip value `c=3.1845`, are the two EXP-157 switch signs one
primitive stable period-2 orbit, paired with an unstable period-1 parent?

## Frozen method

The parent and both child signs are corrected at fixed
`(a,b,c)=(0.1798,0.2,3.1845)` with DOP853. Radau then independently corrects
all three orbits and recomputes their monodromies. The gates require
phase-invariant child-arm identity, DOP853/Radau whole-orbit and Floquet
agreement, failure of half-period closure, period ratio two, winding two,
unstable parent, stable child, and recovery of the child after perturbed
forward integration.

## Result

All gates pass. Independent Radau gives parent multiplier `-1.0021368076` and
child multiplier `0.9914596621`. The switch signs agree up to phase with RMS
`7.82e-8` and phase shift `0.4973857540`. Their half-period closure errors are
`0.1927184` and `0.1931768`; period ratios are `1.9999363266`; and windings are
two to `1.2e-14`. DOP853/Radau orbit RMS differences are below `3.55e-13`, and
multiplier-modulus differences are below `1.60e-12`. Perturbed Radau
integration recovers the child with phase-invariant RMS `3.38e-10`.

## Implication for Jones

The first local logistic-like step on this explicit Hopf-to-hub path is now a
complete flow-bifurcation result: a qualified period-1 flip opens a primitive
attracting period-2 child on the post-flip side. This supports the first rung
of Jones's finite ordering mechanism. It does not yet establish the next flip,
periods through seven, the exact historical `L1`/`L2`, a logistic conjugacy,
or the homoclinic endpoint.

Tracked receipt: `docs/experiments/receipts/EXP-158.json`.

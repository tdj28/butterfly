# FND-042 — The first stable period-2 child is qualified

Status: passed EXP-157 and EXP-158

## Finding

The exact period-1 flip at `c=3.1807265333384103` on the fixed
`(a,b)=(0.1798,0.2)` Hopf-to-hub path opens a primitive stable period-2 child
on the post-flip side.

At `c=3.1845`, independent Radau correction gives an unstable period-1 parent
with multiplier `-1.0021368076` and a stable period-2 child with dominant
multiplier `0.9914596621`. The two transverse switch signs are one orbit up to
a near-half-cycle phase shift. Half-period closure fails by about `0.193`, the
period ratio is `1.9999363`, and the orbit winds twice. Perturbed integration
recovers the child.

## Implication for Jones

This is strong good news for the local part of Jones's argument. The first
claimed logistic-like step is no longer inferred from a raster or a parent
multiplier alone: it is an identity-safe, independently integrated
parent-to-child stability exchange in the flow.

The result does not yet validate finite ordering through period seven, the
exact historical paths, logistic conjugacy, or the proposed equilibrium
homoclinic endpoint. It supplies the first solid rung from which those tests
can proceed.

Tracked receipts: `docs/experiments/receipts/EXP-157.json` and
`docs/experiments/receipts/EXP-158.json`.

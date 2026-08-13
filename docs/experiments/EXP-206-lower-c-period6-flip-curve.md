# EXP-206 — Lower-c period-6 flip-curve continuation

Status: prospectively frozen before coupled continuation

## Question

Do EXP-205's seven scalar roots belong to one densely sampled, identity-safe
real-minus-one Floquet curve at fixed `b=0.2`?

## Frozen design

The source is EXP-205 event `flip-c7244`. The anti-periodic tangent, periodic
orbit, phase, normalization, and free `a` are solved together with the exact
Rössler first- and second-variational Jacobian. Forty-one fixed-`c` targets
cover `c in [7.16,7.32]` at spacing `0.004`, extending `0.032` beyond the
EXP-205 slice range on both sides. Upward and downward continuation use only
the immediately preceding accepted point.

Every target must solve inside `a in [0.21555,0.2159]`, preserve real-minus-one
and neutral Floquet residuals, retain exactly six historical and eight Barrio
section phases, and keep adjacent `a` motion below `1e-5`.

Manifest:
[`../../experiments/manifests/EXP-206-lower-c-period6-flip-curve.json`](../../experiments/manifests/EXP-206-lower-c-period6-flip-curve.json).

## Claim boundary

A pass establishes a dense sampled segment of one orbit-defined flip curve.
It does not prove global curve connectivity, locate its folds or endpoints,
qualify a period-12 child or supercriticality, identify the TBA curve, or
establish double-critical membership.

# EXP-208 — Independent qualification of three period-12 nominations

Status: prospectively frozen before independent correction

## Question

Are the three isolated stable orbits nominated by failed EXP-207 genuinely
primitive period-12 children paired with unstable period-6 parents?

## Frozen design

The exact three negative-direction coordinates observed in EXP-207 are declared
in the manifest, making this a pilot-informed follow-up rather than a blind
discovery experiment. At each fixed `(a,b,c)`, DOP853 separately corrects the
EXP-206 parent and EXP-207 child seeds. Radau then independently recorrects both
orbits and recomputes their monodromies.

All three targets must pass. Gates require DOP853/Radau phase-aligned identity,
period and multiplier agreement, an unstable parent, a stable child, child to
parent period ratio two, exact 6/8 parent and 12/16 child section counts, and
nonclosure at every temporal fraction associated with a proper divisor of the
historical period 12. Proper-subperiod closure must exceed both `1e-4` and
10,000 times the full-period closure.

Manifest:
[`../../experiments/manifests/EXP-208-qualify-period12-children.json`](../../experiments/manifests/EXP-208-qualify-period12-children.json).

## Claim boundary

A pass establishes three sampled primitive stable period-12 children with
local parent/child stability exchange. It does not repair EXP-207's failed
eight-point arm continuation or establish a continuous child curve,
supercritical normal-form scaling, attraction-basin size, the TBA curve, or a
doubly-superstable center.

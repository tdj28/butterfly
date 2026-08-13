# EXP-208 — Independent qualification of three period-12 nominations

Status: passed all independent correction, stability, identity, and primitivity gates

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

## Result

All three targets pass. Independent Radau gives unstable period-6 parent
multiplier moduli `1.20713`, `1.24791`, and `1.29062`, paired with stable
period-12 child moduli `0.149090`, `0.0235436`, and `0.206148`. Child/parent
period ratios are `1.9999320`, `1.9999274`, and `1.9999232`.

The largest correction closure is `5.30e-11`; largest DOP853/Radau
phase-aligned RMS is `6.29e-11`; largest multiplier-modulus difference is
`1.21e-9`; and largest relative period difference is `1.46e-13`. Every parent
retains 6 historical plus 8 Barrio phases and every child retains 12 plus 16.
All five proper-divisor fractions remain open at each target: the smallest
subperiod return distance is `0.09413`, at least `1.77e9` times its child's
full-period closure.

The three EXP-207 nominations are therefore qualified as sampled primitive
stable period-12 children. EXP-207's multi-point branch arms remain failed,
and supercritical normal-form scaling and basin attraction remain separate
tests.

Raw receipt: `artifacts/EXP-208/receipt.json`, 8,893 bytes, SHA-256
`dbe0bc6cfffdc39b7b2e7f7e1d967cbb2662871a388861d318f8ce781b0f7e69`.
Compact receipt:
[`receipts/EXP-208.json`](receipts/EXP-208.json).

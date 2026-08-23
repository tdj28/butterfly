# EXP-299 — Two-solver criticality audit of the seventh birth

Status: completed — failed at the frozen parent-classification gate

EXP-298 supplies two passed period-1536 sign representations at one coordinate.
EXP-299 prospectively selects the positive sign only because it has the larger
half-period closure within the frozen pair. Its preliminary multiplier is not a
selection gate.

DOP853 and Radau independently correct the 1,024-segment parent and
2,048-segment child at fixed `a=0.24070100823781396`. Both solvers must pass
matching, phase, cyclic node identity, multiplier-spread, child half-period
nonclosure, and exact `1792/2048` section identity gates. Consistent
parent-unstable/child-stable or parent-stable/child-unstable classifications
pass; an unresolved or mixed result fails.

A pass qualifies the sampled local birth as supercritical or subcritical. It
does not yet establish tangent-sign equivalence, basin measure, continued
period-1536 attraction, or an eighth event.

Manifest:
[`../../experiments/manifests/EXP-299-jones-period1536-qualified-criticality.json`](../../experiments/manifests/EXP-299-jones-period1536-qualified-criticality.json).

## Result

Both solvers independently correct the same parent and child, and every
nonclassification gate passes. DOP853/Radau classify the primitive
period-1536 child as stable with moduli `0.1241962801/0.1241916440`; their
relative spread is `3.73e-5`, far below the frozen `0.02` ceiling. Matching
residuals remain below `8.88e-11`, the cross-solver child nodes agree exactly
at the stored phases, half-period closures are `2.97e-6/3.17e-6`, and exact
`1792/2048` section identity passes.

The frozen experiment nevertheless fails because the period-768 parent is
still inside the `1e-4` neutral margin. DOP853/Radau give parent moduli
`0.9999914901/1.0000216735`; their relative spread is only `3.02e-5`, but
neither value is far enough from one to establish the parent side. The common
sample is only `1.079e-12` above the finite 8,192-step event coordinate.

This is strong evidence for a stable period-1536 daughter on the sampled side,
and hence is consistent with a supercritical seventh birth, but it is not a
criticality qualification. The next admissible step is exact sparse
continuation of this qualified child away from the neutral frontier, followed
by a separately frozen two-solver parent/child audit at the terminal row.

Raw receipt: `artifacts/EXP-299/receipt.json`, 388,925 bytes, SHA-256
`0cf411d935ff4bd8fcedc70a55d0ea574aa5c1bac9a877885612394c8c209988`.
Compact receipt:
[`receipts/EXP-299.json`](receipts/EXP-299.json).

## High-precision supersession

EXP-324 replays the exact stored DOP853 child seed under the 50-digit,
4,096-step RK4 3/8 map and converges below `1.20e-23`. Its half-node amplitude
collapses to `7.38e-20`, identifying the solution as the doubled period-768
parent. The stable primitive-child interpretation above is therefore retained
as the honest historical EXP-299 result but is not admissible as exact-orbit
evidence. EXP-325 freezes a resolution-doubled replay.

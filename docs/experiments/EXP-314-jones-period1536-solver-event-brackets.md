# EXP-314 — Solver-specific brackets for event eight

Status: completed — passed both solver-specific brackets

EXP-310 and EXP-313 independently correct the same period-1536 parent under
DOP853 and Radau at two fixed coordinates. The near coordinate lies on
opposite sides of real `-1` for the two solvers, while the farther coordinate
is on the unstable side for both. Linear interpolation/extrapolation of the
already frozen signed residuals predicts solver events at
`a=0.24070100822439391` (DOP853) and `a=0.24070100822420018` (Radau).

EXP-314 replays those estimates exactly and makes one new parent-only
2,048-segment evaluation per solver, displaced outward by `5e-13` from the
prediction. Each new endpoint must reverse the corresponding EXP-310 sign by
at least `1e-4`; correction, matching, phase, direct closure, neutral mode,
and block-Floquet gates remain fixed. Both solver-specific brackets must be at
most `7e-13` wide.

A pass establishes bounded solver-specific parent-event coordinates and
quantifies why the shared EXP-310 coordinate was neutral. It does not classify
the period-3072 birth. A successor must refine these brackets and construct a
child on a parent-stability side shared by both representations.

Manifest:
[`../../experiments/manifests/EXP-314-jones-period1536-solver-event-brackets.json`](../../experiments/manifests/EXP-314-jones-period1536-solver-event-brackets.json).

## Result

Both parent-only evaluations pass. DOP853 changes signed multiplier residual
from `-3.87536e-5` at the shared EXP-310 coordinate to `+3.27617e-4` at
`a=0.2407010082248939`, producing a `5.9544e-13` bracket. Radau changes from
`+4.24603e-5` at the shared coordinate to `-2.16818e-4` at
`a=0.2407010082237002`, producing a `5.9827e-13` bracket. Both outward
residuals exceed the frozen `1e-4` floor.

The new DOP853/Radau matching residuals are `8.30e-11/1.86e-11`; direct
closures are `1.17e-6/7.52e-8`; neutral errors are `2.02e-5/1.01e-6`.
Every gate passes. The brackets meet at the common EXP-310 coordinate but lie
on opposite sides of it. This directly explains the prior neutral-margin
split as solver-representation event uncertainty, not physical
multistability.

Raw receipt: `artifacts/EXP-314/receipt.json`, 258,632 bytes, SHA-256
`29b3155f3cfd650afe220f0e2babefaf74250353eae7e60ee20d78de17d6fb6b`.
Compact receipt: [`receipts/EXP-314.json`](receipts/EXP-314.json).

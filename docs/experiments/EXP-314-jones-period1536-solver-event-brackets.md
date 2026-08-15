# EXP-314 — Solver-specific brackets for event eight

Status: frozen; not yet executed

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

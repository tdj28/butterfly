# EXP-034 — Resolved expanded period-5 unit-event curve

Status: preregistered; pending clean local execution
Manifest: `experiments/manifests/EXP-034-resolved-period5-unit-event-a-curve.json`
Claim target: fixed-`c` extent of the EXP-028 pitchfork-like event curve

## Hypothesis and method

The event curve continues across `a in [0.225,0.265]` when the natural
continuation step is kept at the EXP-032-qualified `0.0025`. Solve all seventeen
frozen points independently upward/downward from EXP-028. EXP-033's failed and
valid rows alike are excluded from the numerical input.

## Acceptance and limits

All seventeen points must lie inside `b in [0.15,0.4]`; closure, nontrivial
eigen, and flow-orthogonality residuals must be at most `1e-8`; and the maximum
adjacent `b` jump must not exceed `0.015`.

Passing establishes a resolved local event curve at `c=5.1` across the declared
bounded domain. It does not certify the curve, show that pitchfork scaling
persists at its endpoints, or construct the full surface as `c` varies.

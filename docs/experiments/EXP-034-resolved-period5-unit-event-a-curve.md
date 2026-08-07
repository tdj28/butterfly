# EXP-034 — Resolved expanded period-5 unit-event curve

Status: executed; upward curve resolved; all-point gate failed
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

## Result

The exact frozen command was invoked twice because the first process returned
control before its receipt became visible; both runs showed the same scientific
outcome. The final receipt is bound to clean commit
`d3cb2d92a7033fffa6e3a31217fe9eeee757a30c` and has SHA-256
`e3a885710e71ede1e52fe1bcb090b08fd843eab9d189a696ca8c19e6eaa688cf`.

Thirteen coupled events pass from `a=0.235`, `b=0.23841498` through the EXP-028
source to `a=0.265`, `b=0.34787537`. Their closure and eigen residuals are at
approximately `1e-12` and flow-orthogonality residuals at approximately
`1e-18`. The upward direction completed.

The next downward target at `a=0.2325` converged to a rejected output at
`b=0.305656`, with closure `0.287` and eigen residual `0.105`. Consequently,
the frozen seventeen-point all-or-nothing gate failed and no points below
`a=0.235` were attempted. The figure
`artifacts/EXP-034/EXP-034-period5-unit-event-curve.png` visibly separates the
thirteen accepted events from the rejected corrector output (SHA-256
`606a18b49220b48736ed187afd33d5d310416236acee2a8ab9cfc0ad95544067`).

## Decision

Accept a resolved local coupled-event curve only on the bounded interval
`a in [0.235,0.265]` at `c=5.1`. Preserve EXP-034's formal failure because it
did not cover the declared wider interval. The failure at `a=0.2325` is a
natural-continuation boundary, not evidence that the mathematical curve ends;
the next algorithmic step is pseudo-arclength continuation of the full event
system in `(a,b)` and then extension in `c` to construct a surface.

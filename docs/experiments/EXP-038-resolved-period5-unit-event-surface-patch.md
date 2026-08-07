# EXP-038 — Resolved period-5 unit-event surface patch

Status: preregistered; pending clean local execution
Manifest: `experiments/manifests/EXP-038-resolved-period5-unit-event-surface-patch.json`
Claim target: resolution qualification of the EXP-037 surface domain

## Hypothesis and method

The complete local event surface graph over
`a in [0.24,0.25]`, `c in [4.9,5.3]` can be followed with natural `a`
continuation when its step is reduced from `0.0025` to `0.00125`. Freeze nine
`a` values and the same five `c` slices, for 45 coupled event solves. Each slice
restarts from its accepted EXP-036 center; no EXP-037 output is used.

## Acceptance and limits

All 45 events are required inside `b in [0.15,0.4]`. Closure, eigen, and flow-
orthogonality residuals must remain below `1e-8`, and no grid-adjacent `b` jump
may exceed `0.015`.

Passing establishes a resolution-qualified local graph patch, not a global
fold-safe surface. Normal-form persistence, topology/TBA alignment, and surface
continuation beyond this patch remain open.

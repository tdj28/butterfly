# EXP-038 — Resolved period-5 unit-event surface patch

> **Identity correction after EXP-047.** This patch belongs to the
> period-3-to-period-6 flip surface. The historical title preserves chronology;
> all 45 corrected event points remain valid.

Status: executed; passed
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

## Result

The clean run at commit `d5afb122d552f0d180492459af19384f5a44d53d`
passed all 45 coupled events and all five slices. Maximum closure was
`3.81e-12`, maximum eigen residual `2.28e-12`, maximum flow-orthogonality
residual `1.49e-18`, and maximum grid-adjacent `b` jump `0.014485`, inside the
frozen `0.015` gate. The corrected event parameter spans
`b in [0.23239055,0.31531872]`.

The complete receipt SHA-256 is
`a7b28b07943ef746d8907b0e7f9259b56bee676b5571580e4b1b302f6ff7a3be`.
The surface/contour figure is
`artifacts/EXP-038/EXP-038-period5-unit-event-surface.png` (SHA-256
`848c78e2510ff5a302c499baf59f881c4dcb12bb2da2f431fbc7faa7e1c2d062`).

A disclosed post-result quadratic description centered at `(a,c)=(0.245,5.1)`
is

`b* = 0.2722057 + 3.49329 da - 0.120652 dc + 19.2871 da^2 + 0.14935 da dc + 0.03298 dc^2`,

with `R^2=0.999818` and maximum grid residual `8.85e-4`. This fit is a compact
description of the measured patch, not continuation evidence outside it.

## Decision

Accept the first resolution-qualified local surface patch of the coupled
period-5 `+1` event. The surface is steepest in `a` and decreases with `c` near
the source. This converts the earlier qualitative “hub moves with parameters”
picture into one explicit, orbit-defined bifurcation surface component.

Do not identify the whole surface as pitchfork-like from EXP-031 alone. The
next decisive qualification is branch identity and normal-form scaling at
spatially separated surface points, followed by fold-safe surface continuation
beyond the local graph patch.

# EXP-037 — First period-5 unit-event surface patch

Status: executed; failed
Manifest: `experiments/manifests/EXP-037-period5-unit-event-surface-patch.json`
Claim target: local 2-D surface extension of EXP-035 and EXP-036

## Hypothesis and method

The coupled period-5 nontrivial-unit event forms a smooth graph `b*(a,c)` in a
local neighborhood of the EXP-028 source. Freeze a `5 x 5` grid over
`a in [0.24,0.25]` and `c in [4.9,5.3]`. At each `c`, take the accepted EXP-036
spine point at `a=0.245` as the sole center seed, then continue independently in
both `a` directions at the EXP-032-qualified step `0.0025`.

## Acceptance and limits

All 25 coupled events must pass inside `b in [0.15,0.4]`. Closure, eigen, and
flow-orthogonality residuals must remain below `1e-8`, and no grid-adjacent
event parameter may jump by more than `0.02`.

Passing establishes the first measured local surface patch. The patch is small,
not fold-safe at its boundary, and does not demonstrate a uniform pitchfork
normal form, connect to TBA, or explain every periodic window in the atlas.

## Result and decision

The clean run at commit `e6d6ed390b175dc8e6464f5b593dc4d6d2d4580e`
failed its all-point gate. Four complete slices (`c=5.0,5.1,5.2,5.3`) solved
all five events with approximately `1e-12` residuals. At `c=4.9`, the center
and both upper-`a` points passed, but the first downward target `a=0.2425`
terminated at a rejected high-residual output (`closure=0.219`, eigen residual
`0.0665`, `b=0.36042`), so `a=0.24` was not attempted.

The receipt therefore contains 23 accepted events, one rejected output, and 24
rows total; it is not a passing `5 x 5` patch. Its SHA-256 is
`f992bfc959dcf4825b86c9b2c563078e87d4f321ec94f6b398f465b9f07c1e33`.

The failure is consistent with a slice-resolution limit, not disappearance of
the surface: the source center and upper direction remain valid at `c=4.9`.
EXP-038 retains the exact `(a,c)` domain but halves the natural `a` step to
`0.00125`, requiring all 45 denser grid events. No EXP-037 row is used as a
seed; every slice restarts from EXP-036.

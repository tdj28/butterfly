# EXP-037 — First period-5 unit-event surface patch

Status: preregistered; pending clean local execution
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

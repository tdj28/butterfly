# EXP-266 — Precision audit of the period-192 flip

Status: completed — failed unchanged flip gate

EXP-265 fails only because its DOP853 cyclic direct-product median differs
from `-1` by `1.06496e-7`, just `6.50e-9` beyond the frozen gate, even though
the coupled orbit and anti-periodic tangent residuals are orders of magnitude
smaller and every independent Radau gate passes.

EXP-266 preserves the immutable solved nodes, tangent nodes, period, and
parameter. It re-evaluates the same 256-segment equations and four cyclic
products with maximum step `0.01` under tighter DOP853 and Radau profiles. The
`1e-7` multiplier gate is unchanged, and both solvers must additionally agree
within `1e-7`. Source-failure isolation, residual, realness, cyclic, primitive,
and exact `224/256` gates are mandatory.

A pass qualifies only the event representation for a separately frozen
period-384 switch.

Manifest:
[`../../experiments/manifests/EXP-266-period192-flip-precision-audit.json`](../../experiments/manifests/EXP-266-period192-flip-precision-audit.json).

## Result

Failure remains isolated to the unchanged direct-product flip gate. Tighter
DOP853/Radau give medians `-1.00000022550/-1.00000015845`; their difference
passes the new `1e-7` cross-solver gate, but their respective residuals
`2.25e-7/1.58e-7` both exceed `1e-7`. Residual, realness, cyclic, primitive,
and exact identity gates pass.

This rules out promoting the immutable EXP-265 variables on integration
precision alone. EXP-267 freezes a new coupled correction under the tighter
profiles and strengthens the Radau flip threshold to the same `1e-7` value.

Raw receipt: `artifacts/EXP-266/receipt.json`, 7,572 bytes, SHA-256
`df5fec60a9b49e3bac3962bc5b418c4a8e5f13fadaa3fc8073e3d32b3a11b6a0`.

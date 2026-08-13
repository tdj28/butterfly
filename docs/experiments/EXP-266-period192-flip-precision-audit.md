# EXP-266 — Precision audit of the period-192 flip

Status: frozen — not yet executed

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

# EXP-282 — Precision audit of the period-768 flip

Status: frozen — not yet executed

EXP-281 fails only its independent Radau flip gate: residual `3.22e-7` versus
the unchanged `1e-7` threshold. Its reference event solve, every other Radau
residual, cyclic products, primitivity, and exact section identity pass.

EXP-282 preserves the immutable 1,024 nodes, tangent nodes, period, and `a`.
It re-evaluates that representation with DOP853 and Radau at `rtol=1e-12`,
`atol=1e-14`, and maximum step `0.005`. Both flip residuals and their
cross-solver difference must pass `1e-7`; no threshold is relaxed.

A pass qualifies the seventh exact event representation only. A failure
requires a separately frozen tighter coupled correction before any period-1536
switch is attempted.

Manifest:
[`../../experiments/manifests/EXP-282-period768-flip-precision-audit.json`](../../experiments/manifests/EXP-282-period768-flip-precision-audit.json).

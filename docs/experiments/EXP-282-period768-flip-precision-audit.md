# EXP-282 — Precision audit of the period-768 flip

Status: completed — failed multiplier and cross-solver gates

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

## Result

The immutable tighter-step audit preserves small orbit/tangent residuals under
DOP853 (`8.61e-11/2.33e-12`) and Radau (`8.63e-11/5.77e-12`), real spectra,
cyclic spreads below `4.34e-10`, primitivity, and exact `896/1024` identity.

DOP853 gives multiplier `-0.99999999629`, but Radau gives
`-1.00000036358`. The Radau flip residual (`3.64e-7`) and cross-solver
difference (`3.67e-7`) both fail the unchanged `1e-7` gates. Tighter
integration therefore does not resolve the EXP-281 discrepancy, and the
seventh event remains unqualified.

EXP-283 freezes a deterministic Float64 resolution diagnostic before any new
coupled correction. It tests whether the solver gap and the multiplier change
estimated per representable `a` increment already exceed the event tolerance.

Raw receipt: `artifacts/EXP-282/receipt.json`, 7,550 bytes, SHA-256
`41e409957e70b7069434d845cc9cd7135a3fc7523c62f4f1b5dfe734d940c4e1`.
Compact receipt:
[`receipts/EXP-282.json`](receipts/EXP-282.json).

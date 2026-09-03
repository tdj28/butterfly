# EXP-284 — Decimal segment pilot for the period-768 event

Status: completed — passed

EXP-283 diagnoses a Float64 resolution frontier. EXP-284 tests a dependency-free
50-decimal-digit path before scaling it to all 1,024 segments. Four
phase-separated EXP-281 nodes are integrated with the Rössler state and `3x3`
variational transition using exactly nested 1,024, 2,048, and 4,096-step RK4
profiles per segment.

The pilot requires at least sixfold endpoint and transition error reduction
under each doubling, fine/medium differences below `1e-7`, and fine-grid orbit
and tangent matching below `1e-7/1e-6`. These are feasibility gates, not event
qualification gates.

A pass permits a separately frozen full 1,024-segment high-precision
multiplier audit. It does not qualify the seventh event.

Manifest:
[`../../experiments/manifests/EXP-284-period768-decimal-segment-pilot.json`](../../experiments/manifests/EXP-284-period768-decimal-segment-pilot.json).

## Result

All six feasibility gates pass in 0.87 seconds. Across the four
phase-separated segments, endpoint convergence ratios lie in
`[15.8642270,15.8642285]` and transition ratios in
`[15.7262194,15.7262199]`, closely matching fourth-order convergence.

The largest fine/medium endpoint and transition differences are
`8.53e-9/7.02e-9`. Fine-grid orbit matching is below `5.72e-10`, and tangent
matching is below `3.61e-10`. EXP-285 therefore freezes the full parallel
1,024-segment 50-digit multiplier audit at nested 4,096/8,192-step profiles.

Raw receipt: `artifacts/EXP-284/receipt.json`, 2,903 bytes, SHA-256
`df5bb5ddaa893fad4cfb9a9a1a209d0e5f6349f88c1f769bcd153a245a04bed2`.
Compact receipt:
[`receipts/EXP-284.json`](receipts/EXP-284.json).

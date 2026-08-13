# EXP-284 — Decimal segment pilot for the period-768 event

Status: frozen — not yet executed

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

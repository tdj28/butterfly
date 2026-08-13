# EXP-246 — Near-event period-24/48 stability qualification

Status: completed — passed

EXP-245 nominates primitive period-48 candidates on both mode signs. EXP-246
selects the negative-mode `0.002` candidate, only `2.04e-10` below the exact
period-24 event, and independently corrects its period-24 parent and period-48
child with 32/64-segment DOP853 and Radau systems.

The prospective expectation is again supercritical: parent unstable and child
stable under both solvers outside a `1e-4` neutral margin. Solver-node,
multiplier, half-period nonclosure, and exact `56/64` identity gates remain
mandatory. Attraction and sign equivalence remain separate questions.

Manifest:
[`../../experiments/manifests/EXP-246-jones-period48-near-event-qualification.json`](../../experiments/manifests/EXP-246-jones-period48-near-event-qualification.json).

## Result

Both solvers recover an unstable period-24 parent and stable primitive
period-48 child at `a=0.24070104590857766`. DOP853/Radau parent multipliers are
`-1.00318393/-1.00318197`; child multipliers are
`+0.98725839/+0.98725835`. The child retains `56/64` section identity and
half-period closure near `0.00049213`.

This passes the prospectively declared local supercriticality classification
and qualifies the exact returning-arm cascade through stable period 48.
EXP-247 freezes a short segmented child continuation toward its next event.

Raw receipt: `artifacts/EXP-246/receipt.json`, 23,273 bytes, SHA-256
`eaccf68656f8aa856299c934a0a41c61ea28a4ae3d9ac7eea1c81fc20067dc52`.
Compact receipt:
[`receipts/EXP-246.json`](receipts/EXP-246.json).

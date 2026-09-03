# EXP-241 — Near-event period-12/24 stability qualification

Status: completed — passed

EXP-240 proves that the separated period-24 endpoint is strongly unstable, but
that does not classify the flip at birth. EXP-241 returns to EXP-238's frozen
negative-mode child at predictor length `0.002`, only `3.22e-10` below the
exact event in `a`, and independently corrects its period-12 parent and
period-24 child with 16/32-segment DOP853 and Radau systems.

The prospectively declared expectation is supercritical: parent unstable and
child stable under both solvers, outside a `1e-4` neutral margin. Solver-node,
multiplier, primitivity, and `28/32` identity gates remain mandatory. A pass
classifies the sampled birth; it does not explain the later child instability,
which would motivate a separate period-24-to-48 event search.

Manifest:
[`../../experiments/manifests/EXP-241-jones-period24-near-event-qualification.json`](../../experiments/manifests/EXP-241-jones-period24-near-event-qualification.json).

## Result

Both solvers recover an unstable period-12 parent and stable primitive
period-24 child at `a=0.2407011811534778`. DOP853/Radau parent multipliers are
`-1.0011251882/-1.0011247427`; child multipliers are
`+0.9954981525/+0.9954981722`. Solver node RMS is `1.35e-9` for the parent and
zero at the stored child nodes. The child retains `28/32` identity and
half-period closure near `0.00050183`.

This passes the prospectively declared local supercriticality classification.
Together with EXP-240's strongly unstable separated child, it brackets at
least one later loss of period-24 stability. EXP-242 freezes a complete
multiplier track along the 21 exact EXP-239 rows.

Raw receipt: `artifacts/EXP-241/receipt.json`, 17,602 bytes, SHA-256
`5ff13b1b705e15bf1dd68dbd78e788e863aab1981a7c8580b9945bec32f2aee6`.
Compact receipt:
[`receipts/EXP-241.json`](receipts/EXP-241.json).

# EXP-253 — Near-event period-48/96 stability qualification

Status: completed — passed

EXP-253 selects EXP-252's negative-mode `0.002` candidate, only `4.04e-10`
below the qualified period-48 event, and independently corrects the parent and
child with 64/128-segment DOP853 and Radau systems. Use of the failed-status
EXP-250 event is conditional on the hash-bound passing EXP-251 audit.

The prospective expectation is supercritical: parent unstable and primitive
child stable under both solvers outside a `1e-4` margin. Solver-node,
multiplier, half-period nonclosure, and exact `112/128` identity gates are
mandatory. Basin measure and tangent-sign equivalence remain separate.

Manifest:
[`../../experiments/manifests/EXP-253-jones-period96-near-event-qualification.json`](../../experiments/manifests/EXP-253-jones-period96-near-event-qualification.json).

## Result

Both solvers recover an unstable period-48 parent and stable primitive
period-96 child at `a=0.2407010160045328`. DOP853/Radau parent moduli are
`1.02642736/1.02641856`; child moduli are
`0.89393093/0.89393104`. Their relative child-multiplier spread is
`1.23e-7`, the child retains exact `112/128` section identity, and the two
independent half-period closures are `5.08785e-5/5.08722e-5`.

This passes the prospectively declared local supercriticality classification
and qualifies the returning-arm cascade through stable period 96. Basin
measure, tangent-sign equivalence, the next event, and any universality claim
remain separate tests.

Raw receipt: `artifacts/EXP-253/receipt.json`, 35,444 bytes, SHA-256
`6d084dea91779dd49e9ceb92918915ca278543db37de7c8130c076321ca8be7f`.
Compact receipt:
[`receipts/EXP-253.json`](receipts/EXP-253.json).

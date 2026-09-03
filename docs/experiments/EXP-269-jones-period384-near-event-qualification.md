# EXP-269 — Near-event period-192/384 stability qualification

Status: completed — passed

EXP-269 selects EXP-268's negative-mode `0.001` candidate, only `1.13e-10`
below the exact period-192 event, and independently corrects the period-192
parent and period-384 child with 256/512-segment DOP853 and Radau systems.

The prospective expectation is supercritical: parent unstable and primitive
child stable under both solvers outside a `1e-4` margin. Solver-node,
multiplier, half-period nonclosure, and exact `448/512` identity gates are
mandatory. Basin measure and tangent-sign equivalence remain separate.

Manifest:
[`../../experiments/manifests/EXP-269-jones-period384-near-event-qualification.json`](../../experiments/manifests/EXP-269-jones-period384-near-event-qualification.json).

## Result

At `a=0.24070100850046297`, both independent corrections recover an unstable
period-192 parent and a stable primitive period-384 child. DOP853/Radau parent
moduli are `1.14929836/1.14909171`; child moduli are
`0.39117576/0.39117648`. Their relative child-multiplier spread is `1.83e-6`,
and the child half-period closures are `5.63374e-5/5.64099e-5`.

All matching, phase, solver-node, cyclic-spectrum, stability-margin,
primitivity, and exact `448/512` section-identity gates pass. EXP-269 therefore
qualifies a fifth local supercritical doubling and extends the finite
returning-arm cascade through stable period 384. It does not establish basin
measure, tangent-sign equivalence, another event, a limiting scaling law,
paired shrimp boundaries, TBA membership, double-criticality, or a whole-plane
explanation.

Raw receipt: `artifacts/EXP-269/receipt.json`, 105,963 bytes, SHA-256
`3136e119680f9b0e4e6f7a6a42f5eba7c89b5ff7a8c1e2b2ae22930a8e15ce65`.
Compact receipt:
[`receipts/EXP-269.json`](receipts/EXP-269.json).

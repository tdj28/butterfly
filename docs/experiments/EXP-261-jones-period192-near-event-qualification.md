# EXP-261 — Near-event period-96/192 stability qualification

Status: completed — passed

EXP-261 selects EXP-260's negative-mode `0.002` candidate, only `5.08e-10`
below the exact period-96 event, and independently corrects the period-96
parent and period-192 child with 128/256-segment DOP853 and Radau systems.

The prospective expectation is supercritical: parent unstable and primitive
child stable under both solvers outside a `1e-4` margin. Solver-node,
multiplier, half-period nonclosure, and exact `224/256` identity gates are
mandatory. Basin measure and tangent-sign equivalence remain separate.

Manifest:
[`../../experiments/manifests/EXP-261-jones-period192-near-event-qualification.json`](../../experiments/manifests/EXP-261-jones-period192-near-event-qualification.json).

## Result

At `a=0.24070100957644772`, both independent corrections recover an unstable
period-96 parent and a stable primitive period-192 child. DOP853/Radau parent
moduli are `1.13241659/1.13237635`; child moduli are
`0.46117807/0.46117779`. Their relative child-multiplier spread is `5.96e-7`,
and the child half-period closures are `1.066981e-4/1.067045e-4`.

All matching, phase, solver-node, cyclic-spectrum, stability-margin,
primitivity, and exact `224/256` section-identity gates pass. EXP-261 therefore
qualifies a fourth local supercritical doubling on the corrected returning
arm and extends the finite cascade through stable period 192. It does not
establish basin measure, tangent-sign equivalence, another event, a limiting
scaling law, paired shrimp boundaries, TBA membership, double-criticality, or
a whole-plane explanation.

Raw receipt: `artifacts/EXP-261/receipt.json`, 58,887 bytes, SHA-256
`70e5b63627408a8fce360bbff5c4375d40b277f82a70c1c599645494473de732`.
Compact receipt:
[`receipts/EXP-261.json`](receipts/EXP-261.json).

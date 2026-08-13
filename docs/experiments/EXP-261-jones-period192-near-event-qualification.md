# EXP-261 — Near-event period-96/192 stability qualification

Status: frozen — not yet executed

EXP-261 selects EXP-260's negative-mode `0.002` candidate, only `5.08e-10`
below the exact period-96 event, and independently corrects the period-96
parent and period-192 child with 128/256-segment DOP853 and Radau systems.

The prospective expectation is supercritical: parent unstable and primitive
child stable under both solvers outside a `1e-4` margin. Solver-node,
multiplier, half-period nonclosure, and exact `224/256` identity gates are
mandatory. Basin measure and tangent-sign equivalence remain separate.

Manifest:
[`../../experiments/manifests/EXP-261-jones-period192-near-event-qualification.json`](../../experiments/manifests/EXP-261-jones-period192-near-event-qualification.json).

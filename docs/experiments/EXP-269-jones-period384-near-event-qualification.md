# EXP-269 — Near-event period-192/384 stability qualification

Status: frozen — not yet executed

EXP-269 selects EXP-268's negative-mode `0.001` candidate, only `1.13e-10`
below the exact period-192 event, and independently corrects the period-192
parent and period-384 child with 256/512-segment DOP853 and Radau systems.

The prospective expectation is supercritical: parent unstable and primitive
child stable under both solvers outside a `1e-4` margin. Solver-node,
multiplier, half-period nonclosure, and exact `448/512` identity gates are
mandatory. Basin measure and tangent-sign equivalence remain separate.

Manifest:
[`../../experiments/manifests/EXP-269-jones-period384-near-event-qualification.json`](../../experiments/manifests/EXP-269-jones-period384-near-event-qualification.json).

# EXP-253 — Near-event period-48/96 stability qualification

Status: frozen — not yet executed

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

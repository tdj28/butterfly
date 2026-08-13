# EXP-246 — Near-event period-24/48 stability qualification

Status: frozen — not yet executed

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

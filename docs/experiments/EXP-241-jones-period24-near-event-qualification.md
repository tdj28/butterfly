# EXP-241 — Near-event period-12/24 stability qualification

Status: frozen — not yet executed

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

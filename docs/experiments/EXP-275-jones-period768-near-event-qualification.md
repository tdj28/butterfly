# EXP-275 — Near-event period-768 qualification

Status: frozen — not yet executed

EXP-274 nominates bilateral primitive period-768 children. EXP-275 selects the
negative-sign step-`0.0005` child only `3.85e-11` below the exact EXP-273
event, then independently corrects the period-384 parent and period-768 child
at that same `a` with DOP853 and Radau.

A pass requires both solvers to classify the parent unstable and child stable,
agree on both whole orbits and multiplier moduli, retain nonzero half-period
closure, and recover exact `896/1024` section identity. This is the decisive
local supercriticality gate, not a basin-measure or universality test.

Manifest:
[`../../experiments/manifests/EXP-275-jones-period768-near-event-qualification.json`](../../experiments/manifests/EXP-275-jones-period768-near-event-qualification.json).

# EXP-300 — Continue the stable period-1536 candidate away from neutrality

Status: frozen before execution

EXP-299 independently classifies the EXP-298 positive-mode primitive
period-1536 child as stable under DOP853 and Radau, but the common coordinate
is only about `1e-12` from the finite 8,192-step event coordinate. The
period-768 parent therefore remains inside the unchanged `1e-4` neutral
classification margin.

EXP-300 continues the same prospectively selected child for 32 frozen sparse
pseudo-arclength steps of `0.0003125`, with step halving permitted only on
correction failure down to `0.000009765625`. All 33 rows, at least `1e-11`
terminal separation from the finite event coordinate, matching below `1e-8`,
persistent half-node separation, terminal full/half closure, neutral mode,
period ratio two, and exact `1792/2048` section identity are mandatory.

A pass supplies a farther exact period-1536 child for a separately frozen
DOP853/Radau parent/child criticality audit. It does not classify terminal
stability or establish a supercritical seventh birth by itself.

Manifest:
[`../../experiments/manifests/EXP-300-jones-period1536-qualified-continuation.json`](../../experiments/manifests/EXP-300-jones-period1536-qualified-continuation.json).

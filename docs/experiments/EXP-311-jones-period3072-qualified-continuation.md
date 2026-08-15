# EXP-311 — Continue the unstable period-3072 candidate away from neutrality

Status: frozen; not yet executed

EXP-310 independently classifies the EXP-309 negative-mode primitive
period-3072 child as strongly unstable under DOP853 and Radau, but the common
coordinate is only `1.05e-12` from the bound finite 8,192-step event
coordinate. The period-1536 parent therefore remains inside the unchanged
`1e-4` neutral classification margin.

EXP-311 continues the same prospectively selected child for four frozen sparse
pseudo-arclength steps of `0.000625`, with step halving permitted only on
correction failure down to `0.00001953125`. All five rows, at least `1e-11`
terminal separation from the finite event coordinate, matching below `1e-8`,
persistent half-node separation, terminal full/half closure, neutral mode,
period ratio two, and exact `3584/4096` section identity are mandatory.

A pass supplies a farther exact period-3072 child for a separately frozen
DOP853/Radau parent/child criticality audit. It does not classify terminal
stability or establish a subcritical eighth birth by itself.

Manifest:
[`../../experiments/manifests/EXP-311-jones-period3072-qualified-continuation.json`](../../experiments/manifests/EXP-311-jones-period3072-qualified-continuation.json).

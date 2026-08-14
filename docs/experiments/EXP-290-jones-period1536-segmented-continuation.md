# EXP-290 — Period-1536 continuation away from the seventh event

Status: frozen — not yet executed

EXP-289 independently classifies the period-1536 child as unstable but leaves
the period-768 parent inside the unchanged neutral margin only `7.08e-14` in
`a` from the event. EXP-290 continues the same selected child for eight frozen
sparse pseudo-arclength steps of `0.0003125`, with halving allowed only down to
`0.000009765625` on correction failure.

Nine exact rows, at least `1e-12` total `a` separation from the event, matching
below `1e-8`, persistent half-node separation, terminal full/half closure,
neutral mode, period ratio two, and exact `1792/2048` section identity are all
mandatory. A pass supplies a farther child for a new independently frozen
criticality audit. It does not itself classify stability or criticality.

Manifest:
[`../../experiments/manifests/EXP-290-jones-period1536-segmented-continuation.json`](../../experiments/manifests/EXP-290-jones-period1536-segmented-continuation.json).

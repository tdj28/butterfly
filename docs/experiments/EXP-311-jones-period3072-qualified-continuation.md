# EXP-311 — Continue the unstable period-3072 candidate away from neutrality

Status: completed — failed only the frozen event-separation gate

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

## Result

All four corrector calls pass at the full `0.000625` step in two evaluations.
Matching residuals remain below `3.22e-9`, and half-node RMS grows monotonically
from `9.02e-6` to `5.41e-5`. The parameter coordinate initially moves toward,
then crosses, the bound finite event coordinate: the five successive offsets
are `+1.053e-12`, `+8.401e-13`, `+4.638e-13`, `-7.541e-14`, and
`-7.772e-13`. Thus branch distance in state space is not monotone distance in
`a` at this resolution.

The terminal row passes full closure (`1.73e-5`), neutral mode (`3.34e-3`),
half-period nonclosure (`2.03e-5`), period ratio, and exact `3584/4096`
section identity. Its preliminary direct multiplier is `+4.7455`; this is not
an independent stability classification and is not promoted.

EXP-311 fails only because terminal absolute separation from the finite event
is `7.77e-13 < 1e-11`. The exact accepted prefix is suitable for a separately
frozen receipt-bound resumption from its final two rows. The resumption must
retain the unchanged row-level gates and cannot reinterpret EXP-311 as a
passed continuation.

Raw receipt: `artifacts/EXP-311/receipt.json`, 1,261,376 bytes, SHA-256
`641d2f47ee6f1d726157469ebaff855300a2ca4dfad64476be52499dba6deaeb`.
Compact receipt: [`receipts/EXP-311.json`](receipts/EXP-311.json).

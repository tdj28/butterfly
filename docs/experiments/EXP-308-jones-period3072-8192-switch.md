# EXP-308 — Bilateral period-3072 switch from event eight

Status: completed — failed one positive-sign half-period gate

EXP-307 qualifies an 8,192-step event-eight representation under the direct
DOP853 source and secondary-null gates. EXP-308 doubles its 2,048 orbit nodes
to a sparse 4,096-segment period-3072 system and follows both signs of the
antiperiodic tangent with predictor length `0.00025`, inherited unchanged from
the preceding passed switch.

Both signs must pass matching, phase, closure, neutral, half-period,
half-node, parameter-displacement, period-ratio, and exact `3584/4096` section
identity gates. A pass nominates primitive period-3072 candidates only.
Independent fixed-parameter correction and stability exchange remain
mandatory before child attraction or eighth-birth direction is claimed.

Manifest:
[`../../experiments/manifests/EXP-308-jones-period3072-8192-switch.json`](../../experiments/manifests/EXP-308-jones-period3072-8192-switch.json).

## Result

Both signs correct in two sparse evaluations at
`a=0.2407010082243377`, displaced `1.09e-12` from the finite event source.
Matching residuals are `2.22e-11`; both retain half-node RMS `4.51e-6`, period
ratio `1.999999999999`, and exact `3584/4096` section identities.

The negative sign passes every gate with direct half-period nonclosure
`5.69e-7`. The positive sign fails only that gate:
`4.41e-8 < 5e-8`. Its correction, phase, closure, neutral, half-node,
displacement, period-ratio, and section-identity gates all pass. The bilateral
minimum-candidate gate therefore fails, and no period-3072 child is nominated.

Preserve the result without relaxing the floor. The prospectively natural
successor doubles the predictor length to `0.0005`, retains both signs and all
unchanged gates, and requires a more separated bilateral representation.

Raw receipt: `artifacts/EXP-308/receipt.json`, 758,390 bytes, SHA-256
`ced9b5fbc564027c005ef36a3beea505b6e4c25edd3cde32b9d0aef13c5a446f`.
Compact receipt:
[`receipts/EXP-308.json`](receipts/EXP-308.json).

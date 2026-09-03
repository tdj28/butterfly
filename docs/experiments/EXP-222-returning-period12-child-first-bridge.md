# EXP-222 — Fine bridge across the first returning-child interval

Status: complete — passed all frozen gates

EXP-221's first coarse step selects a different primitive unstable root.
EXP-222 chooses the independently qualified EXP-220 child closest to the event
(`a_child-a_event=-5.73e-7`, multiplier modulus `0.81849`) and bridges exactly
the same two event endpoints with 16 equal subintervals.

The event state, period, and `(a,c)` coordinate are interpolated between the
two phase-aligned exact endpoints only to seed correction. At each substep the
parent and child are corrected at the declared parameter, and all closure,
stability exchange, period-ratio, proper-subperiod, and `7/8` versus `14/16`
identity gates must pass. Endpoints and midpoint receive independent
DOP853/Radau whole-orbit controls.

Manifest:
[`../../experiments/manifests/EXP-222-returning-period12-child-first-bridge.json`](../../experiments/manifests/EXP-222-returning-period12-child-first-bridge.json).

A pass establishes tracking across one interval only. It does not establish a
broad child sheet, paired shrimp boundaries, TBA membership, or
double-criticality.

## Result

All 17 bridge points pass. The period ratio remains
`2.00000258--2.00001902`; parent multiplier modulus is `1.00646--1.04868` and
child modulus `0.80283--0.97414`. Every point retains parent/child
historical/Barrio identity `7/8` versus `14/16`, minimum proper-subperiod
closure is `0.01660`, maximum orbit closure is `4.31e-11`, and maximum adjacent
child-state distance is `6.89e-4`.

Endpoint and midpoint Radau controls all pass. Their maximum child whole-orbit
RMS is `1.27e-8`, multiplier-modulus difference `8.32e-8`, and relative
period difference `1.22e-12`. This proves EXP-221's coarse step selected the
wrong primitive root; the stable child itself persists across the interval.

EXP-223 now freezes adaptive interval bisection over all 52 event endpoints to
the middle slice. A corrected point is accepted only if every scientific gate
passes and its child-state step is at most `0.003`; otherwise the parameter
interval is bisected, to maximum depth six.

Raw receipt: `artifacts/EXP-222/receipt.json`, 34,706 bytes, SHA-256
`03b9c508929688ed81265848a77d617b0cd7120cafe2d0137fe2f0dd3996fd18`.
Compact receipt:
[`receipts/EXP-222.json`](receipts/EXP-222.json).

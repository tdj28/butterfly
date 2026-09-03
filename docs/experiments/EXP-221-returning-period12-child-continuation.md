# EXP-221 — Identity-safe returning-arm child continuation

Status: complete — failed at first coarse event step by primitive-root jump

EXP-220 independently qualifies four stable primitive period-12 children at
the untouched near returning-arm slice but cannot switch directly at the
middle or far slices. EXP-221 tests persistence rather than repeating a fresh
ill-conditioned switch.

The stronger `c=7.16299104`, scale-`0.0005`, signed-`-1` child is selected by
exact receipt identity. Its event-relative offset
`a_child-a_event=-3.6532515e-6` is held fixed while the child is corrected
sequentially along all 52 EXP-217 events through `c=7.70247507`. Every point
must retain unstable parent/stable child exchange, period ratio two,
historical/Barrio identities `7/8` versus `14/16`, proper-subperiod
nonclosure, and adjacent-state coherence. Points 0, 25, and 51 receive full
independent DOP853/Radau whole-orbit controls.

Manifest:
[`../../experiments/manifests/EXP-221-returning-period12-child-continuation.json`](../../experiments/manifests/EXP-221-returning-period12-child-continuation.json).

A pass establishes a regular sampled child strip from the near to middle
returning arm. It does not prove a global child sheet, paired shrimp-boundary
connectivity, TBA membership, or double-criticality.

## Result

The seed point and its independent control pass, but the 52-point claim fails
at the first new event, `c=7.17534380`. Orbit closure, parent instability,
proper-subperiod nonclosure, and `7/8` versus `14/16` identity survive. The
corrected primitive root has period ratio `2.01045` and multiplier modulus
`5588.88`, so it fails child stability and the period-ratio gate.

This is not a doubled-parent collapse. The child corrector jumps from the
qualified branch to a different primitive unstable root across the coarse
`Delta c=0.01235` event spacing. EXP-222 prospectively selects the closest
qualified EXP-220 child to the flip event and freezes a 16-substep bridge over
only this first interval. It changes path resolution and seed distance, not
identity or stability gates.

Raw receipt: `artifacts/EXP-221/receipt.json`, 5,623 bytes, SHA-256
`af57efbcc111ab3c9c16c6ea286f4027218f4b2b55578b3f2cd708bb19ea5575`.
Compact receipt:
[`receipts/EXP-221.json`](receipts/EXP-221.json).

# EXP-221 — Identity-safe returning-arm child continuation

Status: prospectively frozen before execution

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

# EXP-222 — Fine bridge across the first returning-child interval

Status: prospectively frozen before execution

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

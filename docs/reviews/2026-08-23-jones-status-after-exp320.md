# Jones paper status after EXP-320

## Bottom line

The new evidence strengthens rather than debunks the Jones paper's local
periodicity-hub mechanism. One corrected returning-arm orbit now has eight
exact real-`-1` events. The first seven births are independently qualified as
supercritical; the eighth is qualified as subcritical.

## What is stronger than the 2012 evidence

- Each of the eight events is based on corrected periodic orbits and explicit
  Floquet or antiperiodic-tangent equations, not raster pixels alone.
- Seven stable immediate daughters are qualified across two numerical
  representations, extending the local cascade through primitive period 1536.
- The eighth event has a primitive unstable daughter on the stable-parent
  side, showing that the local cascade changes criticality rather than merely
  repeating one universal pattern.
- A misleading stable/stable sample is explained by same-map branch switching:
  the stable higher-`a` period-1536 candidate is not the immediate seventh
  daughter. EXP-324 goes farther: exact correction collapses that old Float64
  seed to the doubled parent, and EXP-325 independently reproduces that result
  at twice the step resolution. This removes spurious topology rather than
  retracting the event.
- EXP-326/327 then continue the exact immediate daughter through event eight
  and register the independently constructed meshes to `6.35e-18` node RMS.
  The eight-event connected chain no longer depends on the collapsed seed.

## What this corrects or narrows

The results reject any simple assumption that every successive local birth in
the hub is supercritical or that one shared Float64 coordinate is sufficient
near the accumulation scale. They do not reject Jones's observed cascade or
nested periodic organization. They also show that an apparently primitive
Float64 candidate can lie along a near-neutral doubled-parent direction and
disappear under exact correction.

## What remains open

The evidence does not yet validate the claimed homoclinic endpoint, prove
Jones's finite symbolic agreement as a global conjugacy, identify TTL23 with
the Barrio-Blesa-Serrano TBA everywhere, establish paired shrimp boundaries,
or explain the full `(a,c)` plane. EXP-325 has now replicated the target
collapse at doubled resolution; the global tasks remain continuation of the
TBA, shrimp boundaries, and homoclinic boundary-value problem.

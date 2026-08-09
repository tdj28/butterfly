# EXP-181 Jones support-gap sprinkler frozen

Date: 2026-08-07

EXP-181 prospectively targets the sole EXP-180 hole at
`(a,b,c)=(0.156,0.2,20)` on the same negative, gated historical section. Two
independent DOP853 attractor clouds calibrate and validate capture; their
maximum symmetric scaled distance must remain below the frozen `0.0002`
radius. A fixed-step Float64 RK4 `128 x 64` section ensemble then retains
middle-time crossings only from trajectories that have not captured into the
banded attractor by time 300.

Both survivor-cloud coordinates must provide at least 1000 return pairs and
resolve the local critical under all seven locally bootstrapped variants. The
physical-location predictions are frozen from the two neighboring EXP-180
rows: `x=-18.57534077 +/- 0.75` and
`z=0.00518306415 +/- 0.00015`. At least 20 survivors, decaying survivor count,
no numerical failures, and at least 90% fixed-step/DOP853 capture agreement are
also required. Global branch count is reported but cannot decide the local
identity result.

The generalized sprinkler supports either oriented axis-aligned section and a
post-interpolation half-plane gate; new regression tests protect the earlier
positive Barrio-section behavior and the added negative Jones-section path.

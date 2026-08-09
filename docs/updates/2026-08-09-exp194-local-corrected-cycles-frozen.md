# EXP-194 freezes local corrected cycles after the EXP-193 egress stop

EXP-193 stopped before integration because its derived EXP-192 frame could not
be transferred under the existing external-upload scope. EXP-194 keeps that
artifact local and strengthens the scientific preparation at the same time.

The successor selects 65 pixels across the isolated second-landmark period-6
component using only normalized parameter geometry. Each is independently
recovered with DOP853, corrected as a flow orbit, Floquet-tested for transverse
stability, and intersected with Barrio's positive-x section to obtain the six
phases required by a `z` return map. The acceptance threshold is 60 complete
candidates. No target word or critical coordinate enters the run.

## Executed result

Fifty-eight of 65 samples reproduce historical period 6 and pass every flow-
orbit and Floquet gate, but EXP-194 fails overall because all 58 have eight,
not six, crossings on Barrio's positive-x section. Six raster-edge samples are
unresolved under DOP853 and one resolves as period 5. The common eight-crossing
result is exact across the qualified set and identifies a representation-
specific phase-count error in the frozen expectation.

EXP-195 changes only that expected count. It retains all raw orbit states and
all ten other checks without recomputation, preventing a numerical rerun from
hiding the original failure.

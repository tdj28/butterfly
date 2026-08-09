# EXP-187 freezes a word-blind period-6 center search

EXP-186 showed that the exact second Figure 6 landmark is an excellent
period-6 orbit seed but not a reproducible symbolic center. EXP-187 now freezes
the next non-circular step: continue that orbit over a bounded local `(a,c)`
grid and search the signed dominant transverse Floquet surface for a stationary
saddle-zero with four enclosing sign changes.

This criterion uses the expected local geometry of two intersecting
superstability curves. It does not read a target word or use alphabet labels.
The coarse `21 x 21` continuation, three shrinking `5 x 5` refinements, exact
six-return identity, and final DOP853/Radau center-plus-ring validation are all
fixed before execution.

A pass will nominate—not prove—a doubly-superstable center. Independent
survivor reconstruction must then show both critical points on the corrected
orbit before word encoding is allowed.

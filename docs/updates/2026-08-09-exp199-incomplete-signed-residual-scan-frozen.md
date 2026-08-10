# EXP-199 freezes an incomplete signed-residual diagnostic

EXP-198 provides 685 individually qualified corrected orbits but fails its
coverage gate. EXP-199 binds that complete immutable artifact and explicitly
limits its claim to an incomplete diagnostic. It retains signed residuals for
both critical-to-orbit assignments at both RK4 steps.

A direct grid point must improve sharply on EXP-197's distances and slope.
Alternatively, a bracket cell requires four eligible corners, one common
phase assignment, and sign changes of both residuals independently at both
steps. Neither outcome is called a center until a coupled adaptive solve and
independent qualification pass.

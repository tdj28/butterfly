# EXP-203 freezes the lower-c stable period-6 extension

EXP-202 leaves the second critical residual positive everywhere but smallest at
the lower-`c` edge. EXP-203 responds without extrapolating that residual: it
freezes 6,283 fresh DOP853 shooting corrections over a new lower-`c` rectangle,
using the lowest-`c` qualified orbit as the only seed and retaining every
EXP-198 identity, section, Floquet, and stability gate.

No return-map critical is evaluated in this stage. Only after the stable-orbit
coverage result is recorded may a successor select candidates and freeze a
scale-ensemble residual replay.

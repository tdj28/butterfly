# EXP-203 freezes the lower-c stable period-6 extension

EXP-202 leaves the second critical residual positive everywhere but smallest at
the lower-`c` edge. EXP-203 responds without extrapolating that residual: it
freezes 6,283 fresh DOP853 shooting corrections over a new lower-`c` rectangle,
using the lowest-`c` qualified orbit as the only seed and retaining every
EXP-198 identity, section, Floquet, and stability gate.

No return-map critical is evaluated in this stage. Only after the stable-orbit
coverage result is recorded may a successor select candidates and freeze a
scale-ensemble residual replay.

EXP-203 completes all 6,283 points. The seed passes, but only 551 points
qualify against the frozen 1,000-point minimum. They form five components
(`331,156,62,1,1`) in a narrow `a in [0.2155,0.2158]`,
`c in [7.132,7.288]` strip. The seed component touches the lower-`a` boundary;
the upper component touches the overlap boundary; and 4,921 points first fail
correction while 806 first fail stability. Continue the actual boundary or
unstable family rather than extrapolating the residual through failed space.

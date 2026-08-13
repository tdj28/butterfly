# EXP-202 freezes a scale-ensemble critical-membership residual

EXP-201 qualifies the shallow lower-`c` critical as a reproducible finite-data
scale object. EXP-202 now freezes the consequence before reading any
scale-ensemble residual: use the three smoothing levels that are universally
three-branch, retain both nested supports and both RK4 steps, and require one
ordered orbit-phase assignment across all 12 reconstructions.

The result can nominate a direct point or a complete two-residual bracket only
after a 70-candidate coverage gate. Even a pass remains a nomination for fresh
zero-slope and independent-integrator tests; a failure remains bounded to the
incomplete sampled stable field.

EXP-202 fails cleanly after preserving all 94 candidates and a common `[7,5]`
phase assignment. No direct point passes and no complete cell brackets both
residuals in all 12 views. The first residual spans zero, but the second is
positive in every one of 1,128 evaluations, with minimum `0.019945` and median
`0.030794`. The next stable-family extension is therefore directed toward
lower `c`, while unstable inter-window continuation remains separate.

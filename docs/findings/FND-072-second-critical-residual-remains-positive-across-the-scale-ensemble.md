# FND-072 — The second critical residual remains positive across the scale ensemble

Status: prospectively qualified bounded negative result

EXP-202 audits the 94 EXP-201-qualified candidates using the three contiguous
low-smoothing levels that are resolved as three-branch in every nested-support
and RK4-step reconstruction. All 94 retain the same ordered orbit-phase
assignment `[7,5]` across all 12 views and pass the critical-location span gate.

No candidate passes the frozen direct gate and none of the 40 complete lattice
cells brackets both residuals in every view. The first residual ranges from
`-0.004116` to `0.002440`; its candidate uncertainty interval contains zero at
44 points, and the view-averaged field brackets zero in eight cells. Yet no
cell brackets it in every individual reconstruction.

The decisive obstruction is the second residual. It is positive in every one
of 1,128 scale/support/step reconstructions, ranging from `0.019945` to
`0.043328` with median `0.030794`. The closest direct candidate is
`(a,c)=(0.21565,7.284)`, but its worst residual is `0.028711`, or 1.436 times
the `0.02` gate.

The low-smoothing ensemble therefore reproduces and strengthens EXP-199's
one-sided second-residual obstruction without the high-smoothing veto. It
rejects a doubly critical center in this sampled, coverage-incomplete stable
field. It does not reject global double superstability: the lower-`c` edge has
the smallest second residual, so the next test should extend the corrected
stable family in that direction while preserving the scale ensemble. An
unstable inter-window continuation remains a separate alternative.

Evidence: [`../experiments/EXP-202-low-smoothing-scale-ensemble-residual.md`](../experiments/EXP-202-low-smoothing-scale-ensemble-residual.md).

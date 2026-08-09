# EXP-148 passes blind as two-branch

Date: 2026-08-07

The untouched midpoint `a=0.1481875` resolves as a two-branch nonattracting
period-4 saddle under the identical censor-aware PIM method at both 128 and 256
returns. All six access-line reconstructions complete, both coordinates agree
across every frozen oracle variant, and no lifetime evaluation fails.

This narrows the finite `c=20` saddle-class bracket from
`[0.148125,0.14825]` to `[0.1481875,0.14825]`. The result was inspected only
for its blind branch class. EXP-149 is now instantiated solely with the frozen
EXP-147/148 paths and hashes; its lobe-exclusion decision and thresholds were
committed before EXP-148 began.

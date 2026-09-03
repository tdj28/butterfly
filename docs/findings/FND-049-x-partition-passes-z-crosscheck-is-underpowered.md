# FND-049 — The neutral `x` partition passes; the held-out `z` cross-check is underpowered

Status: supported for `x`; full two-coordinate qualification failed

EXP-175 used a fresh dense return cloud at the established three-branch
control and kept Figure 6 target cycles out of partition construction. All
seven oracle variants agreed on a three-branch `x` relation in both the frozen
calibration and held-out validation segments. The combined neutral `x`
partition has two bounded critical intervals and maximum normalized
calibration/validation drift `0.0197441`.

The required `z` cross-check did not pass. Calibration resolved unanimously,
and six of seven held-out variants resolved three branches. The only failure
was the 50-bin variant: its nominal fit still contained two critical points
and cleared graph-likeness and coverage, but only 64 of 100 bootstrap resamples
retained the count. No variant resolved to a contradictory branch number.

Consequently the result supports the historical-section `x` partition but
does not yet authorize Jones word assignment, `C/D` identification, or a
coordinate-independent topological claim. The successor increases independent
pair counts while leaving every oracle and acceptance threshold unchanged.

Evidence: [`../experiments/EXP-175-jones-section-operational-partition.md`](../experiments/EXP-175-jones-section-operational-partition.md).

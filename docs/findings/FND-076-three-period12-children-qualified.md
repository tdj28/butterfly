# FND-076 — Three separated period-6 flips have primitive stable period-12 children

Status: qualified at all three prospectively frozen follow-up targets

EXP-207 failed to trace the frozen eight-point branch arms, but nominated one
accurate stable doubled orbit at each of `c=7.18,7.24,7.30`. EXP-208 froze
those exact coordinates, then separately corrected each period-6 parent and
period-12 candidate with DOP853 and Radau.

All three pass. Radau gives unstable parent multiplier moduli
`1.20713--1.29062` and stable child moduli `0.02354--0.20615`. Child/parent
period ratios lie in `1.999923--1.999932`. All parents have exactly 6
historical and 8 Barrio phases; all children have 12 and 16. DOP853/Radau
whole-orbit RMS is at most `6.29e-11`, and every proper divisor of historical
period 12 is rejected. The minimum subperiod return distance is `0.09413`,
over `1.77e9` times the associated full-period closure.

This is constructive, orbit-level evidence that the dense period-6 flip edge
found by EXP-206 genuinely opens onto doubled dynamics at three separated
samples. It strengthens Jones's period-doubling organization beyond a raster
edge. It does not establish a continuous period-12 surface, repair EXP-207's
failed branch continuation, measure supercritical normal-form scaling or
basins, identify the TBA curve, or locate a doubly-superstable center.

Evidence:
[`../experiments/EXP-208-qualify-period12-children.md`](../experiments/EXP-208-qualify-period12-children.md).

# FND-058 — An exact Figure 6 landmark is not a reproducible word center

Status: exact-coordinate interpretation rejected; source word set still open

EXP-186 tests the untouched second printed Figure 6 landmark at
`(a,b,c)=(0.21564,0.2,6.124)` without moving the coordinate, partition,
alphabet, orbit, or target. The underlying period-6 attractor is exceptionally
well resolved: independent DOP853 and Radau corrections close below `2.14e-13`
and agree over the complete orbit within scaled error `1.23e-9`.

The nonattracting survivor calculation is also step-stable in x. Two RK4 step
sizes produce 7,335 and 7,299 return pairs, agree in survivor fractions within
`0.001465`, resolve the same two-branch topology, and place the critical
midpoint within normalized distance `8.41e-5`. Yet z is monotone on both
clouds, so it is not an injective scalar coordinate for this return map.

Most decisively, the x word is `010011` at `dt=0.01` and `C10011` at
`dt=0.005`; both orbit solvers agree within each profile, but neither result
matches any of the five frozen period-6 Figure 6 words. The single-symbol
step-size change occurs where an orbit point lies on the empirical critical-
interval boundary.

The failure rules out treating this exact printed gray-box coordinate as a
reproducible symbolic center. It does not falsify the entire Figure 6 word or
arrow construction because the raster landmarks are approximate and were not
published as exact doubly-superstable centers. A defensible successor must
locate centers through a word-blind dynamical criterion, then apply the already
frozen partition and alphabet without tuning to the expected word.

Evidence: [`../experiments/EXP-186-heldout-jones-landmark-word.md`](../experiments/EXP-186-heldout-jones-landmark-word.md).

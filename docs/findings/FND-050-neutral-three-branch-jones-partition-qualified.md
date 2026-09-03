# FND-050 — A neutral three-branch Jones-section partition is split-cloud qualified

Status: supported at the dense `(0.2,0.2,20)` control

EXP-176 uses a fresh trajectory and unchanged EXP-175 thresholds to recover a
three-branch operational partition on the negative-oriented historical
half-plane. All seven oracle variants agree in the 1000-pair calibration and
1000-pair held-out validation clouds, independently in `x` and `z`. Joint
critical-location drift is `0.0176585` in `x` and `0.0161930` in `z`, below the
frozen `0.04` limit.

This supplies the independently inferred partition layer required before a
target periodic orbit can be encoded. It does not yet supply the source
convention needed to rename neutral critical intervals `K0/K1` as `C/D`, nor
does it qualify the two-branch historical-section control, any Figure 6 word,
or any topological conjugacy.

Evidence: [`../experiments/EXP-176-jones-section-operational-partition-power.md`](../experiments/EXP-176-jones-section-operational-partition-power.md).

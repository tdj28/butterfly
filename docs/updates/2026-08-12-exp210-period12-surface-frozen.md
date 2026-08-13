# EXP-210 freezes a dense two-parameter period-12 surface patch

EXP-209 establishes replicated local supercritical signatures at three slices.
EXP-210 replaces EXP-207's ill-conditioned free-parameter branch predictor
with direct fixed-parameter correction on a rectangular physical-offset grid.

The frozen patch contains 31 exact event slices times four post-flip `a`
offsets. All 124 points must retain parent/child identity, stability,
primitivity, section counts, normal-form scaling, and smooth whole-orbit
adjacency. Six edge/center controls are independently recorrected with Radau.
This is the first experiment capable of promoting the three sampled openings
to a dense two-parameter child-surface patch.

The execution completes all 124 cells but fails. One hundred eight cells pass;
16 single-shooting child corrections land on the doubled period-6 parent.
Their half-period closure vanishes and their opening amplitude falls below
`1.69e-8`. The resulting identity jumps reach RMS `0.0870` and destroy several
four-offset power-law fits.

The pattern is numerical rather than a resolved sheet termination: multiple
collapsed cells are bracketed in `c` by valid primitive stable child cells, and
EXP-209 independently supplies valid child anchors at `c=7.18,7.24,7.30`.
EXP-211 will independently interpolate those anchor children to every surface
cell, accept only a proper-subperiod-nonclosing root, and preserve all original
surface gates.

Receipt: [`../experiments/receipts/EXP-210.json`](../experiments/receipts/EXP-210.json).

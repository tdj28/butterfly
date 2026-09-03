# EXP-164 passes; EXP-165 exact period-4 flip frozen

Date: 2026-08-07

EXP-164 passes on 38 pseudo-arclength points from `c=4.3250936898` through
`c=4.7292613238`. The primitive period-4 child retains four windings to
`6.57e-14`, minimum half-period nonclosure `0.2951`, and maximum closure error
`2.35e-12`. Three independent Radau checks agree with the DOP853 orbits to
`5.56e-12` phase-aligned RMS and with the selected multipliers to `1.55e-11`.

The first real `-1` crossing is bracketed by `c=4.631470750402099` and
`c=4.6511284829018225`, with multipliers `-0.9679953281` and
`-1.0947016212`. EXP-165 freezes that raw receipt hash, bracket, sixteen
shooting segments, exact `c` derivatives, cyclic-product checks, independent
Radau monodromy, half-period nonclosure, and four-winding identity before the
event solve. Its claim is only the exact period-4-to-8 flip.

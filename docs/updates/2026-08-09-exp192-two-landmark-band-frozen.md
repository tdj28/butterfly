# EXP-192 freezes the two-landmark period-6 band test

EXP-191 found that the second exact Jones period-6 landmark belongs to a
coherent 981-pixel component, but the component exits both sampled `c`
boundaries. EXP-192 now expands the same target-word-blind atlas through both
published period-6 landmarks at 92,736 parameter pairs.

The prospective output is deliberately narrow: anchor the component at
`(a,c)=(0.215,7.6)` and report the period and component membership of the
nearest raster pixel to `(0.21564,6.124)`. This can reveal a candidate common
band, but it cannot establish continuation identity, double superstability, or
a center. Those require corrected cycles and direct critical-to-orbit
residuals after the raster result is known.

## Executed result

The secure RTX A5000 run from clean commit `3f42faa` passed all numerical
gates: 92,736 pixels, no failures, and 4,192 period-6 classifications. Both
published landmarks remain period 6 at this resolution, but the preregistered
membership result is negative. The second landmark's 2,598-pixel anchor
component occupies `c in [7.124,8.192]`; the first landmark's period-6 pixel at
`c=6.124` is outside it.

This rules out treating the two printed coordinates as one visibly connected
stable raster band. It does not rule out a subgrid bridge, an unstable
continuation, or a larger organizing family. The direct two-critical search
will now use only the isolated second-landmark component, because that is the
one with the prospectively identified three-branch return-map geometry.

# EXP-191 freezes the second period-6 window atlas

The first landmark's complete Floquet-zero neighborhood is unimodal, while a
post-result diagnostic at Jones's other exact period-6 landmark exposes the
required three-branch geometry on the Barrio section. EXP-191 now freezes a
40,401-pixel local atlas around that second coordinate.

The atlas is target-word blind and selects only the period-6 component
containing the exact anchor. Its purpose is to replace guesswork about the
window bounds with a reproducible domain for corrected-orbit and two-critical
searches. It cannot itself identify a center.

## Executed result

The secure RTX A4500 run from clean commit `28f3651` classified all 40,401
pixels without a numerical failure. The exact source anchor lies in a coherent
981-pixel period-6 component spanning `a in [0.2145,0.21555]`. Because that
component reaches both sampled `c` boundaries while remaining interior in
`a`, EXP-191 identifies a real search band but also falsifies the assumption
that `c in [7.4,7.8]` contains the complete local window.

The next frozen test expands the band vertically through both Jones period-6
landmarks. It will ask only whether their nearest raster pixels lie in the same
eight-connected period-6 component; a positive raster result will still
require corrected-orbit continuation before any family-identity claim.

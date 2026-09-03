# FND-057 — The Jones operational alphabet is qualified

Status: supported on the recovered historical section

Jones's source defines `C` as the critical retained from the unimodal side,
`D` as the added trimodal critical, the branch-3 excursion, and symbol `0` as
the newly deposited innermost point. Combined with EXP-183's independently
qualified critical identity, this froze `K1 -> C`, `K0 -> D`, `B0 -> 2`,
`B2 -> 0`, and residual `B1 -> 1` before any Figure 6 target word was encoded.

EXP-185 passes that mapping across DOP853 and Radau, disjoint calibration and
validation segments, and both x and z representations. All eight geometry
rows order `B2` as the unique innermost interval with strict support
separation; each contains 96--112 `B0 -> B2` depositions and no `B0 -> B0`
return. Every jointly resolved x/z pair agrees in both its source and target
branch label.

This closes the alphabet prerequisite for non-circular Figure 6 word tests. It
does not establish a unique generating partition, topological conjugacy, a
template, the published word/arrow claims, or a global TBA curve.

Evidence: [`../experiments/EXP-185-jones-historical-alphabet.md`](../experiments/EXP-185-jones-historical-alphabet.md).

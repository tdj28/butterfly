# EXP-244 qualifies the period-24 flip; EXP-245 is frozen

The exact 32-segment augmented solve passes at
`a=0.24070104611236293`. DOP853 and Radau independently place the nontrivial
multiplier at `-1` while preserving primitive `28/32` identity. This is a
second exact cascade event only `1.35e-7` in `a` from the period-12 flip.

EXP-245 freezes the corresponding 64-segment period-48 switch with three
predictor scales, both signs, and explicit primitive `56/64` identity gates.

# EXP-236 collapses to the doubled parent; EXP-237 is next

EXP-236 converts the closest EXP-235 trial into a low-residual orbit after 329
evaluations. Its full-period closure, period ratio, and `28/32` section counts
all look like a period-24 candidate, but the decisive half-period closure is
`4.03e-9`: the solution is the period-12 parent traversed twice.

This preserves the value of the exact EXP-232 period-12 flip while rejecting
further iteration of the same full-period switch representation. EXP-237
freezes an exact segmented augmented solve at fixed `(b,c)` with `a` as the
continuation parameter. A passing receipt will provide orbit nodes and the
anti-periodic tangent mode needed for a genuinely segmented period-24 switch.

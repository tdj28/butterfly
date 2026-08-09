# EXP-159 identity failure preserved; EXP-160 frozen

Date: 2026-08-07

EXP-159 fails its scientific gate. The first natural-parameter step from
`c=3.1845` to `3.2044681` collapses half-period nonclosure from `0.1927184` to
`1.67e-13`, proving that the corrector returned to the doubled period-1 parent.
The subsequent positive multiplier sequence is therefore the squared parent
multiplier, not a period-2 child continuation.

EXP-160 replaces coarse natural stepping with pseudo-arclength continuation
seeded by the last two already qualified EXP-157 child points. Step length
grows deterministically from `0.003` to at most `0.02`, with bounded retries
and a hard primitivity stop. All closure, two-winding, Radau identity, and real
`-1` bracket gates remain explicit. No EXP-159 threshold is relaxed or
reinterpreted as a pass.

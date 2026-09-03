# EXP-170 block clustering fails; EXP-171 frozen

Date: 2026-08-07

EXP-170's coupled solve converges at `c=4.7090113823613065`. All 32 direct
monodromy products give `-1` to about `1.8e-14`, and independent Radau gives
`-1.0000000000223`. The run nevertheless fails because the block-root audit
sorts roots only by radius. At a flip, the neutral `+1` and flip `-1` families
have identical modulus, so their 32nd roots interlace; the old grouping mixes
them and reports a spurious block multiplier near zero.

The successor replaces radius slicing with balanced clustering of each root
raised to the segment count. A linear assignment forces exactly 32 roots per
Floquet family, and new unit tests cover both the equal-modulus `+1`/`-1` case
and complex-conjugate families. EXP-171 retains the source, bracket, solvers,
and every numerical acceptance threshold from EXP-170. The failed receipt is
preserved; only the invalid diagnostic representation is repaired.

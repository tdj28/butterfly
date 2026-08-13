# EXP-234 rejects the symmetric tangent stencil; EXP-235 is frozen

The `-1e-5` and center period-12 primary corrections have raw closures
`4.20e-11` and `1.81e-11`; the `+1e-5` correction diverges to `0.00801`.
EXP-235 therefore uses the independently qualified one-sided stencil
`[-2e-5,-1e-5,0]` without changing the switch or candidate gates.

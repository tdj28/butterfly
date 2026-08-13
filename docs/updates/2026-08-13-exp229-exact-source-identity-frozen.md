# EXP-229 freezes an exact source-identity correction

EXP-228 shows that the purported EXP-227 source-arm separation collapses in
both continuation directions. Exact same-`c` diagnostic corrections reveal
the cause: the `5.6e-7--5.8e-7` separation used by EXP-227 is linear
interpolation error, while candidate and source event coordinates agree near
machine precision.

EXP-229 now freezes the full 21-point correction and three independent Radau
controls. The earlier distinct-curve conclusion is suspended pending this
receipt. No GPU is appropriate: this is a small serial stiff orbit and
variational solve.

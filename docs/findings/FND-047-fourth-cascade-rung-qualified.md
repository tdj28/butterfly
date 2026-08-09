# FND-047 — The fourth fixed-path cascade rung is qualified

Status: passed EXP-169 through EXP-173; EXP-168 and EXP-170 failures preserved

## Finding

The primitive period-8 child reaches an exact fourth flip at
`(a,b,c)=(0.1798,0.2,4.7090113823613065)`, with period
`47.019522702249795`. Thirty-two direct monodromy products, a repaired
balanced block-root representation, and independent Radau agree on the `-1`
event. The DOP853 direct-product residual is `1.43e-14`; Radau differs from
`-1` by `2.23e-11`.

At `c=4.716`, the period-8 parent has Radau multiplier `-1.2072088976`; the
primitive period-16 child is stable with multiplier `0.1483901906`. The two
switch signs match after a half-cycle phase shift to RMS `1.17e-6`. Their
period ratio is `1.99999959`, their winding is sixteen, and a perturbed
64-period integration recovers the same child to RMS `7.07e-10`.

The first three event spacings in `c` are `1.1293186051`, `0.3264020625`, and
`0.0725641814`, giving finite ratios `3.45990` and `4.49812`. The trend is
consistent with cascade accumulation, but two ratios do not establish a
universal limit.

## Numerical lesson

EXP-168 honestly failed a point-count gate and EXP-170 honestly failed because
radius sorting mixed equal-modulus neutral and flip root families. Both
successors retained the scientific thresholds. Balanced powered-root
clustering now has regression tests. EXP-173 took `1107.9` seconds locally;
nearly all cost was the serial long-horizon Radau attraction check rather than
the Newton-like orbit correction.

Before routine continuation beyond period 16, switching should use segmented
multiple shooting and long recovery should become checkpointed/parallel while
retaining an independent short-orbit Radau audit. A GPU is useful only after
that parallel workload exists; it does not accelerate the current serial
SciPy solve automatically.

## Implication for Jones

Four independently qualified supercritical rungs now extend the fixed path
through a stable period-16 attractor. This materially strengthens the finite
cascade portion of Jones beyond the original raster evidence. It still does
not supply the missing symbolic partition, exact historical paths, logistic
conjugacy, or equilibrium homoclinic connection.

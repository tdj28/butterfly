# EXP-207 freezes period-12 switching at three flip-curve points

EXP-206 supplies a dense, identity-safe period-6 flip curve. EXP-207 selects
three separated checkpoints and freezes doubled-period nullspace switching
before examining any child branch. Both local arms must depart the doubled
primary and retain 12 historical plus 16 Barrio phases.

A pass will establish branch existence and furnish inputs for a separate
stability-exchange, half-period nonclosure, arm-equivalence, and attraction
audit. It will not by itself call the flip supercritical or identify it with
the TBA curve.

The first invocation produced no receipt. A first arm point corrected, but the
next nominal predictor lay outside the already-frozen `a` guard, so SciPy
stopped before evaluating it. The implementation now shortens predictor steps
only as needed to remain strictly inside that unchanged guard and records each
effective step. Events, gates, bounds, and the nominal maximum step are
unchanged; regression tests cover both unchanged and shortened predictors.

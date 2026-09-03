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

The clean rerun completes with a scientific failure. No event meets the frozen
eight-points-per-direction requirement: each negative arm supplies one point,
and every positive arm supplies zero. This honestly rejects the claim that the
present nullspace predictor/corrector has traced local period-12 arms.

The failed run nevertheless yields a consistent lead. At all three separated
events the negative direction lands on one stable, accurate, non-parent-like
orbit with the expected 12 historical and 16 Barrio phases. The three closure
errors are below `4.13e-10`, the distances from the doubled primary exceed
`0.00416`, and the dominant transverse multiplier moduli are `0.1491`,
`0.02354`, and `0.2061`. These are post-run nominations, not accepted findings.
EXP-208 will freeze their exact coordinates and independently recorrect both
parent and child using DOP853 and Radau, adding half-period, period-ratio,
stability-exchange, and phase-aligned identity gates.

Receipt: [`../experiments/receipts/EXP-207.json`](../experiments/receipts/EXP-207.json).

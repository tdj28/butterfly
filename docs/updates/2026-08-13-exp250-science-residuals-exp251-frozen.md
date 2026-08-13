# EXP-252 nominates period 96; EXP-253 is frozen

The phase-aligned secant seed reduces the augmented orbit residual from
EXP-249's `3.22e-8` to `2.16e-10` and retains a DOP853 flip residual of
`2.00e-8`. The optimizer nevertheless reaches its ceiling, and the long
single-shot Radau calculation drifts enough to fail its multiplier gate.

EXP-251 freezes residual-qualified status handling plus an independent Radau
evaluation in the same segmented representation, including anti-periodic
tangent and cyclic block-Floquet gates. No numerical threshold is relaxed.

The audit passes. Radau gives orbit/tangent residuals `2.16e-10/1.21e-10`,
flip multiplier `-1.000000032852`, and cyclic spread `2.37e-12`. EXP-252 is
therefore frozen to attempt a 128-segment period-96 branch switch, with both
the original event receipt and this passing audit bound by SHA-256.

EXP-252 passes all six attempts. The largest predictors on both signs retain
exact `112/128` identity and have preliminary stable multipliers near `0.893`.
EXP-253 freezes independent DOP853/Radau correction and a prospectively
declared supercritical parent-unstable/child-stable test at the negative-mode
near-event point.

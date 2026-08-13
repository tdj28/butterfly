# EXP-250 passes science residuals; EXP-251 is frozen

The phase-aligned secant seed reduces the augmented orbit residual from
EXP-249's `3.22e-8` to `2.16e-10` and retains a DOP853 flip residual of
`2.00e-8`. The optimizer nevertheless reaches its ceiling, and the long
single-shot Radau calculation drifts enough to fail its multiplier gate.

EXP-251 freezes residual-qualified status handling plus an independent Radau
evaluation in the same segmented representation, including anti-periodic
tangent and cyclic block-Floquet gates. No numerical threshold is relaxed.

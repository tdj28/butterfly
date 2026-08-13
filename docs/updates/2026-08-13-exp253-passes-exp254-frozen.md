# EXP-253 passes; tangent-sign equivalence is frozen

Independent DOP853/Radau corrections classify the period-48 parent as
unstable and the primitive period-96 child as stable at the same near-event
coordinate. FND-093 and the manuscript now record the exact returning-arm
cascade through stable period 96.

EXP-254 freezes a common-parameter, whole-orbit comparison of both tangent
signs under both solvers. Its purpose is to distinguish one phase-shifted
period-96 branch from two accidentally nearby switch roots before continuing
the child toward a fourth event.

EXP-254 passes every orbit and solver gate but fails sign identity at
`1.07e-5` RMS. Both solvers identify a half-period shift; the final phase grid
spacing is `7.45e-9`, too coarse for the frozen `1e-6` RMS gate. EXP-255
preserves the failure and freezes continuous phase minimization on the same
corrected nodes without relaxing the identity threshold.

EXP-255 completes the two phase searches but writes no receipt because a NumPy
boolean status is not JSON serializable. EXP-256 freezes the scientifically
identical successor after only that built-in-type conversion.

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

EXP-256 passes: DOP853/Radau whole-orbit sign RMS is
`3.45e-10/4.57e-9` at a half-period shift, resolving both signs as one stable
primitive period-96 orbit. EXP-257 freezes eight exact continuation steps
toward a separately gated fourth-flip scan.

EXP-257 passes all eight steps and retains exact `112/128` identity while the
dominant multiplier reaches `-148.708`. EXP-258 freezes a magnitude-separated
block-Floquet scan of all nine exact rows.

EXP-258 passes and isolates exactly one real-`-1` bracket with at least
`1.38e18` transverse-mode separation. EXP-259 freezes the exact 128-segment
orbit/tangent solve, using segmented Radau parity rather than a conditioned
full-period replay.

EXP-259 converges in 10 evaluations and passes all DOP853/segmented-Radau
gates at `a=0.2407010100842176`. The third event gap is `6.3246e-9`, giving
successive finite ratios `4.557/4.697`. EXP-260 freezes the period-192 switch;
no fourth supercritical rung is claimed before child qualification.

EXP-260 passes all six bilateral 256-segment candidates with exact `224/256`
identity. EXP-261 freezes the decisive two-solver parent-unstable/child-stable
test at the negative-mode `0.002` point.

EXP-261 passes every frozen gate. At `a=0.24070100957644772`, DOP853/Radau
classify the period-96 parent as unstable (`1.13241659/1.13237635`) and the
primitive period-192 child as stable (`0.46117807/0.46117779`). FND-094 records
the fourth local supercritical doubling; tangent-sign equivalence remains the
next prospective gate before continuation.

EXP-262 freezes that common-parameter tangent-sign gate. It uses the bounded
continuous phase method already validated by EXP-256, now prospectively, with
the unchanged `1e-6` whole-orbit identity threshold and independent
DOP853/Radau corrections.

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

EXP-262 passes all ten gates. Within-solver sign RMS is
`9.18e-10/5.62e-10`, cross-solver whole-orbit RMS is below `2.72e-8`, and all
four stable moduli remain near `0.491`. Both signs are one period-192 orbit.
EXP-263 freezes eight 256-segment continuation steps toward a fifth event.

EXP-263 passes all eight full steps. Its terminal orbit has exact `224/256`
identity, half-period closure `0.001032`, and preliminary multiplier
`-265.739`. EXP-264 freezes a nine-row, eight-orders-separated block-Floquet
scan before any exact fifth-event claim.

EXP-264 passes with exactly one bracket,
`[0.24070100795063762,0.24070100957644772]`, and minimum transverse-mode
separation `1.146e18`. EXP-265 freezes the exact 256-segment orbit/tangent
solve with segmented Radau parity; interpolation alone is not promoted.

EXP-265 converges in four evaluations with orbit/tangent residuals below
`9.15e-11`, but fails one derived DOP853 flip gate: `1.06496e-7` versus
`1e-7`. Every other reference and Radau gate passes. EXP-266 preserves that
failure and freezes a tighter-step two-solver representation audit with the
same threshold plus cross-solver agreement; no fifth event is yet promoted.

EXP-266 fails the unchanged gate under both tighter solvers: DOP853/Radau
residuals are `2.25e-7/1.58e-7`, although their difference passes `1e-7`.
EXP-267 therefore freezes a genuinely new tighter coupled recorrection with
symmetric `1e-7` solver gates. The fifth event remains unqualified meanwhile.

EXP-267 passes every tightened science gate at
`a=0.24070100861338276`. DOP853/Radau flip residuals are
`6.70e-9/7.60e-8`; orbit/tangent residuals are below
`5.31e-11/1.39e-11`. FND-095 records the fifth exact event and the finite
spacing ratios `4.557/4.697/4.300`, which do not support monotone convergence.
EXP-268 freezes the separate bilateral 512-segment period-384 switch.

EXP-268 passes all six candidates with exact `448/512` identity. The largest
negative/positive candidates have half-period closures
`5.63e-5/5.45e-5` and preliminary stable moduli `0.391/0.433`. EXP-269 freezes
the decisive two-solver stability exchange; period 384 is not yet promoted.

EXP-269 passes every gate. At `a=0.24070100850046297`, DOP853/Radau classify
the period-192 parent as unstable (`1.14929836/1.14909171`) and the primitive
period-384 child as stable (`0.39117576/0.39117648`). FND-096 records a fifth
local supercritical birth and the cascade through stable period 384.

EXP-270 freezes a common-parameter correction of both period-384 tangent signs
under both solvers, followed by continuous whole-orbit phase identity at 8,192
samples. Deeper continuation remains blocked on this sign-equivalence gate.

EXP-270 passes all ten gates after 1,192 seconds. Within-solver sign RMS is
`2.15e-10/3.28e-9`, cross-solver whole-orbit RMS is below `4.33e-8`, and all
four stable moduli remain near `0.412`. EXP-271 freezes eight 512-segment
continuation steps toward a sixth event.

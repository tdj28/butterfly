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

EXP-271 passes all eight full steps. Its terminal orbit retains exact
`448/512` identity, half-period closure `5.04e-4`, and preliminary multiplier
`-533.597`. EXP-272 freezes a nine-row, eight-orders-separated block-Floquet
scan before any exact sixth-event claim.

EXP-272 passes with exactly one bracket,
`[0.24070100810074033,0.24070100850046297]`, and minimum transverse-mode
separation `1.908e18`. EXP-273 freezes the exact 512-segment orbit/tangent
solve with tight-step DOP853 and segmented Radau parity; interpolation alone
is not promoted.

EXP-273 passes every frozen gate at `a=0.24070100830924687`. DOP853/Radau
flip residuals are `1.33e-9/3.62e-8`; all orbit/tangent residuals are below
`2.53e-11`, and exact `448/512` identity passes. FND-097 records the sixth
exact event and the non-monotone finite ratios `4.557/4.697/4.300/4.836`.
EXP-274 freezes the separate bilateral 1,024-segment period-768 switch.

EXP-274 passes all six candidates with exact `896/1024` identity. The largest
negative/positive candidates have half-period closures
`6.10e-6/6.18e-6` and preliminary stable moduli `0.0813/0.0854`. EXP-275
freezes the decisive two-solver stability exchange; period 768 is not yet
promoted.

EXP-275 passes every gate. At `a=0.24070100827074953`, DOP853/Radau classify
the period-384 parent as unstable (`1.22260901/1.22168588`) and the primitive
period-768 child as stable (`0.08362765/0.08362578`). FND-098 records the
sixth local supercritical birth and cascade through stable period 768.
EXP-276 freezes common-coordinate whole-orbit equivalence of both switch
signs before deeper continuation.

EXP-276 passes all orbit-identity gates but fails its sole multiplier-spread
gate: `0.003450` versus `0.002`. Within-solver sign RMS is
`1.39e-8/2.72e-8`, and cross-solver RMS is below `4.11e-8`, so the failure is
isolated to long-product precision rather than orbit mismatch. EXP-277 freezes
a tighter-step repeat with no relaxed threshold.

EXP-277 again fails only multiplier spread, improving it to `0.002661` while
sign and cross-solver whole-orbit RMS remain below `2.94e-8/8.80e-9`.
EXP-278 freezes a canonical common-phase audit from the negative sign selected
independently by EXP-275, retaining the unchanged `0.002` multiplier gate.

EXP-278 passes all twelve gates. On one canonical phase representative,
DOP853/Radau stable moduli are `0.0879289933/0.0879290911`, spread `9.78e-8`,
with exact `896/1024` identity. This resolves the conditioning issue without
rewriting the two failed receipts. EXP-279 freezes eight exact period-768
continuation steps toward a seventh event.

EXP-279 passes all eight full steps. Its terminal orbit retains exact
`896/1024` identity, half-period closure `2.88e-5`, and preliminary multiplier
`-946.310`. EXP-280 freezes a nine-row, eight-orders-separated block-Floquet
scan before any exact seventh-event claim.

EXP-280 passes with exactly one bracket,
`[0.24070100814897039,0.24070100827074953]`, and minimum transverse-mode
separation `1.875e17`. EXP-281 freezes the exact 1,024-segment orbit/tangent
solve with tight-step DOP853 and segmented Radau parity; interpolation alone
is not promoted.

EXP-281 reaches `a=0.2407010081734325` with DOP853 orbit/tangent residuals
`8.61e-11/2.31e-12` and multiplier `-1.00000000535`. It fails only the
independent Radau flip gate: `3.22e-7 > 1e-7`, despite Radau orbit/tangent
residuals `8.90e-11/3.80e-11`, cyclic spread `2.25e-10`, proper-subperiod
closure `7.54e-6`, and exact `896/1024` identity. No seventh event is
promoted. EXP-282 freezes a tighter-step DOP853/Radau precision audit of the
unchanged solved representation; no gate is relaxed.

EXP-282 preserves the failure under tighter immutable evaluation. DOP853 gives
`-0.99999999629`, while Radau gives `-1.00000036358`; the `3.67e-7`
cross-solver difference and Radau `3.64e-7` flip residual fail. All orbit,
tangent, real-spectrum, cyclic, primitive, and exact-identity gates pass.
EXP-283 freezes a deterministic diagnostic comparing that disagreement and the
EXP-280 bracket-secant multiplier change per Float64 `a` increment with the
unchanged `1e-7` gate before another coupled correction is chosen.

EXP-283 passes all six deterministic diagnostics. Float64 spacing at the
candidate is `2.776e-17`; the bracket spans 4,387,556 increments and implies
`1.024e-6` multiplier change per increment. Half the tight solver gap is
`1.836e-7`. FND-099 therefore records a Float64 resolution frontier without
promoting event seven. EXP-284 freezes a dependency-free 50-decimal-digit RK4
pilot on four phase-separated state/variational segments before a full
high-precision multiplier replay.

EXP-284 passes all six gates. Four phase-separated endpoint/transition
convergence ratios are approximately `15.86/15.73`; fine-grid orbit and
tangent mismatch remain below `5.72e-10/3.61e-10`. EXP-285 freezes the full
parallel 1,024-segment Decimal audit with nested 4,096/8,192-step profiles and
four cyclic characteristic-polynomial roots. It supplies a converged
high-precision multiplier at the immutable coordinate only, not event
qualification.

EXP-285 passes nine of ten gates. Full-grid orbit/tangent mismatch remains
below `5.54e-11/1.82e-10`, cyclic spread is `1.82e-43`, and characteristic
residual is `1.01e-49`, but raw 4,096/8,192-step multipliers differ by
`7.25e-5`. Their errors decrease by factor `15.988`, nearly the fourth-order
factor 16. EXP-286 freezes a new 16,384-step profile and prospectively gates
successive order-four Richardson estimates before any extrapolated multiplier
is promoted.

EXP-286 passes all eleven gates. The untouched 16,384-step profile preserves
raw convergence ratio `15.970`; successive Richardson flip estimates differ
by `8.97e-9`, and the newest estimate is `-0.999999994828`. EXP-287 freezes a
fully independent 50-digit RK4 3/8-tableau sequence at all three step counts,
with an unchanged `1e-7` cross-tableau gate. Only a pass can rehabilitate the
failed Float64 event representation and promote the seventh exact event.

EXP-287 passes all thirteen gates from clean commit `d5bfe74`. The independent
raw convergence ratio is `15.960`; successive Richardson flip estimates differ
by `1.06e-8`, and the final RK4 3/8 estimate is `-0.999999994881`. It differs
from the classical-RK4 estimate by only `5.22e-11`. Orbit/tangent matching
remain below `3.76e-11/1.02e-11`, cyclic spread is `7.64e-44`, characteristic
residual is `1.00e-49`, and exact `896/1024` identity passes. FND-100 therefore
qualifies the seventh exact numerical event at `a=0.2407010081734325` while
preserving the earlier Float64 failures as a conditioning result. The new
finite spacing ratio is `2.239`; period-1536 child existence and criticality
remain separate.

EXP-288 freezes that next question before execution. It doubles the qualified
event representation to 2,048 segments, tests both tangent signs at three
predictor lengths, requires exact `1792/2048` section identity, and nominates a
child only if at least two candidates pass every closure, neutral, primitive,
displacement, and period-ratio gate. The analytic Jacobian is now optionally
stored as sparse CSR; a dense/sparse regression test passes and the complete
suite is 300/300. This removes the prohibitive dense 6,146-column storage and
factorization without changing the multiple-shooting equations.

EXP-288 passes all six candidates in 801 seconds. Every correction needs only
two evaluations, all matching residuals are below `1.21e-10`, and all retain
exact `1792/2048` identity and period ratio two. The largest-predictor positive
candidate has half-period closure `4.42e-6`, half-node RMS `6.31e-6`, direct
closure `5.32e-7`, and preliminary modulus `0.686`; the six preliminary
multipliers disagree strongly, so none is promoted. EXP-289 prospectively
selects that candidate by separation and closure, not by its apparent
stability, and freezes independent DOP853/Radau correction. Either consistently
supercritical or consistently subcritical exchange passes; an unresolved
classification fails.

EXP-289 fails only that resolution requirement after 2,686 seconds. DOP853 and
Radau independently classify the child as unstable with moduli
`1.1073340/1.1073277` and relative spread `5.74e-6`; all correction, node,
half-period, identity, and spread gates pass. The parent moduli are
`0.9999973/1.0000022`, straddling one inside the frozen `1e-4` neutral margin.
This points toward a subcritical seventh birth but does not qualify it.
EXP-290 freezes eight sparse period-1536 continuation steps to obtain a farther
child coordinate at which the parent classification can be resolved without
relaxing the margin.

EXP-290 passes nine exact rows after 670 seconds, with no step halving. The
terminal child lies `3.014e-12` below the event, its half-node RMS has grown to
`6.95e-5`, half-period closure is `9.07e-5`, and exact `1792/2048` identity
persists. The initial `a` bend occurs below the Float64 conditioning scale and
is not called a fold without a real `+1` event. Because criticality must be
decided on the same side as the unstable EXP-289 child, EXP-291 instead freezes
independent three-level 50-digit classical-RK4 and RK4 3/8 evaluation of the
period-768 parent at exactly that coordinate. The stable-side signal must be
at least `1e-6`, ten times the `1e-7` cross-tableau gate.

EXP-291 passes nine of ten gates in 438 seconds but fails stable-side
classification. The two extrapolated multipliers are
`-1.000000114960/-1.000000115012`, agreeing within `5.22e-11` and lying only
`1.15e-7` on the unstable side. Thus neither subcritical nor supercritical
seventh birth is promoted. The EXP-289 corrected parent differs from the event
representation by only `1.18e-12` node RMS and `2.30e-10` in period, which is
still enough to dominate this tiny multiplier signal. EXP-292 freezes a
50-digit correction of the orbit itself. Cyclic block elimination reduces the
1,024-segment matching Newton step to a phase-fixed 4-by-4 system; a regression
test verifies the eliminated equations and the full suite is 302/302.

EXP-292 fails the correction, source-neighborhood, and raw-convergence gates.
Although the three matching residuals fall to
`1.18e-16/1.63e-15/1.85e-15`, the corrected nodes move
`7.32e-5/9.21e-5/9.32e-5` from the frozen representation and the tracked
`-1` root collapses toward zero. The unconstrained solve is therefore
consistent with attraction to a nearby lower-period double cover. FND-101
retracts FND-100's event promotion: the secure result is six exact
supercritical births through a stable primitive period-768 child, while the
seventh coordinate and ratio `2.239` return to candidate status. EXP-293 will
couple the high-precision orbit to an antiperiodic tangent so the double cover
cannot satisfy the augmented equations.

EXP-293 is frozen before execution. It integrates the exact 30-component
orbit/first-/second-variational system in 50-digit arithmetic at 1,024 steps
on each of 1,024 segments. Cyclic block elimination reduces every Newton
update to an 8-by-8 system in base state, base tangent, period, and `a`; an
algebraic regression test verifies the eliminated orbit, tangent, phase, and
normalization equations. A period-384 double cover cannot pass the
antiperiodic tangent boundary, and an independent half-orbit separation gate
checks that exclusion directly. This is a formulation pilot only: even a pass
will require multi-resolution and independent-tableau reproduction before the
seventh event is restored.

EXP-293 fails two of four gates after 69 seconds, but resolves the structural
question that motivated it. Five Newton updates reduce maximum orbit and
antiperiodic-tangent residuals to `2.75e-31/1.23e-30`; half-orbit RMS remains
`2.58e-5`, so the augmented solution does not collapse to the lower-period
double cover. The 1,024-step coordinate shifts `-4.50e-9` beyond the frozen
bracket, and maximum along-orbit tangent displacement is `4.16 > 0.1` even
though the normalized base tangent changes only `2.24e-4`. The state and
period neighborhoods pass. No gate is relaxed. EXP-294 will use the complete
Decimal solution as a warm start at 2,048 and 4,096 steps, testing whether the
coordinate and tangent field converge at fourth order into the physical
source neighborhood.

EXP-294 is frozen before execution. It preserves the complete 1,024-step
failure and warm-starts 2,048- and 4,096-step augmented corrections. The three
coordinates and periods must converge with ratios in `[12,20]`; both the finest
and fourth-order Richardson coordinate must enter the untouched EXP-280
bracket. All original residual, source-neighborhood, and primitive-separation
gates remain unchanged. A pass will still require an independent RK4 3/8
correction before event seven is restored.

EXP-294 passes six of seven gates after 241 seconds. Both new augmented
systems converge, and `a` and period show fourth-order ratios
`15.718/15.706`. The 4,096-step coordinate
`0.24070100821945930` and Richardson value `0.24070100823758015` both lie
inside the original bracket; residuals are below `1.32e-26`, state and period
neighborhoods pass, and half-orbit separation remains `2.58e-5`. The sole
failure is maximum pointwise tangent displacement `4.162 > 0.1`, unchanged
across resolution even though the base tangent differs by only `2.24e-4` and
the median direction cosine is `0.99999987`. EXP-295 will prospectively test
the converged representation with the independent RK4 3/8 tableau rather than
relax this historical-source gate.

EXP-295 is frozen before execution. It performs independent RK4 3/8 augmented
corrections at all three 1,024/2,048/4,096-step levels, requiring its own
fourth-order `a` and period convergence. Its finest and Richardson coordinates
must stay in the original bracket and agree with EXP-294 within `1e-10`.
Separate gates compare orbit nodes, the normalized base tangent, and the
globally sign-aligned tangent-line field. Only a complete pass can supersede
the old Float64 tangent representation and restore the seventh event; birth
criticality and period-1536 stability remain separate.

EXP-295 passes all ten gates after 337 seconds. The independent RK4 3/8 `a`
and period sequences converge at `15.721/15.707`; its Richardson coordinate
`0.24070100823760069` differs from the classical value by `2.05e-14`.
Extrapolated periods differ by `3.60e-11`, finest nodes by `1.24e-10` maximum,
and base tangents by `1.61e-13`. The global tangent-line cosine is one to the
reported precision and every pointwise direction passes. FND-102 therefore
supersedes the old Float64 tangent representation and restores the seventh
primitive real-`-1` event near `a=0.24070100823759`. The corrected fifth
finite spacing ratio is `4.244`, not the retracted `2.239`. Only six births
are independently supercritical; period-1536 criticality remains open.

EXP-296 is frozen before execution. It discards the old period-1536 candidates
as criticality evidence and repeats all six sparse bilateral switches from the
passed EXP-295 4,096-step RK4 3/8 event nodes and tangent. Predictor lengths,
DOP853 tolerances, event and secondary-null gates, child residual and
primitivity gates, period ratio, and exact `1792/2048` identity are unchanged.
A pass nominates corrected children only; it cannot decide birth direction.

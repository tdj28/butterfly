# High-period cascade frontier

Date: 2026-08-07
Status: stable period-320 child independently qualified

## Verified result entering this checkpoint

The fixed `(a,c)=(0.245,5.1)` period-doubling cascade is now resolved through
the period-160 parent. Event parameters for 5→10, 10→20, 20→40, 40→80, and
80→160 are `0.1834675907716`, `0.1805372082024`, `0.1798912237616`,
`0.1797506213663`, and `0.1797203688505`. EXP-077 gives the precision-
consistent 160→320 candidate `b=0.1797138833005`.

The successive spacing ratios `4.5363`, `4.5944`, `4.6476`, and `4.6646`
approach the classical period-doubling reference. EXP-066's blind prediction
of the 80→160 event missed EXP-072 by only `1.398e-7`, about `0.46%` of the
preceding event spacing. This is strong local scaling evidence, not by itself
a universality theorem or an explanation of the full `(a,c)` plane.

## Numerical frontier

EXP-078 showed that one-segment shooting at doubled duration near `2092` loses
the flip direction: its smallest singular value was `7.75e-7`, and its switch
returned to the double-covered parent. EXP-079 then passed a frozen
conditioning audit. A 32-segment matching system reduced the smallest singular
value to `9.07e-10`, an `854.3`-fold improvement, while retaining matching
residual `1.25e-9`. Multiple shooting is therefore the adopted high-period
representation.

EXP-080 implemented the analytic segmented corrector and tested it first at the
known 40→80 event. All six frozen corrections converged below `5.06e-13`, and
the derived primary/secondary tangents were orthogonal to `1.67e-16`, but the
largest frozen predictor was too small to enter the independently stored child
branch's parameter range. The experiment failed its identity gate honestly.
Its measured amplitude and parameter displacement motivate the prospectively
frozen, larger-scale EXP-081 recovery without changing acceptance thresholds.

EXP-081 passed. All eight larger-scale corrections converged below
`6.15e-13`, and three candidates independently match the known period-80 child
with full closure below `1.37e-12` and whole-orbit RMS between `2.57e-8` and
`3.43e-6`. The segmented equations, event-nullspace split, branch predictor,
and corrector are therefore validated before use at period 320.

EXP-082 then passed at the 160→320 event. All eight 32-segment corrections
converged below `1.90e-12`; four candidates in the frozen near-event window are
distinct from the double-covered parent by two independent half-period tests.
Both nullspace signs succeed, and the child/parent period ratio agrees with two
to `2.53e-8`. This is the first reliable period-320 candidate set in the
program. EXP-083 now freezes common-parameter orbit identity and a segmented
Floquet calculation, validated first against the known period-80 child.

EXP-083 calibrated the block-Floquet method to `4.07e-8` against the known
period-80 multiplier and found both fixed-parameter period-320 candidates
strongly stable near modulus `0.05497`. Its discrete 32-node identity metric
failed because it could not represent a fractional phase shift. EXP-084 then
exposed a non-unimodal phase objective, rather than hiding the failed optimizer.
EXP-085 replaced it prospectively with deterministic multiresolution search
and passed: phase shift `0.5000000198306`, whole-orbit RMS `1.19e-8`, and
segment endpoint error `5.99e-11`. The stable period-320 child is now
independently identified, closing the sixth supercritical rung numerically.

## Execution order

1. Feed the extended event sequence into a prospective accumulation-point and
   scaling analysis.
2. Continue the stable period-320 branch toward its predicted 320→640 event
   using fixed-parameter segmented correction and block Floquet multipliers.
3. In parallel with later computation, continue orbit-defined flip and
   return-section topology surfaces across the multi-`b` atlas. Raster shrimp
   morphology remains discovery evidence, not a substitute for continuation.

No Runpod funds have been spent on this checkpoint. The current bottleneck is
serial high-accuracy orbit integration and corrector design, so moving the same
code to a GPU would not yet shorten the critical path.

## Seventh event and second prospective prediction

EXP-086 froze the 320→640 prediction at `b=0.1797124942943`. EXP-087 then
bracketed a real `-1` crossing without using that value as a fitted target.
EXP-088 honestly exhausted its refinement budget just outside the precision
gate; EXP-089 resumed from the retained nodes and passed at
`b=0.17971249399393`. The prediction error is `3.00e-10`, only `0.0216%` of
the new spacing, and the new spacing ratio is `4.6681920`.

The period-320 parent event is therefore independently verified. EXP-090 now
uses 64 segments to seek a period-640 child. As before, a switched candidate
will not be called a stable cascade rung until fixed-parameter identity and
segmented Floquet qualification also pass.

EXP-090 produced six accepted period-640 candidates from both signs using 64
segments. EXP-091 then passed the independent common-parameter test at
`b=0.17971235`: stable moduli near `0.0707645`, identical periods, and
phase-aligned whole-orbit RMS `1.39e-8`. The period-640 child is established,
closing the seventh local supercritical rung.

EXP-092 consumes all seven verified event receipts and freezes the next
640→1280 prediction at `b=0.1797121964470`. The latest finite spacing ratio is
`4.6681920`, only `0.0010096` from the unchanged reference, and the updated
accumulation estimate is `0.1797121153539`. The next required evidence is a
signed 64-segment Floquet scan across this prediction; period 1280 is not yet
claimed.

## Frozen period-640 scan

EXP-093 binds the full EXP-091 period-640 qualification and EXP-092 prediction
receipts before execution. Its nine `b` values, correction settings, and
acceptance thresholds are frozen in
`experiments/manifests/EXP-093-scan-period640-predicted-flip.json`. Passing
requires a real signed `-1` bracket no wider than `2e-8`; neither a crossing of
the multiplier modulus nor visual proximity to the prediction is sufficient.

EXP-093 passed on the clean preregistration commit. The signed multiplier moves
from `-0.97414250` at `b=0.17971220` to `-1.04676211` at
`b=0.17971219`, while all nine matching residuals remain below `1.72e-12`.
The `1e-8` bracket midpoint is only `1.447e-9` below the frozen prediction,
about `0.49%` of the predicted event spacing. This is the third successful
prospective cascade prediction, but it is still a bracket rather than a
corrected eighth event. EXP-094 must refine the event before branch switching.

EXP-094 is now preregistered against the full EXP-093 receipt. It permits eight
safeguarded secant trials and keeps the same `1e-8` multiplier residual,
`1e-11` parameter uncertainty, and `5e-8` prospective prediction-error gates
used to decide whether a corrected event exists. A period-1280 branch is out of
scope until this event gate passes.

EXP-094 exhausted all eight trials and failed honestly: its best event estimate
`b=0.1797121964332984` is only `1.370e-11` from the frozen prediction and has
matching residual `1.41e-12`, but multiplier residual `3.57e-8` exceeds the
unchanged `1e-8` gate. The retained signed bracket is `6.02e-12` wide.
EXP-095 binds that failed receipt and permits four more trials with a smaller
endpoint margin; it does not relax any scientific acceptance criterion.

EXP-095 also failed the unchanged `1e-8` multiplier gate, but its four new
positive residuals decrease monotonically from `2.20e-5` to `2.85e-6` while
the negative endpoint remains at `-3.57e-8`. The `1%` safeguard forced
midpoints because the secant root is endpoint-near; this is not evidence of a
Floquet noise floor. EXP-096 binds the resulting `3.77e-13` signed bracket and
changes only the numerical endpoint margin to `0.1%`. Scientific gates remain
unchanged, and a further failure will trigger a precision/segmentation audit.

EXP-096 reached that stopping rule. Its point estimate is still only
`1.370e-11` from the blind prediction and has matching residual `1.40e-12`,
but the closest real multiplier residual is `-3.60e-8`. The final nominal sign
interval is `7.22e-16` wide, at which neighboring double-precision corrections
no longer give a stable enough pointwise multiplier for the `1e-8` equality
gate. The scalar resume path is closed. The next experiment must compare
solver precision and multiplier representations on the wider EXP-093 bracket;
it may not simply add more secant iterations.

EXP-097 is preregistered as that audit. It binds the wide EXP-093 sign bracket
and the final EXP-096 center, compares baseline and tenfold-tighter integration,
and evaluates both the 64-block cyclic spectrum and direct 3-by-3 monodromy
products at four cyclic basepoints. Six corrections run across three local CPU
workers. No GPU or Runpod funds are required for this diagnostic.

EXP-097 passed. Baseline and tight profiles both retain the wide signed
bracket, while block-cyclic and direct-product multipliers agree within
`5.83e-14` and cyclic-basepoint spread is below `6.00e-15`. The tight solver
shifts the center multiplier by `7.750e-6`, diagnosing integration accuracy—not
the multiplier representation—as the prior pointwise limit. EXP-098 now binds
the audit and freezes a tight-solver event refinement on the wide bracket with
independent block/product agreement gates.

EXP-098 failed only the unchanged pointwise multiplier gate after eight tight-
solver trials. Its best residual is `1.376e-7`; matching, parameter uncertainty,
block/product agreement, cyclic spread, and prediction-error gates all pass.
The trial sequence shows the `1%` safeguard forced midpoint evaluations after
an endpoint-near positive trial. EXP-099 binds the exact `9.91e-11` sign
bracket, admits the slope-indicated secant point with a `0.01%` numerical
margin, and leaves every scientific gate unchanged.

EXP-099 also failed, narrowly but decisively: its best tight-solver multiplier
residual is `1.697e-8` against the frozen `1e-8` gate. Matching residual,
parameter uncertainty, prediction error, block/product agreement, and cyclic
spread all pass. The retained sign bracket is `3.22e-15` wide. Per its stopping
rule, scalar refinement is closed and the result remains bracket-level evidence.

DEC-003 adopts the replacement: a square augmented multiple-shooting system
solves all orbit nodes, total period, `b`, and transported tangent nodes with
an anti-periodic boundary condition. The implementation must recover the known
EXP-089 period-320 event before it is allowed to decide the period-640 event.
Period 1280 remains unclaimed.

EXP-100 is preregistered as the mandatory known-event validation. It perturbs
the passed EXP-089 period-320 source by `5e-9` in `b` and solves the 194-variable
augmented orbit/tangent system with a sparse local-dependency Jacobian. The
implementation is not allowed to touch the period-640 target unless it recovers
the known event and passes independent block/direct-product spectral gates.

EXP-100 failed at its frozen 30-evaluation cap after `2367.32 s`. The tangent
condition improved by five orders of magnitude to `2.14e-9`, and four cyclic
direct products independently give `-0.9999999856`, but orbit matching remains
`1.73e-7` and the recovered `b` remains `4.91e-9` from EXP-089. The experiment
therefore does not validate the augmented solver and cannot unlock the
period-640 target. It also found that the generic block-cluster labeling swaps
the near `+1` and `-1` roles at this collision; subsequent validation will
select the flip cluster explicitly by distance to `-1`. The next frozen run
will replace colored finite differences with the exact Rössler second-
variational Jacobian while preserving the equations and scientific gates.

EXP-101 now freezes that replacement. Segment-level and full-system analytic
Jacobians pass centered finite-difference tests, and the run binds both the
original EXP-089 source and failed EXP-100 baseline. It keeps the same seed,
bounds, integrator, reference, and scientific gates, permits 20 exact
residual/Jacobian evaluations, and selects the flip spectrum explicitly by
distance to `-1`. Only a pass may unlock the 64-segment target application.

EXP-101 exhausted that cap and therefore fails, but it resolves both EXP-100
diagnoses. In `207.38 s` it reaches orbit residual `1.78e-9`, tangent residual
`1.77e-10`, and direct flip multiplier `-0.9999999763`; block/direct agreement
is `3.20e-14`. This is `11.4x` faster than EXP-100, and explicit proximity-to-
`-1` selection removes the false cluster-label discrepancy. The remaining
failure is the solver-success flag and reference error `1.086e-9` against the
frozen `5e-10` gate. The next experiment will bind the full state and continue
the exact solve under unchanged scientific thresholds.

EXP-102 freezes that single continuation. It binds EXP-101's stored orbit,
period, `b`, and tangent nodes with zero offset, changes only the phase gauge to
the stored first node, and permits 20 more exact evaluations. A failure closes
the current unscaled trust-region path; a pass unlocks—but does not itself
perform—the period-640 target solve.

EXP-102 passed. It terminates successfully at
`b=0.17971249399303613`, only `8.94e-13` from EXP-089, with orbit and tangent
residuals `9.21e-13` and `1.01e-11`. The independent direct flip is
`-0.99999997682431`; block/direct difference is `8.88e-15` and cyclic spread
is `1.67e-15`. DEC-003's known-event gate is therefore closed, and the
validated exact formulation is now authorized for a separately frozen
64-segment period-640 application. No eighth event or period-1280 child is yet
claimed.

EXP-103 is the now-authorized target application. It binds EXP-099's tight
64-node period-640 state and EXP-102's passed validation, uses the audited
EXP-093 bracket `[0.17971219,0.17971220]` as hard bounds, and retains the frozen
prediction solely as a `5e-8` comparison gate. Passing would correct the eighth
parent event, but a period-1280 child and supercriticality remain separate
future qualifications.

EXP-103 passed in three evaluations at `b=0.17971219643223899`. The frozen
prediction misses by only `1.476e-11`; orbit/tangent residuals are
`1.46e-12`/`7.81e-12`, the direct flip multiplier is
`-0.999999999809874`, and block/direct agreement is `6.66e-15`. This corrects
the eighth parent event and completes the third prospective prediction test.
The new finite spacing ratio is `4.6689869`. It does not yet add an eighth
supercritical rung: period-1280 switching, common-parameter identity, and
Floquet stability are the next locked steps.

EXP-104 freezes the switch. It doubles EXP-103's orbit nodes and constructs the
secondary direction directly from the passed anti-periodic tangent field, with
a repeated flow component enforcing the phase row. Two amplitudes and both
signs are attempted with 128-segment tight multiple shooting. Passing creates
candidates only; stability and an eighth supercritical rung remain locked.

EXP-104 passed all four attempts. Its tangent-informed direction has null
residual `1.38e-12`; both signs converge at both amplitudes with matching
residuals below `2.24e-12`. Half-node RMS and half-period closure both double
when the predictor doubles, while the period ratio remains within `9.45e-10`
of two. A distinct period-1280 candidate branch is established. Common-
parameter identity and 128-block Floquet stability remain the final gates for
an eighth supercritical rung.

EXP-105 freezes those final gates at common parameter `b=0.17971215`, using
both EXP-104 signs from predictor `0.001`. It requires deterministic dense-
orbit phase identity, period agreement, persistent half-period distinctness,
and independently stable 128-block Floquet spectra. Only a pass closes the
eighth supercritical rung.

EXP-105 passed. Both signs correct to identical period `8367.041654978086` at
`b=0.17971215`; phase-aligned whole-orbit RMS is `3.94e-8`, endpoint error is
`2.70e-12`, and half-node RMS remains `1.086e-4`. Independent 128-block
dominant moduli are `0.4261745532` and `0.4261741560`. The stable period-1280
child is established, closing the eighth local supercritical rung. The active
frontier now returns to continuation of flip/grazing sets, reinjection, and
global parameter-plane topology.

DEC-004 now makes the next frontier executable: a scalar return-map branch
oracle must pass graph-likeness, domain coverage, critical-point prominence,
and bootstrap gates or return `unresolved`. Synthetic one/two/three-branch and
multivalued controls pass. EXP-106 freezes the first real Rössler calibration
on the published chaotic `(0.2,0.2,20)` control and three nearby section
offsets; it prospectively expects a robust two-branch relation.

EXP-106 fails that expectation cleanly: all three offset sections resolve as
three branches with full domain coverage, conditional spread `0.01832027`, and
100/100 bootstrap agreement. Both critical points drift by only about
`2.2e-6` across the offset family. This is the first modern section-robust local
three-branch evidence relevant to Jones, but it is not yet a two/three-branch
transition or reinjection result. Coordinate, orientation, threshold, and
nearby-parameter sensitivity are now the binding next audit.

EXP-107 is now preregistered to perform that audit without post-result tuning.
It crosses five nearby `(a,c)` points, three section offsets, both genuinely
distinct crossing orientations, both nondegenerate scalar coordinates, and
seven bin/smoothing/prominence choices. The primary gate tests persistence of
the negative-orientation `x` result in 105 cells; a separately reported strong
diagnostic tests all 420 representation cells. This distinction matters
because a scalar projection's critical-point count is not automatically a
topological invariant.

EXP-107 passed its primary gate with no exceptions. All 105 negative-oriented
`x` cells and all 105 independent `z` cells resolve as three branches; every
bootstrap consensus is `1.0`, coverage is at least `0.94`, and conditional
spread is at most `0.02502`. The result survives the frozen nearby-parameter,
section-offset, binning, smoothing, and prominence perturbations.

The strong representation diagnostic failed in a scientifically useful way.
The positive-oriented `x` projection is bootstrap-unstable in 102/105 cells
and resolves as five only in three 30-bin cells; positive-oriented `z` never
covers enough of its normalized domain. We therefore have a robust local
three-branch object on the historically relevant negative half-plane, plus
direct evidence that the full topological explanation must retain the
two-dimensional Poincare map. The next executable frontier is a prospective
search for the qualified map's two/three boundary, followed by a
two-dimensional reinjection observable.

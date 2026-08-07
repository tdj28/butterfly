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

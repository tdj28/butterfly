# High-period cascade frontier

Date: 2026-08-07
Status: period-320 candidates found; independent stability qualification next

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

## Execution order

1. Require EXP-083 to identify both switch signs as one stable period-320
   orbit using independently fixed-parameter segmented corrections.
2. Feed the extended event sequence into a prospective accumulation-point and
   scaling analysis.
3. In parallel with later computation, continue orbit-defined flip and
   return-section topology surfaces across the multi-`b` atlas. Raster shrimp
   morphology remains discovery evidence, not a substitute for continuation.

No Runpod funds have been spent on this checkpoint. The current bottleneck is
serial high-accuracy orbit integration and corrector design, so moving the same
code to a GPU would not yet shorten the critical path.

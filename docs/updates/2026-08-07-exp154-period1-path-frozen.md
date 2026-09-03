# EXP-154 period-1 path qualification frozen

Date: 2026-08-07

The next Jones Figure 2 gate now follows the orbit rather than only the
equilibrium. EXP-154 freezes 118 phase-corrected points from the qualified Hopf
neighborhood to the reported hub on `(a,b)=(0.1798,0.2)`, continuous winding
identity, a square-root Hopf amplitude test, Floquet stability tracking, and
six Radau cross-checks.

The design is explicitly pilot-informed. Passing would qualify the period-1
family along this fixed path, but the equilibrium homoclinic connection remains
a separate global boundary-value problem.

The first clean execution failed only the exact point-count gate: it emitted
119 rows because a below-seed independent checkpoint was placed in both
directions and the seed was duplicated. Every scientific tolerance passed.
EXP-155 freezes the direction-aware correction without changing any scientific
point or threshold.

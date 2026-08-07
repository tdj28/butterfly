# EXP-063 — Switch the period-20 flip to period 40

Status: executed; failed two-arm gate

Represent the verified period-20 parent over twice its duration at the EXP-062
`-1` event. Apply the generalized extended-shooting nullspace switch to both
secondary directions with step `0.0015` and 16 requested steps per arm.

Pass if the smallest singular value is `<=1e-7`, tangent dot is `<=0.25`, both
arms contain at least eight corrected points, endpoint distance from the
doubled parent is `>=1e-5`, endpoint half-period closure is `>=0.005`, and
every full closure is `<=1e-8`. Passing supplies a period-40 candidate; an
independent fixed-parameter phase/stability qualification remains mandatory.

The clean run at `06dbbf4` failed. The smallest singular value `3.19e-8` and
tangent dot `5.55e-17` pass, but the nominal negative direction corrects back
onto a doubled parent (half-period closure near `2e-11`) and the positive
direction supplies only five distinct points before crossing the frozen guard.
Receipt SHA-256:
`2b3e429dda180d5710c0ef0c493c3a02bc5d549eb362706631534297dc710a31`.

The positive-direction prefix is nevertheless a well-closed, half-period-
distinct period-40 candidate. Its first point is strongly stable at
`b=0.179822410665`. EXP-064 treats this as a one-arm candidate and requires
independent recovery from a perturbed trajectory at fixed `b=0.1798`, together
with parent/child stability exchange and period ratio. The failed two-arm
criterion is not retroactively changed.

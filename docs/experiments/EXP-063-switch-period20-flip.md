# EXP-063 — Switch the period-20 flip to period 40

Status: preregistered after EXP-062; pending clean execution

Represent the verified period-20 parent over twice its duration at the EXP-062
`-1` event. Apply the generalized extended-shooting nullspace switch to both
secondary directions with step `0.0015` and 16 requested steps per arm.

Pass if the smallest singular value is `<=1e-7`, tangent dot is `<=0.25`, both
arms contain at least eight corrected points, endpoint distance from the
doubled parent is `>=1e-5`, endpoint half-period closure is `>=0.005`, and
every full closure is `<=1e-8`. Passing supplies a period-40 candidate; an
independent fixed-parameter phase/stability qualification remains mandatory.

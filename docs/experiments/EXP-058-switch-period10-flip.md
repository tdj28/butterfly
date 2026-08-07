# EXP-058 — Switch the period-10 flip to period 20

Status: preregistered after EXP-057; pending clean execution

Represent the verified period-10 parent over twice its fundamental duration at
the EXP-057 `-1` event. Use the nullspace of the extended shooting Jacobian to
separate the parent tangent from a secondary branch direction, then continue
both signs for 14 pseudo-arclength steps.

Pass if the smallest singular value is `<=1e-7`, tangent dot is `<=0.25`, both
arms contain at least 10 corrected points, endpoint distance from the doubled
parent is `>=1e-5`, endpoint half-period closure is `>=0.01`, and every full
closure is `<=1e-8`. No section-count gate is used. Passing establishes a
period-20 branch candidate; phase-invariant arm identity and parent/child
stability still require an independent fixed-parameter qualification.

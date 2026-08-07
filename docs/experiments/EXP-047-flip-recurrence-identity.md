# EXP-047 — Fundamental recurrence identity of the flip component

Status: preregistered after EXP-046; pending clean execution
Manifest: `experiments/manifests/EXP-047-flip-recurrence-identity.json`
Claim target: determine whether the continued flip is period 3→6 rather than period 5→10

## Hypothesis and method

EXP-046 found the orbit-defined fold predictions consistently inside the
independently generated period-3/6 raster band. At the source, separated, and
fold events, correct the stable parent at `b=b*-0.0004` and stable child at
`b=b*+0.0004`. Starting directly on each corrected orbit, collect crossings of
the same legacy small-equilibrium half-plane used by EXP-021 and classify
minimal recurrence prospectively.

## Acceptance and implications

All three parents must classify as fundamental period 3 and all three children
as fundamental period 6 with at least six repeated recurrences. Passing retains
the complete local flip/fold geometry but requires reclassifying the component
from “period-5 flip surface” to “period-3→6 flip surface.” It would also prove
that the continuation originating from the EXP-022 period-5 seed switched
families before the event; locating that switch remains a separate audit.

Failure leaves the EXP-046 raster mismatch unresolved and triggers direct
section-crossing counts and section-sensitivity checks rather than a label
change.

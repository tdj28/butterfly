# EXP-047 — Fundamental recurrence identity of the flip component

Status: executed; passed
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

## Result and decision

The clean run at commit `012cb53fa8b38642fedad69fb64443efe1a0b369`
passed all six frozen classifications. At the source, separated-`c`, and
minimum-`b` fold samples, every parent is fundamental period 3 and every child
is fundamental period 6. Parent recurrence errors are `1.24e-13` to
`1.65e-12`; child errors are `2.51e-13` to `3.26e-13`.

The complete receipt SHA-256 is
`9f450b853543d7f84549a5d190932dfbcdd8f8d55350983ca60a243cd7a18889`.

Reclassify the local object as a supercritical period-3-to-period-6 flip
surface with a smooth projection fold line. All numerical geometry from
EXP-028 through EXP-045 remains valid; the “period-5” family identity does not.
The period-5 source continuation switched to the period-3 family before the
event. A separate provenance audit must locate the first identity change.

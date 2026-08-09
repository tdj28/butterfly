# EXP-174 — Blind Figure 6 landmark classification

Status: preregistered; not yet executed

## Question

What recurrence labels and fundamental periods are present at the ten
approximate parameter landmarks printed in Jones Figure 6 when the coordinates
are evaluated exactly as printed, without supplying expected words or periods?

## Frozen design

The manifest binds the source transcription by SHA-256 and loads its ten
parameter triples in printed order. It deliberately contains no expected
periods, landmark-to-word associations, or local search radius.

Two initial states are tested. DOP853 must return the same recurrence signature
after 800- and 1600-time-unit transients. At the longer profile, independent
Radau must return the same signature. Both profiles collect up to 160 crossings
on the recovered Jones half-plane and test the smallest period through 16 using
six repeated blocks. Every integration must contribute at least 96 crossings.

The experiment passes its numerical gate only if all integrations succeed and
the solver/profile comparisons agree. A consistently unresolved landmark is a
valid scientific outcome because the printed coordinates are explicitly
approximate. Initial-condition disagreement is reported rather than coerced
into one label.

## Claim boundary

EXP-174 is reconnaissance for the Figure 6 target. It cannot validate a
symbolic partition, Jones word, `p -> p+1` arrow, caustic, mutant-shrimp
connection, or homoclinic mechanism. No parameter refinement is permitted in
this experiment.

# EXP-315 passes; solver-relative criticality audit frozen

Date: 2026-08-17

EXP-315 passed both two-step event refinements. The DOP853 and Radau event
intervals are each about `1.5e-13` wide and are disjoint by `1.49575e-13`.
This quantifies the numerical event-location uncertainty that made a shared
absolute coordinate unsuitable for the eighth-birth classification.

EXP-316 is now frozen. It corrects the same multiplier-blind primitive
period-3072 candidate and its parent at a common relative coordinate: exactly
`5e-13` above each solver's own upper event bound. No preliminary multiplier
is used to select the child. The prospective prediction is a stable parent and
unstable child under both solvers, which would classify the eighth birth as
locally subcritical.

All EXP-310 classification and identity gates remain, with explicit direct
closure and neutral-mode bounds added for every corrected family. Failure is
preserved if either solver remains neutral, the child loses its primitive
identity, or the two event-relative representations disagree.

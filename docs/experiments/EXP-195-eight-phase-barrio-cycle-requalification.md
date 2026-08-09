# EXP-195 — Eight-phase Barrio-cycle requalification

Status: preregistered; not yet executed

## Question

Do the otherwise-qualified EXP-194 candidates pass when the target-section
phase count is corrected from six historical-section returns to eight
Barrio-section returns?

## Frozen computation

EXP-195 binds the complete failed EXP-194 candidate artifact by SHA-256. It
does not reintegrate, correct, refit, or modify an orbit. For each row it copies
all data and all checks, then recomputes only `barrio_crossing_count` as true
when the declared section is `barrio_positive_x`, the recorded count is eight,
and the state array contains exactly eight finite three-dimensional points.
Every other original check must already be true. At least 55 candidates must
pass.

Manifest:
[`../../experiments/manifests/EXP-195-eight-phase-barrio-cycle-requalification.json`](../../experiments/manifests/EXP-195-eight-phase-barrio-cycle-requalification.json).

## Claim boundary

Passing establishes a reusable set of corrected stable flow orbits represented
by all eight Barrio-section phases. It does not establish continuous family
identity or either critical membership. A separate hash-frozen GPU scan must
reconstruct the Barrio z return map at two RK4 steps and rank both critical-to-
orbit residuals without symbolic targets.

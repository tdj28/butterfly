# EXP-200 — Lower-c high-support signed-residual scan

Status: prospectively frozen; execution requires authorization to transfer the
264,429-byte derived candidate artifact to a task-owned GPU worker

## Question

Does quadrupling survivor-ensemble support recover a robust three-branch map
on the lower-`c` side selected by EXP-199, and does the strictly positive second
critical residual reach zero before that branch is lost?

## Frozen design

EXP-199 found that its first residual crosses zero but its second remains
positive and decreases toward the lowest eligible `c`. EXP-200 therefore
selects every already-qualified EXP-198 stable orbit in the closed rectangle
`a in [0.21555,0.21565]`, `c in [7.264,7.34]` at `b=0.2`. This deterministic
rule yields 168 candidates and changes no orbit data. Its manifest and the
derived artifact are hash-bound before any new return map is computed.

The GPU ensemble grows from 2,048 to 8,192 initial conditions. Minimum survivor
and return-pair gates grow by the same factor. The positive-x Barrio section,
scalar `z` return coordinate, capture definition, five oracle variants, two
RK4 steps, critical-location and survivor parity, direct-center thresholds,
and same-assignment four-corner bracket rule remain unchanged from EXP-199.

Candidate selection manifest:
[`../../experiments/manifests/EXP-200-lower-c-candidate-selection.json`](../../experiments/manifests/EXP-200-lower-c-candidate-selection.json).
GPU manifest:
[`../../experiments/manifests/EXP-200-lower-c-high-support-signed-residual-scan.json`](../../experiments/manifests/EXP-200-lower-c-high-support-signed-residual-scan.json).

## Claim boundary

A passing direct point or signed bracket is only a candidate for a coupled
adaptive solve. A persistent two-branch classification at higher support would
show that EXP-199's lower-`c` loss is not explained by initial-condition count
alone, but it would not prove a topological branch destruction. A negative
result cannot exclude a center outside this targeted rectangle or beyond the
coverage-incomplete EXP-198 orbit family.

Prepared local artifact: `artifacts/EXP-200/candidates.json`, 264,429 bytes,
SHA-256 `818c93c0d65b1cbbd2109995c0ad6fcfdb058b9dc180396df910c9c9889c85eb`.

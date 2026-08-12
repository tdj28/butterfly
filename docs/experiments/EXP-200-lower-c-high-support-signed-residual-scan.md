# EXP-200 — Lower-c high-support signed-residual scan

Status: executed; strict support-recovery gate failed and exposed smoothing-
scale sensitivity

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

## Result

The quadrupled-support profiles retain roughly 49,000 return pairs near the
selected point, but only 10 and 9 of 168 candidates pass the complete robust
three-branch oracle at `dt=0.01` and `dt=0.005`. Eight agree across steps,
below the frozen minimum of 40. Their maximum survivor-fraction and critical-
location differences are only `0.00281` and `0.000936`, so numerical step
parity is not the limiting issue.

The failure is structured. At both steps, all four baseline bin-count and
prominence variants return three branches for 125 candidates. For 104 of
those, the sole high-smoothing (`1e-4`) variant returns two branches at both
steps. Quadrupling support therefore does not restore strict consensus and
rules out simple sample scarcity as the dominant cause. It does not qualify a
topological loss of the third branch: the same well-supported data contain a
shallow critical that survives the baseline fits and is erased at the higher
smoothing scale.

The eight strict survivors contain no center nomination. Their selected phase
assignment is `[7,5]`; no point passes any direct gate, and the closest point
at `(a,c)=(0.21558,7.32)` retains a positive second residual of `0.03413` and
`0.03451`. A prospectively defined scale-aware smoothing ladder is now required
before continuing that residual beyond the lower-`c` boundary.

Raw receipt: `artifacts/EXP-200/receipt.json`, 891,736 bytes, SHA-256
`63199e4171c1f5a5c1fc1e309804b5f97b693567076c87ab6a94ac1b14fb4497`.
Compact receipt: [`receipts/EXP-200.json`](receipts/EXP-200.json).

## Remote execution

The lowest-cost secure A4000 had no live instance. Secure A4500 worker
`rq2b826twhlu0l` ran at `$0.25/hour`; remote/local source, candidate, and output
hashes match. Two invocations stopped before integration while the archive's
dual import roots were diagnosed. The unchanged run used `PYTHONPATH=.:python`.
The worker was terminated immediately after retrieval, the account pod list was
empty, and elapsed time bounds cost below `$0.11`.

# EXP-122 — Blind saddle midpoint at `a=0.147`

Status: passed

## Question

Which side of the qualified sampled saddle transition contains the midpoint
`a=0.147` at fixed `(b,c)=(0.2,20)`?

## Blind classification

The case has no expected branch label. For every run and coordinate, the
EXP-121 coverage-censor rule is evaluated independently under candidate counts
two and three. Exactly one candidate must pass. All seven runs and both
coordinates must then select the same count, satisfy the unchanged support,
survival, critical-drift, integration, cycle, and DOP853/Hermite gates, and
retain the complete failure if neither or both candidates pass.

New scrambled-Sobol seeds 126--128 use a `2^14,2^15,2^16` ladder. This lies
between the qualified control scale and the eightfold `a=0.145` scale while
retaining a fine run as large as the prior target baseline.

If the blind label is two, the sampled bracket narrows to `[0.147,0.149]`; if
it is three, it narrows to `[0.145,0.147]`. A pass still does not prove
continuity or locate an exact TBA point.

Immutable manifest:
`experiments/manifests/EXP-122-blind-a147-saddle.json`.

## Result

The clean `57e629b` run passes in `272.07 s`. All 14 run--coordinate decisions
uniquely select two branches. Of 210 variant cells, 207 resolve normally and
three are admissible coverage censors; no cell is rejected or selects three.
The weakest run retains 350 survivors and 3008 pairs, maximum across-run
critical drift is `0.01499`, and every numerical gate passes. The sampled
bracket narrows to `[0.147,0.149]`.

Raw receipt SHA-256:
`938896accbfef79e2212588b3174a6ec2f21a3ae9dc51038f925e801932f1928`.

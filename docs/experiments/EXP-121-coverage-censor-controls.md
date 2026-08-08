# EXP-121 — Prospective coverage-censor qualification

Status: preregistered; not executed

## Question

Can a return-map oracle treat a fixed-width coverage failure as right-censored
rather than topologically contradictory without weakening the two/three-branch
distinction?

## Frozen rule

For every run and coordinate, at least 12 of 15 oracle variants must resolve
the expected branch count normally. Every remaining variant must:

- fail only `insufficient invariant-domain coverage`;
- retain coverage of at least `0.65`;
- remain below the unchanged `0.08` graph-likeness spread gate;
- contain exactly the expected number of nominal critical points; and
- remain inside the unchanged `0.03` within-run critical-span gate when its
  nominal critical points are included.

Any opposite resolved branch count, noncoverage failure, missing/extra critical
point, excessive spread, or excessive drift fails the experiment. The
unchanged across-run span, survival, support, DOP853/Hermite, cycle, and
integration gates also remain binding.

## Independent data and controls

Seven new scrambled-Sobol ensembles use seeds 123--125. The published
`a=0.118` two-branch and `a=0.149` three-branch controls use the qualified
`2^12,2^13,2^14` ladder. The `a=0.145` target uses the identical construction
with a three-power offset, `2^15,2^16,2^17`, because EXP-120 prospectively
showed that smaller ensembles were support-limited there.

All three cases and both coordinates must pass, and the ordered labels must be
exactly one nondecreasing two-to-three transition. A pass qualifies
`a=0.145` as a two-branch saddle and narrows only the sampled bracket to
`[0.145,0.149]`. It does not locate a continuous TBA curve. A failure is
retained without threshold revision.

Immutable manifest:
`experiments/manifests/EXP-121-coverage-censor-controls.json`.

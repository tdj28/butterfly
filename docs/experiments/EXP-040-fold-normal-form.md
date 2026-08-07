# EXP-040 — Normal-form qualification at the event-curve b fold

Status: preregistered; pending clean local execution
Manifest: `experiments/manifests/EXP-040-fold-normal-form.json`
Claim target: persistence or change of the pitchfork-like mechanism near a fold

## Hypothesis and method

At the EXP-035 minimum-`b` event near
`(a,b,c)=(0.2185131281,0.2031697977,5.1)`, the periodic-orbit event retains the
supercritical pitchfork-like quotient normal form qualified by EXP-031 and
EXP-039.

Use the accepted fold event directly from the hash-bound EXP-035 trace. Repeat
the complete separated-point protocol: correct the primary branch on both
sides, derive the secondary null direction, switch and continue both coordinate
signs, identify invariant cycles modulo phase, and prospectively fit separation
and Floquet deviations at five positive `b-b*` offsets.

## Acceptance and limits

The acceptance gates are identical to EXP-039: at least twelve switched points
per direction, phase-copy RMS at most `1e-5`, primary-secondary RMS at least
`1e-2`, all closures below `1e-8`, all-point stability exchange, separation
exponent in `[0.4,0.6]` with `R^2 >= 0.98`, and median multiplier ratio in
`[1.5,2.5]`.

Passing supports persistence of the local mechanism at the surface fold.
Failure may instead reveal a changed unfolding, wrong positive control side,
or a branch-switch resolution problem; those possibilities must be separated
before interpreting a failed gate as changed dynamics.

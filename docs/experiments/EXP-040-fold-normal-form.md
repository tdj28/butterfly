# EXP-040 — Normal-form qualification at the event-curve b fold

Status: executed; passed
Manifest: `experiments/manifests/EXP-040-fold-normal-form.json`
Claim target: persistence or change of the local mechanism near a fold; reclassified by EXP-041

> **Reclassification after EXP-041.** The measurements below remain valid. At
> this fold, too, the stored parent closes at half-period with multiplier `-1`;
> the apparent full-period `+1` event is a double-covered fundamental flip.

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

## Result

The clean run at commit `f48476b6ec0b72786d19c69a8f57a8f137ced4c2`
passed all frozen gates. Both coordinate directions supplied all 24 switched
points. At the largest offset the representations align to phase-invariant RMS
`7.56e-8`; stability exchange holds at all five offsets; maximum closure is
`1.05e-12`.

The separation exponent is `0.49287781` with `R^2=0.99996910`. The multiplier-
deviation ratio has median `1.99691` and range `[1.98817,1.99922]`, even closer
to the cubic normal-form value two than at the two nonfold samples. The complete
receipt SHA-256 is
`d2a143549fe085c16ce318c8178ff659541469fc87c83bea2ed67aac8b20cd28`.

The three-point comparison is
`artifacts/EXP-040/EXP-031-039-040-normal-form-comparison.png` (SHA-256
`5838e807b172fcdb30254320852c68edf80451f467804409b232f86e1b9233c8`).

## Decision

Accept persistence of the supercritical square-root second-iterate normal form
at the event-curve minimum in `b`. EXP-041 subsequently identifies the event as
a double-covered fundamental flip. The fold changes how the event set
intersects parameter slices but does not destroy the observed branch opening
or stability exchange. This directly supports a mechanism for repeated
windows: one folded flip surface can produce multiple slice crossings, each
carrying the same local stability-exchange structure.

The former “pitchfork-like” qualifier is superseded by EXP-041. The two
switched coordinates are half-period phase copies of one period-doubled child
cycle; no unknown spatial symmetry is needed to explain them.

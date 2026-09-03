# EXP-044 — Extended c=5.3 flip-surface slice

Status: executed; passed
Manifest: `experiments/manifests/EXP-044-extended-c53-flip-slice.json`
Claim target: resolve the only EXP-043 slice without a `b`-projection reversal

## Hypothesis and method

The `c=5.3` trace in EXP-043 was still approaching its minimum `b` when the 60
frozen steps ended. Continue directly from its last two hash-bound points for
30 additional steps with the same pseudo-arclength step and solver.

## Acceptance and limits

At least 20 new points must correct, the combined 60+ point trace must contain
at least one reversal in `b`, and all event/arclength residuals must remain
below `1e-8`.

Passing, combined with the four reversals already observed by EXP-043, supports
a local fold line across all five sampled `c` values. It does not retroactively
make EXP-043 pass its independent `a<=0.225` gate, and it does not establish
the global topology of the surface.

## Result and decision

The clean run at commit `ce4b32ddc2ec57b32a6ad4109d3ffd641537f5fb`
passed every gate. All 30 new points corrected, for 90 combined points. The
combined trace reverses once in `b`, with its sampled minimum at
`(a,b,c)=(0.20771620,0.15277672,5.3)`. Maximum new-point closure is
`2.45e-12`, eigen residual `4.12e-13`, and arclength residual `3.34e-15`.

The complete receipt SHA-256 is
`5973d62aa29a701eef3f0b389d0061ba62bfbc7ff3daec1fcf166580d8463dcc`.

Accept local fold persistence at the fifth sampled `c` value. Combined with
EXP-043, all five sections now reverse in `b`. EXP-043 remains formally failed
under its original independent reach gate; EXP-044 supplies new successor
evidence rather than altering that record.

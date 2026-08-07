# EXP-044 — Extended c=5.3 flip-surface slice

Status: preregistered after EXP-043; pending clean execution
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

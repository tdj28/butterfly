# EXP-043 — Fold-safe multi-c flip-surface slices

Status: preregistered; pending clean execution
Manifest: `experiments/manifests/EXP-043-fold-safe-flip-surface-slices.json`
Claim target: persistence of the EXP-035 projection fold under changes in `c`

## Hypothesis and method

The minimum-`b` reversal found on the fixed-`c=5.1` flip curve is not an
isolated slice accident. It persists across the local EXP-038 surface patch and
therefore forms a fold line on the three-parameter flip surface.

At each frozen value `c in {4.9,5.0,5.1,5.2,5.3}`, take the accepted EXP-038
events at `a=0.24125` and `a=0.24` as the oriented seed pair. Continue the full
double-covered flip event system for 60 pseudo-arclength predictors toward
lower `a`. This representation is retained because it is the already qualified
event system; EXP-041/042 establish its fundamental flip meaning.

## Acceptance and limits

Each slice must produce at least 30 corrected points, reach `a<=0.225`, and
keep closure, eigencondition, flow-orthogonality, and arclength residuals below
`1e-8`. At least four of five slices must show a reversal in the `b` projection.

Passing supports a local fold line on the flip surface and supplies a
fold-safe strip suitable for atlas overlays. It does not prove global surface
connectivity, establish a cusp, or show that the surface bounds every shrimp.
Failure will be retained as either evidence against fold persistence or a
resolution/guard limitation, according to the recorded diagnostics.

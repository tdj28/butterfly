# Signed saddle-boundary observable checkpoint

Date: 2026-08-07
Status: implementation and calibration passed; blind target frozen

## Outcome

The local PIM transition now has a continuous-valued companion candidate rather
than only an integer branch count. The new observable is the normalized return-
map derivative at the lower occupied support. It is negative for all frozen
two-branch controls and positive for all frozen three-branch controls across
both scalar coordinates, both censor horizons, and all 15 oracle variants.

The weakest existing magnitudes are `0.5227` on the local two side and `0.3715`
on the local three side. EXP-129 freezes a conservative `0.1` resolution floor
and tests the untouched midpoint `a=0.148125`. The implementation adds explicit
unresolved outcomes for sign disagreement, weak slopes, insufficient support,
and degenerate coordinates; the full suite passes 98 tests.

## Why it matters

If the midpoint slope sign prospectively agrees with the blind branch count,
we gain a scalar quantity suitable for parameter sampling and candidate root
continuation. That is a real step toward a computed TBA locus. It remains a
section/coordinate-bounded statistic from the same PIM states, so the next
level after EXP-129 is a mesh, root brackets, held-out curve predictions, and
independent section/two-dimensional-map validation—not an immediate claim of a
global topological curve.

## Next execution item

Run EXP-129 from its clean preregistration commit, preserve the raw receipt and
state hashes, then either begin signed level-set continuation if it passes or
diagnose the first coordinate/horizon/variant disagreement if it fails.

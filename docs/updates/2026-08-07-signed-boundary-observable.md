# Signed saddle-boundary observable checkpoint

Date: 2026-08-07
Status: held-out midpoint prediction passed

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

## Target result

The untouched `a=0.148125` target passes as two-branch in all 60 branch-oracle
cells. All 60 signed fits are negative and predict the same class, with the
weakest absolute slope `0.4994`, almost five times the frozen floor. Both
horizons and coordinates agree, all six PIM lines complete, and no lifetime
integration fails. The finite bracket is now `[0.148125,0.14825]`.

The next action is no longer pure midpoint bisection. Use this qualified sign
in a transverse `(a,c)` discovery/validation pilot and identify whether the
sharp support entry is mediated by an unstable-orbit/manifold collision.

# FND-043 — Branch class prospectively predicts lobe exclusion

Status: passed EXP-149 after blind EXP-148

## Finding

At the untouched midpoint `a=0.1481875`, the independently reconstructed
nonattracting saddle is two-branch and excludes the already frozen UPO left
lobe. All six PIM access-line/horizon clouds contain zero post-burn-in states
below the frozen boundary `y=-31.135026064071056`, while the independent UPO
atlas contains 989 fine and 558 nested-coarse lobe points.

The binary relation and every threshold were committed before the blind PIM
run. Only the resulting EXP-148 paths and hashes were inserted afterward.

## Implication for Jones

This is the first held-out support for lobe membership as the dynamical
companion to the two/three-branch saddle classification. Together with the
retrospective three-side inclusion result and persistence of the recovered UPO
families, it strengthens a pruning or reinjection mechanism over simple local
orbit birth or death.

It does not yet show which stable and unstable manifold sheets intersect,
establish transverse versus tangent contact, recover reinjection rotation, or
continue a global topology-change curve. The next mechanism gate must be an
exact manifold-intersection or symbolic-pruning residual.

Tracked receipt: `docs/experiments/receipts/EXP-149.json`.

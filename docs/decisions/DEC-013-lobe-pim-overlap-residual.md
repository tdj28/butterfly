# DEC-013 — Use lobe/PIM overlap before inverse stable manifolds

## Decision

The next direct mechanism diagnostic will compare the capture-truncated UPO
unstable lobe with the independently reconstructed PIM saddle in the full
two-dimensional Barrio section. It will not infer a stable manifold by
backward Float64 integration.

The left-lobe domain is defined by `y < -31.135026064071056`, the least
restrictive upper endpoint of the independently qualified first critical-point
interval in the EXP-128 three-branch saddle. For each PIM access line and both
128/256-return constructions, the diagnostic asks whether states in that
domain exist and, if so, measures their directed nearest-neighbor distance to
the UPO unstable-lobe atlas in scaled `(y,z)` coordinates.

## Why

The Rössler return is extremely dissipative. A representative lag-3 UPO has a
full-period section-map singular value near `7e-16`; direct backward DOP853
integration misses a forward/backward section round trip by about `4.4e-4`
scaled units. Treating that inverse as a stable manifold would be misleading.

The overlap residual instead tests a concrete distinction. An unstable escape
lobe may exist without belonging to the nonattracting saddle. Reinjection into
the invariant saddle requires PIM states in the lobe and geometric agreement
with the unstable atlas. This is closer to Jones's proposed reinjection than
finite-horizon attractor-capture timing, while remaining weaker than a proved
stable/unstable-manifold intersection.

## Scope

EXP-145 is retrospective because its source artifacts and the exploratory
distance calculation predate its manifest. A pass can select this residual for
a held-out parameter test; it cannot by itself establish a bifurcation,
connection, pruning front, or causal explanation of the parameter-plane hub.

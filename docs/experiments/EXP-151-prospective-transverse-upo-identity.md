# EXP-151 — Prospective transverse UPO primitivity and identity audit

Status: method and gates frozen before EXP-150 execution; source hash pending

## Question

After EXP-150 attempts unchanged-method UPO recovery at both endpoints of the
qualified `c=19.9` bracket, how many accepted recoveries represent distinct
primitive periodic orbits rather than repeated traversals or phase copies?

## Frozen audit

Apply the already implemented EXP-135 audit directly to the eventual hashed
EXP-150 receipt. For every accepted recovery, test every proper integer repeat
factor dividing its reported section lag. The smallest shorter traversal whose
DOP853 flow closure is at most `1e-7` becomes the fundamental lag and period.

For equal-fundamental-lag candidates, require relative period agreement within
`1e-8`; sample 512 phases; use the best discrete phase as a bracket; and
minimize normalized whole-orbit RMS continuously to phase-shift tolerance
`1e-12`. The unchanged identity gate is RMS at most `1e-6`. Coordinate scales
remain `(1,30,0.0006)`. At least one distinct primitive family must remain at
each endpoint.

## Execution boundary

The method, script, and every scientific threshold are frozen before EXP-150
runs. Once EXP-150 completes, an immutable manifest may add only its exact
receipt path and SHA-256 hash plus the corresponding experiment identifiers.
No threshold, source recovery, or family decision may be selected after
inspecting the UPO result.

## Interpretation boundary

A pass qualifies transverse-slice UPO representatives for later lobe tracing.
It does not establish that any family is the continuation of a `c=20` family,
that its lobe enters or leaves a saddle, or that a continuous TBA surface
exists.

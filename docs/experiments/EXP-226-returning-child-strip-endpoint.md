# EXP-226 — Representation-safe endpoint qualification

Status: frozen — awaiting execution

EXP-225 independently localizes the parent real-`-1` crossing and qualifies
the primitive child before it. DOP853 qualifies the parent double cover after
it, but Radau's redundant `2T` Newton correction is singular and reports only
`xtol` termination.

EXP-226 retains the exact root bracket, solvers, bilateral points, and every
threshold. The only change is representation-safe: on the right, Radau
independently corrects the stable fundamental parent and integrates it for
exactly twice its period. The resulting doubled trajectory must pass full
closure, `14/16` doubled section counts, half-period collapse, parent/child
state identity, stability, and monodromy-square gates.

A pass establishes a second period-6 flip crossing bounding this sampled
one-dimensional child strip. It does not establish a global child-sheet
endpoint, a second continued flip curve, paired shrimp boundaries, TBA
membership, or double-criticality.

Manifest:
[`../../experiments/manifests/EXP-226-returning-child-strip-endpoint.json`](../../experiments/manifests/EXP-226-returning-child-strip-endpoint.json).

# EXP-375 — Exact-node sparse homoclinic correction

Status: frozen; not yet run

EXP-374 reduces the projected crossing solve's maximum matching defect to
`5.26837e-6` while retaining a passing plane residual and wide bound margins.
EXP-375 binds that failed receipt by SHA-256 and uses its exact 512 nodes,
flight time, parameters, and common-gauge angle only as the optimizer start.
The scientific branch sources remain the qualified EXP-367/368 roots.

The reduced-step plane, predictor, segmentation, CSR/regularized-LSMR solver,
unit equation weight, manifold construction, solver tolerances, bounds,
40-evaluation budget, and every acceptance threshold are unchanged. This is a
warm numerical correction, not permission to treat EXP-374 as a root.

A pass below `a=0.1798` forms a qualified branch bracket. It does not itself
solve the exact historical section or establish uniqueness or computer-
assisted existence.

Manifest:
[`../../experiments/manifests/EXP-375-jones-homoclinic-sparse-exact-node-restart.json`](../../experiments/manifests/EXP-375-jones-homoclinic-sparse-exact-node-restart.json).

# EXP-375 — Exact-node sparse homoclinic correction

Status: completed; optimizer converged, scientific root gate failed

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

## Result

The exact-node restart terminates normally on `gtol` after 34 evaluations,
with optimizer optimality `4.66598e-12`. It moves only to
`(a,c)=(0.1798174264304,10.3171881918032)` and reduces the maximum matching
defect from `5.26837e-6` to `5.20888e-6`, just `1.13%`. The projected-plane
residual remains passing at `-1.76436e-9`, and all bounds remain comfortably
interior.

This is a stationary non-root of the trust-region least-squares formulation.
Increasing its budget or chaining identical restarts is not justified. The
next recovery must solve the square system through a direct sparse Newton or
block-elimination step, with guarded descent and the same scientific gates.

Raw receipt: `artifacts/EXP-375/receipt.json`, 84,703 bytes, SHA-256
`bd4c1e85c9533e616bf8377cc34c78fece4c43ff7b045e8aa91807e6da38a451`.

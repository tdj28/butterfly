# EXP-382 — JSON-safe collocation positive control

Status: completed; failed collocation positive control

EXP-381 loses its post-solve diagnostics because two NumPy comparison values
reach strict receipt serialization. EXP-382 converts only those values to
native booleans. It otherwise repeats the identical qualified sources,
EXP-368 zero-step plane, deterministic 512-segment mesh, BVP, derivatives,
tolerances, node ceiling, replay, and acceptance gates.

Only a pass licenses small collocation continuation steps away from EXP-368.
A failure is preserved as a representation result, not evidence against the
already qualified multiple-shooting root.

Manifest:
[`../../experiments/manifests/EXP-382-jones-homoclinic-collocation-positive-control-json.json`](../../experiments/manifests/EXP-382-jones-homoclinic-collocation-positive-control-json.json).

## Result

Standard `solve_bvp` fails even on the zero-step plane through qualified
EXP-368. In two iterations it overflows, encounters a singular collocation
Jacobian, and escapes to `a=-1.50e11`, `c=-1.95e11`, angle `-2.75e49`, and
flight time `1279.96`. Boundary residual reaches `1.88e42`; the first replay
arc is finite but the second collapses. Every source-centered margin fails by
many orders of magnitude.

This rejects unconstrained `solve_bvp` as the continuation representation for
this long unstable orbit. It does not reject EXP-368, which remains a qualified
bounded multiple-shooting root. The successor returns to bounded multiple
shooting and must regularize the physical plane without allowing the node-
dominated full-state direction that selected EXP-369's wrong-side root.

Raw receipt: `artifacts/EXP-382/receipt.json`, 173,593 bytes, SHA-256
`68c73bde963335f83f312e4836f1b62013e8fe11c762d94f3df2f416db0e45e3`.

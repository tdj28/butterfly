# EXP-295 — Independent augmented audit of the seventh-event candidate

Status: frozen before execution

EXP-294 establishes fourth-order convergence of the classical-RK4 augmented
coordinate but preserves disagreement with the old Float64 tangent field.
EXP-295 tests the newly converged object rather than relaxing that historical
source gate. It independently corrects the full orbit-plus-antiperiodic-tangent
system with the algebraically distinct RK4 3/8 tableau at 1,024, 2,048, and
4,096 steps on every segment.

The independent `a` and period sequences must each converge with a ratio in
`[12,20]`; finest and extrapolated coordinates must remain inside the untouched
EXP-280 bracket and agree with EXP-294 within `1e-10`. The finest orbit nodes,
normalized base tangent, and globally sign-aligned tangent-line field have
separate prospective identity gates. All residual and primitive half-orbit
gates remain unchanged.

A pass independently qualifies a resolution-converged primitive seventh
real-`-1` event representation and may supersede FND-101's event retraction.
It cannot establish the criticality or stability of the period-1536 birth.

Manifest:
[`../../experiments/manifests/EXP-295-period768-decimal-augmented-independent.json`](../../experiments/manifests/EXP-295-period768-decimal-augmented-independent.json).

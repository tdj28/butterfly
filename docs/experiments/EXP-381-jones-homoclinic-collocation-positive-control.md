# EXP-381 — Collocation positive control at EXP-368

Status: frozen; not yet run

EXP-380 shows that a finite crossing plane can make unconstrained collocation
escape before adapting its mesh. EXP-381 first requires the new representation
to reproduce the already qualified EXP-368 root. It uses EXP-368 as the bound
warm orbit and zero-step physical plane, then deterministically subdivides its
256 exact shooting arcs to a 512-segment collocation mesh.

The manifold boundaries, common angle gauge, unknown `(T,a,c,angle)`, analytic
Jacobians, identical Radau manifold/replay policy, `1e-7` collocation tolerance,
4,096-node ceiling, source-centered margins, and `1e-8` boundary and independent
replay gates are unchanged. Forward direction and historical-section crossing
are explicitly inapplicable to this zero-step representation control.

Only a pass licenses small collocation continuation steps away from EXP-368.

Manifest:
[`../../experiments/manifests/EXP-381-jones-homoclinic-collocation-positive-control.json`](../../experiments/manifests/EXP-381-jones-homoclinic-collocation-positive-control.json).

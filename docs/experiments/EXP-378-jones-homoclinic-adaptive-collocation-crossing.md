# EXP-378 — Adaptive-collocation homoclinic crossing

Status: frozen; not yet run

EXP-377 shows that the 512-arc multiple-shooting square system has a directly
measured near-null mode that neither trust-region regularization nor deeply
damped Newton can resolve reliably. EXP-378 retains the qualified EXP-367/368
physical secant, reduced crossing plane, common eigenspace gauge, unstable and
stable manifold boundary constructions, and exact EXP-377 orbit as a
SHA-bound initial mesh.

The representation changes to adaptive fourth-order collocation. The unknowns
are three state functions and `(T,a,c,angle)`; the seven boundary conditions
are the three unstable-sphere start coordinates, three nonlinear stable-target
coordinates, and the same physical `(a,c)` pseudo-arclength equation. ODE and
boundary Jacobians are analytic except the already declared central
derivatives of endpoint geometry. The collocation residual tolerance is
`1e-7`, with at most 4,096 mesh nodes.

A pass additionally requires an independent uniform 512-arc Radau replay with
maximum defect below `1e-8`, boundary residual below `1e-8`, interior source-
centered margins, forward `c`, and `a<0.1798`. It qualifies a bracket endpoint,
not the exact historical section, uniqueness, or computer-assisted existence.

Manifest:
[`../../experiments/manifests/EXP-378-jones-homoclinic-adaptive-collocation-crossing.json`](../../experiments/manifests/EXP-378-jones-homoclinic-adaptive-collocation-crossing.json).

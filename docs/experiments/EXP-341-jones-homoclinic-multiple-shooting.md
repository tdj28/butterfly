# EXP-341 — Segmented homoclinic multiple shooting

Status: frozen; not yet run

EXP-340's corrected single shooting remains interior and reduces its mismatch,
but exhausts the frozen budget with a scaled Jacobian condition ratio near
`1.47e5`. EXP-341 binds that exact preserved failure and changes the trajectory
representation, not the endpoint problem.

The 234-time-unit orbit is divided into 16 equal-time arcs with 15 free
internal nodes. The unknown vector contains those 45 node coordinates plus
total flight time, `a`, and departure angle; the 48 matching equations require
each arc to land on the following node and the final arc to land on the same
radius-`0.03` positive stable-manifold target. Segment state, time, and `a`
derivatives use the variational equations. Only the `a` dependence of the
unstable seed and nonlinear stable target uses a declared central difference.

The global angle--`a`--time box, integrator tolerances, 60-evaluation budget,
and `1e-8` maximum block-residual threshold are inherited unchanged. A passing
interior root is only a nomination: shrinking matching spheres, independent
Radau integration, and parameter continuation remain mandatory.

Manifest:
[`../../experiments/manifests/EXP-341-jones-homoclinic-multiple-shooting.json`](../../experiments/manifests/EXP-341-jones-homoclinic-multiple-shooting.json).

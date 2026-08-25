# EXP-396 — Standard local-tangent plane positive control

Status: frozen; not yet executed

EXP-395's wall-free quarter step finds an interior root but moves `0.47244`
radians in departure angle and ends `7.03e-8` backward in `c`.  Its weighted
closing normal is `0.87565` node norm but `0.40470` in `c`, whereas the actual
scaled matching-Jacobian tangent is `0.999992` node norm and only `0.0013865`
in `c`.  This nominates closing-plane rotation as the next controlled factor.

EXP-396 is a zero-step positive control.  It sets every scaled tangent-group
weight to one, making the closing-plane normal the normalized local tangent
itself.  It retains the exact source bindings, 512 arcs, analytic
sensitivities, CSR/LSMR correction, wide angle interval, stationary-`c` gate,
12-evaluation budget, manifold/Radau settings, and every tangent, root,
arclength, conditioning, and margin threshold.

A pass licenses one wall-free quarter-step replay with the standard plane.  It
does not add a curve point or qualify the historical intersection, uniqueness,
proof, or global topology.

Manifest:
[`../../experiments/manifests/EXP-396-jones-homoclinic-local-tangent-standard-plane-control.json`](../../experiments/manifests/EXP-396-jones-homoclinic-local-tangent-standard-plane-control.json).

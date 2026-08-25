# EXP-388 — Lower-weight homoclinic-plane positive control

Status: frozen; not yet executed

EXP-386 and EXP-387 both land on prospectively imposed forward-`c` walls under
the `0.01` nuisance-weight plane.  The smaller EXP-387 step improves the
matching floor by about one order of magnitude but does not escape the wall.
EXP-388 therefore changes plane orientation without attempting a forward step.

Node, angle, and flight-time weights are reduced from `0.01` to `0.003`; the
physical `a` and `c` weights remain one.  This is a prospective compromise
between the pure physical plane, whose measured minimum singular value was
`2.70368e-10`, and the `0.01` control, whose value was `1.79318e-9`.  In
addition to the unchanged zero-step root, stationary-`c`, arclength, and
interiority gates, EXP-388 requires a final minimum Jacobian singular value of
at least `5e-10`.  Thus a pass must retain a measured conditioning improvement
over the pure plane rather than merely reproduce the orbit.

A pass licenses one forward step with the same `0.003` plane.  It does not add
a curve point, qualify the historical fixed-`a` intersection, establish
uniqueness, or prove the homoclinic connection.

Manifest:
[`../../experiments/manifests/EXP-388-jones-homoclinic-lower-weight-positive-control.json`](../../experiments/manifests/EXP-388-jones-homoclinic-lower-weight-positive-control.json).

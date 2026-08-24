# EXP-341 — Segmented homoclinic multiple shooting

Status: completed; root nominated below the frozen residual gate, but preserved
with a sole optimizer-termination failure

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

## Result

The maximum arc defect falls from `0.000135120249` to `2.66211e-9`, crossing
the frozen `1e-8` nomination gate after six evaluations. The final root is
interior at `a=0.18264360814275696`, departure angle
`2.486885712586975`, and total flight time `234.24496226773172`.

The optimizer nevertheless continues to its 60-evaluation limit, so the sole
failed check is `optimizer_terminated` and the run remains formally failed. A
direct one-shot replay diverges to endpoint mismatch `2.05988`; this is not a
contradiction. The 16 individually matched arcs have a Jacobian condition ratio
near `1.51e10`, so accumulated initial-value error is exactly what segmentation
is intended to avoid.

This is the first numerical root nomination near Jones's approximately printed
coordinate. It is not yet a qualified homoclinic orbit. The next run doubles
the segmentation and changes independently to Radau; shrinking-radius
persistence and continuation remain open.

Tracked summary: [`receipts/EXP-341.json`](receipts/EXP-341.json). Raw receipt
SHA-256: `ab47e664ed9994c5c219fd864f26781d79b68c37ac040f317afcc8606b84b729`.

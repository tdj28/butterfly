# EXP-334 — Homoclinic residual-cell winding audit

Status: frozen; not yet run

EXP-333 produces 25 direct chord candidates and three cells whose four-corner
ranges contain zero separately in both signed residual coordinates. Separate
component ranges are not enough to establish that the residual-vector loop
surrounds the origin: the two zero contours can miss each other.

EXP-334 binds the complete raw EXP-333 receipt and deterministically audits
every cell with four completed returns to the same stable branch. It must first
reproduce the three source hull cells. It then traverses each residual polygon
in parameter-space order and computes its integer winding number around zero.
A cell is retained for a coupled solve only if that degree is nonzero and its
four first-return times span at most one time unit.

This is an immutable-data logic audit, not another integration. A retained
cell remains only a root nomination. Rejection of the three hull cells would
invalidate that coarse cell criterion, not EXP-333's 25 direct near-matches
and not the existence of a root on a finer mesh.

Manifest:
[`../../experiments/manifests/EXP-334-jones-homoclinic-residual-cell-audit.json`](../../experiments/manifests/EXP-334-jones-homoclinic-residual-cell-audit.json).

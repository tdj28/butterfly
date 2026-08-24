# EXP-334 — Homoclinic residual-cell winding audit

Status: passed; all three coarse hull nominations rejected by winding

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

The audit reproduces all three EXP-333 hull cells among 28 fully completed
same-branch cells. Every residual polygon has winding number zero. Two hull
cells also have crossing-time spreads above 116 time units; the third is
continuous to `0.05745` time units but still has degree zero. Thus none is
eligible for a coupled root solve under the frozen rule.

This rejects only the coarse componentwise rectangle nomination. EXP-333's 25
direct near-matches remain valid discovery evidence. EXP-335 is frozen on a
larger radius and finer grid so degree can be evaluated where inward-return
coverage is substantially higher.

Tracked summary: [`receipts/EXP-334.json`](receipts/EXP-334.json). Raw receipt
SHA-256: `127e0b62f673fe2c164075cebad30069503ecf48492aa54a51b6207bef7774ac`.

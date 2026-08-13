# EXP-219 — One-sided-tangent returning-arm child qualification

Status: prospectively frozen before execution

EXP-218 fails administratively because two higher-`a` auxiliary parent
corrections do not converge. EXP-219 changes only the parent-tangent estimate:
the exact event and two successfully audited lower-`a` parents at offsets
`-1e-5` and `-2e-5` define it. Both signed doubled-period nullspace directions
are still probed, and any failure is now serialized in the receipt.

The scientific prediction and every qualification gate are unchanged. Each of
the three held-out events must yield a primitive stable period-12 child toward
lower `a`, paired with an unstable period-6 parent, correct `7/8` versus
`14/16` section identities, period ratio two, proper-subperiod nonclosure, and
whole-orbit/Floquet agreement between DOP853 and Radau.

Manifest:
[`../../experiments/manifests/EXP-219-returning-period12-children-one-sided.json`](../../experiments/manifests/EXP-219-returning-period12-children-one-sided.json).

A pass establishes local stability exchange on the returning arm compatible
with an opposing shrimp boundary. It does not prove global window
connectivity, a returning child sheet, TBA membership, or double-criticality.

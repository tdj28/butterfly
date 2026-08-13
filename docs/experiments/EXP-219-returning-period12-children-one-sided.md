# EXP-219 — One-sided-tangent returning-arm child qualification

Status: complete — failed with zero generated child candidates

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

## Result

The one-sided parent tangent removes EXP-218's administrative abort, but both
signed secondary correctors produce zero accepted candidates at all three
events. Their first-step residual norms span `0.00239--3.30291`. The smallest
doubled-period singular value grows from `1.28e-7` at the near slice to
`2.62e-6` and `2.50e-5` at the remote slices, exceeding the frozen singularity
gate at the latter two.

Thus EXP-219 is a qualified negative result for this inherited single-scale,
single-shooting switch. It does not test or reject the lower-`a` child
prediction because no candidate reaches the independent stability gates.
EXP-220 freezes tighter exact-event recorrection and a multiscale predictor
ladder without changing the scientific prediction.

Raw receipt: `artifacts/EXP-219/receipt.json`, 13,399 bytes, SHA-256
`87306622334a4dcb21f705c4a6c503f50b4e26bbd4b9445673cef3ee946c64e3`.
Compact receipt:
[`receipts/EXP-219.json`](receipts/EXP-219.json).

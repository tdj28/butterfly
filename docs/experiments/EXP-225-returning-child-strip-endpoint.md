# EXP-225 — Returning-child strip endpoint successor

Status: complete — root and left/DOP853 controls pass; Radau `2T` correction is
administratively singular

EXP-224 reaches its scalar root stage but aborts without a receipt when the
independent Radau child corrector only `5e-5` below the root terminates by
`xtol` without meeting the frozen correction criterion. EXP-225 changes only
that bilateral diagnostic distance to `1.5e-4`, where the primitive child has
larger separation from its parent. All root, orbit, stability, identity,
proper-subperiod, cross-solver, double-cover, and multiplier-square thresholds
are unchanged.

The runner now records child-qualification exceptions as explicit failed
controls. A pass has the same bounded meaning as EXP-224: a second period-6
flip crossing bounds the sampled child strip on this exact one-dimensional
offset path, without proving a global sheet endpoint or shrimp-boundary
connectivity.

Manifest:
[`../../experiments/manifests/EXP-225-returning-child-strip-endpoint.json`](../../experiments/manifests/EXP-225-returning-child-strip-endpoint.json).

## Result

Both scalar parent-flip roots pass every frozen gate. DOP853 gives
`c=7.62537829761012`; Radau gives `c=7.62537829364544`, a difference of
`3.96e-9`. The left primitive child at `c_root-1.5e-4` passes full
DOP853/Radau qualification with parent modulus `1.008333`, child modulus
`0.966599`, period ratio `2.00000098`, and proper half-period separation.

The DOP853 right double cover also passes: parent modulus `0.992098`, child
modulus `0.984259`, half-period closure `8.54e-8`, parent/child state distance
`9.29e-8`, and multiplier-square error `2.08e-8`. The overall experiment fails
only because Radau's redundant `2T` Newton correction reports `xtol`
termination. That is an ill-conditioned representation at a double cover, not
a failed right-side scientific metric.

EXP-226 retains the same roots, points, and thresholds. It changes only the
Radau right-side audit: independently correct the stable parent, integrate it
for exactly `2T`, and test closure, doubled section identity, and monodromy
squaring without a singular redundant-period correction.

Raw receipt: `artifacts/EXP-225/receipt.json`, 18,914 bytes, SHA-256
`cbe550742e82018b804636be209fa9a6164894a15d1da0ffe3cb3dee4ea7e0db`.
Compact receipt:
[`receipts/EXP-225.json`](receipts/EXP-225.json).

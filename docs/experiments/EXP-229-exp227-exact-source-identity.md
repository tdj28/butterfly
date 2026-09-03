# EXP-229 — Exact-coordinate identity audit of EXP-227

Status: complete — passed all frozen gates

EXP-228 accepted 53 exact points, but its interpolation-based source-arm
separation shrank toward zero in both directions. A deterministic diagnostic
then corrected the EXP-217 arm at the exact `c` coordinates of three EXP-227
points. Candidate and source corrections agreed in `a` to about `6.6e-13`
under the looser source solver, whereas linear interpolation had overstated
the source `a` coordinate by roughly `5.7e-7`.

EXP-229 is a post-diagnostic confirmatory audit. At all 21 EXP-227 coordinates,
it freshly corrects the real-`-1` event from the nearest EXP-217 source seed
instead of interpolating the event coordinate. It compares parameter, period,
phase state, sign-invariant flip tangent, and multiplier modulus, with Radau
controls at both endpoints and the center.

A pass retracts the EXP-227 distinct-curve interpretation and establishes
sampled numerical identity with the known returning arm. It does not prove a
global identity theorem, a global child-sheet endpoint, a second shrimp
boundary, TBA membership, or double-criticality.

Manifest:
[`../../experiments/manifests/EXP-229-exp227-exact-source-identity.json`](../../experiments/manifests/EXP-229-exp227-exact-source-identity.json).

## Result

All 21 exact-coordinate comparisons and all three Radau controls pass. The
maximum DOP853 differences are `1.46e-14` in `a`, `2.23e-15` in relative
period, `4.77e-11` in phase state, `4.04e-12` in the sign-invariant flip
tangent, and `1.14e-10` in multiplier modulus. The maximum Radau differences
are `1.61e-13` in `a`, `4.78e-11` in state, and `9.20e-10` in multiplier
modulus.

By contrast, linear interpolation of the sparse EXP-217 arm overstates `a` by
`5.6011e-7--5.8497e-7`, exactly accounting for EXP-227's purported
separation. FND-089 is retracted. The EXP-226 crossing is a recrossing of the
known returning flip arm by the constructed offset path, not a distinct
second boundary.

Raw receipt: `artifacts/EXP-229/receipt.json`, 13,882 bytes, SHA-256
`d09dce1e02a24d06279e30cb5bb8e2c5f19b28af56cdbeb8ce0c8ad46afe5efa`.
Compact receipt:
[`receipts/EXP-229.json`](receipts/EXP-229.json).

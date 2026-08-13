# EXP-229 — Exact-coordinate identity audit of EXP-227

Status: frozen — not yet executed

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

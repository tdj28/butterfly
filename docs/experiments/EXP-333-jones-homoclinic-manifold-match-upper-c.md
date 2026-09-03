# EXP-333 — Upper-c homoclinic manifold-match extension

Status: passed; root nominations require EXP-334 audit

EXP-332's closest nonlinear stable/unstable manifold mismatch decreases at
every sampled `c` value and remains positive at its upper boundary. EXP-333
binds that raw receipt, classification, and exact boundary selection before
extending the same scan from `c=10.3124` through `10.3224` at spacing `0.001`.

The gauge reference, 96 midpoint departure angles, nonlinear stable targets,
matching radius, first-inward-return rule, DOP853 settings, horizon, candidate
gate, execution gates, and claim boundaries are unchanged. A direct chord
candidate or two-residual hull cell remains only a nomination for a coupled
root solve. The extension cannot by itself prove a homoclinic connection or
test uniqueness.

Manifest:
[`../../experiments/manifests/EXP-333-jones-homoclinic-manifold-match-upper-c.json`](../../experiments/manifests/EXP-333-jones-homoclinic-manifold-match-upper-c.json).

All 1,056 departures complete in `88.9844` seconds and 369 return inward to
the matching sphere. The run nominates 25 direct chord candidates across
`c=10.3184`, `10.3194`, and `10.3204`. Its closest row is at `c=10.3194`,
angle `1.8653206380689396`, with chord mismatch `0.0013378700961282038`
and tangent residual `(0.0007694033,-0.0010935779)`.

The source componentwise rule also nominates three sign-hull cells. Because
that rule does not require the residual polygon to enclose zero, EXP-334 is
frozen to audit all cells by winding number and return-time continuity before
any coupled solve. EXP-333 is encouraging evidence for a nearby match, not a
qualified homoclinic connection.

Tracked summary: [`receipts/EXP-333.json`](receipts/EXP-333.json). Raw receipt
SHA-256: `aa9c0daa7f56a4b130448294045c24b90f7cea48a44c07958a30540d7b9a4cdf`.

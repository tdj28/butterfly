# EXP-336 — Fixed-c homoclinic a-band

Status: failed return-coverage gate; discovery rows preserved

The fixed-`a=0.1798` searches at matching radii `0.02` and `0.025` produce
consistent bounded near matches around `c=10.319` but no residual cell of
nonzero degree. Jones's source reports both hub coordinates only approximately
and supplies no exact endpoint table, so EXP-336 tests the orthogonal rounding
direction.

At fixed `(b,c)=(0.2,10.3084)`, 17 `a` values span
`[0.1758,0.1838]` at spacing `0.0005`. The radius-`0.025` nonlinear stable
targets, 192 gauge-aligned unstable angles, first-inward-return rule, DOP853
settings, chord gate, winding number, and one-time-unit continuity gate are
unchanged. A continuous degree cell remains only a coupled-solve nomination.

Manifest:
[`../../experiments/manifests/EXP-336-jones-homoclinic-fixed-c-a-band.json`](../../experiments/manifests/EXP-336-jones-homoclinic-fixed-c-a-band.json).

All 3,264 departures complete in `354.890` seconds, but only 309 return inward
to the matching sphere. The `0.09467` coverage fraction fails the frozen `0.2`
gate; all other source, geometry, event, and finite-value checks pass. EXP-336
is not reclassified.

The completed rows nevertheless localize a much smaller discovery mismatch.
At `a=0.1828`, one return has chord `0.0003443513727835964`, or `0.01377` of
the sphere radius, with tangent residual
`(-0.0001524216,-0.0003087716)`. Seventeen rows meet the direct chord gate, but
both residual hulls have degree zero. EXP-337 binds the exact failed receipt
and failure pattern, narrows to the observed returning band, and enlarges the
sphere to `0.03` to restore cell coverage before any root attempt.

Tracked summary: [`receipts/EXP-336.json`](receipts/EXP-336.json). Raw receipt
SHA-256: `0551d7ee3b699433c0e31f2a4f116f44d93bdf93fdb69eb66123ac2b5222c6ad`.

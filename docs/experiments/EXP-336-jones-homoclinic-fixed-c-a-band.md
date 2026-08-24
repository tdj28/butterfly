# EXP-336 — Fixed-c homoclinic a-band

Status: frozen; not yet run

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

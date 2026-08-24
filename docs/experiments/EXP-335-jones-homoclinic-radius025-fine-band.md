# EXP-335 — Radius-0.025 fine homoclinic band

Status: passed; no nonzero-degree cell on the fixed-a band

EXP-333 finds 25 direct near matches on the radius-`0.02` sphere, but EXP-334
shows that all three coarse componentwise hull cells have residual winding
zero. Only 28 same-branch cells had four inward crossings, so the degree test
was severely coverage-limited.

EXP-335 binds both results, enlarges the matching sphere to `0.025`, and scans
the nominated `c` band `[10.3164,10.3224]` at `0.0005` spacing with 192
midpoint angles. The larger sphere is a discovery device intended to increase
continuous inward-return coverage. The nonlinear stable targets, event logic,
solver, horizon, gauge, and fixed `(a,b)` are otherwise unchanged.

The direct chord gate scales to `0.0025`. More importantly, the scan now
computes oriented residual winding itself and requires a nonzero-degree cell
with no more than one time unit of corner return-time spread. Any such cell is
only eligible for a coupled solve. Qualification still requires a solved root,
shrinking-radius reproduction, and independent integration.

Manifest:
[`../../experiments/manifests/EXP-335-jones-homoclinic-radius025-fine-band.json`](../../experiments/manifests/EXP-335-jones-homoclinic-radius025-fine-band.json).

The 2,496-row scan completes in `221.941` seconds. It records 977 inward
returns, a `0.3914` coverage fraction, and 141 direct chord candidates. The
closest row lies at `c=10.3189` with mismatch `0.0012941009645505146`, closely
agreeing in absolute scale with EXP-333's radius-`0.02` minimum.

Four cells meet the componentwise hull rule, but every residual polygon again
has winding number zero. No coupled solve is nominated on this fixed
`a=0.1798` band. Because Jones reports both coordinates only approximately,
EXP-336 rotates the test: it fixes `c=10.3084` and scans the orthogonal `a`
direction with the same radius, angle count, winding, and continuity rules.

Tracked summary: [`receipts/EXP-335.json`](receipts/EXP-335.json). Raw receipt
SHA-256: `1db45473002963fa34142451fc29ca69519cdaf61afe406ca53feacfd1f6dfa6`.

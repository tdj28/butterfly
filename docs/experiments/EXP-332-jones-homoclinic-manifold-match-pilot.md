# EXP-332 — Parameter-aware homoclinic manifold-match pilot

Status: passed

EXP-329/331 find close recurrent flybys at the approximately printed hub but
no sampled approach along the stable eigendirection. EXP-332 replaces that
fixed-coordinate proximity scan with an explicit stable/unstable manifold
matching problem.

At fixed `(a,b)=(0.1798,0.2)`, nine `c` values span
`[10.3044,10.3124]`. At each value, both nonlinear branches of the local
one-dimensional stable manifold are constructed by integrating a radius-`1e-8`
stable seed backward to the radius-`0.02` matching sphere. A gauge-aligned
96-angle basis launches the two-dimensional unstable manifold. After its
outward crossing and a ten-time-unit gate, the first inward return to the same
sphere is compared with the closer stable target through two signed tangent
coordinates.

A chord mismatch at most `0.002`, or a same-branch grid cell whose two signed
residual ranges both contain zero, is only a nonlinear-root nomination. A run
pass validates source binding, stable targets, coverage, sphere event
accuracy, and finite values; it does not establish a homoclinic orbit. Any
root must survive a coupled solve, shrinking matching radii, an independent
integrator, and parameter continuation before CLM-003 changes state.

Manifest:
[`../../experiments/manifests/EXP-332-jones-homoclinic-manifold-match-pilot.json`](../../experiments/manifests/EXP-332-jones-homoclinic-manifold-match-pilot.json).

All 864 departures completed in `74.0060` seconds and 223 produced an inward
radius-`0.02` return. Both nonlinear stable targets passed sphere residuals at
all nine `c` values. No row met the `0.002` chord gate and no same-branch cell
contained zero in both signed residual ranges.

The minimum chord mismatch nevertheless decreases at every `c` slice, from
`0.0156595` at `c=10.3044` to `0.00656684` at the upper boundary
`c=10.3124`. The selected endpoint has tangent residual
`(0.00507540,0.00402510)`, with both components shrinking but still positive.
This prospectively selects an unchanged-method upper-`c` extension in EXP-333;
it is not yet a root nomination.

Tracked summary: [`receipts/EXP-332.json`](receipts/EXP-332.json). Raw receipt
SHA-256: `32edf3c3f8cc47c7d101f06dd7c790d41ae842c40d39d97f0cb20b350a921557`.

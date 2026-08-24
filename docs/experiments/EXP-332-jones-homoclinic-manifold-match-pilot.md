# EXP-332 — Parameter-aware homoclinic manifold-match pilot

Status: frozen; not yet run

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

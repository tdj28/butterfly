# EXP-335 — Radius-0.025 fine homoclinic band

Status: frozen; not yet run

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

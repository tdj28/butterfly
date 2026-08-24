# EXP-348 — Second homoclinic-curve c step

Status: frozen; not yet run

EXP-347 supplies the first local homoclinic-curve secant and predicts the
historical `a=0.1798` crossing near `c=10.31714`. EXP-348 binds its exact 32
Radau nodes and advances fixed `c` from `10.3104` to `10.3144`.

The radius, branch, integrator, residual gate, and nuisance gauge are unchanged.
The wider `a` box admits the first-secant prediction while requiring a local
change below `0.002`. Passing provides a curvature check before any direct
historical-path intersection solve.

Manifest:
[`../../experiments/manifests/EXP-348-jones-homoclinic-c-continuation-step2.json`](../../experiments/manifests/EXP-348-jones-homoclinic-c-continuation-step2.json).

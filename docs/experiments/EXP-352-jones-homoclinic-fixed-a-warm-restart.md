# EXP-352 — Fixed-a homoclinic warm restart

Status: frozen; not yet run

EXP-351 reduces its maximum defect from `0.0245207` to `0.000209830`
without leaving the local box, but exhausts its budget. Of 128 arc defects,
121 already pass `1e-8`; five of the seven remaining failures are concentrated
in the final five arcs adjacent to the stable target.

EXP-352 binds the exact failed receipt and restarts from all 127 fixed-`a`
internal nodes. It keeps `(a,b)=(0.1798,0.2)`, solves `c`, and changes no
physical geometry, integration tolerance, segmentation, optimization budget,
or scientific residual threshold. Only the local coordinates are recentered
on the prospectively preserved failure so that the analytic Jacobian is
relinearized there.

Manifest:
[`../../experiments/manifests/EXP-352-jones-homoclinic-fixed-a-warm-restart.json`](../../experiments/manifests/EXP-352-jones-homoclinic-fixed-a-warm-restart.json).

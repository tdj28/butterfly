# EXP-348 — Second homoclinic-curve c step

Status: completed; preserved residual/termination failure; recovery required

EXP-347 supplies the first local homoclinic-curve secant and predicts the
historical `a=0.1798` crossing near `c=10.31714`. EXP-348 binds its exact 32
Radau nodes and advances fixed `c` from `10.3104` to `10.3144`.

The radius, branch, integrator, residual gate, and nuisance gauge are unchanged.
The wider `a` box admits the first-secant prediction while requiring a local
change below `0.002`. Passing provides a curvature check before any direct
historical-path intersection solve.

Manifest:
[`../../experiments/manifests/EXP-348-jones-homoclinic-c-continuation-step2.json`](../../experiments/manifests/EXP-348-jones-homoclinic-c-continuation-step2.json).

## Result

The correction remains interior and reaches `a=0.18069045562011257`, nearly
exactly on the first secant. It exhausts 40 evaluations at maximum arc defect
`2.51470e-8`, however, so the `1e-8` gate is not met and the run remains
failed. Its diagnostic secant would predict `c=10.3171353942` at `a=0.1798`,
but that prediction is not promoted until a same-`c` recovery passes.

Tracked summary: [`receipts/EXP-348.json`](receipts/EXP-348.json). Raw receipt
SHA-256: `fdf16d30800abbd259a27f74f7c40957ce0357f471cf020395e9d2ffc9693c54`.

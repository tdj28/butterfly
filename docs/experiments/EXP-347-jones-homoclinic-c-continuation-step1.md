# EXP-347 — First homoclinic-curve c step

Status: frozen; not yet run

EXP-346 qualifies the radius-`0.02` root at fixed `c=10.3084`. EXP-347 binds
its 32 Radau nodes, advances only the fixed parameter to `c=10.3104`, and
solves again for the matched nodes, `a`, departure angle, and flight time.

The radius, branch, integrator, `1e-8` residual gate, and corrected nuisance
gauge are unchanged. The prospective local box permits at most `0.001` change
in `a`, `0.5` in angle, and `2.0` in time. Passing supplies one secant direction
for the homoclinic curve; it does not establish an intersection with the
historical `a=0.1798` path or uniqueness.

Manifest:
[`../../experiments/manifests/EXP-347-jones-homoclinic-c-continuation-step1.json`](../../experiments/manifests/EXP-347-jones-homoclinic-c-continuation-step1.json).

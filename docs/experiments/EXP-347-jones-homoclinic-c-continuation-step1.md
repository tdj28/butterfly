# EXP-347 — First homoclinic-curve c step

Status: passed; first local curve secant qualified

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

## Result

The corrected root passes at maximum arc defect `5.11943e-9` with
`a=0.18199257965495652`. Relative to EXP-346, `dc=0.002` produces
`da=-0.000651028519`, hence local secant slope `da/dc=-0.3255142594`.
Linear extrapolation places the `a=0.1798` crossing near
`c=10.3171357407`, close to the independent fixed-`a` scan's earlier near-miss
band.

This is a qualified first continuation step, not yet the historical-path
intersection or a uniqueness audit.

Tracked summary: [`receipts/EXP-347.json`](receipts/EXP-347.json). Raw receipt
SHA-256: `95d1469277344c9fe9c5373837a502c72f60ca4c071abaaa046dd625a7df5fc3`.

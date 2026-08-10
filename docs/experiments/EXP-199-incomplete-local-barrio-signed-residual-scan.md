# EXP-199 — Incomplete local Barrio signed-residual scan

Status: preregistered; execution requires transfer authorization for the
3,950,130-byte EXP-198 candidate artifact

## Question

Do the 685 individually qualified EXP-198 orbits contain a substantially
closer double-critical candidate or a complete local grid cell in which both
signed critical-to-orbit residuals change sign consistently at two RK4 steps?

## Frozen computation

EXP-199 retains EXP-197's section, survivor ensemble, capture geometry, five
oracle variants, and two RK4 steps. It changes only the prospectively selected
candidate set and makes the signed residuals explicit. Each candidate must
resolve the robust three-branch Barrio z map at both steps, retain the same
distinct phase assignment, and pass survivor and critical-location parity.

The direct-candidate gates are deliberately tighter than EXP-197:
maximum normalized midpoint distance `0.02`, interval distance `0.005`, and
assigned zero-slope residual `0.1`. Independently, the scan records a bracket
only when all four corners of one complete lattice cell are eligible, have the
same phase assignment, and bracket zero for both signed residuals at both RK4
steps. Either condition is only a nomination for an adaptive solve.

Manifest:
[`../../experiments/manifests/EXP-199-incomplete-local-barrio-signed-residual-scan.json`](../../experiments/manifests/EXP-199-incomplete-local-barrio-signed-residual-scan.json).

## Claim boundary

EXP-198 failed its coverage gate, its passing mask is fragmented, and the
center component touches the lower-a boundary. Consequently, even a clean
negative EXP-199 result cannot exclude a nearby center. A bracket is not a
root and must be solved and independently qualified with adaptive integrators.

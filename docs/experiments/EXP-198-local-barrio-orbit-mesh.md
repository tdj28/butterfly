# EXP-198 — Local Barrio orbit mesh

Status: preregistered; not yet executed

## Question

Can the prospectively selected EXP-197 localization support a dense,
phase-consistent mesh of stable corrected flow orbits suitable for a genuinely
coupled signed-critical-residual scan?

## Frozen computation

The only seed is EXP-197's closest frozen point,
`component-sample-059` at `(a,b,c)=(0.21555,0.2,7.372)`. A 31 by 81 lattice
covers `a in [0.2154,0.2157]` and `c in [7.2,7.52]`, for 2,511 parameter
points. Each point is shot directly from the same immutable corrected seed
with DOP853. A candidate must pass flow closure and phase gates, retain a
stable real dominant multiplier and an accurate neutral multiplier, remain
within the frozen flow-period and correction-distance identity bounds, and
intersect the historical section six times and the Barrio positive-x section
eight times per flow period.

This stage does not reconstruct a return map, compute a critical residual, or
select another center. The resulting candidate artifact becomes input to a
separately frozen GPU scan, preventing the dense-mesh acceptance rules from
being tuned after critical information is seen.

Manifest:
[`../../experiments/manifests/EXP-198-local-barrio-orbit-mesh.json`](../../experiments/manifests/EXP-198-local-barrio-orbit-mesh.json).

## Claim boundary

A pass establishes only that the local stable periodic-orbit family has been
sampled and represented consistently on both sections. It does not establish
that either Barrio critical point belongs to any orbit.

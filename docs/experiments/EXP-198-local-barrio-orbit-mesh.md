# EXP-198 — Local Barrio orbit mesh

Status: executed; center passed but frozen coverage-count gate failed

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

## Result

The local no-egress execution from clean commit `eca40c6` completes all 2,511
points without an exception. The frozen center reproduces with flow closure
`2.27e-13`, exactly six historical phases, exactly eight Barrio phases, and
dominant multiplier `-0.59854`. In total, 685 points pass every individual
shooting, identity, section, Floquet, and stability check. This is below the
frozen minimum of 1,000, so EXP-198 fails as a coverage-qualified preparation.

The passing points span `a in [0.2154,0.2157]` and
`c in [7.264,7.5]`, but split into 11 eight-connected raster components with
sizes `355,154,152,11,5,2,2,1,1,1,1`. The selected center belongs to the
152-point component, which reaches the lower `a` boundary. Thus the mesh does
not close a coherent local search domain around the selected point. The most
common failed gate is stability (1,355 points); direct shooting closure and
neutral-multiplier checks also fail in about 800 points. These failures are
preserved and are not reclassified as evidence that the underlying orbit
family is dynamically disconnected.

The 685 individually qualified points remain usable for a separately frozen,
explicitly incomplete GPU diagnostic. Such a successor cannot claim an
exhaustive local rejection because the center component touches the mesh
boundary and EXP-198 failed its coverage gate.

Raw artifact: `artifacts/EXP-198/candidates.json`, SHA-256
`db4c3a0f46ac972c44424a8370f1a0bac4d5545f2a5fe73c86097306463efa6a`.
Compact receipt: [`receipts/EXP-198.json`](receipts/EXP-198.json).

The first invocation stopped before integration because the repository root
was missing from `PYTHONPATH`; the second stopped before integration when the
macOS sandbox denied the process-pool semaphore query. The third used the
scientifically unchanged manifest with local no-egress process-pool access.

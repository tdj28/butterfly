# FND-068 — The local orbit mesh is coverage-limited

Status: qualified preparation failure

EXP-198 shoots a frozen 31 by 81 DOP853 mesh from the prospectively selected
EXP-197 orbit without inspecting any dense return-map critical residual. All
2,511 tasks complete without exceptions, and the exact center independently
reproduces with six historical phases, eight Barrio phases, flow closure
`2.27e-13`, and stable dominant multiplier `-0.59854`.

Only 685 points pass every individual closure, phase, family-identity,
section-count, Floquet, and stability gate, below the frozen preparation
minimum of 1,000. The passing raster splits into 11 eight-connected components.
The selected center belongs to a 152-point component that touches the lower
`a` boundary, so the experiment does not close a coherent local search domain.

This is not evidence that the underlying periodic-orbit family is truly
disconnected: direct shooting and neutral-multiplier gates fail at many points,
and the rectangle deliberately extends outside the stable window. It is an
honest coverage failure. The 685 individually qualified orbits may be scanned
as an explicitly incomplete diagnostic, but a negative critical result on
them cannot exclude a center beyond the passing mask or mesh boundary.

Evidence: [`../experiments/EXP-198-local-barrio-orbit-mesh.md`](../experiments/EXP-198-local-barrio-orbit-mesh.md).

# EXP-198 freezes the dense local corrected-orbit mesh

EXP-197 rejected all 58 sampled corrected orbits as direct double-critical
centers but prospectively localized the nearest residual at
`(a,c)=(0.21555,7.372)`. EXP-198 now freezes a 2,511-point local shooting mesh
around that point before any denser return-map residual is inspected.

Every retained mesh point must remain on a stable, phase-consistent flow-orbit
family; pass both DOP853 shooting and Floquet gates; and have six historical
section phases but eight Barrio phases. Critical reconstruction is deliberately
absent. If the mesh passes, its immutable candidate artifact will be bound into
a separately preregistered two-step GPU signed-residual scan.

## Executed result

All 2,511 points complete without exceptions and the selected center passes,
but only 685 points pass every individual gate, below the frozen minimum of
1,000. EXP-198 therefore fails its coverage-preparation rule. The passing mask
has 11 eight-connected components; the center's 152-point component touches
the lower `a` boundary, so it is not a closed local search domain. The 685
valid corrected orbits may support a separately frozen incomplete diagnostic,
but not an exhaustive local rejection.

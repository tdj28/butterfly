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

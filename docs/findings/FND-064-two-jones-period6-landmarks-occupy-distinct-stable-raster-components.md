# FND-064 — The two Jones period-6 landmarks occupy distinct stable raster components

Status: qualified raster-connectivity result; orbit-family identity remains
open

EXP-192 prospectively extends the second-landmark atlas through both exact
Jones period-6 coordinates. Both remain period 6 on the 92,736-pixel grid, so
the earlier classifications are independently reproduced. The second
landmark belongs to a coherent 2,598-pixel component over
`a in [0.2135,0.215775]` and `c in [7.124,8.192]`. The first landmark's nearest
pixel at `(a,c)=(0.21565,6.124)` is period 6 but is not a member of that
component.

The two approximate source points therefore cannot be treated as two samples
of one visibly connected stable period-6 raster band. This sharpens the Jones
test rather than weakening it: the first component has already failed the
two-critical return-map requirement, while the independently isolated second
component retains the three-branch lead needed for a direct center search.

Raster disconnection does not prove that the periodic orbits are globally
unrelated. A bridge narrower than the grid or a continuation through unstable
period-6 orbits remains possible. Such a claim requires corrected-orbit
pseudo-arclength continuation rather than image adjacency.

Evidence: [`../experiments/EXP-192-two-jones-period6-landmark-band.md`](../experiments/EXP-192-two-jones-period6-landmark-band.md).

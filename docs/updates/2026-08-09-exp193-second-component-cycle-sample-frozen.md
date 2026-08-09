# EXP-193 freezes a geometry-only sample of the second period-6 component

EXP-192 shows that the two exact Jones period-6 landmarks occupy distinct
stable raster components. The second component is the relevant search domain
because it surrounds the prospectively identified three-branch return-map
lead. EXP-193 now selects 257 of its 2,598 pixels without using critical or
symbolic information.

The selection begins at the exact second landmark and applies deterministic
farthest-point coverage in normalized parameter coordinates. A fresh Float64
GPU integration must reproduce period 6 and extract a finite six-return tail
at at least 250 points. Passing prepares a separately hash-frozen input for the
Barrio-section z critical-residual scan; it is not itself orbit correction or
a center result.

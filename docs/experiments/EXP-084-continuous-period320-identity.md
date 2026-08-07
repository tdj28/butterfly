# EXP-084 — Continuously align the segmented period-320 candidates

Status: executed; failed phase-refinement algorithm

Use dense output separately inside each of the 32 well-conditioned shooting
segments from EXP-083. Compare the two fixed-`b` switch signs over 2,048
whole-orbit phase samples, search 256 coarse phase offsets, and continuously
refine the best offset to tolerance `1e-11`. This directly tests the diagnosis
that EXP-083's 32 node-only shifts missed a fractional phase offset.

Pass only if continuous phase-aligned RMS is `<=1e-5`, every reconstructed
segment endpoint agrees with its stored successor within `1e-8`, candidate
periods agree within `1e-8`, both already measured block-Floquet moduli remain
`<=0.999`, and the independent lower-period Floquet calibration error remains
`<=1e-5`. No orbit correction or stability threshold is changed after
EXP-083.

The clean run at `7e085885a9b36e33fe6b7566ccc9beb2dba80fe5` failed. Dense
segment reconstruction itself passed with maximum endpoint error `5.99e-11`,
and the coarse search retained its best offset at exactly `0.5` with RMS
`3.17e-4`. The bounded scalar refiner then jumped to offset `0.5028604` and
RMS `4.70`, revealing that its assumed unimodal objective interval is invalid
for this long orbit. Full receipt SHA-256:
`3869c79bc62f767b6b96fb4ad52ad540729139212159f0f36555ed11773f5f5a`.

This failure does not change the fixed-parameter corrections or stability
measurements. EXP-085 freezes a deterministic multiresolution grid centered on
the best coarse phase. Each stage searches every subgrid point before reducing
the interval, so it cannot jump across a narrow chaotic-orbit identity minimum.

# EXP-084 — Continuously align the segmented period-320 candidates

Status: preregistered after EXP-083; pending clean execution

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

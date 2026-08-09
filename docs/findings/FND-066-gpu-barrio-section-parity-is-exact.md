# FND-066 — GPU Barrio-section statistical parity is exact

Status: qualified implementation gate

EXP-196 independently regenerates the corrected eight-phase cycle at the
second Jones landmark, then runs the same 2,048-seed survivor construction on
the CPU reference and generalized Float64 CUDA kernel at RK4 steps `0.01` and
`0.005`.

At both steps, CPU and GPU survivor counts match at all four checkpoints,
return-pair counts match exactly, and all five branch-oracle variants resolve
the same three-branch scalar z return map. The largest normalized difference
between corresponding critical midpoints is `8.24e-11`, against a frozen
ceiling of `0.03`. Both physical critical intervals also remain stable under
factor-two step refinement.

This qualifies the positive-x section, `(y,z)` capture geometry, eight-phase
cycle handling, and z-map output for multi-candidate GPU discovery. It does not
show that either critical belongs to the orbit at the exact landmark or
elsewhere.

Evidence: [`../experiments/EXP-196-gpu-barrio-section-parity.md`](../experiments/EXP-196-gpu-barrio-section-parity.md).

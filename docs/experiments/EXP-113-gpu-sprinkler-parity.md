# EXP-113 — Runpod Float64 sprinkler statistical parity

Status: preregistered; not yet executed

EXP-112 qualifies the CPU sampler. This experiment ports its 8192-point
seed-112 baseline to a Triton Float64 kernel without demanding chaotic
trajectory identity.

The GPU implements the same RK4 equations, positive-oriented Barrio section,
cubic-Hermite section points, four-cycle capture rule, checkpoint survivor
counts, and final-survivor midpoint pairs. It must recover two branches at
`a=0.118` and three at `a=0.149` through the same 15 oracle variants and both
coordinates.

Pass each control only if:

- CPU and GPU survivor fractions differ by at most `0.02` at every checkpoint;
- the GPU returns the expected branch count with variant consensus `1.0`;
- the combined CPU/GPU normalized critical-location span is at most `0.04`;
- the GPU supplies at least 1000 pairs per coordinate and has no numerical
  failure; and
- five GPU seeds agree with DOP853 over their first five returns within scaled
  state error `0.001` and time error `2e-5`.

The live 2026-08-07 catalog supports a secure-cloud NVIDIA A40 at `$0.35/hour`
with high stock. Launch is capped at `$0.40/hour`, two wall hours, and `$0.80`
total. The tracked-source-only archive is authorized by the repository owner.
No-progress for 15 minutes triggers teardown. The receipt and hashes must be
retrieved before the pod is terminated and the account list verified empty.

A pass qualifies GPU statistical parity only at the two controls. It does not
qualify a plane scan until a separately frozen TBA workload is defined.

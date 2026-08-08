# EXP-113 — Runpod Float64 sprinkler statistical parity

Status: passed on 2026-08-07

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

## Execution and result

The source archive bound commit `03a77bf` and was verified remotely before
execution. Its SHA-256 was
`8d81c77684e420b4e4279fb8966a4ab4781580ed7ecae62af93abc393fd590c5`.
The live A40 offer was adjusted to `$0.44/hour`, above the frozen launch cap,
so the controller terminated it automatically. A secure-cloud RTX A5000 with
24 GB was then accepted at `$0.27/hour`.

Both controls pass every frozen gate. The GPU survivor counts are
`[8179,7190,5851,4692,3780,2990]` at `a=0.118`, versus CPU
`[8179,7190,5851,4692,3780,2991]`; the maximum fraction difference is
`0.0001221`. At `a=0.149`, GPU and CPU counts are exactly
`[8192,6571,4773,3395,2440,1757]`. Both `y` and `z` return two branches for
the first control and three for the second, with variant consensus `1.0`.
The largest combined CPU/GPU critical span is `0.01463`.

The DOP853 audit passes all ten trajectories. Maximum scaled state and event-
time errors are `2.46e-6` and `3.16e-6`. The first timed case, which includes
Triton compilation, processes 51.66 million state-steps/second; the warm
second case processes 597.65 million state-steps/second.

The raw receipt is 26,569 bytes. Its remote and local SHA-256 values match at
`98428448119c4e428364bfcbcb220b7ae67c81c208abfc409eb44ff1cf5bd48a`;
the tracked summary is `docs/experiments/receipts/EXP-113.json`. The source was
transferred under the owner's explicit private-source authorization. Total
provisioning-to-teardown time bounds spend below `$0.06`; provider billing is
authoritative. All task-owned pods were terminated and the account list was
verified empty.

The state integrator is Float64 RK4. The four bounded Newton updates only
locate the section root inside an RK4 step on a cubic-Hermite interpolant; they
are not an alternative time integrator. Adaptive DOP853 supplies the
independent short-horizon reference.

## Interpretation

The GPU is qualified for statistically convergent sprinkler ensembles at the
two controls. This is engineering parity, not independent saddle-method
corroboration and not a TBA continuation. The next scientific gate remains a
PIM-triple or stagger-and-step construction.

# EXP-018 — GPU Poincare-crossing and period-classification parity

Status: preregistered; paid execution pending
Manifest: `experiments/manifests/EXP-018-gpu-crossing-parity.json`
Claim targets: P1-002 and P1-003

## Purpose

Replace the short-horizon endpoint-only CUDA check with the exact observables
needed by production atlas and basin workloads: interpolated legacy-section
crossings and fundamental-period classification.

## Frozen controls and acceptance gate

Six stable periodic controls span the newly confirmed high-`a` periods 1, 2,
3, 7, and 12. CPU DOP853 uses the published reference section after transient
4,800. The Float64 GPU path uses fixed-step RK4 at both `dt=0.005` and
`dt=0.0025`, detects either crossing orientation, linearly interpolates the
section state, applies the small-equilibrium half-plane gate, and passes the
crossings to the same CPU recurrence classifier.

Both GPU step sizes must recover every expected fundamental period. The final
periodic crossing set must agree with the DOP853 orbit set within maximum cyclic
error `0.005`. The receipt also measures raw Float64 state-step throughput on a
32,768-trajectory batch. Chaotic trajectory identity and Lyapunov parity are
explicitly outside this gate.

## Paid-run authorization

The owner authorized a cumulative USD 100 ceiling. The live 2026-08-06 catalog
lists a community V100 PCIe at USD 0.19/hour. EXP-018 has a run-specific hard
ceiling of USD 0.20/hour and a 45-minute wall ceiling (USD 0.15 compute before
any provider rounding). The task-owned pod must be terminated after receipt and
artifact hashes are retrieved, whether the parity gate passes or fails.

No broad scan follows automatically from a failed parity result. A passing
result permits a separately frozen basin-scaling or multi-`b` atlas workload
with its own cost estimate.

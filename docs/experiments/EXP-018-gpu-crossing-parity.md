# EXP-018 — GPU Poincare-crossing and period-classification parity

Status: passed on NVIDIA L4; receipt hash verified; all pods terminated
Manifest: `experiments/manifests/EXP-018-gpu-crossing-parity.json`
Claim targets: P1-002 and P1-003

## Purpose

Replace the short-horizon endpoint-only CUDA check with the observables needed
by production atlas and basin workloads: legacy-section crossings and
fundamental-period classification.

## Frozen controls and acceptance gate

Six stable periodic controls span the newly confirmed high-`a` periods 1, 2,
3, 7, and 12. CPU DOP853 uses the published reference section after transient
4,800. The Float64 GPU path uses fixed-step RK4 at both `dt=0.005` and
`dt=0.0025`, detects either crossing orientation, localizes the section event
with a cubic-Hermite dense interpolant and bounded Newton refinement, applies
the small-equilibrium half-plane gate, and passes the crossings to the same CPU
recurrence classifier.

Both GPU step sizes must recover every expected fundamental period. The final
periodic crossing set must agree with the DOP853 orbit set within maximum cyclic
error `0.005`. The receipt also measures raw Float64 state-step throughput on a
32,768-trajectory batch. Chaotic trajectory identity and Lyapunov parity are
explicitly outside this gate.

## Why the first scientific run failed

The first authorized A40 run at source commit `7eff7c7` completed and correctly
failed the period-parity gate. Its linearly interpolated section points agreed
geometrically with the CPU orbit within the broad frozen orbit tolerance, but
the strict `1e-6` recurrence test returned spurious periods 8–19 or unresolved
labels. Halving the GPU step reduced the crossing-orbit discrepancy by about
four, the signature of the second-order event interpolation dominating the
fourth-order RK4 state step.

The tolerance was not relaxed. Commit `facf4b0` replaced linear section events
with fourth-order-compatible cubic-Hermite dense output. A subsequent L4 run
revealed that Triton 3.3 could not lower a nested compile-time Newton loop;
commit `20bd0b6` explicitly unrolled the four bounded Newton updates through a
JIT helper. This compiler-only correction left the numerical gate unchanged.

## Passing result

The final frozen source was commit
`20bd0b61865f9569e4d0cd8e3ffd2a70ea84bfdd`. Its 166,124-byte tracked-file-only
archive had SHA-256
`3e15a7e177e259c64dce401300e085261b200fcb231177c2543e8478f5d390e3`;
the remote hash matched before extraction.

The passing host was an NVIDIA L4 with compute capability 8.9 and 23.67 GB,
using Python 3.11.11, NumPy 2.1.2, SciPy 1.14.1, PyTorch
`2.8.0.dev20250319+cu128`, CUDA 12.8, and Triton 3.3.0.

- At `dt=0.005`, all six controls recovered periods 12, 3, 1, 7, 1, and 2.
  The largest cyclic orbit error was `4.633e-6`.
- At `dt=0.0025`, all six controls again recovered the same periods. The
  largest cyclic orbit error was `2.922e-7`.
- The 32,768-trajectory raw benchmark sustained 717,090,882 Float64
  state-steps/second. This is a throughput measurement only; it is not a
  period-classification rate.

The final receipt SHA-256 is
`880ad141085f1a81aa0a7f93aa38e3fe408a92df498f4716a74fe7321d1bcca6`.
The remote and retrieved hashes matched exactly. The full receipt is retained
under ignored `artifacts/EXP-018/receipt-passed.json`; its durable summary is
`docs/experiments/receipts/EXP-018.json`.

## Provisioning and spend record

The owner explicitly authorized uploading the frozen private repository archive
to task-owned Runpod hosts and retained the cumulative USD 100 project ceiling.
Several catalog allocations failed before creating a pod or never exposed a
runtime. A V100 that did boot could not run the installed PyTorch build because
compute capability 7.0 was below its supported minimum. An A40 produced the
useful failed numerical receipt; an L4 exposed the Triton compile issue; the
final L4 passed.

Every created host was terminated, and the final account pod list was verified
empty. A conservative upper bound for all EXP-018 provisioning and execution is
USD 0.25; provider billing is authoritative if it differs. No credential file,
Git metadata, untracked artifact, or working-tree state was uploaded.

## Decision

P1-002 and P1-003 pass for stable periodic Poincare observables. The GPU kernel
is now qualified to accelerate separately frozen basin-scaling and multi-`b`
atlas workloads. It is not yet qualified for chaotic trajectory identity,
Lyapunov spectra, continuation, or interval validation; those remain separate
gates.

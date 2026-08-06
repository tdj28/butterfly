# 2026-08-06 — Foundation and first resolved atlas

## Outcome

The recovered code has been turned into a tested reference implementation with
explicit scientific boundaries, reproducible receipts, and a staged AI/GPU
research program. The work has reached a trustworthy small-atlas pipeline, but
has not yet reproduced the periodicity hub at adequate spatial resolution.

## Completed

- Audited the recovered C/MPI code against Jones's paper claims.
- Recorded Jones and Barrio-Blesa-Serrano as independent, near-simultaneous
  co-discoverers of the return-map topology transition's relationship to
  periodicity-hub/shrimp organization.
- Implemented Float64 Rössler dynamics, analytic Jacobian and equilibria,
  adaptive DOP853 integration, interpolated Poincaré crossings, and conservative
  minimal-period recurrence.
- Implemented the full variational-equation/QR Lyapunov spectrum, integrated
  divergence trace identity, block uncertainty, and an independent nonlinear
  two-trajectory largest-exponent check.
- Added uncertainty-aware chaotic, quasiperiodic, periodic, conflict,
  multistable, escaping, failure, and unresolved classification rules.
- Qualified the classifier against four published Barrio-Blesa-Serrano controls:
  two chaotic attractors and two stable period-4 attractors.
- Ran the first `5 x 5` combined recurrence/Lyapunov hub-region pilot.

## Evidence

- EXP-004: hub-coordinate spectrum `(0.104322, 0.001399, -10.091625)`;
  trace-identity error `1.41e-9`; independent largest exponent `0.095542`.
- EXP-005: all four frozen published attracting-state labels matched; the two
  regular controls independently resolved as period 4.
- EXP-006: all 25 integrations succeeded; all points were decisively chaotic;
  largest-exponent two-standard-error lower bounds ranged from `0.05978` to
  `0.10357`; worst trace-identity error `1.81e-9`.
- Test suite at the checkpoint: 30 passing tests.

## Interpretation limits

EXP-006 is resolved at each sampled coordinate but scientifically under-sampled.
Its all-chaotic outcome cannot establish that periodic windows are absent
between grid points and does not test the hub claim. The result instead shows
that a coarse uniform grid is unsuitable for the narrow periodic structure.

The coexisting chaotic saddles at the published regular controls have not been
reconstructed. Continuation, Floquet multipliers, topology-change curves,
return-map critical structure, and validated numerics also remain open.

## Source checkpoints

- `c6f807b` — clean EXP-005 classifier receipt.
- `9e4c91e` — Lyapunov-resolved scan pipeline.
- `9f6e032` — clean EXP-006 resolved-atlas receipt.

## Next execution item

Immutable scan tiles, verified resume, corruption rejection, and deterministic
aggregation now pass EXP-007. A real local worker kill and verified restart pass
EXP-008. EXP-009 completed a clean `41 x 41` search in 212 seconds with four
workers; all strict labels remained unresolved, while three near-recurrences
were sharply separated from the bulk. EXP-010 then evaluated the frozen
lowest-1%-plus-neighbors set with spectra and two basin probes: 135 targets were
chaotic, two unresolved, and two periodic/chaotic multistability candidates.
The next execution item is focused longer-horizon replication, periodic-orbit
recovery, and Floquet analysis at those two candidates.

GPU spending remains behind the written cost gate. Transfer of private source
to a third-party worker also remains prohibited without explicit approval.

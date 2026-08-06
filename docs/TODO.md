# Execution backlog

This is the live implementation queue. A checkbox closes only when its
acceptance evidence exists in tests, receipts, or a cited experiment record.

## P0 — trustworthy Rössler reproduction

- [x] **P0-001 — Repository and paper claim audit.** Evidence:
  `docs/experiments/EXP-000-repository-audit.md` and `docs/claim-ledger.md`.
- [x] **P0-002 — Reference Rössler model.** Float64 vector field, analytic
  Jacobian, equilibria, and hub eigenstructure are implemented with unit tests.
- [x] **P0-003 — Adaptive CPU integration baseline.** DOP853 path has declared
  tolerances, equilibrium-invariance test, and a short-horizon convergence test.
- [x] **P0-004 — Poincaré section object.** Oriented, interpolated events;
  explicit section definition; section unit tests; legacy-section adapter.
- [ ] **P0-005 — Fundamental-period classifier.** Minimal recurrence period,
  escape/failure/unresolved labels, confidence, and synthetic tests exist;
  Lyapunov/convergence rules for chaotic/quasiperiodic/multistable remain.
- [ ] **P0-006 — Lyapunov spectrum.** Variational equations, QR cadence,
  convergence diagnostics, and cross-check against an independent implementation.
- [ ] **P0-007 — Reproducible scan artifacts.** Frozen manifests, atomic local
  result/receipt writes, hashes, and one-command tiny-grid scan exist; immutable
  multi-shard storage, resume, schema files, and archival promotion remain.
- [ ] **P0-008 — Legacy parity suite.** Recover representative legacy pixels and
  characterize discrepancies caused by fixed-step crossing/classifier logic.
- [ ] **P0-009 — Primary hub reproduction.** Coarse adaptive atlas, convergence
  sweeps, multiple initial conditions, and explicit unresolved regions.

## P1 — GPU qualification and bifurcation geometry

- [x] **P1-001 — Safe Runpod control script.** API key remains outside Git;
  list/catalog/launch/status/terminate commands; duplicate and hourly-cost gates.
- [ ] **P1-002 — GPU ensemble kernel.** Short-horizon endpoint kernel and parity
  gate exist; still required: manifest binding, compact Poincaré/classification
  observables, and deterministic production inputs.
- [ ] **P1-003 — Cheap NVIDIA qualification.** One cost-capped pod, environment
  receipt, measured throughput, artifact retrieval, hash verification, teardown.
- [ ] **P1-004 — Forced-kill/resume test.** Immutable tile IDs, atomic completion,
  verified restart before interruptible production use.
- [ ] **P1-005 — Continuation layer.** Hopf/equilibrium/periodic-orbit branches,
  Floquet multipliers, TBA/TTL curve, topology-change locus, independent cross-check.
- [ ] **P1-006 — Jones path definitions.** Exact `L1`/`L2` parameterizations and
  caustic/window-order reconstruction.

## P2 — topology, validation, and atlas expansion

- [ ] **P2-001 — Return-map topology.** Critical points, branch count, symbolic
  partitions, kneading data, entropy, and coordinate/section sensitivity.
- [ ] **P2-002 — Global bifurcations.** Homoclinic/heteroclinic boundary-value
  problems and bounded focal-point uniqueness claim.
- [ ] **P2-003 — Validated numerics.** Interval validation of selected decisive
  orbits, windows, crossings, and forcing/covering statements.
- [ ] **P2-004 — Two-system qualification.** Add two structurally different
  chaotic flows before scaling the registry.
- [ ] **P2-005 — Dozens-system atlas.** Curated systems, prospective parameter
  planes, negative results retained, uniform provenance and publication pipeline.

## Checkpoint policy

Commit and push after a coherent, verified milestone—not each file edit. The
current planned checkpoints are: reference core; event/classifier vertical
slice; first tiny atlas; GPU qualification; and each frozen experiment result.

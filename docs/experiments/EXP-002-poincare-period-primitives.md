# EXP-002 — Poincaré and period primitives

Status: exploratory implementation verification
Date: 2026-08-06
Claim targets: prerequisites for CLM-001, CLM-003, CLM-004, and CLM-006

## Purpose

Replace the recovered code's fixed-step, post-step crossing test and occupied-bin
proxy with explicit numerical objects that can be tested independently.

## Implemented checks

- A Poincaré section is a declared plane, orientation, and optional half-plane
  gate.
- Crossings are roots interpolated by the adaptive solver rather than the state
  after a sign-changing fixed step.
- The legacy compatibility section is `y=y_small_equilibrium` with
  `x<x_small_equilibrium`, accepting both orientations exactly as the C test did.
- Fundamental period is the smallest repeated return block passing declared
  absolute/relative tolerances for multiple repeats.
- Failure to find a period returns `unresolved`; it is not silently relabeled
  chaotic or quasiperiodic.

## Execution and result

```sh
.venv/bin/pytest
```

Result: 17 tests passed on Python 3.12.13. New tests cover crossing root error,
orientation, ordering, half-plane acceptance, exact/minimal/noisy periods,
insufficient data, numerical failure, escape, and unresolved nonperiodic input.

## Interpretation boundary

These are validated primitives, not a validated paper classifier. Promotion of
P0-005 still requires Lyapunov/convergence diagnostics, explicit chaotic and
quasiperiodic decision rules, multistability across initial conditions, and
period parity on frozen Rössler cases.

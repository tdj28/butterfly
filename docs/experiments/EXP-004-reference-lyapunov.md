# EXP-004 — Reference Lyapunov spectrum

Status: exploratory implementation qualification
Date: 2026-08-06
Claim target: CLM-003 and classification infrastructure

## Purpose

Implement the complete Rössler variational equations and compute the full
finite-time Lyapunov spectrum using periodic QR orthonormalization. This replaces
any scalar or undocumented Lyapunov proxy with an inspectable Float64 reference
path.

## Algorithm

- integrate the declared transient without tangent accumulation;
- integrate the state and a `3 x 3` tangent basis together;
- perform QR every declared interval;
- accumulate logarithms of the absolute diagonal of `R`;
- independently integrate the flow divergence `a + x - c`; and
- compare the sum of exponents with mean divergence as a trace-identity check.

The running finite-time estimates are retained as convergence diagnostics.

## Acceptance checks

1. At the proposed hub's small equilibrium, the finite-time spectrum approaches
   the real parts of the analytic Jacobian eigenvalues.
2. The exponent sum agrees with integrated mean divergence.
3. Invalid states and failed integrations produce explicit failures.
4. A chaotic trajectory has one positive, one near-zero, and one negative
   exponent, subject to a horizon sweep before freezing numerical values.

## Initial observations

At `(a,b,c)=(0.1798,0.2,10.3084)`, initial state `(0,4,0)`, a 200-unit
transient and 500-unit accumulation gave approximately
`(0.09137, 0.00180, -10.10505)`. With a 500-unit transient and 1500-unit
accumulation, the estimate was approximately
`(0.10432, 0.00140, -10.09162)`. The respective trace-identity errors were
`1.34e-9` and `1.41e-9`.

These runs support chaotic saddle/attractor-like spectral structure but do not
yet establish converged headline values: the largest exponent still shows
material finite-time variation. The next qualification is a declared
transient/horizon/QR/tolerance sweep plus an independent implementation.

The clean 1500-unit receipt is checked in at
[`receipts/EXP-004.json`](receipts/EXP-004.json). It is bound to source commit
`ffaf901bc26e5666ed7d260a96b675643f32ee6d`; the complete local artifact's
independently checked SHA-256 is
`91900209075f581baa746578f5424bb7ba510921d5bf2b5a05b307536678ad9b`.

## Reproducible command

```sh
.venv/bin/butterfly lyapunov \
  --a 0.1798 --b 0.2 --c 10.3084 \
  --initial-state 0 4 0 \
  --transient 500 --duration 1500 --qr-interval 0.5 \
  --rtol 1e-10 --atol 1e-12 --max-step 0.05 \
  --output artifacts/EXP-004/hub-lyapunov.json
```

## Interpretation boundary

The spectrum is a finite-time numerical observable. A near-zero exponent is not
forced to zero, and a single horizon is not considered converged. P0-006 remains
open until sweep criteria and an independent cross-check pass.

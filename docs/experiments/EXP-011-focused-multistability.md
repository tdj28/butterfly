# EXP-011 — Focused multistability and Floquet replication

Status: failed prospective qualification; transient-capture successor required
Manifest: `experiments/manifests/EXP-011-focused-multistability.json`
Claim target: focused replication of the two EXP-010 basin candidates

## Purpose

Rerun the period-6/chaos and period-8/chaos coexistence candidates with tighter
tolerances, doubled transients and Lyapunov horizons, stricter recurrence, an
independent nonlinear largest-exponent estimate for each chaotic basin, and
flow-monodromy/Floquet diagnostics for each periodic basin.

## Acceptance criterion

For each parameter point:

- the declared chaotic initial state remains chaotic;
- the independent largest exponent is positive and agrees within `0.03`;
- the periodic initial state passes the stricter expected fundamental period;
- both spectra pass the trace identity within `1e-6`;
- one Floquet multiplier lies within `0.05` of the neutral multiplier one; and
- every nontrivial multiplier recoverable in Float64 has modulus below one.

The monodromy calculation diagnoses a near-closed orbit recovered from section
returns. Exact shooting/collocation correction remains the next continuation
step and is not implied by this experiment.

## Result

The clean run from commit `c6dbb7d7f5cff115fac584b4e607ae383f2c425e`
failed the full prospective criterion.

The period-6 orbit itself passed strongly:

- fundamental period 6 with recurrence error `5.72e-12`;
- flow closure error `1.27e-11` over period time `40.0584`;
- neutral Floquet multiplier `1.000000000007`;
- leading nontrivial multiplier `-0.673339`; and
- smallest multiplier numerically near zero under extreme dissipation.

However, the other initial condition was uncertainty-limited rather than
decisively chaotic over the longer window. Its variational largest exponent was
`0.03237 +/- 0.01748` block standard error, while the independent nonlinear
estimate was positive at `0.04991`.

At the period-8 point, the nominal periodic initial condition was chaotic over
the EXP-011 window, so period-8 persistence failed at that horizon. This rejects
the simple persistent-multistability interpretation from EXP-010. EXP-012 tests
whether both cases are instead long nonperiodic transients followed by capture
into stable periodic windows.

The checked-in failure receipt is
[`receipts/EXP-011.json`](receipts/EXP-011.json). Failed acceptance is retained
as evidence rather than overwritten.

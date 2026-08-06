# EXP-011 — Focused multistability and Floquet replication

Status: prospective focused qualification
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

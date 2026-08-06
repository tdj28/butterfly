# EXP-012 — Long transient capture versus multistability

Status: passed; persistent-multistability interpretation rejected
Manifest: `experiments/manifests/EXP-012-transient-capture.json`
Claim target: distinguish the EXP-010 multistability appearance from CLM-015's
nonattracting chaotic-saddle mechanism

## Purpose

Track both initial conditions at the period-6 and period-8 parameter points
through transients from 800 to 12,800 time units. Persistent multistability
would retain distinct asymptotic labels. Transient capture instead predicts
unresolved/nonperiodic intermediate windows followed by convergence of both
initial states to the same stable periodic attractor.

## Acceptance criterion

At each parameter point, both initial states must classify as the same expected
period at transient 12,800, while at least one initial state must have an earlier
unresolved window. All integrations and crossing records are retained.

Passing supports long transient capture and rejects the simple persistent-
multistability interpretation. It does not alone compute or certify the
nonattracting chaotic saddle; sprinkler/edge-tracking or another invariant-set
method remains required for CLM-015.

## Result

The clean run from commit `e688a660a35a45533bd220c3314d7e364520b8a7`
passed in 96.5 seconds. Every checkpoint produced all 192 crossings.

| Point | Initial state | 800 | 1,600 | 3,200 | 6,400 | 12,800 |
| --- | --- | --- | --- | --- | --- | --- |
| period 8 | `(0,4,0)` | unresolved | unresolved | unresolved | period 8 | period 8 |
| period 8 | `(1,1,1)` | period 8 | period 8 | period 8 | period 8 | period 8 |
| period 6 | `(0,4,0)` | unresolved | unresolved | period 6 | period 6 | period 6 |
| period 6 | `(1,1,1)` | period 6 | period 6 | period 6 | period 6 | period 6 |

At transient 12,800, period-8 recurrence errors were `7.79e-9` and `2.46e-9`;
period-6 errors were `2.72e-10` for both initial states.

The two initial conditions therefore do not provide persistent distinct
attractors. EXP-010's finite-time `multistable` labels are revised to long
transient capture. Earlier positive finite-time Lyapunov evidence shows that the
transient is chaotic over substantial windows, but a nonattracting chaotic
saddle is not yet directly computed or certified.

The checked-in receipt is
[`receipts/EXP-012.json`](receipts/EXP-012.json).

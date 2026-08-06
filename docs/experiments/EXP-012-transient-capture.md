# EXP-012 — Long transient capture versus multistability

Status: prospective interpretation test
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

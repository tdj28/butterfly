# EXP-015 — High-`a` transient checkpoints

Status: preregistered; execution pending
Manifest: `experiments/manifests/EXP-015-high-a-transient-checkpoints.json`
Source: EXP-014 aggregate SHA-256
`85f8553ce644dd13b96e7596a7b85b613a8f2a233fd3147a3643ce28e898d75b`

## Purpose

Determine whether four EXP-014 finite-time multistability labels and one
boundary capture case collapse to common periodic attractors under much longer
transients. EXP-012 demonstrated that an apparent chaotic/periodic basin split
can instead be nonattracting chaotic-saddle capture; the same distinction is
mandatory before interpreting the high-`a` atlas.

## Frozen cases and method

The cases are `(a,c)=(0.245,5.75)`, `(0.255,12.5)`, `(0.26,11.75)`,
`(0.35,10.25)`, and `(0.36,5.0)`, all at `b=0.2`, with initial states
`(0,4,0)` and `(1,1,1)`.

Each trajectory is independently sampled after transients 1,200, 2,400, 4,800,
9,600, and 19,200. Each checkpoint then collects up to 192 crossings over
1,600 time units and tests minimal periods through 32 with eight repeats.
DOP853 uses `rtol=1e-10`, `atol=1e-12`, and `max_step=0.05`.

Common final periodic capture rejects persistent multistability for these two
basin probes. Distinct final periods retain—not prove—a persistent-
multistability candidate. Any unresolved or nonperiodic final state remains
open and requires still longer survival analysis or direct invariant-set work.

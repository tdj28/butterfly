# EXP-015 — High-`a` transient checkpoints

Status: completed; one persistent candidate promoted to Floquet gate
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

## Result

All 50 integrations completed successfully from clean commit
`7a7ae07`. Four cases collapsed to common periodic capture:

| `(a,c)` | Final common period | Notable transition |
| --- | ---: | --- |
| `(0.255,12.5)` | 1 | earlier period-2 appearance decayed |
| `(0.26,11.75)` | 7 | default initial state unresolved at 1,200, captured by 2,400 |
| `(0.35,10.25)` | 1 | period-2 appearance decayed between 2,400 and 4,800 |
| `(0.36,5.0)` | 2 | stable at every checkpoint |

At `(a,c)=(0.245,5.75)`, the default initial state remained period 12 and the
second initial state remained period 3 at every checkpoint through transient
19,200. Final recurrence errors were `2.60e-11` and `1.78e-11`. This retains a
strong persistent-multistability candidate and motivates EXP-016's independent
Floquet-stability gate for both cycles.

The checked-in receipt is [`receipts/EXP-015.json`](receipts/EXP-015.json).

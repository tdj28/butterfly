# EXP-133 — PIM-seeded UPO discovery

Status: preregistered exploratory experiment; unexecuted

## Question

Can close returns on the independently qualified `c=20` two- and three-branch
PIM saddles seed identity-qualified unstable periodic orbits?

This is a mechanism-discovery step, not a confirmation experiment. Prior
inspection identified promising lagged recurrences, so the selection is
explicitly recorded as informed rather than held out. No result from EXP-133
can by itself establish a TBA curve or a branch-opening manifold event.

## Frozen recovery gates

For each of the three 256-return PIM access trajectories on each side, the
selector ranks scaled close returns at lags 2 through 20. It retains at most
one candidate per lag and line below normalized distance `1e-4`, then caps the
case at the best 18 candidates.

Every candidate is independently advanced for its proposed number of exact
DOP853 section returns. A normalized exact-return closure above `1e-3` is
rejected before shooting; this is the protection against PIM pseudo-orbit
refinement resets. The remaining seed is corrected by phase-conditioned flow
shooting. Acceptance requires flow and phase residuals at most `1e-8`, a
neutral multiplier within `1e-4` of one, exactly the proposed number of
oriented Barrio-section crossings per flow period, and a nontrivial Floquet
modulus at least `1.001`.

At least one accepted UPO is required on each side. Stable period-4 convergence
is recorded but rejected by the transverse-instability gate. Direct and
divergence-predicted determinants are retained diagnostically; extreme
contraction makes their Float64 agreement nonbinding.

Immutable manifest:
`experiments/manifests/EXP-133-pim-seeded-upo-discovery.json`.

## Reproduction command

```bash
PYTHONPATH=python .venv/bin/python scripts/discover_pim_seeded_upos.py \
  --manifest experiments/manifests/EXP-133-pim-seeded-upo-discovery.json \
  --output artifacts/EXP-133/receipt.json
```

## Remote-execution boundary

A secure task-owned A5000 pod (`yztl38ljv875h4`) was provisioned under a
`$0.40/hour` cap and returned `$0.27/hour`. The attempted transfer correctly
stopped because the user's explicit private-upload authorization covered the
source archive but not the two derived PIM `.npz` inputs. The pod lacked
`rsync`, no source or state artifact transferred, no workload started, and the
pod was terminated with the account verified empty. Conservative provisioning
spend was below `$0.03`. EXP-133 therefore remains local-only unless those two
hashed derived inputs are separately authorized for remote upload.

## Result

The clean `bc6a3f8` local run passes in `23.47 s`. Nine of ten selected
recoveries pass on the two-branch saddle, at reported lags
`3,5,7,8,12,13`; one lag-15 shooting correction is retained as failed. All
six selected recoveries pass on the three-branch saddle at reported lags
`4,8,12`. Across accepted recoveries, maximum exact-return normalized closure
is `9.473e-5`, maximum corrected flow closure is `4.307e-11`, maximum neutral
multiplier error is `1.539e-9`, and the weakest unstable modulus is `3.484`.

These are recovery counts, not unique primitive-orbit counts. The exact
doubling of period and squaring of multiplier in some lag-8/lag-4 results
exposes a missing primitivity distinction. EXP-134 freezes the divisor-closure
and phase-invariant deduplication audit before any manifold use. Raw receipt
SHA-256:
`5c1135f8278ca6a836d50d0e855d8061ededf36b35aaeab787f5a385d703930c`.

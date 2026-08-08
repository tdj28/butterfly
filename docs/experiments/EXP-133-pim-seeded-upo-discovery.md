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

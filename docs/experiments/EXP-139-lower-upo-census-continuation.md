# EXP-139 — Complete lower-side primitive-UPO census continuation

Status: preregistered; unexecuted

## Question

Do any of the eight as-yet uncontinued primitive UPO families recovered from
the two-branch PIM saddle terminate or change fundamental section identity
inside the local two/three-branch interval?

## Frozen design

EXP-135 qualified nine distinct primitive lower-side families. EXP-138 already
continued family 06 (lag 12). EXP-139 continues representatives of the other
eight families from `a=0.148` to `a=0.14825` at fixed `(b,c)=(0.2,20)` on the
same 21-point `1.25e-5` grid.

The frozen source families have lags `13,5,7,8,7,13,7,3`. At every point,
phase-conditioned correction, DOP853 flow closure, neutral Floquet accuracy,
proper-divisor nonclosure, and transverse instability are stopping gates.
Their oriented Barrio crossing counts are evaluated separately over
`(0.1 T,1.1 T]` and must equal each branch's fundamental lag at all completed
points. No adaptive step rescue or family substitution is allowed.

The experiment passes only if all eight families reach the upper endpoint and
all 168 phase-robust section counts retain fundamental identity. A failure
selects the first stopped family for smaller-step or pseudo-arclength event
refinement; it does not alone prove a bifurcation.

Immutable manifest:
`experiments/manifests/EXP-139-lower-upo-census-continuation.json`.

## Reproduction command

```bash
PYTHONPATH=python:scripts .venv/bin/python scripts/continue_pim_upos_in_a.py \
  --manifest experiments/manifests/EXP-139-lower-upo-census-continuation.json \
  --source-receipt artifacts/EXP-133/receipt.json \
  --identity-receipt artifacts/EXP-135/receipt.json \
  --output artifacts/EXP-139/receipt.json
```

## Interpretation boundary

Even complete persistence of this finite census does not prove that no UPO is
created or destroyed at the boundary. It rules out that mechanism only for the
ten identity-qualified families now sampled across it and strengthens the case
for a manifold/pruning event.

# EXP-146 — Held-out midpoint UPO manifold seeds

Status: passed

## Question

Do all eleven continued primitive UPO families provide independently validated
unstable-manifold seeds at the untouched midpoint `a=0.1481875`?

## Frozen design

The source continuation receipts and every scientific threshold are unchanged
from passed EXP-142. The sole case is the exact midpoint between the last blind
two-branch point (`a=0.148125`) and the first blind three-branch point
(`a=0.14825`). All source continuations contain an identity-qualified row at
that exact value, but no midpoint manifold or PIM result has been inspected.

For each family, the section-tangent real unstable direction must reproduce
the signed fundamental-lag Floquet multiplier on both signs and at two of three
perturbation sizes. Base closure, section speed, direction normalization, and
independent exact-return integration retain the EXP-142 limits.

Immutable manifest:
`experiments/manifests/EXP-146-held-out-midpoint-upo-seeds.json`.

## Reproduction command

```bash
PYTHONPATH=python .venv/bin/python scripts/validate_upo_manifold_seeds.py \
  --manifest experiments/manifests/EXP-146-held-out-midpoint-upo-seeds.json \
  --output artifacts/EXP-146/receipt.json
```

## Interpretation boundary

A pass only qualifies the UPO side of the prospective midpoint association
test. It reveals neither the midpoint's saddle branch class nor whether its
PIM saddle includes the left lobe.

## Result

The clean `c623dee` run passes all eleven family instances in `22.15 s`.
Maximum signed-multiplier relative error is `2.946e-4`, maximum transverse
residual ratio is `3.313e-4`, and maximum independent base-lag closure is
`3.675e-9`. The midpoint PIM saddle remains uncomputed and blind.

Raw receipt SHA-256:
`9c57ddcd8d32ce78007b5d4aaa33477a04423573e77bd0c98262a2838cb0619e`.

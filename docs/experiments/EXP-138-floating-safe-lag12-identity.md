# EXP-138 — Floating-safe lag-12 flow-family identity

Status: passed

## Question

Does the complete EXP-137 flow-continuation result qualify when mathematical
grid equality is tested with a frozen `1e-14` absolute parameter tolerance
instead of bitwise Float64 equality?

## Frozen repair

EXP-137 passed both 21-point flow continuations and all 42 phase-shifted
section counts. Its only failed gate compared `0.14812499999999998` with
`0.148125` using `==`. The `2.78e-17` discrepancy is binary representation
roundoff, not a different parameter value.

EXP-138 changes only that implementation detail. The two stored midpoint
parameters must each lie within `1e-14` of the manifest value. Every flow,
Floquet, primitivity, shifted-section-count, and same/distinct identity
threshold is unchanged from EXP-137. The complete calculation is rerun from a
clean commit rather than editing or reclassifying the failed receipt.

Immutable manifest:
`experiments/manifests/EXP-138-floating-safe-lag12-identity.json`.

## Reproduction command

```bash
PYTHONPATH=python:scripts .venv/bin/python scripts/continue_pim_upos_in_a.py \
  --manifest experiments/manifests/EXP-138-floating-safe-lag12-identity.json \
  --source-receipt artifacts/EXP-133/receipt.json \
  --identity-receipt artifacts/EXP-135/receipt.json \
  --output artifacts/EXP-138/receipt.json
```

## Interpretation boundary

A pass qualifies the finite persistence and distinctness of these two
primitive lag-12 UPO families. It does not locate the manifold event that
changes the chaotic-saddle return-map branch count.

## Result

The clean `61c56d3` run passes in `127.16 s`. Both independent natural
continuations reach the opposite endpoint with 21/21 flow-orbit audits passed.
All 42 shifted crossing counts equal 12. At `a=0.148125`, the two families are
decisively distinct: relative period difference `1.7970e-3` and scaled
phase-invariant RMS `6092.16`. The maximum parameter representation error is
`2.78e-17`, safely below the frozen `1e-14` tolerance. Raw receipt SHA-256:
`a4ad0a077efd1b99b5b2947ed804bcd1e944eecf814b9d1e234a02ff354d71fb`.

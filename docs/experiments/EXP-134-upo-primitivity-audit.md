# EXP-134 — Prospective UPO primitivity and identity audit

Status: preregistered; unexecuted

## Trigger

EXP-133 passes its exploratory recovery gate with 15 accepted shooting
recoveries, but the three-branch lag-8 period and unstable multiplier are
numerically the square/double of the lag-4 result. Crossing-count identity
alone therefore does not distinguish a primitive orbit from repeated
traversal. No EXP-133 recovery will seed a manifold until this audit passes.

## Frozen audit

For every accepted recovery, test every proper integer repeat factor dividing
its reported section lag. A shorter traversal with flow closure at most
`1e-7` replaces the reported lag by the smallest recovered fundamental lag.
The audit then samples one fundamental traversal at 512 uniform flow phases
and groups only equal-lag candidates whose relative periods agree within
`1e-8` and whose best cyclic normalized RMS is at most `1e-6`.

At least one unique primitive family must remain on each side. A pass qualifies
finite UPO representatives for subsequent manifold seeding, not a manifold
intersection, branch-opening event, or TBA curve.

Immutable manifest:
`experiments/manifests/EXP-134-upo-primitivity-audit.json`.

## Reproduction command

```bash
PYTHONPATH=python .venv/bin/python scripts/audit_pim_upo_primitivity.py \
  --manifest experiments/manifests/EXP-134-upo-primitivity-audit.json \
  --source-receipt artifacts/EXP-133/receipt.json \
  --output artifacts/EXP-134/receipt.json
```

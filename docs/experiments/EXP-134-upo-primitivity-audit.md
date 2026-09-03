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

## Result

The clean `33f8498` run passes the frozen minimum in `4.08 s`. All nine
two-side recoveries are primitive under every proper-divisor closure test. On
the three side, both reported lag-8 recoveries close after half their periods
at approximately `1.1e-11` and reduce to lag 4; lag 12 remains primitive.

The nominal unique-family counts are nine below and four above. The above-side
count is not promoted: three lag-4 periods and spectra are numerically
identical but the coarse 512-shift comparison does not merge their different
phases. EXP-135 freezes continuous phase refinement before representative
selection. Raw receipt SHA-256:
`a269d64b04cb93777924f744551bb4e871e13a8158f59c96fcff6fc84aa88a93`.

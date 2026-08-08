# EXP-140 — High-precision lag-13 family-01 continuation

Status: preregistered; unexecuted

## Question

Was EXP-139's lone family stop caused by reference-integration precision, or
does lag-13 family 01 still fail natural continuation under tighter numerics?

## Frozen design

The original EXP-133 family-01 seed is rerun over the unchanged 21-point
`a in [0.148,0.14825]` grid. Relative and absolute DOP853 tolerances tighten
from `1e-10/1e-12` to `1e-11/1e-13`, maximum step halves from `0.05` to
`0.025`, and the corrector evaluation limit rises from 80 to 100. The
corrector tolerance, all scientific orbit/Floquet/primitivity thresholds, the
natural continuation step, and the phase-shifted lag-13 count are unchanged.

No adaptive step reduction is allowed. A pass classifies the EXP-139 stop as a
precision artifact. A repeated stop selects smaller-step and pseudo-arclength
refinement without proving a bifurcation.

Immutable manifest:
`experiments/manifests/EXP-140-lag13-high-precision-continuation.json`.

## Reproduction command

```bash
PYTHONPATH=python:scripts .venv/bin/python scripts/continue_pim_upos_in_a.py \
  --manifest experiments/manifests/EXP-140-lag13-high-precision-continuation.json \
  --source-receipt artifacts/EXP-133/receipt.json \
  --identity-receipt artifacts/EXP-135/receipt.json \
  --output artifacts/EXP-140/receipt.json
```

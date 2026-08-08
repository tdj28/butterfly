# EXP-141 — Acceptance-aligned lag-13 family-01 continuation

Status: passed

## Question

Does lag-13 family 01 cross the complete local branch interval when optimizer
convergence and scientific orbit acceptance are evaluated separately?

## Frozen repair

EXP-140 passes the original EXP-139 stop under tighter DOP853 integration, then
hits the same hardcoded `1e-10` corrector floor near the midpoint with closure
`1.025e-10` and normal `xtol` convergence. The failure location moved under
the numerical refinement and is not locked to the saddle branch boundary.

EXP-141 retains EXP-140's `1e-11/1e-13` DOP853 tolerances, `0.025` maximum
step, 21-point parameter grid, and every orbit/Floquet/primitivity/section
threshold. It changes only success bookkeeping:

1. the least-squares optimizer itself must report success;
2. its corrected seed must have closure and phase residual at most `1e-8`; and
3. the independent monodromy integration must still pass the unchanged
   `1e-8` flow-closure and all other scientific gates.

This does not loosen the declared scientific acceptance. It removes an
undocumented stricter floor from the control flow and records optimizer status
explicitly in future correction receipts.

Immutable manifest:
`experiments/manifests/EXP-141-lag13-acceptance-aligned-continuation.json`.

## Reproduction command

```bash
PYTHONPATH=python:scripts .venv/bin/python scripts/continue_pim_upos_in_a.py \
  --manifest experiments/manifests/EXP-141-lag13-acceptance-aligned-continuation.json \
  --source-receipt artifacts/EXP-133/receipt.json \
  --identity-receipt artifacts/EXP-135/receipt.json \
  --output artifacts/EXP-141/receipt.json
```

## Result

The clean `5a8f271` run passes all 21 points in `81.02 s`. All least-squares
optimizers converge, maximum corrected-seed closure is `1.172e-10`, and maximum
independent flow closure is `2.291e-9`. Every Floquet, primitivity, and shifted
lag-13 gate passes. Combined with EXP-136/138/139, this completes an eleven-
family cross-boundary UPO census. Raw receipt SHA-256:
`c245dbb1e4aa6a51651f918662acf0cc9bf75116f4bd854c38e9090ad262753b`.

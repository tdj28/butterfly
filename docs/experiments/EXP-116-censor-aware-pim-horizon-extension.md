# EXP-116 — Censor-aware PIM horizon extension

Status: preregistered; target controls not executed

## Hypothesis

The fixed 128-return two/three-branch PIM result retained from EXP-115 is
stable when the censor ceiling is doubled to 256 returns.

## Frozen reference and method

The 128-return critical intervals are copied exactly from EXP-115's raw
receipt, SHA-256
`f7b483334fa911ace7c11c499bb38d97756fb4623535c5200f7f606ea7d7e9b5`,
whose state artifact has SHA-256
`73962228b0d037c4e2c6e9dd16fc4b1a681af750e09aaf108a780459fc55b551`.
Those values are not recomputed or retuned.

Only the censor horizon changes from 128 to 256 returns. The three section
lines, 33-point censor-aware refinement, adaptive DOP853 solver, capture
neighborhood, 800 straddle returns, 100-return burn-in, two coordinates, CPU
reference, and 15 oracle variants are unchanged from EXP-115. The source must
be clean and committed before target execution.

## Acceptance criteria

Each 256-return control must independently have:

- a period-4 stable-cycle reference;
- at least two of three complete straddles and no integration failure;
- at least 1000 pooled consecutive return pairs per coordinate;
- all 15 oracle variants agreeing on the expected two/three count;
- within-profile normalized critical span at most `0.03`; and
- combined EXP-112/256-return PIM span at most `0.05`.

For each coordinate, the combined frozen-128/new-256 critical span must be at
most `0.04`. The experiment passes only if both controls pass every gate. A
pass qualifies 128/256 finite-horizon stability at the two controls; it does
not establish an infinite-lifetime saddle, a continued TBA, or Jones's
reinjection mechanism.

## Frozen execution

```sh
PYTHONPATH=python:scripts ./.venv/bin/python \
  scripts/qualify_censored_pim_horizon_extension.py \
  --manifest experiments/manifests/EXP-116-censor-aware-pim-horizon-extension.json \
  --output artifacts/EXP-116/receipt.json \
  --states-output artifacts/EXP-116/censor-aware-pim-256-straddles.npz
```

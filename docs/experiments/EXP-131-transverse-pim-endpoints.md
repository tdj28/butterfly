# EXP-131 — Prospective transverse PIM endpoint validation

Status: preregistered; PIM targets unexecuted

## Question

Do adaptive-DOP853 PIM constructions validate the two finite transverse
brackets selected—without claimed labels—by failed GPU discovery EXP-130?

The frozen predictions are:

| `c` | lower endpoint | prediction | upper endpoint | prediction |
|---:|---:|---:|---:|---:|
| 19.8 | `a=0.145` | 2 branches / negative slope | `a=0.148` | 3 branches / positive slope |
| 19.9 | `a=0.145` | 2 branches / negative slope | `a=0.150` | 3 branches / positive slope |

No PIM state has been generated at these four parameter points. The EXP-130
finite-sprinkler observations are selection data and cannot satisfy this test.

## Frozen method

Each endpoint must first recover a stable fundamental period-4 attractor using
DOP853. The exact censor-aware PIM method qualified in EXP-115/116 then refines
three fixed access segments at a 128-return censor ceiling, advances each
resolved straddle for 800 returns, and discards the first 100. At least two
lines must complete without a failed lifetime integration and provide 1000
pooled pairs in both `y` and `z`.

All 15 frozen branch-oracle variants must agree with critical-location span at
most `0.03`. All 15 signed lower-support variants must agree, clear magnitude
`0.1`, and map negative to two or positive to three. Both coordinates, the
critical-point count, the signed prediction, and the prospectively declared
endpoint class must agree.

Every endpoint must pass for EXP-131 to establish the two finite brackets. A
failed endpoint remains unresolved; it cannot be silently moved or relabeled.
A successful 128-return result is still finite evidence and triggers a frozen
256-return replication before curve continuation.

Immutable manifest:
`experiments/manifests/EXP-131-transverse-pim-endpoints.json`.

## Reproduction command

```bash
PYTHONPATH=python .venv/bin/python \
  scripts/qualify_censored_pim_saddle_controls.py \
  --manifest experiments/manifests/EXP-131-transverse-pim-endpoints.json \
  --output artifacts/EXP-131/receipt.json \
  --states-output artifacts/EXP-131/transverse-pim-straddles.npz
```

The run must start from the clean pushed preregistration commit. Raw artifacts
remain ignored; their hashes and a compact result receipt will be tracked.

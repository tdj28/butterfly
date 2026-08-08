# EXP-131 — Prospective transverse PIM endpoint validation

Status: failed as preregistered; one prediction prospectively falsified

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

Preflight provenance note: commit `d70c484` contained truncated literal hashes
for the two EXP-116 calibration rows. The calibration gate stopped before
cycle construction or target-state generation. The manifest was corrected to
the already frozen EXP-129 values; predictions and every numerical setting are
unchanged.

## Result

The clean `2eddd2f` run fails the strict four-endpoint gate in `9671.83 s`.
This is not a numerical or access failure: all twelve PIM lines resolve, every
case supplies 2097 return pairs in each coordinate, and all 72,717 lifetime
integrations succeed.

Only `(c,a)=(19.9,0.150)` passes fully as three/positive in all 30 branch and
30 signed-slope variants. Both `a=0.145` endpoints are 12/15 two-branch in
each coordinate with uniformly negative slope; their last three variants fail
only domain coverage at `0.675`. The frozen strict oracle therefore leaves
them unresolved even though their failure form matches the coverage censor
qualified independently in EXP-121.

Most importantly, `(19.8,0.148)` prospectively contradicts its three/positive
prediction: it is 12/15 two-branch in both coordinates, the remaining variants
are bootstrap-unstable, and all signed slopes are negative with intervals
`[-1.4647,-0.8185]` in `y` and `[-1.7981,-1.0380]` in `z`. The finite GPU
sprinkler prediction is therefore rejected rather than rescued. No transverse
bracket or curve is promoted from EXP-131.

Raw receipt SHA-256:
`21ae8580e0b9542868d69d91f3339c5477d8ca6b6024239c66abbf1680330dda`.
State archive SHA-256:
`3d7d1cd80d5e30664fa62fdbf48ff043dcad7033d39cf37681cb981ed943dd63`.
The compact tracked receipt is
`docs/experiments/receipts/EXP-131.json`.

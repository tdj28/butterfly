# EXP-132 — Prospective 256-return transverse PIM brackets

Status: preregistered; target state unexecuted

## Question

Does a higher 256-return censor ceiling validate the finite saddle-topology
brackets implied by EXP-131's prospective falsification?

| `c` | lower endpoint | prediction | upper endpoint | prediction |
|---:|---:|---:|---:|---:|
| 19.8 | `a=0.148` | 2 branches / negative slope | `a=0.150` | 3 branches / positive slope |
| 19.9 | `a=0.145` | 2 branches / negative slope | `a=0.150` | 3 branches / positive slope |

The `c=19.8,a=0.150` PIM target is untouched. Its three/positive prediction
comes from a stable period-4 gate and positive EXP-130 finite-sprinkler slopes
in both coordinates and both seeds. The other endpoint predictions come from
EXP-131's 128-return data and are tested here at a new censor horizon.

## Frozen coverage-censor rule

EXP-132 uses the rule independently qualified on new controls in EXP-121. At
least 12 of 15 variants must resolve the expected count normally. Every
remaining variant must fail only `insufficient invariant-domain coverage`,
retain coverage of at least `0.65`, remain below the unchanged `0.08`
conditional-spread gate, preserve exactly the expected nominal critical-point
count, and fit within the unchanged `0.03` joint critical-location span. Any
bootstrap instability, opposite branch count, noncoverage failure, or excess
drift fails.

The strict all-variant oracle is also retained in the receipt and is never
overwritten. Both coordinates must pass the censor rule, all signed slopes must
agree with the branch count and clear `0.1`, at least two PIM lines must
complete, and no lifetime integration may fail. All four endpoints must pass
to establish both finite brackets.

Even a complete pass establishes only two finite straddles at one `b`; it does
not establish a continuous TBA curve, its differentiability, or its mechanism.

Immutable manifest:
`experiments/manifests/EXP-132-transverse-pim-256-brackets.json`.

## Reproduction command

```bash
PYTHONPATH=python .venv/bin/python \
  scripts/qualify_censored_pim_saddle_controls.py \
  --manifest experiments/manifests/EXP-132-transverse-pim-256-brackets.json \
  --output artifacts/EXP-132/receipt.json \
  --states-output artifacts/EXP-132/transverse-pim-256-straddles.npz
```

The run must start from the clean pushed preregistration commit. Raw artifacts
remain ignored; their hashes and a compact result receipt will be tracked.

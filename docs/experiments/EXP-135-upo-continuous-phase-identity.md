# EXP-135 — Continuous-phase UPO identity audit

Status: preregistered; unexecuted

## Trigger

EXP-134 correctly reduces both three-side lag-8 recoveries to lag-4 double
traversals, but its frozen 512-point cyclic alignment does not merge three
lag-4 recoveries whose periods agree to approximately `4e-14` and whose
Floquet spectra are numerically identical. A grid phase error as large as half
a sample is incompatible with the `1e-6` identity gate.

## Frozen correction

Repeat the EXP-134 proper-divisor audit from the hashed EXP-133 receipt. For
same-fundamental-lag candidates whose relative periods agree within `1e-8`,
use the best of 512 phase shifts only as a bracket, then minimize the normalized
whole-orbit RMS continuously inside the adjacent phase cells to tolerance
`1e-12`. The unchanged family gate is RMS at most `1e-6`.

Both the EXP-133 and EXP-134 receipt hashes are binding. At least one unique
primitive family must remain on each side. The result selects finite orbit
families only; it does not identify their invariant manifolds or a TBA event.

Immutable manifest:
`experiments/manifests/EXP-135-upo-continuous-phase-identity.json`.

## Reproduction command

```bash
PYTHONPATH=python .venv/bin/python scripts/audit_pim_upo_primitivity.py \
  --manifest experiments/manifests/EXP-135-upo-continuous-phase-identity.json \
  --source-receipt artifacts/EXP-133/receipt.json \
  --predecessor-receipt artifacts/EXP-134/receipt.json \
  --output artifacts/EXP-135/receipt.json
```

## Result

The clean `3bffa13` run passes in `23.42 s`. The two-side result remains nine
distinct primitive families. On the three side, continuous phase alignment
merges all three direct lag-4 recoveries and both lag-8 double traversals into
one lag-4 family, with maximum member RMS `8.681e-7`; lag 12 remains a second
family. The qualified unique counts are therefore nine below and two above.

This qualifies representatives for orbit continuation and manifold seeding,
not a manifold event. Raw receipt SHA-256:
`e14655511f032efb16a5a8a69baeeadbbff522cb350e3b2a7229d373318e0c0f`.

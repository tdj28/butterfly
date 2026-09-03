# EXP-005 — Published classifier controls

Status: passed implementation qualification
Date: 2026-08-06
Claim target: classifier prerequisite for CLM-001 and CLM-003

## Purpose

Test the combined recurrence/Lyapunov classifier on real parameter values
declared in the 2012 Barrio-Blesa-Serrano paper rather than relying only on
synthetic sequences.

Figure 2 declares `b=0.2`, `c=20` and identifies:

- `a=0.11` and `a=0.2` as chaotic attractors; and
- `a=0.118` and `a=0.149` as stable periodic orbits coexisting with chaotic
  saddles.

The manifest freezes those four expected attracting-state labels before the
qualification run. It does not prescribe the periods of the stable orbits.

## Method

- one common initial state `(0,4,0)`;
- 1000-unit transient;
- up to 120 interpolated legacy-section crossings;
- minimal recurrence periods through 24 with five required repeats;
- 1000-unit full Lyapunov spectrum with five uncertainty blocks; and
- uncertainty-aware combined classification with conflict detection.

## Command

```sh
.venv/bin/python scripts/qualify_classifier_controls.py \
  --manifest experiments/manifests/EXP-005-classifier-controls.json \
  --output artifacts/EXP-005/classifier-controls.json
```

## Acceptance criterion

All four observed attracting-state labels must match the paper roles. Periods,
recurrence errors, three-exponent spectra, block errors, trace diagnostics, and
the exact source state must be retained. This does not yet reconstruct the
nonattracting chaotic saddles at the two regular points.

## Result

The clean qualification run passed all four frozen attracting-state labels:

| `a` | Paper role | Observed label | Recurrence | Lyapunov spectrum |
| ---: | --- | --- | --- | --- |
| 0.110 | chaotic attractor | chaotic | no period through 24 | `(0.078062, 0.001859, -19.796311)` |
| 0.118 | stable orbit with chaotic saddle | periodic | period 4, error `3.77e-12` | `(0.000985, -0.141263, -19.649704)` |
| 0.149 | stable orbit with chaotic saddle | periodic | period 4, error `5.95e-12` | `(0.001599, -0.041842, -19.615981)` |
| 0.200 | chaotic attractor | chaotic | no period through 24 | `(0.099999, 0.000324, -19.395212)` |

Every spectrum also passed the integrated-divergence trace diagnostic. The
largest exponents at the two periodic controls are compatible with the neutral
flow direction once the block uncertainty is included; the other two
exponents are contracting. At the chaotic controls the positive largest
exponent is well separated from its block uncertainty.

Clean source commit: `d76c7afe303ee0112608eaf3164d55db0ec9ecc9`

Manifest SHA-256: `529fba1a094dd0b72666a9c19152b9a27dd6db9125c6bf23d0963eb87c8ab1bc`

Full artifact SHA-256: `e086a14ff6f5b6f54674acbf5813278b040b272fea441d574e3ce351fc652a95`

The checked-in receipt is
[`receipts/EXP-005.json`](receipts/EXP-005.json). The larger machine-generated
artifact remains under ignored `artifacts/EXP-005/` and can be reproduced with
the command above.

## Interpretation and remaining gap

This qualifies the combined classifier on published periodic and chaotic
attractors and gives an independent period finding for the two regular
controls. It does **not** reconstruct, continue, or certify the coexisting
nonattracting chaotic saddles reported at `a=0.118` and `a=0.149`. Those require
dedicated saddle-preserving methods and remain future work.

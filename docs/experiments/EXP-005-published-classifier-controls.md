# EXP-005 — Published classifier controls

Status: implementation qualification
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

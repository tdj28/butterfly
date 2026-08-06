# EXP-003 — Tiny hub scan

Status: exploratory infrastructure qualification
Manifest: `experiments/manifests/EXP-003-tiny-hub.json`
Claim target: infrastructure prerequisite for CLM-001

## Purpose

Exercise the complete local path from a frozen parameter-plane manifest through
interpolated crossings, conservative period classification, immutable result
serialization, and a hash-verifiable receipt.

## Prospective boundary

The `3 x 3` grid is intentionally too small to reproduce the hub. Success means
only that all nine declared points produce schema-valid records whose plan,
input, source state, environment, and result bytes are captured. Scientific
interpretation of the labels is prohibited at this resolution.

## Command

```sh
.venv/bin/butterfly scan \
  --manifest experiments/manifests/EXP-003-tiny-hub.json \
  --output-dir artifacts/EXP-003
```

The generated directory is ignored by Git. Its `receipt.json` binds the exact
result hash and source state; promotion to a durable dataset will require an
external immutable archive and dataset ID.

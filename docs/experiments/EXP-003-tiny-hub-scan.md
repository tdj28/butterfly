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

## Observed qualification result

The clean-source run at commit `0316c7ab1a286ed94f5a4ece7b3286f0774176d8`
completed all nine integrations in 2.364 seconds on arm64 macOS. Every point
produced 35 or 36 accepted crossings and was conservatively labeled
`unresolved`. That label distribution is infrastructure evidence only and is
not evidence that periodic windows are absent.

The result SHA-256 was
`c5c2c5b9e752fd65c0ebaf963edefbdc15f5b1fcef1ecd21ed781f5e1fd77ff3`;
an independent `shasum -a 256` invocation matched it. The checked-in receipt is
[`receipts/EXP-003.json`](receipts/EXP-003.json). The ignored result bytes remain
local pending a durable dataset/archive policy.

# EXP-006 — Resolved hub pilot

Status: prospective pilot
Manifest: `experiments/manifests/EXP-006-resolved-hub-pilot.json`
Claim target: first bounded step toward CLM-001 and P0-009

## Purpose

Replace the recurrence-only `3 x 3` infrastructure scan in EXP-003 with a
small parameter-plane scan whose nonperiodic labels require uncertainty-aware
full-spectrum Lyapunov evidence. This is a pipeline and resolution pilot, not a
reproduction of the periodicity hub.

## Prospective boundary

The frozen `5 x 5` grid spans `a in [0.175, 0.185]`, `c in [10.1, 10.5]` at
`b=0.2`. Its 0.0025-by-0.1 spacing is far too coarse to resolve narrow periodic
windows or hub spirals. A chaotic label asserts only the declared finite-time
signature at that grid point; an unresolved label remains unresolved.

The pilot uses one initial condition. Basin and multistability checks belong to
the next refinement and no claim about absence of windows is permitted.

## Method

- 500-unit crossing transient and up to 96 interpolated section crossings;
- minimal recurrence periods through 24 with five required repeats;
- 300-unit Lyapunov transient and 600-unit spectrum;
- six contiguous uncertainty blocks; and
- the same sufficient, conflict-detecting rules qualified in EXP-005.

## Command

```sh
.venv/bin/butterfly scan \
  --manifest experiments/manifests/EXP-006-resolved-hub-pilot.json \
  --output-dir artifacts/EXP-006
```

## Acceptance criterion

All 25 points must complete with finite spectra and trace-identity diagnostics,
retain recurrence and Lyapunov evidence, and produce hash-bound artifacts from
a clean source commit. The outcome must explicitly report label counts and may
be entirely chaotic or unresolved without being treated as a failed run.

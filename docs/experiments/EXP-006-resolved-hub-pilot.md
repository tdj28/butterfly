# EXP-006 — Resolved hub pilot

Status: passed pipeline pilot; scientifically under-resolved
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

## Result

The clean run passed the pipeline criterion from source commit
`9e4c91e8fa89bcc1238eeb7574cb1f7497725c5c`:

- all 25 crossing integrations and Lyapunov integrations succeeded;
- every point produced all 96 requested crossings;
- all 25 points were classified `chaotic`;
- the largest finite-time exponent ranged from `0.07745` to `0.11015`;
- its conservative lower bound `lambda_1 - 2 SE` ranged from `0.05978` to
  `0.10357`; and
- the maximum absolute trace-identity error was `1.81e-9`.

The result SHA-256 is
`b769bf01904566935be59c8ed809c4925f8ad50acf34f035f930fa7db6e16f4f`;
an independent `shasum -a 256` invocation matched it. The checked-in receipt is
[`receipts/EXP-006.json`](receipts/EXP-006.json).

## Interpretation

This grid is **resolved but under-sampled**: the individual classifications are
decisive at the sampled coordinates, while the spacing is inadequate to detect
the hub's narrow periodic windows. Therefore the all-chaotic result must not be
rendered as a featureless parameter region or used against CLM-001. It is direct
evidence that the next pass needs periodic-candidate discovery on a substantially
finer grid followed by full-spectrum confirmation only at candidates and their
boundaries. That staged design is also the correct target for GPU qualification.

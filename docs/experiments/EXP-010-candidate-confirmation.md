# EXP-010 — Candidate confirmation with basin probes

Status: prospective confirmation run
Manifest: `experiments/manifests/EXP-010-candidate-confirmation.json`
Claim target: confirmation stage for P0-005 and P0-009

## Purpose

Confirm or reject the frozen EXP-009 lowest-1%-plus-neighbors set using longer
crossing records, full Lyapunov spectra, uncertainty-aware classification, and
two initial conditions per parameter point.

## Frozen selection

The manifest binds the exact EXP-009 aggregate result hash, selects the lowest
1% of finite normalized near-recurrence scores, and adds every in-grid neighbor
within Chebyshev radius one. This deterministically produces 17 core points and
139 total targets. Selection is recomputed and verified at runtime; the cases
are not chosen manually after inspecting their confirmation behavior.

## Method

- initial states `(0,4,0)` and `(1,1,1)`;
- 800-unit crossing transient and up to 128 interpolated crossings;
- minimal periods through 24 with six required repeats;
- 400-unit Lyapunov transient and 800-unit full spectrum;
- six uncertainty blocks; and
- aggregation across initial conditions with explicit multistability.

## Command

```sh
.venv/bin/python scripts/confirm_candidates.py \
  --manifest experiments/manifests/EXP-010-candidate-confirmation.json \
  --source-result artifacts/EXP-009/aggregate/result.json \
  --output-root artifacts/EXP-010 \
  --tile-count 32 \
  --workers 4 \
  --resume
```

## Acceptance criterion

Every selected point must produce a retained result for both initial conditions
or an explicit failure. Periodic recurrence conflicting with positive Lyapunov
evidence remains unresolved. Distinct resolved attractor signatures are labeled
multistable. The receipt must bind the source aggregate, selection, manifest,
source commit, tile outputs, and confirmation aggregate.

No candidate is promoted solely because it ranked highly in EXP-009.

# EXP-147 — Held-out midpoint UPO lobe atlas

Status: preregistered; not yet executed

## Question

Does the qualified midpoint UPO library populate the unchanged left-lobe
domain with density-converged, capture-truncated unstable traces before the
midpoint PIM saddle is classified?

## Frozen design

All eleven passed EXP-146 seeds are traced on both signs and the unchanged nine
logarithmic amplitudes for 64 exact returns: 198 trajectories. Stable period-4
capture, occupancy domain, nested five/nine-amplitude coverage, solver, and
group gates match EXP-143. The unchanged left-lobe threshold is
`y < -31.135026064071056`; at least 500 fine and 250 coarse pre-capture points
must enter it.

Immutable manifest:
`experiments/manifests/EXP-147-held-out-midpoint-upo-lobe.json`.

## Reproduction command

```bash
PYTHONPATH=python:scripts .venv/bin/python scripts/trace_midpoint_upo_lobe.py \
  --manifest experiments/manifests/EXP-147-held-out-midpoint-upo-lobe.json \
  --output artifacts/EXP-147/receipt.json
```

## Interpretation boundary

This run deliberately cannot classify the midpoint saddle. It only freezes the
UPO lobe reference against which the later independent PIM reconstruction will
be tested.

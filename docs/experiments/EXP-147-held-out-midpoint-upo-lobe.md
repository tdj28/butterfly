# EXP-147 — Held-out midpoint UPO lobe atlas

Status: passed; midpoint PIM remains blind

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

## Result

The clean `abe7da6` run passes all 198 trajectories and 22 family/sign groups
in `71.18 s`, with no integration failure. It retains 11,740 pre-capture
points; the weakest group has 451. All points remain inside the declared
domain, and minimum nested-grid occupancy coverage is `0.9423`.

The unchanged left lobe contains 989 fine-grid and 558 coarse-grid points, both
reaching `y=-31.7490706791`. The independent midpoint PIM saddle has still not
been generated or inspected.

Raw receipt SHA-256:
`2f6a80c968dc3f9afbba3b25bb82919fa5b4456f1e2ed4014287f93b2359c54e`.

# EXP-143 — Capture-truncated UPO unstable-lobe atlas

Status: passed; four exploratory refinement targets selected

## Question

Which validated UPO unstable branches show the largest reproducible change in
first-return occupancy between the local two- and three-branch endpoints?

## Frozen design

All 22 passed EXP-142 family-endpoint seeds are traced on both unstable signs.
Each sign uses nine nested logarithmic amplitudes from `1e-9` to `1e-8` and 64
exact Barrio returns. Four consecutive returns within scaled radius `1e-4` of
an independently recovered stable period-4 cycle qualify capture; the capture
streak and all later points are removed from lobe analysis.

The stable cycle is reconstructed from `(1,1,1)` after 1000 flow-time units and
must repeat after four section returns to scaled error `1e-7`. Each of the 44
family/sign groups must retain at least 50 pre-capture points, keep at least 95%
inside the frozen `(y,z)` analysis domain, and have a five-amplitude coarse
subset cover at least half the nine-amplitude occupancy within one 48-bin cell.

For each family/sign, endpoint change is ranked by

`1 - dilated occupancy Jaccard + 0.25 * |capture-fraction change|`.

The four highest eligible scores are selected automatically for later adaptive
curve refinement. Selection is exploratory: it is not a pruning or connection
claim.

Immutable manifest:
`experiments/manifests/EXP-143-capture-truncated-upo-lobe-atlas.json`.

## Reproduction command

```bash
PYTHONPATH=python:scripts .venv/bin/python scripts/trace_upo_unstable_lobe_atlas.py \
  --manifest experiments/manifests/EXP-143-capture-truncated-upo-lobe-atlas.json \
  --output artifacts/EXP-143/receipt.json
```

## Interpretation boundary

The atlas compares finite, capture-truncated point-cloud occupancy under one
section and grid. A candidate must subsequently pass adaptive seed refinement,
alternate occupancy resolution, orbit-phase coverage, and a direct connection
residual before it can support a topological mechanism.

## Result

The clean `a13e043` host run passes in `144.31 s`. All 396 trajectories and 44
groups qualify, retaining 23,871 pre-capture points. Minimum coarse-to-fine
occupancy coverage is `0.9423`; no point leaves the analysis domain. The frozen
score selects lower family 06 lag 12 negative, family 03 lag 7 positive,
family 02 lag 5 positive, and family 07 lag 13 positive. Their endpoint
occupancy remains highly overlapping, so the selection is explicitly driven
in part by capture-fraction changes. Raw receipt SHA-256:
`f0dda22c2739859633883b53d80de5558a8f4f3bc4d1ec669a5f685ee9b82c1d`.

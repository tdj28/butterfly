# EXP-144 — Phase-resolved capture refinement

Status: preregistered; not yet executed

## Question

Do the four capture-sensitive unstable branches selected by EXP-143 retain the
same endpoint shift when seed density, orbit phase, and censor horizon are
changed prospectively?

## Frozen design

The candidate list and order are read from the hash-bound EXP-143 receipt.
For each of its four branches, both local endpoints are evaluated at three
approximately one-third-orbit phase offsets and 17 nested logarithmic seed
amplitudes from `1e-9` through `1e-8`. This gives 408 exact-return trajectories.

Floquet directions are transported to each phase by central differences of
the exact Poincare return. Each transported direction must reproduce the
original signed fundamental-lag multiplier to 1% relative error with at most
1% transverse residual. The stable period-4 capture target and four-crossing,
scaled-radius-`1e-4` definition are unchanged from EXP-143.

Capture time is summarized at administrative horizons 64 and 96. A capture
counts at a horizon only if all four required close crossings have occurred by
that horizon. At each phase and endpoint, the nine-amplitude nested subset
must reproduce the 17-amplitude restricted mean to within two returns. The
three-branch endpoint must shift the mean by at least five returns in the same
direction at all three orbit phases and both horizons.

Immutable manifest:
`experiments/manifests/EXP-144-phase-resolved-capture-refinement.json`.

## Reproduction command

```bash
PYTHONPATH=python:scripts .venv/bin/python scripts/refine_upo_lobe_capture.py \
  --manifest experiments/manifests/EXP-144-phase-resolved-capture-refinement.json \
  --output artifacts/EXP-144/receipt.json
```

## Interpretation boundary

A pass qualifies a phase- and density-robust change in capture timing for a
specific unstable branch. It does not establish a heteroclinic connection,
symbolic pruning event, reinjection rotation, or causal explanation of the
two/three-branch transition. A failure remains informative and prevents the
exploratory EXP-143 ranking from being promoted.

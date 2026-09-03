# EXP-144 — Phase-resolved capture refinement

Status: failed prospectively; exploratory capture contrast rejected

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

## Result

The clean `2fb5843` host run completes all 408 trajectories without an
integration failure in `159.73 s`, and all 24 transported phase directions
pass. The largest multiplier error is `0.001875` and the largest transverse
residual ratio is `0.002057`, both well inside the frozen 1% gates.

The scientific gate fails. Only 13 of 24 phase/endpoint summaries pass the
nested-grid tolerance, whose maximum discrepancy is `5.242` returns. No
candidate has an absolute 96-return endpoint difference of at least five
returns at all three phases. Two candidates also reverse endpoint direction
between administrative horizons at one phase. The four EXP-143 capture
contrasts are therefore rejected as robust mechanism observables.

Raw receipt SHA-256:
`3bf51ed589efbfa98ee3c968f008d804bde9c48bc36fa550e359a7afd72b5987`.

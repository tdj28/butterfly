# EXP-136 — Primitive UPO continuation across the local boundary

Status: executed; strict gate failed with qualified positive and negative result

## Question

Do the shared lag-12 UPO recoveries form one continuous primitive family across
`a in [0.148,0.14825]`, and does the upper lag-4 UPO persist to the two-branch
side?

## Frozen continuations

At fixed `(b,c)=(0.2,20)`, natural continuation uses steps of `1.25e-5`:

- lag 12 from the qualified lower recovery upward;
- lag 12 independently from the qualified upper recovery downward; and
- lag 4 from the qualified upper representative downward.

Every point must pass DOP853 flow closure `1e-8`, neutral-multiplier error
`1e-5`, the exact fundamental section lag, transverse instability margin
`0.001`, and nonclosure above `1e-3` at every proper integer divisor. The two
lag-12 paths must both land exactly at `a=0.148125`, agree in period to `1e-6`
relative, and agree by continuous phase-invariant whole-orbit RMS at `1e-5`.

Any failed correction or identity gate stops and fails that path; no adaptive
step reduction is allowed in this prospective test. A lag-4 pass to the lower
endpoint rules out birth/death of this orbit as the branch-opening event over
the sampled interval, but leaves a manifold rearrangement possible. A failure
selects a smaller-step or pseudo-arclength event audit; it does not by itself
prove an orbit bifurcation.

Immutable manifest:
`experiments/manifests/EXP-136-upo-continuation-across-local-boundary.json`.

## Reproduction command

```bash
PYTHONPATH=python:scripts .venv/bin/python scripts/continue_pim_upos_in_a.py \
  --manifest experiments/manifests/EXP-136-upo-continuation-across-local-boundary.json \
  --source-receipt artifacts/EXP-133/receipt.json \
  --identity-receipt artifacts/EXP-135/receipt.json \
  --output artifacts/EXP-136/receipt.json
```

## Result

The clean `2535614` run fails its strict all-branch gate in `30.58 s`. The
lag-4 path passes all 21 points through the entire bracket. Its unstable
modulus changes smoothly from `3.484` to `3.664` and every proper-divisor
closure remains above `5.36`.

Both lag-12 paths stop only on the frozen crossing-count gate. The lower path
reports 11 rather than 12 crossings at `a=0.148025`; the upper does so at
`a=0.1482375`. At both failed points, correction, flow closure, neutral
multiplier, primitivity, and transverse instability pass. Because neither path
reaches the declared midpoint, the endpoint families are not classified as
equal or different.

The initial physical interpretation of this failure as a section tangency has
been rejected by a post-hoc boundary audit. The shooting phase is within about
`1.1e-6` time units of the section, but the frozen one-period window had only a
`7.5e-7` terminal allowance. Moving the window to `(0.1 T, 1.1 T]` returns 12
crossings at all five tested lag-12 points, while the closest x-extremum is
more than 8 units from the section. EXP-136 therefore selects a prospective
phase-robust flow continuation, not tangency refinement. Raw receipt SHA-256:
`6c10804172d3463f99be9340744a849cb61cf7015036ba57340db7bcfcde1b4e`.

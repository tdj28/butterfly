# FND-007 — The published saddle branch is shallow and requires statistical convergence

Status: reproducible diagnostic after a retained prospective failure

## Result boundary

EXP-110 is the first frozen survival-ensemble reconstruction at the two regular
controls in Barrio, Blesa, and Serrano's Figure 2. It **did not pass** its
preregistered acceptance gate. The complete ignored artifact is
`artifacts/EXP-110/receipt.json`; its tracked summary and hash are in
`docs/experiments/receipts/EXP-110.json`.

The run nevertheless resolves the obstruction unusually clearly:

- DOP853 recovers a stable period-4 section cycle at both `a=0.118` and
  `a=0.149`.
- No one of the 16,384 fixed-step trajectories escapes numerically or becomes
  nonfinite.
- Survivor populations decay from 8192 to 2775 and 1564, respectively.
- Final survivors supply 23,022 and 12,892 within-trajectory return pairs per
  coordinate.
- At `a=0.118`, both coordinates pass the frozen oracle with the published
  two branches, full bootstrap consensus, and full domain coverage.
- At `a=0.149`, both coordinates are graph-like and densely covered, but the
  frozen 3-percent global-prominence rule reports only two branches.

## The missing branch is present but below the frozen prominence cutoff

Direct inspection of the retained `a=0.149` relation shows a shallow left-hand
maximum followed by the large minimum. This is the same qualitative feature
visible in the published Figure 2(d). A post-result threshold diagnostic—not a
prospective claim—finds:

| Coordinate | Diagnostic prominence | Critical points | Bootstrap agreement |
|---|---:|---|---:|
| `y` | 0.005 of global target range | `-31.1847088`, `-20.9115707` | 100/100 |
| `z` | 0.010 of global target range | `0.0093615262`, `0.0095429341` | 100/100 |

For `y`, the first critical point persists across smoothing values from
`1e-6` through `3e-5` when prominence is at most `0.005`; for `z`, it persists
through prominence `0.010` for the baseline smoothing. The frozen `0.03`
criterion removes this shallow extremum by construction.

This is good evidence that the sprinkler ensemble has reached the published
bimodal saddle shape. It is not yet a qualified reproduction because the
original acceptance threshold rejected it. A new oracle must measure a local
feature relative to local sampling uncertainty rather than impose a fixed
fraction of the entire map's amplitude. This matters theoretically: a branch
born at a topology transition begins with vanishing prominence, so a positive
global cutoff displaces the detected transition away from the bifurcation.

## Why the pointwise precision audit failed

The frozen fixed-step versus DOP853 capture audit agrees on 12/16 labels at
`a=0.118` and 13/16 at `a=0.149`, below the required 90 percent. The mismatches
occur in both directions. After many chaotic returns, microscopic integration
differences change an individual trajectory's finite-time capture history;
pointwise identity is therefore an ill-conditioned long-horizon convergence
observable even when ensemble statistics agree.

The replacement qualification must retain short-horizon numerical checks but
compare long-horizon methods statistically: survivor curves, capture-time
distributions, invariant-domain coverage, conditional spread, and critical
point confidence. CPU-to-GPU parity should use the same ensemble-level gates;
bitwise survivor identity is too strong for independently rounded chaotic
trajectories.

## Implication for the 2012 claims

This result is encouraging for both papers' shared topology direction. It is
the first modern finite-time saddle ensemble in this project to expose the
shallow additional extremum at the published regular control. It strengthens
the interpretation that the attracting-set gap in EXP-109 hides a continuing
chaotic invariant structure rather than ending it.

It does not yet establish the TBA curve, a topological template, or Jones's
third-branch reinjection mechanism. Those require a prospectively qualified
local-uncertainty oracle, time/step/grid convergence, and an independent
chaotic-saddle construction.

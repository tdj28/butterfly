# EXP-014 — Spatially diverse high-`a` target qualification

Status: completed finite-time qualification; transient successor pending
Manifest: `experiments/manifests/EXP-014-wide-target-qualification.json`
Source: EXP-013 aggregate result SHA-256
`58aa45114962c285edff6deab08915f89f953b5b7437996b82bb9a7ad6e50e3d`

## Purpose

Test whether the periodic islands and near-recurrences discovered by EXP-013
survive stronger finite-time classification across two basin probes. This is a
qualification gate before spending effort on local mesh refinement, Floquet
analysis, or continuation.

## Frozen selection

The 39 explicit point indices were frozen after the EXP-013 family summary:

- 24 periodic detections spanning periods 1, 2, 4, 5, 6, 8, and 12, the main
  diagonal band, separated high-`a` islands, and both search boundaries; and
- 15 unresolved near-recurrences spanning candidate periods 2, 4, 6, 7, 8,
  12, and 16 and several disconnected parts of the rectangle.

The exact source-result hash and point indices are inputs to the execution plan.
The selection is intentionally spatially and dynamically diverse rather than a
post hoc claim of statistical representativeness.

## Method and acceptance gate

- initial states `(0,4,0)` and `(1,1,1)`;
- DOP853 at `rtol=1e-10`, `atol=1e-12`, and `max_step=0.05`;
- crossing transient 1,200, 1,200 observation units, and 160 crossings;
- recurrence periods through 32 with six repeats;
- full variational Lyapunov spectrum after an 800-unit transient for 800 units;
- eight uncertainty blocks; and
- immutable tiled output bound to clean source and the EXP-013 result hash.

Every target must retain both initial-condition results or an explicit numerical
failure. Agreement of both probes on a stable period promotes a point to exact
periodic-orbit recovery and Floquet analysis. Chaos is only a finite-time label;
EXP-012 requires long transient checkpoints before an asymptotic claim.

## Result

The clean run from commit `fc64ad7c52f95e8344449d5e247a264ad79cfbef`
completed all 39 targets and 78 initial-condition integrations without a
numerical failure. The combined labels were 26 periodic, nine unresolved, and
four finite-time multistable. The summed tile runtime was 590.2 seconds.

The four distinct finite-time outcomes were:

| `(a,c)` | Initial `(0,4,0)` | Initial `(1,1,1)` |
| --- | --- | --- |
| `(0.245,5.75)` | period 12 | period 3 |
| `(0.255,12.5)` | period 2 | period 1 |
| `(0.26,11.75)` | chaotic | period 7 |
| `(0.35,10.25)` | chaotic | period 2 |

These are not promoted to persistent multistability. EXP-015 freezes checkpoint
tests through transient 19,200. The 26 consensus-periodic targets support the
existence of periodic structure throughout the high-`a` rectangle and become
candidates for exact orbit/Floquet recovery.

Aggregate result SHA-256:
`85f8553ce644dd13b96e7596a7b85b613a8f2a233fd3147a3643ce28e898d75b`.
The checked-in receipt is [`receipts/EXP-014.json`](receipts/EXP-014.json).

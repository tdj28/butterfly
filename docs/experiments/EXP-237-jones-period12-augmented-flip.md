# EXP-237 — Segmented augmented period-12 flip

Status: frozen — not yet executed

EXP-236's full-period corrector converges to the period-12 parent traversed
twice. EXP-237 changes representation rather than thresholds. It samples the
qualified EXP-232 period-12 orbit into 16 shooting segments and solves the
orbit plus its anti-periodic tangent field as one exact augmented system at
fixed `b=0.2` and `c=7.625815600403827`, with `a` as the event parameter.

The frozen gates require small orbit, phase, tangent, and normalization
residuals; agreement with the EXP-232 event; independent Radau closure and
real-`-1` multiplier; primitive `14/16` section identity; and nonclosure at
every proper subperiod. A pass supplies event nodes and the tangent mode for a
separately frozen segmented period-24 switch. It does not itself establish a
period-24 child or its stability.

Manifest:
[`../../experiments/manifests/EXP-237-jones-period12-augmented-flip.json`](../../experiments/manifests/EXP-237-jones-period12-augmented-flip.json).

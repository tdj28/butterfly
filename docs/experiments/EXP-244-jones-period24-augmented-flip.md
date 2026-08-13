# EXP-244 — Exact segmented period-24 flip

Status: frozen — not yet executed

EXP-243 supplies one unambiguous real-`-1` bracket on the primitive period-24
branch. EXP-244 initializes from the exact index-2 nodes and solves the
32-segment orbit plus anti-periodic tangent field as one augmented system,
holding `b=0.2` and `c=7.625815600403827` fixed and solving `a` inside the
frozen bracket.

The gates require small orbit, phase, tangent, and normalization residuals;
independent Radau closure and a real-`-1` multiplier; exact `28/32` section
identity; and nonclosure at every proper subperiod. A pass supplies the event
and tangent representation for a separately frozen period-48 switch.

Manifest:
[`../../experiments/manifests/EXP-244-jones-period24-augmented-flip.json`](../../experiments/manifests/EXP-244-jones-period24-augmented-flip.json).

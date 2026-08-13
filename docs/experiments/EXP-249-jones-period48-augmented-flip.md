# EXP-249 — Exact segmented period-48 flip

Status: frozen — not yet executed

EXP-248 supplies one unambiguous real-`-1` bracket on the primitive period-48
branch. EXP-249 initializes from the exact index-2 nodes and solves the
64-segment orbit plus anti-periodic tangent field as one augmented system at
fixed `(b,c)`, with `a` constrained to that bracket.

The gates require small orbit, phase, tangent, and normalization residuals;
independent Radau closure and a real-`-1` multiplier; exact `56/64` section
identity; and nonclosure at every proper subperiod. A pass supplies the event
and tangent representation for a separately frozen period-96 switch.

Manifest:
[`../../experiments/manifests/EXP-249-jones-period48-augmented-flip.json`](../../experiments/manifests/EXP-249-jones-period48-augmented-flip.json).
